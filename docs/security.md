# Security Guidelines

## Overview

This document outlines security best practices for the Vercel Python React Supabase template.

## Secret Management

### Environment Variables

**Never commit sensitive credentials to version control.** Use environment variables for all secrets:

- `NEXT_PUBLIC_SUPABASE_URL` - Public Supabase project URL (safe to commit)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Public anonymous key (safe to commit)
- `SUPABASE_SERVICE_ROLE_KEY` - **NEVER commit this to git**
- `DATABASE_URL` - **NEVER commit this to git**

### MCP Server Configuration

The `.mcp.json` file contains sensitive credentials and **must never be committed** to version control.

**Setup Process:**

1. Copy the example configuration:
   ```bash
   cp .mcp.json.example .mcp.json
   ```

2. Replace placeholders with your actual credentials:
   ```json
   {
     "mcpServers": {
       "supabase": {
         "env": {
           "SUPABASE_ACCESS_TOKEN": "your-actual-token-here"
         }
       }
     }
   }
   ```

3. Verify `.mcp.json` is listed in `.gitignore`

### Files to Never Commit

- `.mcp.json` - Contains Supabase access tokens
- `.env.local` - Contains environment-specific secrets
- `.env` - Contains local development secrets
- Any file with `password`, `secret`, `key`, or `token` in the content

## Access Token Management

### Supabase Access Tokens

Supabase access tokens (format: `sbp_xxxxx`) provide **administrative access** to your Supabase project.

**If a token is exposed:**

1. **Immediately revoke the token:**
   - Go to [Supabase Dashboard](https://app.supabase.com)
   - Navigate to Settings → API
   - Revoke the exposed token
   - Generate a new token

2. **Remove from git history:**
   ```bash
   # If already committed, remove from history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .mcp.json" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (use with caution)
   git push origin --force --all
   ```

3. **Update all local configurations** with the new token

### GitHub Token Scanning

GitHub automatically scans commits for exposed secrets. If a secret is detected:

- You'll receive an email notification
- The repository may be flagged
- **Follow the immediate action steps above**

## Pre-commit Hooks

Use pre-commit hooks to prevent accidental secret commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

## Environment-Specific Configuration

### Development

```bash
# .env.local (never commit)
SUPABASE_ACCESS_TOKEN=sbp_dev_token_here
```

### Production

Set environment variables in Vercel dashboard:
- Never include tokens in vercel.json
- Use Vercel environment variable encryption
- Rotate tokens regularly

## API Security

### Authentication

- Always validate JWT tokens on the backend
- Never trust client-side authentication alone
- Use Supabase RLS (Row Level Security) policies

### Rate Limiting

Implement rate limiting for API endpoints:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/endpoint")
@limiter.limit("5/minute")
async def endpoint():
    pass
```

## Database Security

### Row Level Security (RLS)

Always enable RLS on Supabase tables:

```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own data"
  ON users
  FOR SELECT
  USING (auth.uid() = id);
```

### Connection Security

- Use connection pooling (Supabase provides this)
- Never expose database credentials in client-side code
- Use prepared statements to prevent SQL injection

## Dependency Security

### Regular Audits

```bash
# Node.js dependencies
pnpm audit

# Python dependencies
pip-audit
```

### Automated Updates

Configure Dependabot in `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "pip"
    directory: "/apps/api"
    schedule:
      interval: "weekly"
```

## CORS Configuration

Configure CORS properly to prevent unauthorized access:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Never use "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Incident Response

### If Credentials Are Exposed

1. **Immediate Actions:**
   - Revoke exposed credentials
   - Generate new credentials
   - Update all services
   - Remove from git history

2. **Assessment:**
   - Check access logs for unauthorized usage
   - Review recent database changes
   - Audit API calls

3. **Prevention:**
   - Update security procedures
   - Review access controls
   - Implement additional monitoring

4. **Communication:**
   - Notify team members
   - Document the incident
   - Update security guidelines

## Security Checklist

Before deploying:

- [ ] All secrets in environment variables, not code
- [ ] `.mcp.json` is gitignored and not in repo
- [ ] `.env.local` is gitignored and not in repo
- [ ] No hardcoded API keys or tokens
- [ ] RLS policies enabled on all tables
- [ ] CORS configured with specific origins
- [ ] Rate limiting implemented
- [ ] Dependencies audited for vulnerabilities
- [ ] Authentication validated on backend
- [ ] Error messages don't expose sensitive info

## Resources

- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Vercel Security](https://vercel.com/docs/security)
