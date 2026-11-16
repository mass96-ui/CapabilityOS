# Merge protection readiness

The existing CI workflow runs on every pull request without path filters, so frontend, backend, shared-package, and infrastructure changes receive the same checks. It also runs on pushes to `main`.

## Required status checks

Configure these exact job names as required status checks for `main`:

- `Frontend quality`
- `Backend tests and lint`

Each name is a GitHub Actions job check. Keep these names stable or update the branch rule when the workflow changes.

Backend Ruff runs on changed Python files, while the full backend test suite runs on every pull request. Mypy is not configured in the repository; CI skips that optional check unless a mypy configuration is added.

## Administrator setup

At the time this document was prepared, GitHub reported that `main` had no branch protection rule and the repository had no rulesets. This document does not enable protection; a repository administrator must do so.

In the repository, open **Settings → Branches** and add a branch protection rule for `main`, or create a repository ruleset targeting `main`. Require pull requests before merging and require both status checks above. Optionally require the branch to be up to date before merging. Confirm the checks have reported on a pull request so they are selectable, then save the rule.

The branch-protection and ruleset settings are repository administration controls; this workflow only supplies the checks.
