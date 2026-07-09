from app.modules.auth.services import hash_password, verify_password


def test_hash_and_verify_password_roundtrip() -> None:
    hashed = hash_password("Creator@123")
    assert hashed != "Creator@123"
    assert verify_password("Creator@123", hashed) is True
    assert verify_password("WrongPass1", hashed) is False


def test_verify_password_handles_invalid_hash() -> None:
    assert verify_password("Creator@123", None) is False
    assert verify_password("Creator@123", "not-a-bcrypt-hash") is False
