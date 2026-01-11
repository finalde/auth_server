"""Entry point for running webapi as a module: python -m apps.webapi"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    
    # Load config to get host and port
    try:
        from apps.webapi.dependencies import get_config
        config = get_config()
        host = config.get_server_host()
        port = config.get_server_port()
    except Exception:
        # Fallback if config fails
        host = "0.0.0.0"
        port = 8000
    
    # Use import string format to enable reload
    uvicorn.run("apps.webapi.main:app", host=host, port=port, reload=True)
