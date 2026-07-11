from email_validator import validate_email as ev_validate_email, EmailNotValidError


def validate_email(email: str) -> str:
    if not email or not email.strip():
        raise ValueError("Email cannot be empty.")

    try:
        valid_email = ev_validate_email(email)
        return valid_email.normalized
    except EmailNotValidError as error:
        raise ValueError(error)


def validate_password(password: str) -> str:
    if not password or not password.strip() or len(password.strip()) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    return password
