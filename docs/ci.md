# CI validation

Pull requests run the following checks, and pushes to `main` run the same
validation except dependency review:

- **Frontend quality** installs from the frozen pnpm lockfile, audits
  production dependencies for high/critical advisories, then runs `pnpm lint`,
  `pnpm typecheck`, `pnpm test`, and `pnpm build`.
- **Backend tests and lint** runs the complete API pytest suite. Ruff is applied
  to changed API Python files because a full-repository Ruff run currently has
  existing findings outside the scope of each change. Mypy runs when an API or
  root mypy configuration exists; the repository currently has none.
- **Database migrations** starts a temporary PostgreSQL 16 service with
  CI-only credentials, applies every Alembic revision to an empty database,
  then runs `alembic check` to detect model/schema drift.
- **Production container builds** builds the final frontend and API runtime
  stages locally on the runner. These images are never pushed or deployed.
- **Dependency review** checks dependency changes in pull requests and fails on
  high or critical severity. The job uses read-only repository and pull-request
  permissions and does not post comments.

The workflow has read-only default token permissions. The PostgreSQL
credentials are ephemeral test values supplied to the service container; no
repository secrets are needed for pull-request validation. Third-party actions
are pinned to full commit SHAs.

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
python -m alembic check
```

Migration checks require a reachable PostgreSQL database; the workflow creates
an isolated service for them. Ruff checks only Python files changed by the
push or pull request. Run `python -m ruff check <paths>` on those files to
reproduce lint failures. If a mypy configuration is added, the backend job
automatically runs `python -m mypy app tests`.

Build the runtime images locally without publishing them:

```sh
docker build --pull --file Dockerfile --target runtime --tag capabilityos-web:ci .
docker build --pull --file apps/api/Dockerfile --target runtime --tag capabilityos-api:ci .
```

The frontend dependency audit currently uses a high-severity threshold; lower
severity advisories are reported by the registry but do not fail that step.
The API has no configured mypy baseline, and a full Ruff run currently reports
pre-existing findings outside changed files. API dependency changes are gated
by dependency review, which evaluates dependency changes rather than auditing
the unchanged baseline. A full `pip-audit -r apps/api/requirements.txt`
currently reports existing advisories, including dependencies without a known
fixed release, so it is not configured as a blocking check. Run it when
updating the API dependency set and address findings before considering those
dependencies safe to ship; no advisory allowlist is configured.
