"""Send email tool using Power Automate flow webhook."""
import os
import re
from typing import Any

import httpx

# Constants
_EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
_MAX_SUBJECT_LENGTH = 500
_MAX_BODY_LENGTH = 50000
_ERROR_TEXT_TRUNCATE_LENGTH = 200


async def send_email_tool(
    to_email: str, subject: str, body: str
) -> dict[str, Any]:
    """
    Send an email by triggering a Power Automate flow via HTTP POST webhook.

    This tool sends an HTTP POST request to a Power Automate flow webhook URL
    with the email details. The webhook URL must be configured via the
    POWER_AUTOMATE_WEBHOOK_URL environment variable.

    Args:
        to_email: Recipient's email address (required, must be valid email format)
        subject: Email subject (required, max 500 characters)
        body: Email body content (required, max 50,000 characters)

    Returns:
        Dictionary with success status and details:
        - success: Boolean indicating if email was sent successfully
        - message: Description of the result
        - error: Error message if applicable

    Example:
        >>> result = await send_email_tool(
        ...     to_email="user@example.com",
        ...     subject="Meeting Summary",
        ...     body="Here is the summary of our meeting..."
        ... )
        >>> print(result)
        {'success': True, 'message': 'Email sent successfully'}

    Schema for input parameters:
        {
            "to_email": "string (required)",
            "subject": "string (required)",
            "body": "string (required)"
        }
    """
    # Get webhook URL from environment variable
    webhook_url = os.getenv("POWER_AUTOMATE_WEBHOOK_URL")
    if not webhook_url:
        return {
            "success": False,
            "error": (
                "Power Automate webhook URL not configured. "
                "Please set POWER_AUTOMATE_WEBHOOK_URL environment variable."
            ),
        }

    # Validate to_email
    if not isinstance(to_email, str):
        return {
            "success": False,
            "error": "to_email is required and must be a string",
        }

    to_email = to_email.strip()
    if not to_email or not re.match(_EMAIL_PATTERN, to_email):
        return {
            "success": False,
            "error": f"Invalid email format: {to_email if to_email else '(empty)'}",
        }

    # Validate subject
    if not isinstance(subject, str):
        return {
            "success": False,
            "error": "subject is required and must be a string",
        }

    subject = subject.strip()
    if not subject:
        return {
            "success": False,
            "error": "subject cannot be empty",
        }

    if len(subject) > _MAX_SUBJECT_LENGTH:
        return {
            "success": False,
            "error": f"subject exceeds maximum length of {_MAX_SUBJECT_LENGTH} characters",
        }

    # Validate body
    if not isinstance(body, str):
        return {
            "success": False,
            "error": "body is required and must be a string",
        }

    body = body.strip()
    if not body:
        return {
            "success": False,
            "error": "body cannot be empty",
        }

    if len(body) > _MAX_BODY_LENGTH:
        return {
            "success": False,
            "error": f"body exceeds maximum length of {_MAX_BODY_LENGTH} characters",
        }

    # Prepare payload for Power Automate
    payload = {
        "to_email": to_email,
        "subject": subject,
        "body": body,
    }

    # Send HTTP POST request to Power Automate webhook
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()

            return {
                "success": True,
                "message": "Email sent successfully",
                "to_email": to_email,
                "subject": subject,
            }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": (
                f"Power Automate webhook error: {e.response.status_code} - "
                f"{e.response.text[:_ERROR_TEXT_TRUNCATE_LENGTH]}"
            ),
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Network error connecting to Power Automate: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error sending email: {str(e)}",
        }
