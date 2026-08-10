from app.core.config import settings
from app.security import create_session, hash_password, read_session, verify_password


def test_password_hash_roundtrip():
    encoded = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong password", encoded)


def test_signed_session_roundtrip(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", "test-secret-key")
    token = create_session("admin")
    assert read_session(token) == "admin"
    assert read_session("tampered-token") is None
