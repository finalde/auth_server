"""OAuth2 Client DAO."""

from sqlalchemy import Boolean, Column, String, Table
from sqlalchemy.dialects.postgresql import ARRAY

from libs.infrastructure.data_access_objects.base__db_dao import BaseDAO


class OAuth2ClientDAO(BaseDAO):
    """OAuth2 Client database model."""

    __tablename__ = "oauth2_clients"

    client_id: Column = Column(String(255), unique=True, nullable=False, index=True)
    client_secret: Column = Column(String(255), nullable=False)
    client_name: Column = Column(String(255))
    client_uri: Column = Column(String(512))
    redirect_uris: Column = Column(ARRAY(String))
    grant_types: Column = Column(ARRAY(String))
    response_types: Column = Column(ARRAY(String))
    scopes: Column = Column(ARRAY(String))
    logo_uri: Column = Column(String(512))
    tos_uri: Column = Column(String(512))
    policy_uri: Column = Column(String(512))
    is_active: Column = Column(Boolean, default=True, nullable=False)
