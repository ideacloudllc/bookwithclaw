"""Stripe Connect escrow and two-phase commit settlement."""

import logging
from datetime import datetime

import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.state_machine import NegotiationStateMachine
from app.models.session import SessionState
from app.models.transaction import Transaction, TransactionStatus

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.stripe_secret_key


class EscrowManager:
    """Manage Stripe Connect escrow and two-phase commit."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_intent(
        self,
        session_id: str,
        buyer_email: str,
        seller_stripe_account: str,
        agreed_price_cents: int,
    ) -> str:
        """
        Create a Stripe PaymentIntent for escrow.

        Args:
            session_id: BookWithClaw session ID
            buyer_email: Buyer's email for receipt
            seller_stripe_account: Seller's Stripe Connect account ID
            agreed_price_cents: Amount in cents

        Returns:
            Stripe PaymentIntent ID
        """
        # Calculate platform fee (in basis points)
        platform_fee_cents = int(agreed_price_cents * settings.platform_fee_bps / 10000)
        seller_payout_cents = agreed_price_cents - platform_fee_cents

        # Generate booking reference
        booking_ref = f"BWCLAW-{session_id[:12].upper()}"

        try:
            intent = stripe.PaymentIntent.create(
                amount=agreed_price_cents,
                currency="usd",
                payment_method_types=["card"],
                confirm=False,  # Don't auto-confirm; require manual confirmation
                capture_method="manual",  # Manual capture for two-phase commit
                metadata={
                    "bookwithclaw_session_id": session_id,
                    "bookwithclaw_booking_ref": booking_ref,
                    "buyer_email": buyer_email,
                },
                application_fee_amount=platform_fee_cents,
                stripe_account=seller_stripe_account,
            )

            logger.info(
                f"Payment intent created for session {session_id}: {intent.id}"
            )
            return intent.id

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            raise

    async def confirm_escrow_funded(self, payment_intent_id: str) -> bool:
        """
        Check if PaymentIntent is in escrow (Phase 1).

        Status == 'requires_capture' means funds are authorized and escrowed.

        Args:
            payment_intent_id: Stripe PaymentIntent ID

        Returns:
            True if escrowed, False otherwise
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == "requires_capture":
                logger.info(f"Payment {payment_intent_id} escrowed successfully")
                return True
            else:
                logger.warning(
                    f"Payment {payment_intent_id} status: {intent.status} (expected requires_capture)"
                )
                return False

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error checking escrow: {e}")
            return False

    async def capture_payment(self, payment_intent_id: str) -> bool:
        """
        Capture escrowed payment (Phase 2).

        This releases funds to the seller and marks settlement as COMPLETE.

        Args:
            payment_intent_id: Stripe PaymentIntent ID

        Returns:
            True if captured successfully, False otherwise
        """
        try:
            intent = stripe.PaymentIntent.capture(payment_intent_id)

            if intent.status == "succeeded":
                logger.info(f"Payment {payment_intent_id} captured successfully")
                return True
            else:
                logger.warning(f"Payment {payment_intent_id} capture status: {intent.status}")
                return False

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error capturing payment: {e}")
            return False

    async def cancel_payment_intent(self, payment_intent_id: str) -> bool:
        """
        Cancel and release escrowed payment (settlement failure).

        Args:
            payment_intent_id: Stripe PaymentIntent ID

        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            intent = stripe.PaymentIntent.cancel(payment_intent_id)

            if intent.status == "canceled":
                logger.info(f"Payment {payment_intent_id} cancelled successfully")
                return True
            else:
                logger.warning(f"Payment {payment_intent_id} cancel status: {intent.status}")
                return False

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling payment: {e}")
            return False

    async def settle_transaction(
        self,
        session_id: str,
        buyer_agent_id: str,
        seller_agent_id: str,
        agreed_price_cents: int,
        seller_stripe_account: str,
        buyer_email: str,
    ) -> dict:
        """
        Execute full settlement: Phase 1 (escrow) + Phase 2 (capture).

        Args:
            session_id: BookWithClaw session ID
            buyer_agent_id: Buyer agent UUID
            seller_agent_id: Seller agent UUID
            agreed_price_cents: Agreed price in cents
            seller_stripe_account: Seller's Stripe Connect account
            buyer_email: Buyer's email for receipt

        Returns:
            Dict with transaction status:
            {
                "success": bool,
                "transaction_id": str (if successful),
                "error": str (if failed),
                "payment_intent_id": str,
                "booking_ref": str,
            }
        """
        # Calculate fees
        platform_fee_cents = int(
            agreed_price_cents * settings.platform_fee_bps / 10000
        )
        seller_payout_cents = agreed_price_cents - platform_fee_cents
        booking_ref = f"BWCLAW-{session_id[:12].upper()}"

        try:
            # Phase 1: Create PaymentIntent (escrow)
            payment_intent_id = await self.create_payment_intent(
                session_id,
                buyer_email,
                seller_stripe_account,
                agreed_price_cents,
            )

            # Create transaction record (PENDING)
            transaction_id = f"txn-{session_id[:12]}"
            transaction = Transaction(
                transaction_id=transaction_id,
                session_id=session_id,
                booking_ref=booking_ref,
                buyer_agent_id=buyer_agent_id,
                seller_agent_id=seller_agent_id,
                agreed_price_cents=agreed_price_cents,
                platform_fee_cents=platform_fee_cents,
                seller_payout_cents=seller_payout_cents,
                status=TransactionStatus.PENDING,
                stripe_payment_intent_id=payment_intent_id,
            )
            self.db.add(transaction)
            await self.db.commit()

            # Check Phase 1: Escrow funded
            is_escrowed = await self.confirm_escrow_funded(payment_intent_id)
            if not is_escrowed:
                transaction.status = TransactionStatus.FAILED
                await self.db.commit()
                return {
                    "success": False,
                    "error": "Escrow not funded",
                    "payment_intent_id": payment_intent_id,
                }

            transaction.status = TransactionStatus.ESCROW_LOCKED
            await self.db.commit()

            logger.info(f"Settlement {booking_ref}: Phase 1 (escrow) complete")

            # Phase 2: Capture payment
            is_captured = await self.capture_payment(payment_intent_id)
            if not is_captured:
                transaction.status = TransactionStatus.FAILED
                await self.db.commit()
                return {
                    "success": False,
                    "error": "Capture failed",
                    "payment_intent_id": payment_intent_id,
                }

            transaction.status = TransactionStatus.CAPTURED
            transaction.completed_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"Settlement {booking_ref}: Phase 2 (capture) complete")

            return {
                "success": True,
                "transaction_id": transaction_id,
                "payment_intent_id": payment_intent_id,
                "booking_ref": booking_ref,
            }

        except Exception as e:
            logger.error(f"Settlement error for {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
