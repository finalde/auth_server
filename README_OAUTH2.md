# OAuth2 Management System

This document describes the OAuth2 management system implementation with CRUD endpoints.

## Overview

The OAuth2 management system provides CRUD (Create, Read, Update, Delete) operations for:
- **OAuth2 Clients** - Client applications that use OAuth2
- **Users** - User accounts
- **Resources** - APIs/resources protected by OAuth2
- **Scopes** - OAuth2 scopes/permissions

## Architecture

The system follows Domain-Driven Design (DDD), CQRS, and DI/IoC principles:

### Domain Layer
- **Entities**: `OAuth2Client`, `User`, `Resource`, `Scope`
- **Value Objects**: `ClientId`, `Email`, `RedirectUri`

### Application Layer
- **DTOs**: Request/Response data transfer objects
- **Commands**: Create, Update, Delete operations
- **Queries**: Read operations
- **Mappers**: Layer translation between domain, DAO, and DTO

### Infrastructure Layer
- **DAOs**: Database models (SQLAlchemy)
- **Readers**: Database read operations
- **Writers**: Database write operations

### Controllers
- **CRUD Endpoints**: RESTful API endpoints

## API Endpoints

### Clients

- `GET /api/v1/clients` - Get all clients
- `GET /api/v1/clients/{client_id}` - Get client by ID
- `POST /api/v1/clients` - Create new client
- `PUT /api/v1/clients/{client_id}` - Update client
- `DELETE /api/v1/clients/{client_id}` - Delete client

### Users

- `GET /api/v1/users` - Get all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Resources

- `GET /api/v1/resources` - Get all resources
- `GET /api/v1/resources/{resource_id}` - Get resource by ID
- `POST /api/v1/resources` - Create new resource
- `PUT /api/v1/resources/{resource_id}` - Update resource
- `DELETE /api/v1/resources/{resource_id}` - Delete resource

### Scopes

- `GET /api/v1/scopes` - Get all scopes
- `GET /api/v1/scopes/{scope_name}` - Get scope by name
- `POST /api/v1/scopes` - Create new scope
- `DELETE /api/v1/scopes/{scope_name}` - Delete scope

## Implementation Status

✅ Domain entities and value objects
✅ DTOs for all entities
✅ Command objects (Create, Update, Delete)
✅ Mappers between layers
✅ Database DAOs
✅ Controller structure

⏳ Command handlers (in progress)
⏳ Query implementations (in progress)
⏳ Infrastructure readers/writers (in progress)
⏳ Database session management (in progress)

## Next Steps

1. Implement command handlers for all commands
2. Complete query implementations
3. Implement infrastructure readers and writers
4. Set up database session management
5. Integrate with IdPyOIDC
6. Add authentication/authorization
7. Implement proper error handling
8. Add input validation
9. Add unit tests
10. Add integration tests
