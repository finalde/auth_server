"""Test Application - Calls Resource Server.

This Python script demonstrates calling both public and protected endpoints
on the resource server using OAuth2 client credentials flow.

Usage:
    python test_clients/test_app/main.py
"""

import asyncio
import sys
from typing import Optional

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client


# Configuration
AUTH_SERVER_URL: str = "http://localhost:8000"
RESOURCE_SERVER_URL: str = "http://localhost:8001"
CLIENT_ID: str = "test_client"
CLIENT_SECRET: str = "test_secrets"
SCOPE: str = "openid read write"


async def get_access_token() -> Optional[str]:
    """Get access token using client credentials flow.
    
    Returns:
        Access token string if successful, None otherwise.
    """
    try:
        # Fetch discovery document manually for better compatibility
        discovery_url = f"{AUTH_SERVER_URL}/.well-known/openid-configuration"
        async with httpx.AsyncClient() as http_client:
            discovery_resp = await http_client.get(discovery_url, timeout=10)
            discovery_resp.raise_for_status()
            discovery_data = discovery_resp.json()
            
            token_endpoint = discovery_data.get("token_endpoint")
            if not token_endpoint:
                print("❌ Error: No token_endpoint in discovery document")
                return None
            
            print(f"   ✓ Discovery successful")
            print(f"   ✓ Token endpoint: {token_endpoint}")
        
        # Create OAuth2 client
        client = AsyncOAuth2Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
        )
        
        # Get token using client credentials flow
        token_response = await client.fetch_token(
            token_endpoint,
            grant_type="client_credentials",
        )
        
        access_token: str = token_response.get("access_token")
        if not access_token:
            print("❌ Error: No access token in response")
            print(f"Response: {token_response}")
            return None
        
        print(f"✅ Successfully obtained access token")
        print(f"   Token type: {token_response.get('token_type', 'Bearer')}")
        print(f"   Expires in: {token_response.get('expires_in', 'unknown')} seconds")
        print(f"\n   📋 Token Details:")
        print(f"   Full access token: {access_token}")
        
        # Decode token header to show details
        try:
            import base64
            import json
            parts = access_token.split('.')
            if len(parts) >= 2:
                header = json.loads(base64.urlsafe_b64decode(parts[0] + '==').decode())
                payload = json.loads(base64.urlsafe_b64decode(parts[1] + '==').decode())
                print(f"   Token header: {json.dumps(header, indent=6)}")
                print(f"   Token payload (iss): {payload.get('iss')}")
                print(f"   Token payload (kid in header): {header.get('kid')}")
        except Exception as e:
            print(f"   Could not decode token: {e}")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Error getting access token: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def call_public_endpoint() -> None:
    """Call the public endpoint (no authentication required)."""
    print("\n" + "="*60)
    print("📞 Calling PUBLIC endpoint (no auth required)")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RESOURCE_SERVER_URL}/")
            response.raise_for_status()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response:")
            import json
            print(json.dumps(response.json(), indent=2))
            
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def call_protected_endpoint(access_token: str) -> None:
    """Call the protected endpoint (requires authentication).
    
    Args:
        access_token: OAuth2 access token.
    """
    print("\n" + "="*60)
    print("🔒 Calling PROTECTED endpoint (auth required)")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            response = await client.get(
                f"{RESOURCE_SERVER_URL}/protected",
                headers=headers,
            )
            response.raise_for_status()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response:")
            import json
            print(json.dumps(response.json(), indent=2))
            
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def call_protected_data_endpoint(access_token: str) -> None:
    """Call the protected /api/data endpoint.
    
    Args:
        access_token: OAuth2 access token.
    """
    print("\n" + "="*60)
    print("📊 Calling PROTECTED /api/data endpoint")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            response = await client.get(
                f"{RESOURCE_SERVER_URL}/api/data",
                headers=headers,
            )
            response.raise_for_status()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response:")
            import json
            print(json.dumps(response.json(), indent=2))
            
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def main() -> None:
    """Main test function."""
    print("="*60)
    print("🧪 OAuth2/OIDC Test Application")
    print("="*60)
    print(f"Auth Server: {AUTH_SERVER_URL}")
    print(f"Resource Server: {RESOURCE_SERVER_URL}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Scope: {SCOPE}")
    
    # Step 1: Call public endpoint (no auth)
    await call_public_endpoint()
    
    # Step 2: Get access token
    print("\n" + "="*60)
    print("🔑 Getting access token (client credentials flow)")
    print("="*60)
    access_token = await get_access_token()
    
    if not access_token:
        print("\n❌ Failed to get access token. Cannot test protected endpoints.")
        sys.exit(1)
    
    # Step 3: Call protected endpoint
    await call_protected_endpoint(access_token)
    
    # Step 4: Call protected data endpoint
    await call_protected_data_endpoint(access_token)
    
    print("\n" + "="*60)
    print("✅ Test completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
