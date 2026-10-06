# mikehealth API

A modern, production-ready healthcare API for patient records, clinical notes, and billing management. Built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.

## Features

- **Patient Records Management** - CRUD operations with role-based access control
- **Clinical Notes** - Secure clinical documentation for healthcare providers
- **Billing Management** - Insurance and balance tracking for billing department
- **Audit Logging** - Comprehensive audit trail for HIPAA compliance
- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **Role-Based Access Control** - Doctor, Nurse, Patient, Billing roles
- **Structured Logging** - JSON logs with correlation IDs for tracing
- **Database Migrations** - Alembic for schema versioning
- **Docker Support** - Multi-stage builds for production
- **Comprehensive Testing** - Unit, integration, and contract tests
- **CI/CD Pipeline** - GitHub Actions with linting, testing, security scanning

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose (recommended)

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/mikehealth.git
cd mikehealth

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
# pgAdmin at http://localhost:5050
```

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install poetry
poetry install --with dev,test

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Start PostgreSQL (or use Docker)
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=mikehealth \
  -p 5432:5432 \
  postgres:16-alpine

# Run migrations
alembic upgrade head

# Start development server
poetry run python -m mikehealth.main
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## Authentication

The API uses JWT Bearer tokens. Include the `Authorization: Bearer <token>` header with requests.

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@example.com", "password": "password123"}'
```

### Example Requests

```bash
# Get patient record (doctor/nurse on care team)
curl -X GET http://localhost:8000/api/v1/patients/{patient_id} \
  -H "Authorization: Bearer <token>"

# Update clinical notes (doctor/nurse on care team)
curl -X PATCH http://localhost:8000/api/v1/patients/{patient_id}/clinical-notes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"clinical_notes": "Patient reports improved symptoms..."}'

# Get billing (billing role or patient)
curl -X GET http://localhost:8000/api/v1/billing/{patient_id} \
  -H "Authorization: Bearer <token>"
```

## Role Permissions

| Action | Doctor | Nurse | Patient | Billing |
|--------|--------|-------|---------|---------|
| View own record | ✓ | ✓ | ✓ | ✓ |
| View any record (care team) | ✓ | ✓ | ✗ | ✗ |
| Update clinical notes | ✓ | ✓ | ✗ | ✗ |
| View billing | ✓ | ✓ | ✓ (own) | ✓ |
| Update billing | ✗ | ✗ | ✗ | ✓ |
| View audit logs | ✓ | ✓ | ✗ | ✓ |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/mikehealth` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | Required |
| `ENVIRONMENT` | `development`, `staging`, `production` | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000", "http://localhost:8080"]` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `REDIS_URL` | Redis for rate limiting (optional) | None |

## Project Structure

```
mikehealth/
├── src/mikehealth/
│   ├── api/              # API routes and dependencies
│   ├── auth/             # Authentication & authorization
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection
│   ├── middleware/       # Custom middleware
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── tests/                # Test suites
├── docker-compose.yml    # Local development stack
├── Dockerfile            # Production container
├── pyproject.toml        # Project configuration
└── README.md
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/mikehealth --cov-report=html

# Run specific test types
poetry run pytest tests/unit/
poetry run pytest tests/integration/
```

## Deployment

### Docker

```bash
# Build image
docker build -t mikehealth:latest .

# Run container
docker run -d \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e SECRET_KEY=your-production-secret \
  -e ENVIRONMENT=production \
  -p 8000:8000 \
  mikehealth:latest
```

### Kubernetes

Helm chart available in `helm/` directory (if added).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Security

- All passwords hashed with bcrypt
- JWT tokens with short expiration
- Rate limiting on authentication endpoints
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration
- Security headers via middleware

Report security issues to security@mikehealth.example.com

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Documentation: https://docs.mikehealth.example.com
- Issues: https://github.com/yourusername/mikehealth/issues
- Discussions: https://github.com/yourusername/mikehealth/discussions