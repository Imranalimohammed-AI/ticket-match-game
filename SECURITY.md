# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| `main` | ✅ |
| `develop` | ✅ |
| Older | ❌ |

## Reporting
**Do not open public issues for security vulnerabilities.**
Email: imranali.mohammed@cotiviti.com
Response within 48 hours, fix timeline within 7 days.

## Security Controls
| Control | Implementation |
|---------|---------------|
| Admin password | SHA-256 hash stored in `.env` only |
| Database | All queries parameterised — no SQL injection |
| Session cookies | `HttpOnly`, `SameSite=Lax` |
| Secrets | `.env` and `*.sqlite` excluded from version control |
| HTTPS | Set `SESSION_COOKIE_SECURE=True` when serving over TLS |
