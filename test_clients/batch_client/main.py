"""Batch Client - Python script using Client Credentials Flow.

This batch client uses the Client Credentials flow via Authlib to get an access token
and then accesses protected resources from the resource server.
"""

import asyncio
import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

# Configuration
AUTH_SERVER_URL = "http://localhost:8000"
RESOURCE_SERVER_URL = "http://localhost:8001"
CLIENT_ID = "batch_client"
CLIENT_SECRET = "batch_secret"  # In production, use environment variables or secrets manager


async def main() -> None:
    """Main batch client function."""
    print("Batch Client - Client Credentials Flow (Authlib)")
    print("=" * 50)

    try:
        # Initialize OAuth2 client with discovery
        print("\n1. Initializing OAuth2 client with OIDC Discovery...")
        client = AsyncOAuth2Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope="api:read",  # Request appropriate scopes
        )
        
        # Load server metadata via discovery
        await client.load_server_metadata(
            f"{AUTH_SERVER_URL}/.well-known/openid-configuration"
        )
        print(f"   ✓ Discovery successful")
        print(f"   ✓ Issuer: {client.metadata.get('issuer')}")
        print(f"   ✓ Token endpoint: {client.metadata.get('token_endpoint')}")

        # Get access token using client credentials flow
        print("\n2. Requesting access token using Client Credentials flow...")
        token_response = await client.fetch_token(
            grant_type="client_credentials"
        )
        access_token = token_response.get("access_token")
        print(f"   ✓ Access token obtained: {access_token[:20] if access_token else 'N/A'}...")
        print(f"   ✓ Token type: {token_response.get('token_type')}")
        print(f"   ✓ Expires in: {token_response.get('expires_in')} seconds")

        # Access protected resource
        print("\n3. Accessing protected resource...")
        async with httpx.AsyncClient() as http_client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await http_client.get(
                f"{RESOURCE_SERVER_URL}/api/data", headers=headers, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Resource accessed successfully")
                print(f"   Data: {data}")
            else:
                print(f"   ✗ Failed to access resource: {response.status_code}")
                print(f"   Response: {response.text}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
