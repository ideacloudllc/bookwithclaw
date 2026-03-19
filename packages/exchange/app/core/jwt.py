"""JWT token generation and verification for agents."""

from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.config import settings


def create_agent_token(agent_id: str, role: str, public_key: str, expires_in: int = 86400) -> str:
    """
    Create JWT token for an agent.
    
    Payload: { agent_id, role, public_key, iat, exp: 24h }
    """
    now = datetime.utcnow()
    expires = now + timedelta(seconds=expires_in)
    
    payload = {
        "agent_id": agent_id,
        "role": role,
        "public_key": public_key,
        "iat": now.timestamp(),
        "exp": expires.timestamp(),
    }
    
    token = jwt.encode(
        payload,
        settings.exchange_secret_key,
        algorithm="HS256"
    )
    return token


def verify_agent_token(token: str) -> dict:
    """
    Verify JWT token and extract payload.
    
    Raises:
        ValueError if token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.exchange_secret_key,
            algorithms=["HS256"]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
