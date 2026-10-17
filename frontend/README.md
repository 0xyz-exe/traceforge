# TraceForge Frontend

Next.js dashboard for TraceForge observability platform.

## Setup

### 1. Install Node.js 18+

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment

```bash
cp .env.local.example .env.local
```

Default API URL: `http://localhost:8000/api`

### 4. Start development server

```bash
npm run dev
```

Dashboard available at http://localhost:3000

## Build

```bash
npm run build
npm start
```

## Project Structure

```
app/
├── layout.tsx           # Root layout
├── page.tsx             # Home page
├── providers.tsx        # React Query provider
├── services/
│   └── page.tsx         # Service list
└── globals.css          # Global styles

lib/
└── api.ts               # API client and types
```

## Features

- Service list with health status
- Dark mode (default)
- React Query for caching
- Tailwind CSS styling
