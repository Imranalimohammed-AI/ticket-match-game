# Contributing to IT Ticket Triage Game

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready, protected — PR-only |
| `develop` | Integration — all PRs target here |
| `feature/<name>` | New features from `develop` |
| `fix/<name>` | Bug fixes from `develop` |
| `hotfix/<name>` | Critical fixes from `main` |

## Workflow
1. `git checkout -b feature/your-feature develop`
2. Commit with clear messages
3. Open PR targeting `develop`

## Commit Format
```
type(scope): short description
Types: feat | fix | docs | style | refactor | test | chore | security
```

## Security Requirements
- Admin password stored as SHA-256 hash in `.env` — never in code
- All DB queries use parameterised statements — no SQL injection risk
- Never commit `.env` or `cotiviti_game.sqlite`
- See [SECURITY.md](SECURITY.md)
