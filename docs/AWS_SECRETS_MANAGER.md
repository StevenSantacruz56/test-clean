# AWS Secrets Manager Integration

Este documento explica cómo se integra AWS Secrets Manager en el proyecto para gestionar secretos y configuraciones sensibles en los ambientes de testing, staging y producción.

## Configuración

### Variables de Entorno

Para que la aplicación pueda conectarse a AWS Secrets Manager, necesitas configurar las siguientes variables de entorno:

```bash
# Ambiente (testing, staging, production)
ENVIRONMENT=production

# Región de AWS donde están tus secretos
AWS_REGION=us-east-1

# Credenciales de AWS (opcional si usas IAM roles)
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

### Métodos de Autenticación

La aplicación soporta múltiples métodos de autenticación con AWS:

1. **Variables de entorno** (recomendado para desarrollo local):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. **IAM Roles** (recomendado para producción en EC2/ECS/Lambda):
   - La aplicación automáticamente usará el IAM role asignado al recurso

3. **AWS CLI credentials** (`~/.aws/credentials`):
   - Útil para desarrollo local

## Estructura de Secretos

### Nomenclatura

Los secretos deben seguir el patrón: `{environment}/{secret-name}`

Ejemplos:
- `testing/database-url`
- `staging/database-url`
- `production/database-url`
- `production/redis-url`
- `production/secret-key`

### Secretos Individuales (String)

Para secretos simples, almacena el valor directamente como string:

**Nombre del secreto**: `production/database-url`
**Valor**:
```
postgresql+asyncpg://user:password@host:5432/dbname
```

### Secretos Múltiples (JSON)

Para múltiples valores relacionados, puedes usar un único secreto JSON:

**Nombre del secreto**: `production/app-config`
**Valor**:
```json
{
  "database_url": "postgresql+asyncpg://user:password@host:5432/dbname",
  "redis_url": "redis://redis-host:6379/0",
  "secret_key": "your-super-secret-key-here"
}
```

## Uso en la Aplicación

### Configuración Automática

La aplicación carga automáticamente los secretos según el ambiente:

```python
from app.core.config import settings

# En development/local: usa .env y variables de entorno
# En testing/staging/production: usa AWS Secrets Manager con fallback a env vars

print(settings.database_url)  # Automáticamente cargado del secreto apropiado
print(settings.redis_url)
print(settings.secret_key)
```

### Uso Manual del Cliente

Para casos más avanzados, puedes usar el cliente directamente:

```python
from app.core.secret_manager import AWSSecretsManagerClient

# Crear cliente
sm = AWSSecretsManagerClient(region_name="us-east-1")

# Obtener secreto como string
db_password = sm.get_secret("production/database-password")

# Obtener secreto como JSON
config = sm.get_secret_json("production/app-config")
print(config["database_url"])

# Obtener secreto con fallback a variable de entorno
api_key = sm.get_secret_or_env(
    secret_name="production/api-key",
    env_var_name="API_KEY",
    default="default-api-key"
)

# Listar todos los secretos
secrets = sm.list_secrets()
for secret in secrets:
    print(secret["Name"])
```

## Crear Secretos en AWS

### Usando AWS Console

1. Ve a AWS Secrets Manager en la consola
2. Click "Store a new secret"
3. Selecciona "Other type of secret"
4. Ingresa el valor del secreto (plaintext o JSON)
5. Nombre del secreto: `{environment}/{secret-name}`
6. Configura rotación automática (opcional)
7. Revisa y crea

### Usando AWS CLI

```bash
# Crear secreto simple
aws secretsmanager create-secret \
    --name production/database-url \
    --secret-string "postgresql+asyncpg://user:password@host:5432/db" \
    --region us-east-1

# Crear secreto JSON
aws secretsmanager create-secret \
    --name production/app-config \
    --secret-string file://secrets.json \
    --region us-east-1

# Actualizar secreto existente
aws secretsmanager update-secret \
    --secret-id production/database-url \
    --secret-string "new-value" \
    --region us-east-1

# Obtener secreto
aws secretsmanager get-secret-value \
    --secret-id production/database-url \
    --region us-east-1
```

### Usando Terraform

```hcl
resource "aws_secretsmanager_secret" "database_url" {
  name = "production/database-url"
  description = "PostgreSQL connection URL for production"

  tags = {
    Environment = "production"
    Application = "test-clean"
  }
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = var.database_url
}
```

## Permisos IAM Necesarios

La aplicación necesita los siguientes permisos IAM:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:production/*",
        "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:staging/*",
        "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:testing/*"
      ]
    }
  ]
}
```

Para listar secretos (opcional):
```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:ListSecrets"
  ],
  "Resource": "*"
}
```

## Ambientes

### Development/Local

- **NO** usa AWS Secrets Manager
- Lee de `.env` y variables de entorno
- Útil para desarrollo sin necesidad de credenciales AWS

### Testing

- Usa secretos con prefijo `testing/`
- Ejemplo: `testing/database-url`
- Puedes usar una cuenta AWS separada para testing

### Staging

- Usa secretos con prefijo `staging/`
- Ejemplo: `staging/database-url`
- Ambiente de pre-producción

### Production

- Usa secretos con prefijo `production/`
- Ejemplo: `production/database-url`
- Máxima seguridad, rotación automática recomendada

## Fallback y Prioridades

La configuración se carga en el siguiente orden (mayor a menor prioridad):

1. **Variables de entorno** directas
2. **AWS Secrets Manager** (solo en testing/staging/production)
3. **Archivo `.env`** (solo en development/local)
4. **Valores por defecto** en `app/core/config.py`

Esto permite:
- Override temporal con variables de entorno
- Configuración segura en producción con Secrets Manager
- Desarrollo local sin AWS

## Manejo de Errores

Si un secreto no se encuentra en AWS Secrets Manager:

```python
# La aplicación automáticamente:
# 1. Intenta AWS Secrets Manager
# 2. Si falla, usa variable de entorno
# 3. Si no existe, usa valor por defecto
# 4. Log de warning con el método usado

# Ejemplo de log:
# WARNING: Could not load production/database-url from AWS Secrets Manager.
#          Using environment variable
```

## Seguridad

### Mejores Prácticas

1. **NUNCA** commits secretos en el código
2. Usa IAM roles en lugar de access keys cuando sea posible
3. Habilita rotación automática para passwords
4. Usa diferentes secretos para cada ambiente
5. Audita el acceso a secretos con CloudTrail
6. Aplica el principio de mínimo privilegio en IAM policies

### Rotación de Secretos

AWS Secrets Manager soporta rotación automática:

```bash
aws secretsmanager rotate-secret \
    --secret-id production/database-password \
    --rotation-lambda-arn arn:aws:lambda:region:account:function:rotation-function
```

### Encriptación

- Los secretos se encriptan automáticamente en reposo con AWS KMS
- Puedes usar tu propia KMS key:

```bash
aws secretsmanager create-secret \
    --name production/database-url \
    --secret-string "value" \
    --kms-key-id alias/my-custom-key
```

## Costos

AWS Secrets Manager tiene los siguientes costos (precios de referencia):

- **$0.40** por secreto por mes
- **$0.05** por 10,000 llamadas a la API

Estrategias para optimizar costos:

1. Agrupa secretos relacionados en un JSON
2. Cachea secretos en la aplicación (ya implementado)
3. Usa secretos compartidos entre microservicios cuando sea apropiado

## Troubleshooting

### Error: "AccessDeniedException"

**Causa**: Permisos IAM insuficientes

**Solución**: Verifica que el IAM role/user tenga los permisos necesarios

### Error: "ResourceNotFoundException"

**Causa**: El secreto no existe en AWS Secrets Manager

**Solución**:
1. Verifica el nombre del secreto (case-sensitive)
2. Verifica la región
3. Crea el secreto si no existe

### Error: "InvalidRequestException"

**Causa**: Formato de request inválido

**Solución**: Verifica que el nombre del secreto siga el formato correcto

### Los secretos no se cargan

**Debug**:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from app.core.config import settings
# Revisa los logs para ver qué método se está usando
```

## Migración desde Variables de Entorno

Si actualmente usas variables de entorno, migrar es simple:

1. Crea los secretos en AWS Secrets Manager con los valores actuales
2. Configura las credenciales AWS en el ambiente
3. Cambia `ENVIRONMENT=production` (la app detectará y usará AWS automáticamente)
4. Las variables de entorno seguirán funcionando como fallback

## Referencias

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [boto3 Secrets Manager Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html)
- [Best Practices for Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
