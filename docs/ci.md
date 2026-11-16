# CI validation

Pull requests run the following checks, and pushes to `main` run the same
validation:

- **Frontend quality** installs from the frozen pnpm lockfile, audits
  production dependencies for high/critical advisories, then runs `pnpm lint`,
  `pnpm typecheck`, `pnpm test`, and `pnpm build`.
- **Backend tests and lint** runs the complete API pytest suite. Ruff is applied
  to changed API Python files because a full-repository Ruff run currently has
  existing findings outside the scope of each change. Mypy runs when an API or
  root mypy configuration exists; the repository currently has none.
- **Database migrations** starts a temporary PostgreSQL 16 service with
  CI-only credentials, applies every Alembic revision to an empty database,
  and reports the migration graph's heads.
- **Production container builds** builds the final frontend and API runtime
  stages locally on the runner. The API image smoke test verifies its
  non-root user, excludes test-only packages, waits for database-aware
  readiness, and checks graceful shutdown. These images are never pushed or
  deployed.

The workflow has read-only default token permissions. The PostgreSQL
credentials are ephemeral test values supplied to the service container; no
repository secrets are needed for pull-request validation. Third-party actions
are pinned to full commit SHAs.

The frontend production dependency audit fails on high or critical advisories.
GitHub's dependency-review action is not currently supported because this
repository has its dependency graph disabled; enable that repository security
setting before adding dependency review to CI. Do not mask the action's
unsupported-repository failure as a passing check.

## Diagnosing failures

Reproduce the frontend checks from the repository root:

```sh
corepack pnpm install --frozen-lockfile
corepack pnpm audit --prod --audit-level high
corepack pnpm lint
corepack pnpm typecheck
corepack pnpm test
corepack pnpm build
```

Reproduce the API tests and migrations from `apps/api`:

```sh
python -m pip install -r requirements.txt
python -m pytest -v
python -m alembic upgrade head
python -m alembic heads
```

Migration checks require a reachable PostgreSQL database; the workflow creates
an isolated service for them. A manual `python -m alembic check` currently
reports pre-existing differences between model metadata and the migration
history, so it is not a blocking CI step until those differences can be
reviewed and reconciled in a dedicated schema change. Ruff checks only Python files changed by the
push or pull request. Run `python -m ruff check <paths>` on those files to
reproduce lint failures. If a mypy configuration is added, the backend job
automatically runs `python -m mypy app tests`.

Build the runtime images locally without publishing them:

```sh
docker build --pull --file Dockerfile --target runtime --tag capabilityos-web:ci .
docker build --pull --file apps/api/Dockerfile --target runtime --tag capabilityos-api:ci .
```

The API runtime image installs pinned production dependencies from
`apps/api/requirements-runtime.txt`; pytest, pytest-asyncio, and the HTTP test
client dependencies remain in the full development/test requirements only.
The image runs as UID/GID 10001 and its health check calls
`/api/v1/health/ready`. Readiness runs `SELECT 1` and returns only a generic
503 response if the database is unavailable; `/api/v1/health/live` remains a
process liveness check and does not depend on the database.

## Migration safety

The original baseline revision (`21b2ae104f6f`) used `DATETIME` declarations
that prevented its DDL from running on PostgreSQL. The existing CI repair
changed those declarations to portable `TIMESTAMP` types; this task does not
rewrite that revision or any other migration history.

CI verifies applying the full migration history to a **new, empty PostgreSQL
database**. The API's test suite exercises SQLite. Neither check demonstrates
an upgrade of a populated production database. Alembic does not rerun a
revision already recorded in `alembic_version`, so an existing database at
the baseline revision will not have its column types changed by editing the
baseline source. Production startup checks connectivity but deliberately
does not apply migrations. Existing installations therefore require a
separately reviewed forward migration and a tested backup/restore procedure
before any schema upgrade; do not use the edited baseline to infer that
existing data has been transformed.

Before upgrading an existing PostgreSQL database, rehearse the proposed
forward migration against a sanitized, restorable copy of its schema and
representative data on the same supported PostgreSQL major version. Verify
the recorded Alembic revision, run the migration, compare schema and data
invariants before and after, and rehearse rollback or restore from backup.
Do not run an unverified migration or downgrade against production.

`alembic check` reports drift because the current ORM metadata and historical
baseline are not fully equivalent: the model-defined index/constraint
metadata differs from the indexes and constraints created by the migration
history. This is a known, pre-existing difference, not evidence that the
baseline was safely upgraded. It remains unresolved; reconcile it in a
separate schema change before using `alembic check` as an upgrade guarantee.

The frontend dependency audit currently uses a high-severity threshold; lower
severity advisories are reported by the registry but do not fail that step.
The API has no configured mypy baseline, and a full Ruff run currently reports
pre-existing findings outside changed files. A full
`pip-audit -r apps/api/requirements.txt` currently reports existing API
advisories, including dependencies without a known fixed release, so it is not
configured as a blocking check. Run it when updating API dependencies and
address findings before considering those dependencies safe to ship; no
advisory allowlist is configured.

The production-only API audit is:

```sh
python -m pip_audit -r apps/api/requirements-runtime.txt
```

The current runtime scan reports nine advisory records across
`dnspython==2.8.0`, `ecdsa==0.19.2`, `pyasn1==0.6.4`, and
`python-jose==3.5.0`. The audit
identifies fixed releases for `dnspython` and `pyasn1`, but no fixed release
for `ecdsa` or `python-jose`; the package index currently lists `python-jose
3.5.0` as its latest version. These findings are not allowlisted and remain
production dependency risks requiring a separate compatibility/security
review.
