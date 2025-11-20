# Estructura Proyecto

## Arquitectura: Clean Architecture + DDD + SOLID + FastAPI + PostgreSQL + Redis

```
project-root/
│
├── pyproject.toml                      # Configuración de Poetry (dependencias)
├── poetry.lock                         # Lock file de Poetry
├── README.md                           # Documentación principal del proyecto
├── CLAUDE.md                           # 🆕 Buenas prácticas y guía de desarrollo
├── .env.example                        # Variables de entorno de ejemplo
├── .gitignore                          # Archivos ignorados por Git
├── docker-compose.yml                  # Configuración de Docker (PostgreSQL + Redis)
│
├── src/
│   └── app/
│       ├── __init__.py
│       │
│       ├── domain/                     # 🔵 CAPA DE DOMINIO (DDD Core)
│       │   ├── __init__.py             # Núcleo de la lógica de negocio
│       │   │                           # NO tiene dependencias de otras capas
│       │   │                           # Define interfaces que otros implementan
│       │   │
│       │   ├── entities/               # Entidades con identidad única
│       │   │   ├── __init__.py         # Objetos con ciclo de vida
│       │   │   ├── user.py             # Entidad User (id, propiedades mutables)
│       │   │   ├── order.py            # Entidad Order
│       │   │   └── product.py          # Entidad Product
│       │   │
│       │   ├── value_objects/          # Value Objects (inmutables, sin identidad)
│       │   │   ├── __init__.py         # Objetos que se comparan por valor
│       │   │   ├── email.py            # VO: Email (validación, formato)
│       │   │   ├── phone.py            # VO: Phone
│       │   │   ├── money.py            # VO: Money (amount + currency)
│       │   │   ├── user_id.py          # VO: UserId (UUID wrapper)
│       │   │   └── address.py          # VO: Address (street, city, country)
│       │   │
│       │   ├── aggregates/             # Agregados (raíces de consistencia transaccional)
│       │   │   ├── __init__.py         # Agrupan entidades relacionadas
│       │   │   ├── user_aggregate.py   # Raíz: User + sus entidades relacionadas
│       │   │   └── order_aggregate.py  # Raíz: Order + OrderItems
│       │   │
│       │   ├── repositories/           # Interfaces de repositorios (abstracciones)
│       │   │   ├── __init__.py         # Define QUÉ operaciones, NO CÓMO
│       │   │   ├── user_repository.py  # Interface: save(), find_by_id(), etc.
│       │   │   ├── order_repository.py # Infrastructure las implementará
│       │   │   └── product_repository.py
│       │   │
│       │   ├── services/               # Domain Services (lógica que no pertenece a una entidad)
│       │   │   ├── __init__.py         # Operaciones entre múltiples entidades
│       │   │   ├── user_domain_service.py   # Ej: validar email único
│       │   │   └── order_domain_service.py  # Ej: calcular precio total con reglas complejas
│       │   │
│       │   ├── events/                 # Domain Events (hechos importantes del dominio)
│       │   │   ├── __init__.py         # Notifican cambios de estado
│       │   │   ├── base_event.py       # Clase base para eventos
│       │   │   ├── user_created.py     # Evento: usuario creado
│       │   │   ├── user_updated.py     # Evento: usuario actualizado
│       │   │   ├── order_placed.py     # Evento: orden colocada
│       │   │   └── order_completed.py  # Evento: orden completada
│       │   │
│       │   ├── specifications/         # Specifications Pattern (reglas de negocio encapsuladas)
│       │   │   ├── __init__.py         # Criterios de selección reutilizables
│       │   │   ├── base_specification.py
│       │   │   ├── user_specifications.py   # Ej: UserIsActive, UserIsVerified
│       │   │   └── order_specifications.py  # Ej: OrderIsPending, OrderIsExpired
│       │   │
│       │   └── exceptions/             # Excepciones del dominio
│       │       ├── __init__.py         # Errores específicos de negocio
│       │       ├── domain_exception.py # Excepción base del dominio
│       │       ├── user_exceptions.py  # UserNotFoundException, UserAlreadyExistsException
│       │       └── order_exceptions.py # OrderNotFoundException, InvalidOrderException
│       │
│       ├── application/                # 🟢 CAPA DE APLICACIÓN (Casos de Uso)
│       │   ├── __init__.py             # Orquesta el dominio
│       │   │                           # Coordina flujos de trabajo
│       │   │                           # Usa Domain + Infrastructure
│       │   │
│       │   ├── use_cases/              # Casos de uso (Application Services)
│       │   │   ├── __init__.py         # Un caso de uso = una acción del usuario
│       │   │   │
│       │   │   ├── user/               # Casos de uso de User
│       │   │   │   ├── __init__.py
│       │   │   │   ├── create_user.py      # UC: Crear usuario
│       │   │   │   ├── update_user.py      # UC: Actualizar usuario
│       │   │   │   ├── delete_user.py      # UC: Eliminar usuario
│       │   │   │   ├── get_user.py         # UC: Obtener usuario
│       │   │   │   └── list_users.py       # UC: Listar usuarios
│       │   │   │
│       │   │   ├── order/              # Casos de uso de Order
│       │   │   │   ├── __init__.py
│       │   │   │   ├── create_order.py     # UC: Crear orden
│       │   │   │   ├── update_order.py     # UC: Actualizar orden
│       │   │   │   ├── cancel_order.py     # UC: Cancelar orden
│       │   │   │   ├── get_order.py        # UC: Obtener orden
│       │   │   │   └── list_orders.py      # UC: Listar órdenes
│       │   │   │
│       │   │   └── product/            # Casos de uso de Product
│       │   │       ├── __init__.py
│       │   │       ├── create_product.py   # UC: Crear producto
│       │   │       ├── update_product.py   # UC: Actualizar producto
│       │   │       ├── get_product.py      # UC: Obtener producto
│       │   │       └── list_products.py    # UC: Listar productos
│       │   │
│       │   ├── dtos/                   # DTOs (Data Transfer Objects)
│       │   │   ├── __init__.py         # Objetos para transferir datos entre capas
│       │   │   ├── user_dto.py         # CreateUserDTO, UpdateUserDTO, UserDTO
│       │   │   ├── order_dto.py        # CreateOrderDTO, OrderDTO
│       │   │   ├── product_dto.py      # CreateProductDTO, ProductDTO
│       │   │   └── common_dto.py       # DTOs compartidos (PaginationDTO, etc.)
│       │   │
│       │   ├── services/               # Application Services (servicios transversales)
│       │   │   ├── __init__.py         # Coordinan casos de uso
│       │   │   ├── event_bus.py        # Publicador/Suscriptor de eventos
│       │   │   └── unit_of_work.py     # Patrón Unit of Work (transacciones)
│       │   │
│       │   └── mappers/                # Mappers (conversión entre capas)
│       │       ├── __init__.py         # Domain ↔ DTO conversions
│       │       ├── user_mapper.py      # UserAggregate → UserDTO
│       │       ├── order_mapper.py     # OrderAggregate → OrderDTO
│       │       └── product_mapper.py   # Product → ProductDTO
│       │
│       ├── infrastructure/             # 🟡 CAPA DE INFRAESTRUCTURA
│       │   ├── __init__.py             # Implementaciones técnicas
│       │   │                           # Acceso a BD, Cache, APIs externas
│       │   │                           # Implementa interfaces del Domain
│       │   │
│       │   ├── database/               # Configuración de bases de datos
│       │   │   ├── __init__.py
│       │   │   │
│       │   │   ├── postgres/           # PostgreSQL
│       │   │   │   ├── __init__.py
│       │   │   │   ├── connection.py       # Configuración de conexión
│       │   │   │   ├── session.py          # Session factory (SQLAlchemy async)
│       │   │   │   └── models/             # ORM Models (SQLAlchemy)
│       │   │   │       ├── __init__.py
│       │   │   │       ├── base.py         # Base declarativa
│       │   │   │       ├── user_model.py   # Tabla users
│       │   │   │       ├── order_model.py  # Tabla orders
│       │   │   │       └── product_model.py # Tabla products
│       │   │   │
│       │   │   └── redis/              # Redis
│       │   │       ├── __init__.py
│       │   │       ├── connection.py       # Configuración de conexión Redis
│       │   │       └── client.py           # Cliente Redis async
│       │   │
│       │   ├── repositories/           # Implementaciones de repositorios
│       │   │   ├── __init__.py         # Implementan interfaces del Domain
│       │   │   ├── postgres_user_repository.py    # UserRepository con PostgreSQL
│       │   │   ├── postgres_order_repository.py   # OrderRepository con PostgreSQL
│       │   │   └── postgres_product_repository.py # ProductRepository con PostgreSQL
│       │   │
│       │   ├── cache/                  # Implementaciones de caché
│       │   │   ├── __init__.py
│       │   │   ├── redis_cache.py          # Clase para operaciones de cache
│       │   │   ├── cache_repository.py     # Repositorio con cache automático
│       │   │   └── decorators/
│       │   │       ├── __init__.py
│       │   │       └── cache_decorator.py  # Decorador @cache para métodos
│       │   │
│       │   ├── messaging/              # Sistema de mensajería/eventos
│       │   │   ├── __init__.py
│       │   │   ├── event_publisher.py      # Publicador de eventos
│       │   │   ├── event_subscriber.py     # Suscriptor de eventos
│       │   │   └── handlers/               # Handlers de eventos
│       │   │       ├── __init__.py
│       │   │       ├── user_event_handlers.py   # Maneja UserCreated, etc.
│       │   │       └── order_event_handlers.py  # Maneja OrderPlaced, etc.
│       │   │
│       │   ├── persistence/            # Patrones de persistencia
│       │   │   ├── __init__.py
│       │   │   └── sqlalchemy_uow.py       # Unit of Work con SQLAlchemy
│       │   │
│       │   └── external/               # Integraciones con servicios externos
│       │       ├── __init__.py         # Anti-Corruption Layer
│       │       ├── adapters/           # Adaptadores para servicios externos
│       │       │   ├── __init__.py
│       │       │   └── payment_adapter.py  # Ej: Stripe, PayPal
│       │       └── translators/        # Traducen modelos externos a Domain
│       │           ├── __init__.py
│       │           └── payment_translator.py
│       │
│       ├── presentation/               # 🔴 CAPA DE PRESENTACIÓN
│       │   ├── __init__.py             # API REST, GraphQL, CLI, etc.
│       │   │                           # Punto de entrada de la aplicación
│       │   │
│       │   ├── api/
│       │   │   ├── __init__.py
│       │   │   │
│       │   │   ├── dependencies/       # 🔥 Sistema de Dependency Injection
│       │   │   │   ├── __init__.py     # Re-exporta todo para imports limpios
│       │   │   │   │                   # from presentation.api.dependencies import UserFactory
│       │   │   │   │
│       │   │   │   ├── database.py     # get_db_session() - Dependencia base
│       │   │   │   ├── cache.py        # get_redis_cache() - Dependencia base
│       │   │   │   │
│       │   │   │   └── factories/      # Factories (Inyección de dependencias compuestas)
│       │   │   │       ├── __init__.py # Re-exporta todas las factories
│       │   │   │       │               # Cada factory crea Use Cases con todas sus dependencias
│       │   │   │       │
│       │   │   │       ├── user_factory.py      # UserFactory
│       │   │   │       │                         # - create_user_use_case()
│       │   │   │       │                         # - update_user_use_case()
│       │   │   │       │                         # - get_user_use_case()
│       │   │   │       │                         # - list_users_use_case()
│       │   │   │       │                         # - delete_user_use_case()
│       │   │   │       │
│       │   │   │       ├── order_factory.py     # OrderFactory
│       │   │   │       │                         # - create_order_use_case()
│       │   │   │       │                         # - cancel_order_use_case()
│       │   │   │       │                         # - get_order_use_case()
│       │   │   │       │                         # - list_orders_use_case()
│       │   │   │       │
│       │   │   │       └── product_factory.py   # ProductFactory
│       │   │   │                                 # - create_product_use_case()
│       │   │   │                                 # - update_product_use_case()
│       │   │   │                                 # - get_product_use_case()
│       │   │   │                                 # - list_products_use_case()
│       │   │   │
│       │   │   ├── schemas/            # Schemas compartidos (opcional)
│       │   │   │   ├── __init__.py
│       │   │   │   ├── common.py       # Schemas comunes (ErrorResponse, etc.)
│       │   │   │   └── responses.py    # Response schemas genéricos
│       │   │   │
│       │   │   ├── routers/            # 🌍 Routers organizados por versión y país
│       │   │   │   ├── __init__.py
│       │   │   │   │
│       │   │   │   ├── v1/             # API versión 1
│       │   │   │   │   ├── __init__.py
│       │   │   │   │   │
│       │   │   │   │   ├── co/         # 🇨🇴 Colombia
│       │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   │           # Endpoints: /api/v1/co/*
│       │   │   │   │   │   │
│       │   │   │   │   │   ├── users.py        # POST/GET/PUT/DELETE /api/v1/co/users
│       │   │   │   │   │   ├── orders.py       # POST/GET /api/v1/co/orders
│       │   │   │   │   │   ├── payments.py     # POST /api/v1/co/payments (PSE, Nequi, etc.)
│       │   │   │   │   │   │
│       │   │   │   │   │   └── schemas/        # Schemas específicos de Colombia
│       │   │   │   │   │       ├── __init__.py
│       │   │   │   │   │       ├── payment_schema.py   # PaymentMethodCO (PSE, Nequi)
│       │   │   │   │   │       └── order_schema.py     # OrderSchemaCO
│       │   │   │   │   │
│       │   │   │   │   ├── mx/         # 🇲🇽 México
│       │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   │           # Endpoints: /api/v1/mx/*
│       │   │   │   │   │   │
│       │   │   │   │   │   ├── users.py        # POST/GET/PUT/DELETE /api/v1/mx/users
│       │   │   │   │   │   ├── orders.py       # POST/GET /api/v1/mx/orders
│       │   │   │   │   │   ├── payments.py     # POST /api/v1/mx/payments (SPEI, OXXO, etc.)
│       │   │   │   │   │   │
│       │   │   │   │   │   └── schemas/        # Schemas específicos de México
│       │   │   │   │   │       ├── __init__.py
│       │   │   │   │   │       ├── payment_schema.py   # PaymentMethodMX (SPEI, OXXO)
│       │   │   │   │   │       └── order_schema.py     # OrderSchemaMX
│       │   │   │   │   │
│       │   │   │   │   ├── cross/      # Lógica transversal/compartida entre países
│       │   │   │   │   │   ├── __init__.py
│       │   │   │   │   │   │           # Endpoints: /api/v1/*
│       │   │   │   │   │   │
│       │   │   │   │   │   ├── health.py       # GET /api/v1/health
│       │   │   │   │   │   ├── metrics.py      # GET /api/v1/metrics
│       │   │   │   │   │   ├── products.py     # GET /api/v1/products (catálogo global)
│       │   │   │   │   │   │
│       │   │   │   │   │   └── schemas/
│       │   │   │   │   │       ├── __init__.py
│       │   │   │   │   │       └── health_schema.py
│       │   │   │   │   │
│       │   │   │   │   └── router.py   # Agrega todos los routers de v1
│       │   │   │   │                   # Combina: co, mx, cross
│       │   │   │   │
│       │   │   │   └── v2/             # API versión 2 (futura)
│       │   │   │       ├── __init__.py
│       │   │   │       ├── co/
│       │   │   │       ├── mx/
│       │   │   │       ├── cross/
│       │   │   │       └── router.py
│       │   │   │
│       │   │   └── middleware/         # Middleware de FastAPI
│       │   │       ├── __init__.py
│       │   │       ├── error_handler.py        # Manejo global de errores
│       │   │       ├── logging_middleware.py   # Logging de requests/responses
│       │   │       ├── correlation_id.py       # Agrega correlation ID a requests
│       │   │       ├── rate_limiter.py         # Rate limiting
│       │   │       └── country_validator.py    # Valida país en la ruta
│       │   │
│       │   └── main.py                 # Punto de entrada de FastAPI
│       │                               # Inicializa app, registra routers y middleware
│       │
│       └── core/                       # ⚙️ Configuración y utilidades
│           ├── __init__.py             # Shared Kernel técnico
│           ├── config.py               # Settings con Pydantic (variables de entorno)
│           ├── logging.py              # Configuración de logging
│           ├── security.py             # Utilidades de seguridad (hashing, JWT, etc.)
│           └── constants.py            # Constantes de la aplicación
│
├── tests/                              # 🧪 Tests organizados por tipo
│   ├── __init__.py
│   ├── conftest.py                     # Fixtures compartidos (pytest)
│   │
│   ├── unit/                           # Tests unitarios (sin I/O)
│   │   ├── __init__.py
│   │   │
│   │   ├── domain/                     # Tests del dominio
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── entities/
│   │   │   │   ├── test_user.py
│   │   │   │   └── test_order.py
│   │   │   │
│   │   │   ├── value_objects/
│   │   │   │   ├── test_email.py
│   │   │   │   └── test_money.py
│   │   │   │
│   │   │   ├── aggregates/
│   │   │   │   └── test_user_aggregate.py
│   │   │   │
│   │   │   └── services/
│   │   │       └── test_user_domain_service.py
│   │   │
│   │   └── application/                # Tests de casos de uso (con mocks)
│   │       ├── __init__.py
│   │       └── use_cases/
│   │           ├── test_create_user.py
│   │           └── test_get_user.py
│   │
│   ├── integration/                    # Tests de integración (con DB real)
│   │   ├── __init__.py
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── repositories/
│   │   │   │   ├── test_user_repository.py
│   │   │   │   └── test_order_repository.py
│   │   │   └── cache/
│   │   │       └── test_redis_cache.py
│   │   │
│   │   └── api/                        # Tests de endpoints
│   │       ├── test_user_endpoints.py
│   │       └── test_order_endpoints.py
│
├── scripts/                            # Scripts de utilidad
│   ├── __init__.py
│   ├── init_db.py                      # Inicializa base de datos
│   ├── seed_data.py                    # Seed de datos de prueba
│   └── clear_cache.py                  # Limpia cache de Redis
│
└── docs/                               # Documentación del proyecto
    ├── architecture.md                 # Documentación de arquitectura
    ├── api.md                          # Documentación de API
    └── domain_model.md                 # Diagrama del modelo de dominio
```

---

# Flujo de datos entre capas

## Request → Response flow

```
1. HTTP Request
   ↓
2. Presentation Layer (Router/Endpoint)
   - Recibe request
   - Valida con Pydantic Schema
   - Convierte a DTO
   ↓
3. Presentation Layer (Factory)
   - Crea Use Case con dependencias
   - Inyecta: Repository, Services, UoW, EventBus
   ↓
4. Application Layer (Use Case)
   - Orquesta la lógica
   - Valida reglas de aplicación
   ↓
5. Domain Layer (Domain Service)
   - Ejecuta reglas de negocio complejas
   - Valida invariantes del dominio
   ↓
6. Domain Layer (Aggregate/Entity)
   - Manipula estado del dominio
   - Registra Domain Events
   ↓
7. Application Layer (Use Case)
   - Llama Repository para persistir
   ↓
8. Infrastructure Layer (Repository)
   - Convierte Aggregate → ORM Model
   - Guarda en PostgreSQL
   - Actualiza cache en Redis
   ↓
9. Application Layer (Use Case)
   - Publica Domain Events
   - Commit de Unit of Work
   ↓
10. Application Layer (Mapper)
    - Convierte Domain → DTO
    ↓
11. Presentation Layer (Endpoint)
    - Convierte DTO → Pydantic Schema
    - Retorna HTTP Response
```

---

# Principios aplicados

## Clean Architecture
- ✅ **Dependency Rule**: Las dependencias apuntan hacia adentro (Domain ← Application ← Infrastructure/Presentation)
- ✅ **Independencia de frameworks**: Domain no depende de FastAPI, SQLmodel, etc.
- ✅ **Testeable**: Puedes testear Domain sin BD, API, etc.

## DDD (Domain-Driven Design)
- ✅ **Entities**: Objetos con identidad única (User, Order)
- ✅ **Value Objects**: Objetos inmutables comparados por valor (Email, Money)
- ✅ **Aggregates**: Raíces de consistencia transaccional (UserAggregate)
- ✅ **Domain Events**: Eventos que representan hechos del dominio
- ✅ **Domain Services**: Lógica que no pertenece a una entidad
- ✅ **Repositories**: Abstracción de persistencia
- ✅ **Specifications**: Reglas de negocio encapsuladas

## SOLID
- ✅ **Single Responsibility**: Cada módulo tiene una única razón para cambiar
- ✅ **Open/Closed**: Abierto a extensión, cerrado a modificación
- ✅ **Liskov Substitution**: Las implementaciones sustituyen las interfaces
- ✅ **Interface Segregation**: Interfaces específicas en lugar de generales
- ✅ **Dependency Inversion**: Depende de abstracciones, no de concreciones

## Patrones aplicados
- ✅ **Repository Pattern**: Abstracción de persistencia
- ✅ **Unit of Work**: Manejo de transacciones
- ✅ **Factory Pattern**: Creación de objetos complejos (en Presentation)
- ✅ **Specification Pattern**: Reglas de negocio encapsuladas
- ✅ **Event-Driven Architecture**: Domain Events + Event Bus
- ✅ **Dependency Injection**: Factories en Presentation
- ✅ **Anti-Corruption Layer**: Para servicios externos

---

# Convenciones de nombres

## Capas
- `domain/`: Minúsculas, sin sufijos
- `application/`: Minúsculas, sin sufijos
- `infrastructure/`: Minúsculas, prefijos descriptivos
- `presentation/`: Minúsculas, sin sufijos

## Archivos
- **Entities**: `user.py`, `order.py` (singular)
- **Value Objects**: `email.py`, `money.py` (singular)
- **Aggregates**: `user_aggregate.py`, `order_aggregate.py`
- **Repositories (interface)**: `user_repository.py`
- **Repositories (impl)**: `postgres_user_repository.py`
- **Use Cases**: `create_user.py`, `get_user.py` (verbo + sustantivo)
- **DTOs**: `user_dto.py`
- **Schemas**: `user_schema.py`
- **Factories**: `user_factory.py`

## Clases
- **Entities**: `User`, `Order` (PascalCase)
- **Value Objects**: `Email`, `Money` (PascalCase)
- **Aggregates**: `UserAggregate`, `OrderAggregate`
- **Repositories (interface)**: `UserRepository` (abstract)
- **Repositories (impl)**: `PostgresUserRepository`
- **Use Cases**: `CreateUserUseCase`, `GetUserUseCase`
- **DTOs**: `CreateUserDTO`, `UserDTO`
- **Schemas**: `UserCreateRequest`, `UserResponse`
- **Factories**: `UserFactory`

## Métodos
- **Repositories**: `save()`, `find_by_id()`, `find_all()`, `delete()`
- **Use Cases**: `execute(dto)`
- **Factories**: `create_user_use_case()`, `get_user_use_case()`

---

# Tecnologías principales

## Backend
- **Python 3.13**
- **FastAPI**: Framework web async
- **Pydantic**: Validación y serialización
- **SQLModel**: ORM
- **Poetry**: Gestión de dependencias

## Bases de datos
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y sesiones

## Testing
- **pytest**: Framework de testing
- **pytest-asyncio**: Tests async
- **pytest-cov**: Coverage
- **httpx**: Cliente HTTP para tests

## Herramientas
- **Docker**: Contenedores
- **docker-compose**: Orquestación local
- **Ruff**: Linting y Formateo

---

## 🎯 Principios Fundamentales

### 1. Dependency Rule (Regla de Dependencias)

**REGLA DE ORO**: Las dependencias SIEMPRE apuntan hacia adentro, nunca hacia afuera.

```
Presentation → Application → Domain ← Infrastructure
    ↓              ↓            ↑          ↑
 (usa)         (usa)      (define)    (implementa)
```
---

### 2. Single Responsibility Principle

Cada módulo debe tener **UNA ÚNICA razón para cambiar**.

---

### 3. Open/Closed Principle

Abierto para **extensión**, cerrado para **modificación**.

---

## 🏗️ Reglas de las Capas

### Domain Layer (Núcleo)

**PUEDE:**
- ✅ Definir entidades, value objects, aggregates
- ✅ Definir interfaces (repositories, services externos)
- ✅ Lanzar domain exceptions
- ✅ Registrar domain events
- ✅ Contener lógica de negocio pura

**NO PUEDE:**
- ❌ Importar de otras capas (Application, Infrastructure, Presentation)
- ❌ Usar frameworks (FastAPI, SQLAlchemy, Redis)
- ❌ Acceder a BD directamente
- ❌ Hacer llamadas HTTP
- ❌ Depender de detalles técnicos
---

### Application Layer

**PUEDE:**
- ✅ Importar del Domain
- ✅ Definir casos de uso
- ✅ Orquestar Domain + Infrastructure
- ✅ Usar DTOs
- ✅ Manejar transacciones (Unit of Work)
- ✅ Publicar eventos

**NO PUEDE:**
- ❌ Contener lógica de negocio (va en Domain)
- ❌ Conocer detalles de implementación de Infrastructure
- ❌ Depender de Presentation
- ❌ Usar frameworks de UI/API

---

### Infrastructure Layer

**PUEDE:**
- ✅ Importar de Domain y Application
- ✅ Implementar interfaces del Domain
- ✅ Usar frameworks técnicos (SQLAlchemy, Redis, etc.)
- ✅ Acceder a BD, cache, APIs externas
- ✅ Convertir entre Domain y ORM

**NO PUEDE:**
- ❌ Contener lógica de negocio
- ❌ Depender de Presentation

---

### Presentation Layer

**PUEDE:**
- ✅ Importar de Application
- ✅ Definir endpoints, schemas de API
- ✅ Manejar HTTP requests/responses
- ✅ Validar entrada con Pydantic
- ✅ Inyectar dependencias (Factories)
- ✅ Manejar errores HTTP

**NO PUEDE:**
- ❌ Contener lógica de negocio
- ❌ Acceder directamente a Infrastructure
- ❌ Acceder directamente a Domain

---

## 💡 Buenas Prácticas por Capa

### Domain Layer

#### Value Objects

**✅ HACER:**
```python
# domain/value_objects/email.py
from dataclasses import dataclass
import re

@dataclass(frozen=True)  # ✅ Inmutable
class Email:
    value: str
    
    def __post_init__(self):
        """Validación en construcción"""
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email: {self.value}")
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __str__(self) -> str:
        return self.value

# Uso
email = Email("user@example.com")  # ✅ Válido
email2 = Email("invalid")  # ❌ Lanza ValueError
```

**❌ NO HACER:**
```python
class Email:
    def __init__(self, value: str):
        self.value = value  # ❌ No valida
    
    def set_value(self, value: str):  # ❌ Mutable
        self.value = value
```

---

#### Aggregates

**✅ HACER:**
```python
# domain/aggregates/order_aggregate.py
from typing import List
from domain.entities.order_item import OrderItem
from domain.value_objects.money import Money
from domain.events.order_placed import OrderPlaced

class OrderAggregate:
    """Raíz del agregado - mantiene invariantes"""
    
    def __init__(self, user_id: str):
        self.id = None
        self.user_id = user_id
        self._items: List[OrderItem] = []
        self.total = Money(0, "USD")
        self.status = "draft"
        self.events = []
    
    def add_item(self, product_id: str, quantity: int, price: Money):
        """Mantiene invariante: total = sum(items)"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        item = OrderItem(product_id, quantity, price)
        self._items.append(item)
        self._recalculate_total()  # ✅ Mantiene consistencia
    
    def place(self):
        """Transición de estado con validación"""
        if len(self._items) == 0:
            raise ValueError("Cannot place empty order")
        
        if self.status != "draft":
            raise ValueError("Order already placed")
        
        self.status = "pending"
        self.events.append(OrderPlaced(self.id, self.total))
    
    def _recalculate_total(self):
        """Invariante privado"""
        self.total = sum(item.subtotal for item in self._items)
    
    @property
    def items(self) -> List[OrderItem]:
        """Exponer items como read-only"""
        return self._items.copy()
```

**❌ NO HACER:**
```python
class OrderAggregate:
    def __init__(self):
        self.items = []  # ❌ Lista pública mutable
        self.total = 0
    
    # ❌ No valida invariantes
    # Cliente puede hacer: order.items.append(...) sin recalcular total
```

---

#### Domain Services

**✅ HACER:**
```python
# domain/services/order_domain_service.py
class OrderDomainService:
    """Lógica que involucra múltiples agregados"""
    
    def __init__(self, order_repository, product_repository):
        self.order_repository = order_repository
        self.product_repository = product_repository
    
    async def can_place_order(self, order: OrderAggregate) -> bool:
        """Regla de negocio compleja entre Order y Product"""
        for item in order.items:
            product = await self.product_repository.find_by_id(item.product_id)
            
            if not product:
                return False
            
            if not product.is_available():
                return False
            
            if product.stock < item.quantity:
                return False
        
        return True
```

**❌ NO HACER:**
```python
# ❌ Lógica de negocio en Repository
class OrderRepository:
    async def save(self, order):
        # ❌ Validación de negocio no va aquí
        if order.total > 10000:
            raise ValueError("Order too large")
        
        # Guardar...
```

---

### Application Layer

#### Use Cases

**✅ HACER:**
```python
# application/use_cases/order/create_order.py
class CreateOrderUseCase:
    """Un caso de uso = una acción del usuario"""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
        order_domain_service: OrderDomainService,
        event_bus: EventBus,
        uow: UnitOfWork
    ):
        self.order_repository = order_repository
        self.user_repository = user_repository
        self.product_repository = product_repository
        self.order_domain_service = order_domain_service
        self.event_bus = event_bus
        self.uow = uow
    
    async def execute(self, dto: CreateOrderDTO) -> OrderDTO:
        """Orquesta el flujo completo"""
        async with self.uow:
            # 1. Validar usuario existe
            user = await self.user_repository.find_by_id(dto.user_id)
            if not user:
                raise UserNotFoundException()
            
            # 2. Crear orden (lógica en Domain)
            order = OrderAggregate(dto.user_id)
            
            # 3. Agregar items (validación en Domain)
            for item_dto in dto.items:
                product = await self.product_repository.find_by_id(item_dto.product_id)
                order.add_item(product.id, item_dto.quantity, product.price)
            
            # 4. Validar con Domain Service
            if not await self.order_domain_service.can_place_order(order):
                raise InvalidOrderException("Cannot place order")
            
            # 5. Colocar orden (transición en Domain)
            order.place()
            
            # 6. Persistir
            saved = await self.order_repository.save(order)
            
            # 7. Publicar eventos
            for event in order.events:
                await self.event_bus.publish(event)
            
            # 8. Commit
            await self.uow.commit()
            
            return OrderMapper.to_dto(saved)
```

**❌ NO HACER:**
```python
class OrderUseCase:
    """❌ Múltiples responsabilidades"""
    async def create_order(self, dto): pass
    async def cancel_order(self, id): pass
    async def ship_order(self, id): pass
    async def generate_invoice(self, id): pass  # ❌ Demasiado
    
    async def send_email(self, order):  # ❌ No es responsabilidad del Use Case
        pass
```

---

#### DTOs

**✅ HACER:**
```python
# application/dtos/order_dto.py
from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class OrderItemDTO:
    product_id: str
    quantity: int
    unit_price: float

@dataclass
class CreateOrderDTO:
    """DTO para crear orden"""
    user_id: str
    items: List[OrderItemDTO]
    shipping_address: dict
    payment_method: str

@dataclass
class OrderDTO:
    """DTO para respuesta"""
    id: str
    user_id: str
    items: List[OrderItemDTO]
    total: float
    status: str
    created_at: datetime
```

**❌ NO HACER:**
```python
# ❌ Usar entidades del Domain como DTO
def execute(self, order: OrderAggregate):  # ❌ Domain no debe cruzar capas
    pass

# ❌ DTOs con lógica
class OrderDTO:
    def calculate_total(self):  # ❌ Lógica va en Domain
        pass
    
    def validate(self):  # ❌ Validación va en Domain o Presentation
        pass
```

---

### Infrastructure Layer

#### Repositories

**✅ HACER:**
```python
# infrastructure/repositories/postgres_order_repository.py
class PostgresOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession, cache: RedisCache):
        self.session = session
        self.cache = cache
    
    async def save(self, order: OrderAggregate) -> OrderAggregate:
        """Implementación con cache + BD"""
        # Convertir Domain → ORM
        order_model = self._aggregate_to_model(order)
        
        # Guardar en BD
        self.session.add(order_model)
        await self.session.flush()
        await self.session.refresh(order_model)
        
        # Guardar en cache
        cache_key = f"order:{order_model.id}"
        await self.cache.set(cache_key, self._model_to_dict(order_model), ttl=3600)
        
        # Convertir ORM → Domain
        return self._model_to_aggregate(order_model)
    
    async def find_by_id(self, order_id: str) -> Optional[OrderAggregate]:
        """Cache-aside pattern"""
        # 1. Intentar cache
        cache_key = f"order:{order_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return self._dict_to_aggregate(cached)
        
        # 2. Consultar BD
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        # 3. Actualizar cache
        await self.cache.set(cache_key, self._model_to_dict(model), ttl=3600)
        
        return self._model_to_aggregate(model)
    
    def _aggregate_to_model(self, aggregate: OrderAggregate) -> OrderModel:
        """Conversión Domain → ORM"""
        return OrderModel(
            id=aggregate.id,
            user_id=aggregate.user_id,
            total=aggregate.total.amount,
            currency=aggregate.total.currency,
            status=aggregate.status,
            items=[
                OrderItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price.amount
                )
                for item in aggregate.items
            ]
        )
    
    def _model_to_aggregate(self, model: OrderModel) -> OrderAggregate:
        """Conversión ORM → Domain"""
        # Reconstituir el agregado
        order = OrderAggregate.__new__(OrderAggregate)
        order.id = model.id
        order.user_id = model.user_id
        order.total = Money(model.total, model.currency)
        order.status = model.status
        # ... etc
        return order
```

**❌ NO HACER:**
```python
class PostgresOrderRepository:
    async def save(self, order: OrderAggregate):
        # ❌ Lógica de negocio en Repository
        if order.total > 10000:
            order.status = "requires_approval"
        
        # ❌ No devolver el agregado actualizado
        self.session.add(order)
        await self.session.commit()
        # Sin return
    
    async def find_by_id(self, id: str) -> OrderModel:  # ❌ Devolver ORM en lugar de Domain
        return await self.session.query(OrderModel).filter_by(id=id).first()
```

---

### Presentation Layer

#### Factories

**✅ HACER:**
```python
# presentation/api/dependencies/factories/order_factory.py
class OrderFactory:
    """Centraliza la creación de Use Cases"""
    
    @staticmethod
    def create_order_use_case(
        session: AsyncSession = Depends(get_db_session),
        cache: RedisCache = Depends(get_redis_cache)
    ) -> CreateOrderUseCase:
        """Factory para CreateOrderUseCase con todas sus dependencias"""
        # Repositories
        order_repository = PostgresOrderRepository(session, cache)
        user_repository = PostgresUserRepository(session, cache)
        product_repository = PostgresProductRepository(session, cache)
        
        # Domain Services
        order_domain_service = OrderDomainService(order_repository, product_repository)
        
        # Application Services
        event_bus = EventBus()
        uow = UnitOfWork(session)
        
        # Use Case
        return CreateOrderUseCase(
            order_repository=order_repository,
            user_repository=user_repository,
            product_repository=product_repository,
            order_domain_service=order_domain_service,
            event_bus=event_bus,
            unit_of_work=uow
        )
```

**❌ NO HACER:**
```python
# ❌ Crear dependencias directamente en endpoint
@router.post("/orders")
async def create_order(dto: CreateOrderDTO, db = Depends(get_db)):
    repo = PostgresOrderRepository(db)  # ❌ Construcción manual
    service = OrderDomainService(repo)
    uow = UnitOfWork(db)
    use_case = CreateOrderUseCase(repo, service, uow)  # ❌ Complejidad en endpoint
    return await use_case.execute(dto)
```

---

#### Endpoints

**✅ HACER:**
```python
# presentation/api/routers/v1/co/orders.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders - Colombia"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=OrderResponse,
    summary="Crear nueva orden",
    description="Crea una nueva orden para el usuario en Colombia"
)
async def create_order(
    request: OrderCreateRequest,
    use_case: CreateOrderUseCase = Depends(OrderFactory.create_order_use_case)
) -> OrderResponse:
    """
    Endpoint para crear orden.
    
    Solo maneja:
    - Validación de entrada (Pydantic)
    - Conversión Schema ↔ DTO
    - Manejo de errores HTTP
    """
    try:
        # Convertir Schema → DTO
        dto = CreateOrderDTO(
            user_id=request.user_id,
            items=[
                OrderItemDTO(
                    product_id=item.product_id,
                    quantity=item.quantity
                )
                for item in request.items
            ],
            shipping_address=request.shipping_address,
            payment_method=request.payment_method
        )
        
        # Ejecutar Use Case
        result = await use_case.execute(dto)
        
        # Convertir DTO → Schema
        return OrderResponse(
            id=result.id,
            user_id=result.user_id,
            items=result.items,
            total=result.total,
            status=result.status,
            created_at=result.created_at
        )
        
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=f"User not found: {e}")
    except InvalidOrderException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log error
        logger.error(f"Unexpected error creating order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Obtener orden por ID"
)
async def get_order(
    order_id: str,
    use_case: GetOrderUseCase = Depends(OrderFactory.get_order_use_case)
) -> OrderResponse:
    """Obtener una orden específica"""
    try:
        result = await use_case.execute(order_id)
        return OrderResponse.from_dto(result)
    except OrderNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="Listar órdenes"
)
async def list_orders(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    use_case: ListOrdersUseCase = Depends(OrderFactory.list_orders_use_case)
) -> List[OrderResponse]:
    """Listar órdenes con filtros opcionales"""
    results = await use_case.execute(
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return [OrderResponse.from_dto(order) for order in results]
```

**❌ NO HACER:**
```python
@router.post("/orders")
async def create_order(request: OrderCreateRequest, db = Depends(get_db)):
    # ❌ Lógica de negocio en endpoint
    if request.items is None or len(request.items) == 0:
        raise HTTPException(400, "No items")
    
    # ❌ Acceso directo a BD
    order_model = OrderModel(user_id=request.user_id)
    db.add(order_model)
    
    # ❌ Lógica de cálculo en endpoint
    total = sum(item.price * item.quantity for item in request.items)
    order_model.total = total
    
    db.commit()
    return order_model  # ❌ Devolver ORM directamente
```

---

#### Schemas (Pydantic)

**✅ HACER:**
```python
# presentation/api/routers/v1/co/schemas/order_schema.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class OrderItemRequest(BaseModel):
    """Schema para item de orden en request"""
    product_id: str = Field(..., description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad (debe ser positiva)")
    
    @validator('product_id')
    def validate_product_id(cls, v):
        if not v or len(v) == 0:
            raise ValueError("product_id no puede estar vacío")
        return v

class OrderCreateRequest(BaseModel):
    """Schema para crear orden (request)"""
    user_id: str = Field(..., description="ID del usuario")
    items: List[OrderItemRequest] = Field(..., min_items=1, description="Items de la orden")
    shipping_address: dict = Field(..., description="Dirección de envío")
    payment_method: str = Field(..., description="Método de pago")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "items": [
                    {"product_id": "prod_123", "quantity": 2}
                ],
                "shipping_address": {
                    "street": "Calle 123",
                    "city": "Bogotá",
                    "country": "CO"
                },
                "payment_method": "PSE"
            }
        }

class OrderItemResponse(BaseModel):
    """Schema para item de orden en response"""
    product_id: str
    quantity: int
    unit_price: float
    subtotal: float

class OrderResponse(BaseModel):
    """Schema para respuesta de orden"""
    id: str
    user_id: str
    items: List[OrderItemResponse]
    total: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def from_dto(cls, dto: OrderDTO) -> "OrderResponse":
        """Factory method para convertir desde DTO"""
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal
                )
                for item in dto.items
            ],
            total=dto.total,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    
    class Config:
        schema_extra = {
            "example": {
                "id": "ord_123",
                "user_id": "usr_456",
                "items": [
                    {
                        "product_id": "prod_789",
                        "quantity": 2,
                        "unit_price": 50.00,
                        "subtotal": 100.00
                    }
                ],
                "total": 100.00,
                "status": "pending",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
```

**❌ NO HACER:**
```python
class OrderSchema(BaseModel):
    """❌ Un solo schema para request y response"""
    id: Optional[str]  # ❌ id opcional confunde
    user_id: str
    items: List[dict]  # ❌ No tipar items
    total: float
    
    def calculate_total(self):  # ❌ Lógica en schema
        return sum(item['price'] for item in self.items)

# ❌ Usar Domain entities como schemas
class OrderResponse(OrderAggregate):  # ❌ No heredar de Domain
    pass
```

---

## 🚫 Anti-Patrones (Qué NO hacer)

### 1. God Object / God Class

**❌ NO:**
```python
class UserService:
    """❌ Clase que hace TODO"""
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def authenticate_user(self): pass
    def send_email(self): pass
    def generate_report(self): pass
    def calculate_statistics(self): pass
    def export_to_pdf(self): pass
    # ... 50 métodos más
```

**✅ SÍ:**
```python
class CreateUserUseCase:
    """Una clase, una responsabilidad"""
    def execute(self, dto): pass

class AuthenticateUserUseCase:
    def execute(self, credentials): pass

class UserReportService:
    def generate(self, user_id): pass
```

---

### 2. Anemic Domain Model

**❌ NO:**
```python
# domain/entities/order.py
class Order:
    """❌ Entidad sin comportamiento (solo getters/setters)"""
    def __init__(self):
        self.id = None
        self.items = []
        self.total = 0
        self.status = ""
    
    def get_total(self): return self.total
    def set_total(self, value): self.total = value
    def get_status(self): return self.status
    def set_status(self, value): self.status = value

# application/services/order_service.py
class OrderService:
    """❌ Toda la lógica fuera del Domain"""
    def place_order(self, order: Order):
        total = sum(item.price * item.quantity for item in order.items)
        order.set_total(total)
        order.set_status("pending")
```

**✅ SÍ:**
```python
# domain/aggregates/order_aggregate.py
class OrderAggregate:
    """✅ Lógica EN el Domain"""
    def add_item(self, product_id, quantity, price):
        item = OrderItem(product_id, quantity, price)
        self._items.append(item)
        self._recalculate_total()  # Lógica aquí
    
    def place(self):
        """Comportamiento rico"""
        if len(self._items) == 0:
            raise InvalidOrderException("Cannot place empty order")
        self.status = "pending"
        self.events.append(OrderPlaced(self.id))
```

---

### 3. Leaky Abstraction

**❌ NO:**
```python
# domain/repositories/user_repository.py
class UserRepository(ABC):
    """❌ Interfaz que expone detalles de implementación"""
    @abstractmethod
    def execute_sql(self, query: str): pass
    
    @abstractmethod
    def get_session(self) -> Session: pass
```

**✅ SÍ:**
```python
# domain/repositories/user_repository.py
class UserRepository(ABC):
    """✅ Interfaz abstracta"""
    @abstractmethod
    async def save(self, user: UserAggregate) -> UserAggregate: pass
    
    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[UserAggregate]: pass
```

---

### 4. Transaction Script (toda la lógica en un método gigante)

**❌ NO:**
```python
class CreateOrderUseCase:
    async def execute(self, dto):
        """❌ Método de 300 líneas con toda la lógica"""
        # Validar usuario
        user = await db.query(User).filter_by(id=dto.user_id).first()
        if not user:
            raise Exception("User not found")
        if not user.is_active:
            raise Exception("User not active")
        
        # Validar productos
        products = []
        for item in dto.items:
            product = await db.query(Product).filter_by(id=item.product_id).first()
            if not product:
                raise Exception("Product not found")
            if product.stock < item.quantity:
                raise Exception("Insufficient stock")
            products.append(product)
        
        # Calcular total
        total = 0
        for i, item in enumerate(dto.items):
            subtotal = products[i].price * item.quantity
            total += subtotal
        
        # Aplicar descuentos
        if total > 1000:
            total *= 0.9
        
        # Crear orden
        order = Order()
        order.user_id = dto.user_id
        order.total = total
        order.status = "pending"
        db.add(order)
        
        # Crear items
        for item in dto.items:
            order_item = OrderItem()
            order_item.order_id = order.id
            order_item.product_id = item.product_id
            order_item.quantity = item.quantity
            db.add(order_item)
        
        # Actualizar stock
        for i, item in enumerate(dto.items):
            products[i].stock -= item.quantity
        
        # Enviar email
        # ... 50 líneas más
        
        await db.commit()
```

**✅ SÍ:**
```python
class CreateOrderUseCase:
    async def execute(self, dto: CreateOrderDTO) -> OrderDTO:
        """✅ Orquesta, delega lógica"""
        async with self.uow:
            # Validar (delega a Domain Service)
            user = await self._validate_user(dto.user_id)
            products = await self._validate_products(dto.items)
            
            # Crear (delega a Domain)
            order = OrderAggregate.create(dto.user_id)
            
            # Agregar items (lógica en Domain)
            for item_dto in dto.items:
                product = products[item_dto.product_id]
                order.add_item(product, item_dto.quantity)
            
            # Aplicar descuentos (Domain Service)
            await self.discount_service.apply_discounts(order)
            
            # Colocar orden (Domain)
            order.place()
            
            # Persistir
            saved = await self.order_repository.save(order)
            
            # Eventos
            await self._publish_events(order.events)
            
            await self.uow.commit()
            return OrderMapper.to_dto(saved)
```

---

### 5. Feature Envy (una clase que usa mucho otra clase)

**❌ NO:**
```python
class OrderService:
    def calculate_shipping(self, order: Order):
        """❌ Usa demasiado los datos internos de Order"""
        total_weight = sum(item.product.weight * item.quantity for item in order.items)
        total_volume = sum(item.product.volume * item.quantity for item in order.items)
        
        if order.shipping_address.country == "CO":
            return total_weight * 2.5
        else:
            return total_weight * 5.0
```

**✅ SÍ:**
```python
class OrderAggregate:
    """✅ La lógica está donde están los datos"""
    def calculate_shipping(self) -> Money:
        total_weight = self._calculate_total_weight()
        
        if self.shipping_address.country == "CO":
            return Money(total_weight * 2.5, "USD")
        else:
            return Money(total_weight * 5.0, "USD")
    
    def _calculate_total_weight(self) -> float:
        return sum(item.weight * item.quantity for item in self._items)
```

---

## ✅ Code Review Checklist

### Domain Layer
- [ ] ¿Las entidades tienen comportamiento (no son anémicas)?
- [ ] ¿Los value objects son inmutables?
- [ ] ¿Los agregados mantienen invariantes?
- [ ] ¿Las interfaces de repositorios están en Domain?
- [ ] ¿No hay imports de otras capas?
- [ ] ¿Las excepciones son de dominio?
- [ ] ¿Los eventos están bien nombrados (pasado)?

### Application Layer
- [ ] ¿Cada Use Case tiene una única responsabilidad?
- [ ] ¿Usa DTOs en lugar de Domain entities?
- [ ] ¿Orquesta Domain + Infrastructure correctamente?
- [ ] ¿Maneja transacciones con Unit of Work?
- [ ] ¿Publica Domain Events?
- [ ] ¿No contiene lógica de negocio?

### Infrastructure Layer
- [ ] ¿Implementa interfaces de Domain?
- [ ] ¿Convierte correctamente Domain ↔ ORM?
- [ ] ¿Usa cache apropiadamente?
- [ ] ¿Maneja errores de BD/Red?
- [ ] ¿No contiene lógica de negocio?

### Presentation Layer
- [ ] ¿Los endpoints solo manejan HTTP?
- [ ] ¿Usa Factories para DI?
- [ ] ¿Convierte Schemas ↔ DTOs?
- [ ] ¿Maneja errores HTTP apropiadamente?
- [ ] ¿Tiene documentación (docstrings, examples)?
- [ ] ¿No accede directamente a Domain/Infrastructure?

### General
- [ ] ¿El código sigue SOLID?
- [ ] ¿Hay tests (unitarios, integración)?
- [ ] ¿Los nombres son descriptivos?
- [ ] ¿Está bien documentado?
- [ ] ¿Sigue las convenciones del proyecto?

---

## 📝 Guía de Estilo

### Nomenclatura

```python
# Clases: PascalCase
class UserAggregate: pass
class CreateUserUseCase: pass
class PostgresUserRepository: pass

# Funciones/métodos: snake_case
def create_user(): pass
def find_by_email(): pass
async def execute(): pass

# Variables: snake_case
user_id = "123"
total_amount = 100.0
is_active = True

# Constantes: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"

# Privados: prefijo _
class Order:
    def _calculate_total(self): pass  # Método privado
    def __init__(self):
        self._items = []  # Atributo privado
```

### Imports

```python
# Orden de imports:
# 1. Standard library
import os
import sys
from typing import List, Optional
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select
from pydantic import BaseModel

# 3. Local (absolutos, no relativos)
from domain.aggregates.user_aggregate import UserAggregate
from application.use_cases.user.create_user import CreateUserUseCase
from infrastructure.repositories.postgres_user_repository import PostgresUserRepository
```

### Docstrings

```python
def create_order(user_id: str, items: List[dict]) -> Order:
    """
    Crea una nueva orden para el usuario.
    
    Args:
        user_id: ID del usuario que crea la orden
        items: Lista de items con product_id y quantity
        
    Returns:
        Order: La orden creada con estado 'pending'
        
    Raises:
        UserNotFoundException: Si el usuario no existe
        InvalidOrderException: Si la orden no es válida
        
    Example:
        >>> order = create_order("user_123", [{"product_id": "prod_1", "quantity": 2}])
        >>> print(order.status)
        'pending'
    """
    pass
```

### Type Hints

```python
from typing import List, Optional, Dict, Any
from domain.aggregates.user_aggregate import UserAggregate

# Siempre usar type hints
async def find_user(user_id: str) -> Optional[UserAggregate]:
    pass

def calculate_total(items: List[Dict[str, Any]]) -> float:
    pass

class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,  # Interfaces, no implementaciones
        event_bus: EventBus
    ) -> None:
        self.user_repository = user_repository
        self.event_bus = event_bus
```

---

## Git Workflow
- Before you make any change create and checkout feature branch: `feature-[functionality]` or `fix-[issue-number]`
- Make and then commit your changes with clear messages
- Types of Commits You Should Know:
  - feat: To add new features.
  - fix: To correct errors in the code.
  - docs: For changes in the documentation.
  - style: For changes that don't affect the logic of the code (whitespace, formatting, etc.).
  - refactor: To improve the code without fixing bugs or adding new features.
  - test: To add or modify tests.
  - chore: For maintenance and configuration tasks that don't affect the source code or tests.
  - perf: To improve performance.
- Update CHANGELOG.md with clear user-facing description

## Code Quality Standards
- Follow Ruff with line length limit of 120 characters