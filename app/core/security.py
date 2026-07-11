import bcrypt


def hash_password(password: str) -> str:
    if not password.strip():
        raise ValueError("Password cannot be empty")

    try:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except:
        raise


def verify_password(password: str, hashed_password: str) -> bool:
    if not password.strip() or not hashed_password.strip():
        raise ValueError("Password cannot be empty")

    return bcrypt.checkpw(password.encode(), hashed_password.encode())
