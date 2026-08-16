# Contributing to CapabilityOS

Thank you for your interest in contributing to CapabilityOS. This document provides guidelines and best practices for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive. We are committed to providing a welcoming experience for everyone.

## How to Contribute

### 1. Fork and Clone

```bash
git clone https://github.com/<your-org>/CapabilityOS.git
cd CapabilityOS
git checkout -b feature/my-feature
```

### 2. Install Dependencies

```bash
pnpm install
```

### 3. Environment Setup

Copy `.env.example` to `.env` and configure the required variables.

```bash
cp .env.example .env
```

### 4. Make Changes

- Follow the existing code style and architecture.
- Keep changes focused and minimal.
- Do not reformat unrelated code.
- Update documentation when behavior changes.
- Add tests for new functionality or bug fixes.

### 5. Verify

```bash
# Lint
pnpm lint

# Type check
pnpm typecheck

# Tests
pnpm test
```

### 6. Commit

Use clear, descriptive commit messages.

```bash
git add <files>
git commit -m "feat(backend): add capability scoring validation"
```

### 7. Push and Open a Pull Request

```bash
git push origin feature/my-feature
```

## Architecture

CapabilityOS follows an Evidence-First Capability Intelligence architecture:

- **Assessment** → **Attempt** → **Answer / Response**
- **AssessmentEvidence** → **Capability Measurement**
- **Scoring Policy** → **CapabilityEstimate**
- **UserCapability** → **CapabilityScoreHistory**

Evidence, measurement, scoring policy, and capability state are intentionally separated.

## Branching

- `main` — production-ready code
- `feature/*` — new features
- `fix/*` — bug fixes
- `docs/*` — documentation changes

## Pull Request Guidelines

- PRs should target `main`.
- Keep PRs small and focused.
- Include tests.
- Ensure CI passes.
- Provide a clear description of the change and the rationale.

## Reporting Bugs

Please use the GitHub issue tracker. Include:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details

## Questions

Open a GitHub Discussion for general questions.
