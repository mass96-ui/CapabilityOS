# CapabilityOS

**Human + AI Engineering OS**

CapabilityOS is an evidence-first capability intelligence platform. It measures, tracks, and develops engineering capability through assessments, evidence collection, and deterministic scoring policies.

The platform supports:

- **Learners** — assessments, evidence, capability measurement, and Engineering Passport development.
- **Managers** — team capability visibility and evidence-based talent/project decisions.
- **CEO / Platform Admin** — platform governance, capability management, and analytics.

---

## Architecture

CapabilityOS separates raw evidence from derived capability state through an intentional pipeline:

```
Assessment
  → Attempt
    → Answer / Response
      → AssessmentEvidence
        → Capability Measurement (CapabilityScoringService)
          → Scoring Policy (ProficiencyPolicy)
            → CapabilityEstimate
              → UserCapability (current state)
                → CapabilityScoreHistory (longitudinal history)
```

This separation ensures that scoring policy changes do not silently corrupt historical data, and that evidence remains auditable independent of interpretation.

---

## Repository Structure

```
CapabilityOS/
├── apps/
│   ├── web/                # Next.js learner application
│   ├── admin/              # Next.js admin dashboard
│   ├── api/                # FastAPI backend service
│   │   └── app/
│   │       ├── api/v1/     # API routers
│   │       ├── core/       # Config, security, logging, exceptions
│   │       ├── database/   # Session, base, init_db
│   │       ├── models/     # SQLAlchemy ORM models
│   │       ├── repositories/ # Data access layer
│   │       ├── schemas/    # Pydantic request/response schemas
│   │       ├── services/   # Business logic
│   │       └── utils/      # JWT, password, OTP, refresh token
│   └── ...
├── packages/
│   ├── ui/                  # Shared UI component library
│   └── types/               # Shared TypeScript types
├── infrastructure/          # Deployment and environment configuration
├── docker/                  # Container definitions
├── docs/                    # Architecture and specification docs
├── tools/                   # Developer utilities
├── .github/workflows/       # CI/CD pipelines
└── docker-compose.yml       # Local development orchestration
```

---

## Prerequisites

- **Node.js** >= 20.0.0
- **pnpm** >= 9.15.0
- **Python** >= 3.12
- **PostgreSQL** >= 16 (or SQLite for local development)
- **Docker** and Docker Compose (optional, for containerized development)

---

## Local Development

### 1. Clone and Install

```bash
git clone https://github.com/<your-org>/CapabilityOS.git
cd CapabilityOS
pnpm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your local configuration. Ensure `SECRET_KEY` and `JWT_SECRET_KEY` are set to strong random values in production.

### 3. Start Development Services

```bash
# Start PostgreSQL via Docker Compose
docker compose up -d postgres

# Or use SQLite for quick local development (default in .env.example)
```

### 4. Run Applications

```bash
# Start all apps in parallel (frontend, admin, API)
pnpm dev

# Or run individually:
pnpm --filter web dev      # Next.js on http://localhost:3000
pnpm --filter admin dev    # Next.js on http://localhost:3001
cd apps/api && uvicorn app.main:app --reload  # FastAPI on http://localhost:8000
```

---

## Backend

### Startup

```bash
cd apps/api
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
cd apps/api
pytest tests/ -v
```

### API Documentation

- Swagger UI: `http://localhost:8000/docs` (development only)
- ReDoc: `http://localhost:8000/redoc` (development only)

### Health Endpoints

- `GET /` — Root status
- `GET /api/v1/health` — Health check
- `GET /api/v1/health/ready` — Readiness probe
- `GET /api/v1/health/live` — Liveness probe

---

## Frontend

### Web Application (Learner)

```bash
pnpm --filter web dev
```

Open `http://localhost:3000`

### Admin Dashboard

```bash
pnpm --filter admin dev
```

Open `http://localhost:3001`

---

## Testing

```bash
# Run all tests
pnpm test

# Run backend tests only
cd apps/api && pytest tests/ -v

# Run frontend tests only
pnpm --filter web test
pnpm --filter admin test
```

---

## Environment Configuration

All configuration is environment-driven. See `.env.example` for all available variables.

Key categories:
- Application settings
- Security secrets
- Database connection
- Redis (optional)
- SMTP / email
- CORS origins
- Trusted hosts
- Rate limiting
- Logging level

**Never commit `.env` or secrets to version control.**

---

## CI/CD

GitHub Actions runs on every push and pull request:

- **Frontend quality**: lint, typecheck, test, build
- **Backend tests**: pytest suite

---

## Security

See [SECURITY.md](SECURITY.md) for our security policy and how to report vulnerabilities.

Key security practices in this repository:
- Email/password authentication with bcrypt
- Email OTP verification
- Server-side refresh token rotation with HMAC-SHA256 hashing
- JWT access tokens with short expiration
- CORS and TrustedHost middleware
- Centralized exception handling (no stack traces in production responses)
- Evidence-first capability architecture (no collapsed scoring)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on branching, commits, and pull requests.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Project Status

CapabilityOS is under active development. The core evidence-first capability intelligence pipeline, authentication system, assessment engine, and frontend applications are implemented. Project matching, admin tooling, and additional assessment types are in progress.
