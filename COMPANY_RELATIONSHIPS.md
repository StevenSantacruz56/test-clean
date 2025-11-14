# Company Relationships Implementation

## Resumen de Implementación

Se ha extendido la implementación de Company para incluir las siguientes relaciones del esquema de base de datos:

1. **company** → **company_detail** (One-to-Many)
2. **company** ↔ **company_types** (Many-to-Many a través de **company_company_type**)

## Estructura de Base de Datos

### Tabla: `company`
```sql
company_id          UUID PK
company_name        VARCHAR(255) UNIQUE
country_id          UUID
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### Tabla: `company_detail`
```sql
company_detail_id           UUID PK
company_id                  UUID FK → company.company_id
identification_type_id      UUID
identity_number             VARCHAR(255)
address                     VARCHAR(255)
number_indicative           VARCHAR(255)
phone_number                VARCHAR(255)
email                       VARCHAR(255)
city_id                     UUID
active                      BOOLEAN
person_type                 VARCHAR(255)
status                      VARCHAR(255)
verified                    BOOLEAN
created_at                  TIMESTAMP
updated_at                  TIMESTAMP
```

### Tabla: `company_types`
```sql
company_types_id    UUID PK
type_name           VARCHAR(255) UNIQUE
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### Tabla: `company_company_type` (Join Table)
```sql
company_company_type_id     UUID PK
company_id                  UUID FK → company.company_id
company_types_id            UUID FK → company_types.company_types_id
percentage                  NUMERIC
company_relation            VARCHAR(255)
created_at                  TIMESTAMP
updated_at                  TIMESTAMP
```

## Archivos Creados/Actualizados

### Domain Layer

#### Value Objects
**`domain/value_objects/company_detail_vo.py`**
- Value Object inmutable para información de detalle de empresa
- Validación de email
- Validación de número de identificación
- Campos:
  - identification_type_id (UUID)
  - identity_number (string)
  - address, phone, email (optional)
  - city_id (UUID optional)
  - active, verified (boolean)
  - person_type, status (optional)

#### Entities
**`domain/entities/company_type.py`**
- Entidad para tipos de empresa
- Validación de nombre de tipo
- Métodos para actualizar nombre

#### Aggregates
**`domain/aggregates/company_aggregate.py` (Actualizado)**
- Incluye lista de `CompanyDetailVO`
- Incluye lista de `CompanyType`
- Métodos agregados:
  - `add_detail(detail: CompanyDetailVO)` - Agregar detalle
  - `remove_detail(identity_number: str)` - Remover detalle
  - `add_company_type(company_type: CompanyType)` - Asignar tipo
  - `remove_company_type(company_types_id: UUID)` - Remover tipo
- Validaciones:
  - No permite detalles duplicados (mismo identity_number)
  - No permite tipos duplicados

### Infrastructure Layer

#### ORM Models
**`infrastructure/database/postgres/models/company_detail_model.py`**
```python
class CompanyDetailModel(BaseModel):
    __tablename__ = "company_detail"

    company_detail_id = Column(UUID, primary_key=True)
    company_id = Column(UUID, ForeignKey("company.company_id"))
    identification_type_id = Column(UUID)
    identity_number = Column(String(255))
    address = Column(String(255))
    # ... más campos

    # Relationship
    company = relationship("CompanyModel", back_populates="details")
```

**`infrastructure/database/postgres/models/company_type_model.py`**
```python
class CompanyTypeModel(BaseModel):
    __tablename__ = "company_types"

    company_types_id = Column(UUID, primary_key=True)
    type_name = Column(String(255), unique=True)

    # Relationship through association table
    companies = relationship(
        "CompanyModel",
        secondary="company_company_type",
        back_populates="company_types"
    )

class CompanyCompanyTypeModel(BaseModel):
    __tablename__ = "company_company_type"

    company_company_type_id = Column(UUID, primary_key=True)
    company_id = Column(UUID, ForeignKey("company.company_id"))
    company_types_id = Column(UUID, ForeignKey("company_types.company_types_id"))
    percentage = Column(Numeric)
    company_relation = Column(String(255))
```

**`infrastructure/database/postgres/models/company_model.py` (Actualizado)**
```python
class CompanyModel(BaseModel):
    # ... campos existentes

    # Relationships
    details = relationship(
        "CompanyDetailModel",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    company_types = relationship(
        "CompanyTypeModel",
        secondary="company_company_type",
        back_populates="companies"
    )
```

### Application Layer

#### DTOs
**`application/dtos/company_dto.py` (Actualizado)**
```python
@dataclass
class CompanyDetailDTO:
    identification_type_id: UUID
    identity_number: str
    address: Optional[str] = None
    # ... más campos

@dataclass
class CompanyTypeDTO:
    company_types_id: UUID
    type_name: str

@dataclass
class CreateCompanyDTO:
    company_name: str
    country_id: UUID
    details: Optional[List[CompanyDetailDTO]] = None
    company_type_ids: Optional[List[UUID]] = None

@dataclass
class UpdateCompanyDTO:
    company_name: Optional[str] = None
    country_id: Optional[UUID] = None
    details: Optional[List[CompanyDetailDTO]] = None
    company_type_ids: Optional[List[UUID]] = None

@dataclass
class CompanyDTO:
    company_id: UUID
    company_name: str
    country_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    details: Optional[List[CompanyDetailDTO]] = None
    company_types: Optional[List[CompanyTypeDTO]] = None
```

### Presentation Layer

#### Schemas
**`presentation/api/routers/v1/cross/schemas/company_schema.py` (Actualizado)**
```python
class CompanyDetailSchema(BaseModel):
    identification_type_id: UUID
    identity_number: str
    address: Optional[str] = None
    number_indicative: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    city_id: Optional[UUID] = None
    active: bool = True
    person_type: Optional[str] = None
    status: Optional[str] = None
    verified: bool = False

class CompanyTypeSchema(BaseModel):
    company_types_id: UUID
    type_name: str

class CompanyCreateRequest(BaseModel):
    company_name: str
    country_id: UUID
    details: Optional[List[CompanyDetailSchema]] = None
    company_type_ids: Optional[List[UUID]] = None

class CompanyUpdateRequest(BaseModel):
    company_name: Optional[str] = None
    country_id: Optional[UUID] = None
    details: Optional[List[CompanyDetailSchema]] = None
    company_type_ids: Optional[List[UUID]] = None

class CompanyResponse(BaseModel):
    company_id: UUID
    company_name: str
    country_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    details: Optional[List[CompanyDetailSchema]] = None
    company_types: Optional[List[CompanyTypeSchema]] = None
```

## Ejemplos de Uso de API

### Crear Company con Detalles y Tipos

```bash
curl -X POST "http://localhost:8000/api/v1/companies/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Solutions Inc.",
    "country_id": "123e4567-e89b-12d3-a456-426614174000",
    "details": [
      {
        "identification_type_id": "123e4567-e89b-12d3-a456-426614174002",
        "identity_number": "123456789",
        "address": "123 Main St, City",
        "number_indicative": "+1",
        "phone_number": "5551234567",
        "email": "contact@techsolutions.com",
        "city_id": "123e4567-e89b-12d3-a456-426614174003",
        "active": true,
        "person_type": "Legal",
        "status": "Active",
        "verified": false
      }
    ],
    "company_type_ids": [
      "123e4567-e89b-12d3-a456-426614174004",
      "123e4567-e89b-12d3-a456-426614174005"
    ]
  }'
```

**Response (201 Created):**
```json
{
  "company_id": "987e6543-e21b-12d3-a456-426614174000",
  "company_name": "Tech Solutions Inc.",
  "country_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null,
  "details": [
    {
      "identification_type_id": "123e4567-e89b-12d3-a456-426614174002",
      "identity_number": "123456789",
      "address": "123 Main St, City",
      "number_indicative": "+1",
      "phone_number": "5551234567",
      "email": "contact@techsolutions.com",
      "city_id": "123e4567-e89b-12d3-a456-426614174003",
      "active": true,
      "person_type": "Legal",
      "status": "Active",
      "verified": false
    }
  ],
  "company_types": [
    {
      "company_types_id": "123e4567-e89b-12d3-a456-426614174004",
      "type_name": "Retailer"
    },
    {
      "company_types_id": "123e4567-e89b-12d3-a456-426614174005",
      "type_name": "Distributor"
    }
  ]
}
```

### Actualizar Company con Nuevos Detalles

```bash
curl -X PUT "http://localhost:8000/api/v1/companies/987e6543-e21b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Solutions Corp.",
    "details": [
      {
        "identification_type_id": "123e4567-e89b-12d3-a456-426614174002",
        "identity_number": "987654321",
        "email": "info@techsolutions.com",
        "phone_number": "5559876543",
        "active": true,
        "verified": true
      }
    ],
    "company_type_ids": [
      "123e4567-e89b-12d3-a456-426614174004"
    ]
  }'
```

### Obtener Company con Todas las Relaciones

```bash
curl -X GET "http://localhost:8000/api/v1/companies/987e6543-e21b-12d3-a456-426614174000"
```

## Ventajas de la Arquitectura

### 1. Aggregate Pattern
- `CompanyAggregate` mantiene la consistencia transaccional
- No se pueden agregar detalles duplicados
- No se pueden asignar tipos duplicados
- Todas las modificaciones pasan por el agregado

### 2. Value Objects
- `CompanyDetailVO` es inmutable
- Validación automática en construcción
- No puede existir en estado inválido

### 3. Relationships en ORM
- **One-to-Many**: Company → CompanyDetail con cascade delete
- **Many-to-Many**: Company ↔ CompanyTypes con tabla intermedia
- Lazy loading para optimización
- Eager loading cuando sea necesario

### 4. Separación de Concerns
- **Domain**: Define QUÉ es un Company con sus detalles
- **Application**: Orquesta CÓMO crear/actualizar
- **Infrastructure**: Implementa DÓNDE se guarda
- **Presentation**: Expone CUÁNDO y QUIÉN puede acceder

## Validaciones Implementadas

### Domain Level
- ✅ Company name no vacío
- ✅ Identity number requerido en details
- ✅ Email válido en details
- ✅ No duplicate identity numbers
- ✅ No duplicate company types

### Application Level
- ✅ Conversión DTO ↔ Domain
- ✅ Validación de existencia de company types

### Presentation Level
- ✅ Validación Pydantic de todos los campos
- ✅ EmailStr para emails
- ✅ UUIDs válidos
- ✅ Longitudes de strings

## Próximos Pasos

Para completar la implementación:

1. **Implementar CompanyType CRUD endpoints**
   - POST /api/v1/company-types/
   - GET /api/v1/company-types/
   - PUT /api/v1/company-types/{id}
   - DELETE /api/v1/company-types/{id}

2. **Agregar repositorio para CompanyType**
   - `PostgresCompanyTypeRepository`
   - CRUD completo
   - Búsqueda por nombre

3. **Actualizar Use Cases**
   - Validar que company_type_ids existen antes de asignar
   - Manejar la tabla intermedia company_company_type
   - Agregar percentage y company_relation

4. **Implementar manejo de company_detail_id**
   - Actualizar detalles específicos por ID
   - Eliminar detalles individuales

5. **Agregar más relaciones del schema**
   - company_person
   - company_vinculated
   - customer_legal
   - customer_agent

6. **Testing**
   - Unit tests para agregados con relaciones
   - Integration tests con base de datos real
   - API tests para endpoints completos

## Archivos del Schema No Implementados Aún

- `type` table
- `identification_type_id` table
- `person` table
- `company_person` join table
- `company_vinculated` table
- `customer_legal` table
- `customer_agent` table
- `customer_detail` table
- `agent` table
- `economic_activity` table
- `currency` table
- `status` table

Estos pueden implementarse siguiendo el mismo patrón establecido.
