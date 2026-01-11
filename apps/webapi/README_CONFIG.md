# Configuration

The WebAPI application uses a YAML configuration file for settings.

## Configuration File

The configuration file is located at `apps/webapi/config.yml`. 

**Important**: The `config.yml` file is in `.gitignore` - it should not be committed to version control. Use `config.yml.example` as a template.

## Setup

1. Copy the example configuration file:
```bash
cp apps/webapi/config.yml.example apps/webapi/config.yml
```

2. Update the configuration values in `config.yml`:
```yaml
database:
  host: "localhost"
  port: 5432
  database: "auth_server"
  user: "postgres"
  password: "your_password"

application:
  debug: false
  log_level: "INFO"

server:
  host: "0.0.0.0"
  port: 8000
```

## Environment Variable Override

You can override the database connection string using the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

If `DATABASE_URL` is set, it takes precedence over the database configuration in `config.yml`.

## Configuration Structure

### Database Configuration

- `host`: Database host (default: "localhost")
- `port`: Database port (default: 5432)
- `database`: Database name (default: "auth_server")
- `user`: Database user (default: "postgres")
- `password`: Database password (default: "")

### Application Configuration

- `debug`: Debug mode flag (default: false)
- `log_level`: Logging level - DEBUG, INFO, WARNING, ERROR (default: "INFO")

### Server Configuration

- `host`: Server host to bind to (default: "0.0.0.0")
- `port`: Server port (default: 8000)

## Dependency Injection

The configuration is loaded and registered in the DI container as `IAppConfig`. 

Example usage:
```python
from apps.webapi.dependencies import get_config

config = get_config()
database_url = config.get_database_url()
```

The configuration is initialized when the DI container is first accessed via `get_container()`.
