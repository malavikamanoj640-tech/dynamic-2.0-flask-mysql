# Security notes

- Never commit a real database password, `.env` file, or production secret key.
- Set `DYNAMIC_SECRET_KEY` to a persistent random value before deployment.
- Keep Flask debug mode disabled outside local development.
- Use HTTPS and set `DYNAMIC_HTTPS=true` when deployed behind HTTPS.
- Unsafe HTTP methods require a session-backed CSRF token.
- Use a dedicated MySQL account with only the permissions the application needs.
- Back up your database before applying application updates.
- Do not post credentials or private security reports in public issue threads.
