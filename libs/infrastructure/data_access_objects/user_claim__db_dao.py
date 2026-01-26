"""UserClaim DAO for user_claims table."""

from sqlalchemy import Boolean, Column, String, Text

from libs.infrastructure.data_access_objects.base__db_dao import BaseDAO


class UserClaimDAO(BaseDAO):
    """User claim database model."""

    __tablename__ = "user_claims"

    user_id = Column(String(36), nullable=False, index=True)
    claim_name = Column(String(255), nullable=False, index=True)
    claim_value = Column(Text, nullable=False)
    claim_type = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

