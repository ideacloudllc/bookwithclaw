"""SendGrid email notifications for settled transactions."""

import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.config import settings
from app.models.session import Session
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


class NotificationManager:
    """Send email notifications via SendGrid."""

    def __init__(self):
        if settings.sendgrid_api_key:
            self.sg = SendGridAPIClient(settings.sendgrid_api_key)
        else:
            self.sg = None
            logger.warning("SendGrid API key not configured; emails will be logged only")

    async def notify_deal_complete(
        self,
        session: Session,
        transaction: Transaction,
        buyer_email: str,
        seller_email: str,
    ) -> bool:
        """
        Send settlement completion emails to both parties.

        Args:
            session: Negotiation session
            transaction: Completed transaction
            buyer_email: Buyer's email address
            seller_email: Seller's email address

        Returns:
            True if emails sent successfully, False otherwise
        """
        booking_ref = transaction.booking_ref
        agreed_price_usd = transaction.agreed_price_cents / 100
        platform_fee_usd = transaction.platform_fee_cents / 100
        seller_payout_usd = transaction.seller_payout_cents / 100

        try:
            # Email to buyer
            buyer_subject = f"Your booking is confirmed — {booking_ref}"
            buyer_body = f"""
Dear Guest,

Your booking has been confirmed!

Booking Reference: {booking_ref}
Amount Charged: ${agreed_price_usd:.2f}
Status: CONFIRMED

Payment has been processed securely through Stripe.

Thank you for choosing BookWithClaw!

Best regards,
BookWithClaw Team
"""
            await self._send_email(buyer_email, buyer_subject, buyer_body)

            # Email to seller
            seller_subject = f"New booking confirmed — {booking_ref}"
            seller_body = f"""
Hello Host,

You have a new booking!

Booking Reference: {booking_ref}
Guest Payment: ${agreed_price_usd:.2f}
Platform Fee: ${platform_fee_usd:.2f}
Your Payout: ${seller_payout_usd:.2f}
Status: CONFIRMED

The payment has been captured and will be transferred to your Stripe account within 1-2 business days.

Best regards,
BookWithClaw Team
"""
            await self._send_email(seller_email, seller_subject, seller_body)

            logger.info(f"Settlement notifications sent for {booking_ref}")
            return True

        except Exception as e:
            logger.error(f"Error sending settlement notifications: {e}")
            return False

    async def notify_settlement_failed(
        self,
        booking_ref: str,
        buyer_email: str,
        seller_email: str,
        reason: str,
    ) -> bool:
        """
        Send settlement failure notification to both parties.

        Args:
            booking_ref: Booking reference
            buyer_email: Buyer's email
            seller_email: Seller's email
            reason: Reason for failure

        Returns:
            True if emails sent successfully, False otherwise
        """
        try:
            # Email to buyer
            buyer_subject = f"Booking confirmation failed — {booking_ref}"
            buyer_body = f"""
Dear Guest,

Unfortunately, we were unable to complete your booking.

Booking Reference: {booking_ref}
Reason: {reason}

Your payment has been cancelled and your funds will be returned within 1-3 business days.

If you have questions, please contact support@bookwithclaw.com

Best regards,
BookWithClaw Team
"""
            await self._send_email(buyer_email, buyer_subject, buyer_body)

            # Email to seller
            seller_subject = f"Booking cancelled — {booking_ref}"
            seller_body = f"""
Hello Host,

A booking request could not be completed.

Booking Reference: {booking_ref}
Reason: {reason}

No payment was processed.

Best regards,
BookWithClaw Team
"""
            await self._send_email(seller_email, seller_subject, seller_body)

            logger.info(f"Settlement failure notifications sent for {booking_ref}")
            return True

        except Exception as e:
            logger.error(f"Error sending settlement failure notifications: {e}")
            return False

    async def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send a single email via SendGrid.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.sg:
            # Log-only mode (dev environment)
            logger.info(f"[EMAIL] To: {to_email}")
            logger.info(f"[EMAIL] Subject: {subject}")
            logger.info(f"[EMAIL] Body: {body}")
            return True

        try:
            message = Mail(
                from_email=settings.sendgrid_from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body,
            )

            response = self.sg.send(message)

            if 200 <= response.status_code < 300:
                logger.info(f"Email sent to {to_email}: {subject}")
                return True
            else:
                logger.error(
                    f"SendGrid error ({response.status_code}) sending to {to_email}"
                )
                return False

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
