"""IdPyOIDC Client Database (CDB) implementation.

This module provides a custom CDB for IdPyOIDC that queries clients from our PostgreSQL database.
IdPyOIDC CDB interface: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#client-database-cdb
"""

from typing import Any, Dict, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker


class OIDCClientDatabase:
    """IdPyOIDC CDB (Client Database) class.
    
    This class provides both dict-like access (cdb[client_id]) and callable access (cdb(client_id))
    to support different IdPyOIDC usage patterns.
    """
    
    def __init__(self, database_url: str) -> None:
        """Initialize CDB with database URL.
        
        Args:
            database_url: PostgreSQL connection URL.
        """
        self._database_url: str = database_url
        self._engine = create_engine(database_url, pool_pre_ping=True)
        self._SessionLocal = sessionmaker(bind=self._engine)
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def __call__(self, client_id: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Callable interface: cdb(client_id)."""
        return self._lookup(client_id)
    
    def __getitem__(self, client_id: str) -> Dict[str, Any]:
        """Dict-like interface: cdb[client_id].
        
        Raises KeyError if client not found (dict-like behavior).
        """
        result = self._lookup(client_id)
        if result is None:
            raise KeyError(f"Client {client_id} not found")
        return result
    
    def get(self, client_id: str, default: Any = None) -> Any:
        """Dict-like get method: cdb.get(client_id, default)."""
        result = self._lookup(client_id)
        return result if result is not None else default

    # --- Minimal mapping / dict-like API for IdPyOIDC compatibility ---

    def keys(self):
        """Return known client_ids (dict-like API).

        IdPyOIDC sometimes expects the CDB to behave like a dict and call .keys().
        For this implementation we only expose keys that have been loaded into the
        in-memory cache so far. This is sufficient for IdPyOIDC's typical usage,
        where direct lookups (cdb[client_id]) are the primary operation.
        """
        return self._cache.keys()

    def items(self):
        """Return (client_id, client_info) pairs for cached clients."""
        return self._cache.items()

    def values(self):
        """Return client_info values for cached clients."""
        return self._cache.values()

    def __contains__(self, client_id: object) -> bool:
        """Support `client_id in cdb` checks."""
        return isinstance(client_id, str) and (client_id in self._cache or self._lookup(client_id) is not None)

    def __iter__(self):
        """Iterate over cached client_ids (dict-like API)."""
        return iter(self._cache)

    def __len__(self) -> int:
        """Number of cached clients."""
        return len(self._cache)
    
    def _lookup(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Internal lookup method."""
        """CDB function for IdPyOIDC.
        
        This function is called by IdPyOIDC to look up client information.
        It must be synchronous.
        
        Args:
            client_id: The client ID to look up.
            **kwargs: Additional arguments (ignored).
            
        Returns:
            Client information dict in IdPyOIDC format, or None if not found.
        """
        print(f"CDB lookup called for client_id: {client_id}")
        
        # Check cache first
        if client_id in self._cache:
            print(f"Client {client_id} found in cache")
            return self._cache[client_id]
        
        try:
            print(f"Querying database for client_id: {client_id}")
            # Query database using raw SQL to avoid ORM annotation issues
            with self._SessionLocal() as session:
                stmt = text("""
                    SELECT 
                        client_id,
                        client_secret,
                        redirect_uris,
                        grant_types,
                        response_types,
                        scopes,
                        client_name,
                        client_uri,
                        logo_uri,
                        tos_uri,
                        policy_uri
                    FROM oauth2_clients
                    WHERE client_id = :client_id
                      AND is_active = TRUE
                """)
                result = session.execute(stmt, {"client_id": client_id}).fetchone()
                
                if not result:
                    print(f"Client {client_id} not found in database")
                    # Debug: Check if any clients exist
                    check_stmt = text("SELECT COUNT(*) as count FROM oauth2_clients WHERE is_active = TRUE")
                    count_result = session.execute(check_stmt).fetchone()
                    print(f"Total active clients in database: {count_result.count if count_result else 0}")
                    return None
                
                # Convert row to IdPyOIDC format
                client_info: Dict[str, Any] = {
                    "client_id": result.client_id,
                    "client_secret": result.client_secret,
                    "redirect_uris": list(result.redirect_uris) if result.redirect_uris else [],
                    "grant_types": list(result.grant_types) if result.grant_types else [],
                    "response_types": list(result.response_types) if result.response_types else [],
                    "scopes": list(result.scopes) if result.scopes else [],
                    "client_name": result.client_name or "",
                    "client_uri": result.client_uri or "",
                    "logo_uri": result.logo_uri or "",
                    "tos_uri": result.tos_uri or "",
                    "policy_uri": result.policy_uri or "",
                }
                
                # Cache it
                self._cache[client_id] = client_info
                
                return client_info
                
        except Exception as e:
            # Log error and return None (client not found)
            import traceback
            print(f"Error looking up client {client_id}: {e}")
            traceback.print_exc()
            return None


def create_oidc_cdb(database_url: str) -> OIDCClientDatabase:
    """Create an IdPyOIDC CDB (Client Database) instance.
    
    This creates a CDB object that supports both dict-like access (cdb[client_id])
    and callable access (cdb(client_id)) to work with different IdPyOIDC usage patterns.
    
    Args:
        database_url: PostgreSQL connection URL.
        
    Returns:
        CDB instance for IdPyOIDC.
    """
    return OIDCClientDatabase(database_url)
