# Security Policy

## Reporting a Vulnerability

CapabilityOS takes security seriously. If you discover a security vulnerability, please report it responsibly.

**Do not** open a public GitHub issue for security vulnerabilities.

### How to Report

Send a detailed report to the CapabilityOS Engineering Team at the repository's security tab or directly to the maintainers.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- We will acknowledge receipt within 3 business days.
- We will provide a detailed response within 10 business days.
- We will work with you to understand and resolve the issue.

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

### Security Best Practices for Contributors

- Never commit secrets, API keys, or credentials.
- Use environment variables for all sensitive configuration.
- Follow the principle of least privilege.
- Validate and sanitize all user inputs.
- Use parameterized queries to prevent SQL injection.
- Hash passwords with bcrypt or stronger algorithms.
- Use HTTPS in production.
- Implement proper authentication and authorization checks.
