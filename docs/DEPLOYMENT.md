# Deployment Architecture

## Components
- **Frontend**: Next.js (Static/Node build). Deployable to Vercel or Node.js Docker container.
- **Backend**: FastAPI. Deployable via Docker (Uvicorn + Gunicorn).
- **Database**: SQLite (Ephemeral/Disk attached).
- **Cache**: SQLite-based model cache.

## Vercel Compatibility
- The **Frontend** is 100% Vercel compatible.
- The **Backend** should NOT be deployed as serverless functions. Research workloads take minutes and require background threads, blocking I/O, and subprocess execution (Z3). Deploy on Fly.io, Render, or a VPS.
