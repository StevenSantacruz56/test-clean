# Domain Model

## Overview

This document describes the core domain model of the application.

## Bounded Contexts

### User Management
Handles user accounts, authentication, and profiles.

### Order Management
Manages orders, order items, and order lifecycle.

### Product Catalog
Product information and inventory management.

## Aggregates

### User Aggregate
**Root**: User Entity

**Components**:
- User (Entity)
- Email (Value Object)
- Phone (Value Object)
- Address (Value Object)

**Invariants**:
- Email must be unique
- Email must be valid format
- User must have at least one contact method

**Events**:
- UserCreated
- UserUpdated
- UserDeleted

### Order Aggregate
**Root**: Order Entity

**Components**:
- Order (Entity)
- OrderItem (Entity)
- Money (Value Object)
- Address (Value Object)

**Invariants**:
- Order must have at least one item
- Total must equal sum of item subtotals
- Cannot modify placed orders (only cancel)

**Events**:
- OrderCreated
- OrderPlaced
- OrderCancelled
- OrderCompleted

### Product Aggregate
**Root**: Product Entity

**Components**:
- Product (Entity)
- Money (Value Object)

**Invariants**:
- Price must be positive
- Stock cannot be negative

**Events**:
- ProductCreated
- ProductUpdated
- StockUpdated

## Value Objects

### Email
Immutable email address with validation.

### Money
Represents monetary value with amount and currency.

### Address
Physical address with street, city, country, etc.

### Phone
Phone number with country code and validation.

## Domain Services

### OrderDomainService
- Validates if order can be placed
- Checks product availability
- Applies business rules for orders

### UserDomainService
- Validates email uniqueness
- Handles user-related business rules

## Specifications

### UserSpecifications
- `UserIsActive`: Checks if user is active
- `UserIsVerified`: Checks if user is verified

### OrderSpecifications
- `OrderIsPending`: Checks if order is pending
- `OrderIsExpired`: Checks if order has expired

## Domain Events

Events are named in past tense and represent facts that have occurred:

### User Events
- `UserCreated`
- `UserUpdated`
- `UserDeleted`

### Order Events
- `OrderPlaced`
- `OrderCancelled`
- `OrderCompleted`

### Product Events
- `ProductCreated`
- `ProductUpdated`
- `StockUpdated`

## Repositories

### UserRepository
```python
- save(user: UserAggregate) -> UserAggregate
- find_by_id(user_id: str) -> Optional[UserAggregate]
- find_by_email(email: Email) -> Optional[UserAggregate]
- find_all() -> List[UserAggregate]
- delete(user_id: str) -> None
```

### OrderRepository
```python
- save(order: OrderAggregate) -> OrderAggregate
- find_by_id(order_id: str) -> Optional[OrderAggregate]
- find_by_user_id(user_id: str) -> List[OrderAggregate]
- find_all() -> List[OrderAggregate]
```

### ProductRepository
```python
- save(product: ProductAggregate) -> ProductAggregate
- find_by_id(product_id: str) -> Optional[ProductAggregate]
- find_all() -> List[ProductAggregate]
- update_stock(product_id: str, quantity: int) -> None
```
