# Deployment Guide

## Vercel Monorepo Setup

This project uses a **pnpm workspace monorepo** structure. The configuration is optimized for deploying both the Next.js frontend and Python API together:

- **Framework Detection**: Next.js is listed in root `package.json` devDependencies to enable Vercel framework detection
- **Workspace Filtering**: Uses `pnpm --filter=web` to build only the web app from `apps/web`
- **Automatic API Routing**: Python functions in `/api` directory are automatically deployed as serverless functions
- **Custom Build Commands**: Override default Vercel build behavior to work with monorepo structure

**Important**: The root `package.json` includes Next.js, React, and React DOM as devDependencies solely for Vercel detection. The actual Next.js app and its dependencies are in `apps/web/package.json`.

## Vercel Configuration

### Main App Deployment

- **Build Command**: `pnpm install && pnpm --filter=web build` (configured in vercel.json)
- **Output Directory**: `apps/web/.next`
- **Install Command**: `pnpm install`
- **Framework**: Next.js (auto-detected from root package.json)

### Python API Deployment

- **Runtime**: python3.11
- **Function Location**: `/api/index.py` (wraps `apps/api/index.py`)
- **Handler**: Uses Mangum adapter to wrap FastAPI app for Vercel serverless
- **Routes**:
  - `/api/*` → Python serverless function (automatic)
  - GraphQL endpoint available at `/api/graphql`
  - Health check available at `/api/health`

### Environment Variables

Required in Vercel dashboard:

```
# Supabase Configuration (for frontend)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Database Configuration (for Python API)
POSTGRES_URL_NON_POOLING=postgresql://postgres:password@db.your-project-id.supabase.co:5432/postgres
```

**Note**: The `POSTGRES_URL_NON_POOLING` is required for the Python API to connect to the database. Get this from Supabase Dashboard → Settings → Database → Connection string → URI (Direct connection).

## Build Process

### Frontend Build

1. Turbo builds shared packages first
2. Next.js builds web app with workspace dependencies
3. Static files generated in `apps/web/.next`

### Python Build

1. Dependencies installed from `apps/api/requirements.txt`
2. FastAPI app at `apps/api/index.py` becomes serverless function
3. Vercel handles Python runtime automatically

## Monitoring

### Health Checks

- Frontend: Standard Next.js health
- API: `/api/health` endpoint returns `{"ok": true}`
- GraphQL: `/api/graphql` provides GraphQL endpoint

### Logs

- Vercel Function Logs: Monitor Python API performance
- Next.js Logs: Frontend build and runtime logs
- Database: Supabase dashboard for query performance

## Production Considerations

### Performance

- Next.js automatic static optimization
- Python cold starts on Vercel (consider warming strategies)
- Supabase connection pooling for database efficiency

### Security

- CORS configured for production domains
- Supabase RLS (Row Level Security) for data protection
- Environment variables for sensitive configuration
