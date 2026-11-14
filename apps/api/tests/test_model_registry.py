import app.models
from app.database.base import Base
from app.models import PasswordResetToken


def test_password_reset_token_is_registered_in_model_metadata():
    assert app.models.PasswordResetToken is PasswordResetToken
    assert Base.metadata.tables["password_reset_tokens"] is PasswordResetToken.__table__
