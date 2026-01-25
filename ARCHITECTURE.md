# Architecture Documentation

**This is the single source of truth for all architectural decisions, patterns, and conventions.**

**MANDATORY: Always read this document before writing any code.**

## Project Overview

The auth_server solution follows Domain-Driven Design (DDD), Command Query Responsibility Segregation (CQRS), and Dependency Injection/Inversion of Control (DI/IoC) principles using the `dependency-injector` library.

## Project Structure

```
auth_server/
├── apps/
│   ├── webapi/          # Web API application (Python, IdPyOIDC)
│   └── auth_ui/         # Admin UI application (React SPA for managing clients, users, resources)
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

### AuthUI (`apps/auth_ui/`)

React SPA Admin UI for managing the auth server:
- **Components** - React components for CRUD operations
- **Store** - State management (Redux or similar)
- **Services** - API client services for WebAPI endpoints
- **Features**:
  - Manage OAuth2 clients (create, update, delete, view)
  - Manage users (create, update, delete, view)
  - Manage resources (create, update, delete, view)
  - Manage scopes (create, update, delete, view)
  - Grant user access to resources/scopes
  - Admin operations and permissions management

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

- **Library**: Use `dependency-injector` library for all DI
- **No Direct Instantiation**: All services, readers, writers, queries, commands MUST be injected via DI container
- **Interfaces First**: All dependencies are defined as interfaces in `libs/common/interfaces.py`
- **Registration**: Services registered in application-specific containers (e.g., `apps/webapi/di_container.py`)
- **Dependencies Flow Inward**: Infrastructure → Application → Domain
- **Domain Layer**: NO dependency injection (pure business logic, stateless)
- **Infrastructure Layer**: Dependencies injected via constructor (database session, etc.)
- **Application Layer**: All dependencies injected via constructor (readers, writers, mappers)
- **Application Boundaries**: FastAPI `Depends()` resolves from DI container

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

4. **Applications (WebAPI/AuthUI)**:
   - ✅ Can depend on: `application/` (DTOs, queries, commands), `common/`
   - ❌ Cannot depend on: `domain/`, `infrastructure/` (directly)

5. **Common Layer**:
   - ✅ Can depend on: `common/` only (itself)
   - ❌ Cannot depend on: Any other layer

### 5. DTO Flow (CRITICAL)

**Application boundaries (WebAPI/AuthUI) MUST ONLY work with DTOs:**
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

### Step-by-Step Process

1. **Define Interface** (in `libs/common/interfaces.py`):
   ```python
   class IClientReader(ABC):
       @abstractmethod
       async def get_by_id_async(self, client_id: str) -> Optional[ClientDAO]:
           pass
   ```

2. **Implement Infrastructure** (in `libs/infrastructure/db_readers/client__reader.py`):
   ```python
   class ClientReader(IClientReader):
       def __init__(self, session: Session):  # Session injected via DI
           self._session = session
   ```

3. **Implement Application Query** (in `libs/application/queries/client_query.py`):
   ```python
   class ClientQuery(IClientQuery):
       def __init__(self, reader: IClientReader, mapper: ClientMapper):  # Both injected via DI
           self._reader = reader
           self._mapper = mapper
   ```

4. **Register in DI Container** (in `apps/webapi/di_container.py`):
   ```python
   # Database session (singleton or factory per request)
   database_session = providers.Factory(create_session, config=app_config)
   
   # Infrastructure: Reader
   client_reader = providers.Factory(
       ClientReader,
       session=database_session,
   )
   
   # Application: Mapper (singleton - stateless)
   client_mapper = providers.Singleton(ClientMapper)
   
   # Application: Query
   client_query = providers.Factory(
       ClientQuery,
       reader=client_reader,
       mapper=client_mapper,
   )
   ```

5. **Create FastAPI Dependency** (in `apps/webapi/dependencies.py`):
   ```python
   def get_client_query() -> IClientQuery:
       container = get_container()
       return container.client_query()
   ```

6. **Use in Controller** (in `apps/webapi/controllers/clients__controller.py`):
   ```python
   @router.get("/")
   async def get_all_clients_async(
       query: IClientQuery = Depends(get_client_query),  # Use dependency function
   ) -> List[ClientDTO]:
       return await query.get_all_async()
   ```

### Checklist

- ✅ Interface defined in `libs/common/interfaces.py`
- ✅ Implementation in appropriate layer (infrastructure/application)
- ✅ All dependencies injected via constructor (no direct instantiation)
- ✅ Registered in DI container (`apps/webapi/di_container.py`)
- ✅ FastAPI dependency function created (`apps/webapi/dependencies.py`)
- ✅ Controller uses `Depends(dependency_function)` not `Depends(Interface)`
- ✅ Layer dependencies respected (Domain → Common only, etc.)
- ✅ Data representation correct (DAO in infrastructure, Entity/ValueObject in domain, DTO in application)

## Dependency Injection (DI) / Inversion of Control (IoC)

### DI Library

This project uses **`dependency-injector`** library for dependency injection. All dependencies MUST be injected through the DI container, never instantiated directly.

### DI Principles

1. **All Dependencies Through DI**: No direct instantiation of services, readers, writers, or mappers
2. **Interfaces First**: All dependencies are defined as interfaces in `libs/common/interfaces.py`
3. **Layer-Specific Containers**: Each application (WebAPI, Batch, etc.) has its own DI container configuration
4. **Registration in Application Layer**: DI container configuration happens at the application boundary

### DI Container Structure

```
libs/common/
  └── di_container.py          # Base DI container using dependency-injector

apps/webapi/
  └── di_container.py          # WebAPI-specific DI container configuration
```

### Dependency Registration Patterns

#### Singleton Registration
For services that should have a single instance (configuration, logger, database session):
```python
container.singleton(IAppConfig, WebAPIConfig)
container.singleton(ILogger, Logger)
```

#### Factory Registration
For services that need to be created per request (readers, writers, queries):
```python
container.factory(IClientReader, ClientReader)
container.factory(IClientQuery, ClientQuery)
```

#### Provider Registration
For complex dependencies that need other services injected:
```python
container.provides(IClientQuery)(
    ClientQuery,
    reader=Provide[IClientReader],
    mapper=Provide[ClientMapper]
)
```

### Dependency Injection Rules

1. **Domain Layer**: 
   - NO dependency injection (pure business logic)
   - Entities, value objects, domain services are stateless or use static methods

2. **Infrastructure Layer**:
   - Dependencies injected via constructor
   - Implements interfaces from `common/interfaces.py`
   - Example: `ClientReader(IClientReader)` receives database session via DI

3. **Application Layer**:
   - All dependencies injected via constructor
   - Queries receive readers and mappers via DI
   - Commands receive writers and mappers via DI
   - Example: `ClientQuery(reader: IClientReader, mapper: ClientMapper)`

4. **Application Boundaries (WebAPI/AuthUI)**:
   - Controllers receive queries/commands via FastAPI `Depends()`
   - FastAPI dependencies resolve from DI container
   - Example: `async def get_clients(query: IClientQuery = Depends(get_client_query))`

### Example: Complete DI Flow

```python
# 1. Interface defined in libs/common/interfaces.py
class IClientReader(ABC):
    @abstractmethod
    async def get_by_id_async(self, client_id: str) -> Optional[ClientDAO]:
        pass

# 2. Implementation in libs/infrastructure/db_readers/client__reader.py
class ClientReader(IClientReader):
    def __init__(self, session: Session):
        self._session = session  # Injected via DI
    
    async def get_by_id_async(self, client_id: str) -> Optional[ClientDAO]:
        # Implementation

# 3. Query in libs/application/queries/client_query.py
class ClientQuery(IClientQuery):
    def __init__(self, reader: IClientReader, mapper: ClientMapper):
        self._reader = reader  # Injected via DI
        self._mapper = mapper  # Injected via DI

# 4. Registration in apps/webapi/di_container.py
container.factory(IClientReader, ClientReader)
container.provides(IClientQuery)(
    ClientQuery,
    reader=Provide[IClientReader],
    mapper=Provide[ClientMapper]
)

# 5. FastAPI dependency in apps/webapi/dependencies.py
def get_client_query() -> IClientQuery:
    return container.resolve(IClientQuery)

# 6. Controller usage
@router.get("/clients")
async def get_clients(query: IClientQuery = Depends(get_client_query)):
    return await query.get_all_async()
```

### CQRS with DI

#### Read Operations (Queries)
- **Query Interface**: `IClientQuery` in `libs/application/queries/`
- **Query Implementation**: `ClientQuery` receives `IClientReader` and `Mapper` via DI
- **Reader Interface**: `IClientReader` in `libs/common/interfaces.py`
- **Reader Implementation**: `ClientReader` in `libs/infrastructure/db_readers/` receives database session via DI

#### Write Operations (Commands)
- **Command Object**: `CreateClientCommand` in `libs/application/commands/command_objects/`
- **Command Handler**: `CreateClientCommandHandler` receives `IClientWriter` and `Mapper` via DI
- **Writer Interface**: `IClientWriter` in `libs/common/interfaces.py`
- **Writer Implementation**: `ClientWriter` in `libs/infrastructure/db_writers/` receives database session via DI

## Technology Stack

- **Backend**: Python, FastAPI, IdPyOIDC
- **Frontend**: React, Redux
- **Database**: SQLAlchemy (ORM)
- **DI Container**: `dependency-injector` library
- **Type Checking**: mypy
