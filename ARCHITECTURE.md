# Architecture Documentation

## Project Overview

The auth_server solution follows Domain-Driven Design (DDD), Command Query Responsibility Segregation (CQRS), and Dependency Injection/Inversion of Control (DI/IoC) principles.

## Project Structure

```
auth_server/
├── apps/
│   ├── webapi/          # Web API application (Python, IdPyOIDC)
│   └── webui/           # Web UI application (React Redux)
└── libs/
    ├── common/          # Shared utilities and interfaces
    ├── domain/          # Domain layer (business logic)
    ├── application/     # Application layer (orchestration)
    └── infrastructure/  # Infrastructure layer (external concerns)
```

## Architecture Layers

### Common Layer (`libs/common/`)

Shared utilities and interfaces used across all layers:
- **`interfaces.py`** - Core interfaces
- **`enums.py`** - All enum definitions
- **`constants.py`** - Application-wide constants
- **`logger.py`** - Structured logging setup
- **`di_container.py`** - Dependency injection container
- **`di_registry.py`** - DI registration utilities

### Domain Layer (`libs/domain/`)

Pure business logic with no infrastructure dependencies:
- **Entities** - Domain entities representing core business concepts
- **Value Objects** - Immutable value objects
- **Domain Services** - Static services (no DI) for domain logic
- **Domain Factories** - Factories for creating domain entities
- **Domain Errors** - Domain-specific error types

### Application Layer (`libs/application/`)

Orchestration layer that coordinates domain and infrastructure:
- **Commands** - CQRS command pattern (command objects, handlers, dispatcher)
- **Queries** - CQRS query pattern for read operations
- **Mappers** - Layer translation between domain, infrastructure, and DTOs
- **DTOs** - Data Transfer Objects for API boundaries
- **Services** - Application services

### Infrastructure Layer (`libs/infrastructure/`)

Technical implementations and external system integrations:
- **Data Access Objects** - Database ORM models and data access abstractions
- **Database Readers** - Read operations from database
- **Database Writers** - Write operations to database
- **File Readers** - File system operations
- **Services** - Infrastructure services (IdPyOIDC integration, etc.)
- **Database** - Database session management

## Applications

### WebAPI (`apps/webapi/`)

Python-based Web API implementing OpenID Connect Provider using IdPyOIDC:
- **Controllers** - API endpoints
- **Routes** - Route constants
- **Dependencies** - FastAPI dependency injection
- **DI Container** - WebAPI DI container configuration
- **Configuration** - Application configuration

### WebUI (`apps/webui/`)

React Redux Web UI:
- **Components** - React components
- **Store** - Redux store configuration
- **Actions** - Redux actions
- **Reducers** - Redux reducers
- **Services** - API client services

## Key Principles

### 1. Domain-Driven Design (DDD)

- Domain layer contains business logic and entities
- Infrastructure layer handles external concerns (database, file system, external services)
- Application layer orchestrates use cases
- Domain is pure and has no dependencies on infrastructure or application layers

### 2. CQRS (Command Query Responsibility Segregation)

- **Commands** - Modify state (use command handlers)
- **Queries** - Read state (use query services)
- Separate command and query models
- Commands go through: Controller → Command → Command Handler
- Queries go through: Controller → Query → Query Service

### 3. Dependency Injection (DI) / IoC

- Use interfaces for all dependencies
- Register implementations in DI container
- Dependencies flow inward: Infrastructure → Application → Domain
- All interfaces defined in common layer

### 4. Layer Dependencies

**CRITICAL RULES:**
1. **Domain Layer**:
   - ✅ Can depend on: `common/` only
   - ❌ Cannot depend on: `application/`, `infrastructure/`, `apps/`

2. **Application Layer**:
   - ✅ Can depend on: `domain/`, `common/`, `infrastructure/` (via interfaces)
   - ❌ Cannot depend on: `apps/`

3. **Infrastructure Layer**:
   - ✅ Can depend on: `common/` (interfaces, enums, constants)
   - ❌ Cannot depend on: `domain/`, `application/`, `apps/`

4. **Applications (WebAPI/WebUI)**:
   - ✅ Can depend on: `application/` (DTOs, queries, commands), `common/`
   - ❌ Cannot depend on: `domain/`, `infrastructure/` (directly)

5. **Common Layer**:
   - ✅ Can depend on: `common/` only (itself)
   - ❌ Cannot depend on: Any other layer

### 5. DTO Flow (CRITICAL)

**Application boundaries (WebAPI/WebUI) MUST ONLY work with DTOs:**
- Data flow: DAO → Domain (via mapper, optional) → DTO (via mapper) → Controller
- Controllers receive DTOs from query/command services
- DTOs are used directly as response models
- Never expose DAOs or Domain objects to application boundaries

## Naming Conventions

### File Naming
- All Python files use **double underscore** (`__`) to separate words: `user__entity.py`
- This distinguishes from single underscore which is Python's private convention

### Module Organization
Each major domain concept has its own files across layers:
- Entity: `user__entity.py`
- Value Object: `email__value_object.py`
- DAO: `user__db_dao.py`
- Mapper: `user__mapper.py`
- Command: `create_user__command.py`
- Handler: `create_user__command_handler.py`
- Controller: `users__controller.py`

### Function Naming
- All async functions MUST have `_async` suffix: `async def get_user_async(...)`
- Controller methods: `async def get_user_async(...)`
- Query methods: `async def get_user_by_id_async(...)`

## Error Handling

- Domain operations return `Either[Success, DomainError]`
- Domain-specific errors defined in domain layer
- Application layer handles domain errors and converts to appropriate responses

## Value Objects

**IMPORTANT**: Value objects must encapsulate meaningful, composite values, not single fields.

### ❌ DO NOT Create Single-Field Value Objects

Value objects should NOT be created to wrap single primitive fields, even if they include validation logic.

**Bad Examples:**
- `ClientId(value: str)` - Just wraps a string
- `Email(value: str)` - Just wraps a string (even with validation)
- `RedirectUri(value: str)` - Just wraps a string (even with validation)

**Why**: Single-field value objects add unnecessary indirection without providing meaningful domain concepts.

### ✅ DO Create Value Objects for Composite Concepts

Value objects should represent meaningful domain concepts that combine multiple related values or have significant behavior.

**Good Examples:**
- `Money(amount: Decimal, currency: str)` - Represents a monetary value
- `Address(street: str, city: str, postal_code: str, country: str)` - Represents a complete address
- `TimeRange(start: datetime, end: datetime)` - Represents a time period with validation logic
- `Credentials(username: str, password_hash: str)` - Represents authentication credentials

### Validation Rules

- **Single-field validation**: Use validation at the entity or application layer (DTOs, commands)
- **Composite concepts**: Use value objects when multiple fields form a cohesive domain concept
- **Behavior**: Value objects should encapsulate behavior related to the concept, not just data

## When Adding New Features

1. **Domain Logic**: Add to `libs/domain/` (entities, value objects, domain services)
2. **Application Logic**: Add to `libs/application/` (commands, queries, mappers)
3. **Infrastructure**: Add to `libs/infrastructure/` (DAOs, readers, writers, services)
4. **Interfaces**: Define in `libs/common/interfaces.py`
5. **Enums**: Add to `libs/common/enums.py`
6. **Controllers**: Add to `apps/webapi/controllers/` with `_async` suffix
7. **Route Constants**: Define route paths as constants in route files

## Technology Stack

- **Backend**: Python, FastAPI, IdPyOIDC
- **Frontend**: React, Redux
- **Database**: SQLAlchemy (ORM)
- **DI Container**: Custom DI container implementation
- **Type Checking**: mypy
