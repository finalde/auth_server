# Setup Instructions

## Installation

To use the authorization library and other modules in test clients, install the package in editable mode:

```bash
# From project root
pip install -e .
```

This makes all modules (`libs`, `apps`, `test_clients`) available for import without modifying `sys.path`.

## Running Test Clients

After installation, you can run test clients from anywhere:

```bash
# Resource server
python test_clients/resource_server/main.py

# Test app
python test_clients/test_app/main.py
```

## Alternative: Run as Module

If you prefer not to install, you can run scripts as modules from the project root:

```bash
# Resource server
python -m test_clients.resource_server.main

# Test app
python -m test_clients.test_app.main
```

## Development

For development, editable installation is recommended as it:
- Makes imports work consistently
- Allows code changes without reinstallation
- Works with IDEs and linters
- Follows Python packaging best practices
