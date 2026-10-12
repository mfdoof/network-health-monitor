# Security

## Reporting a vulnerability

Report privately through GitHub: open the repo's **Security** tab and click **Report a vulnerability**. Please don't open a public issue or use email.

Include what you found, how to reproduce it, and the impact. You'll get a reply in the advisory thread.

## In scope

- Bypassing the target checks (reaching private, loopback, link-local, metadata or other blocked addresses, including through DNS rebinding)
- Redaction leaks: real IPs or hostnames reaching the LLM while `LLM_REDACT=true`
- Injection: command injection through ping, header injection, or prompt injection that leaks data
- Secrets (such as `LLM_API_KEY`) in logs, API responses or the frontend

## Out of scope

- Problems that only exist when the app is exposed to the public internet, which the README advises against (for example, no authentication or rate limits that are too loose for public use)
- Findings that need `ALLOW_PRIVATE_TARGETS=true` or `LLM_REDACT=false`, since those turn the protections off on purpose
