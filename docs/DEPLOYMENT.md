# TraceForge Deployment Guide

## Production Deployment Options

### Option 1: Docker Compose (Recommended for Quick Deploy)

**Prerequisites:**
- Docker 24+
- Docker Compose 2+

**Steps:**

1. **Create docker-compose.yml:**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: traceforge
      POSTGRES_USER: traceforge
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://traceforge:${DB_PASSWORD}@postgres:5432/traceforge
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: ${FRONTEND_URL}
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    depends_on:
      - backend
    environment:
      NEXT_PUBLIC_API_URL: ${BACKEND_URL}/api
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

2. **Create .env file:**
```bash
DB_PASSWORD=<generate-secure-password>
SECRET_KEY=<generate-secure-secret>
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

3. **Deploy:**
```bash
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

### Option 2: Kubernetes (Production Scale)

**Prerequisites:**
- Kubernetes cluster
- kubectl configured
- Helm 3+

**Steps:**

1. **Create Helm chart structure:**
```
traceforge/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment-backend.yaml
    ├── deployment-frontend.yaml
    ├── service-backend.yaml
    ├── service-frontend.yaml
    ├── ingress.yaml
    ├── postgresql.yaml
    └── configmap.yaml
```

2. **Deploy PostgreSQL:**
```bash
helm install postgresql bitnami/postgresql \
  --set auth.username=traceforge \
  --set auth.password=<password> \
  --set auth.database=traceforge
```

3. **Deploy TraceForge:**
```bash
helm install traceforge ./traceforge \
  --set backend.secretKey=<secret> \
  --set postgresql.password=<password>
```

---

### Option 3: Cloud Providers

#### AWS (ECS + RDS)

1. **Create RDS PostgreSQL instance:**
```bash
aws rds create-db-instance \
  --db-instance-identifier traceforge-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username traceforge \
  --master-user-password <password> \
  --allocated-storage 20
```

2. **Create ECS task definitions:**
```json
{
  "family": "traceforge-backend",
  "containerDefinitions": [{
    "name": "backend",
    "image": "<your-registry>/traceforge-backend:latest",
    "memory": 512,
    "cpu": 256,
    "essential": true,
    "environment": [
      {"name": "DATABASE_URL", "value": "postgresql://..."},
      {"name": "SECRET_KEY", "value": "..."}
    ],
    "portMappings": [{"containerPort": 8000}]
  }]
}
```

3. **Deploy via ECS:**
```bash
aws ecs create-service \
  --cluster traceforge \
  --service-name backend \
  --task-definition traceforge-backend \
  --desired-count 2 \
  --load-balancer targetGroupArn=<arn>,containerName=backend,containerPort=8000
```

#### GCP (Cloud Run + Cloud SQL)

1. **Create Cloud SQL instance:**
```bash
gcloud sql instances create traceforge-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

2. **Deploy backend to Cloud Run:**
```bash
gcloud run deploy traceforge-backend \
  --image gcr.io/<project>/traceforge-backend \
  --add-cloudsql-instances <instance-connection-name> \
  --set-env-vars DATABASE_URL=<url>,SECRET_KEY=<secret> \
  --allow-unauthenticated
```

3. **Deploy frontend:**
```bash
gcloud run deploy traceforge-frontend \
  --image gcr.io/<project>/traceforge-frontend \
  --set-env-vars NEXT_PUBLIC_API_URL=<backend-url>/api \
  --allow-unauthenticated
```

---

## Environment Variables

### Backend Required
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=<minimum-32-character-random-string>
```

### Backend Optional
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
```

### Frontend Required
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## Security Checklist

### Before Production:
- [ ] Change SECRET_KEY to a strong random value
- [ ] Use strong database password
- [ ] Enable SSL/TLS for PostgreSQL connection
- [ ] Set ALLOWED_ORIGINS to your actual frontend domain
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set up rate limiting (nginx, CloudFlare, etc.)
- [ ] Configure firewall rules (only expose 80/443)
- [ ] Enable database backups
- [ ] Set up monitoring and alerting
- [ ] Review and restrict CORS origins
- [ ] Enable audit logging
- [ ] Implement field redaction for sensitive data
- [ ] Set up secret management (AWS Secrets Manager, etc.)

---

## Database Migrations

### Apply migrations:
```bash
# Docker
docker-compose exec backend alembic upgrade head

# Kubernetes
kubectl exec -it <backend-pod> -- alembic upgrade head

# Direct
cd backend
alembic upgrade head
```

### Create new migration:
```bash
cd backend
alembic revision --autogenerate -m "description"
```

---

## Monitoring

### Health Checks

**Backend:**
```bash
curl http://localhost:8000/
# Expected: {"message": "TraceForge API", "version": "0.1.0"}
```

**Frontend:**
```bash
curl http://localhost:3000/
# Expected: 200 OK
```

### Metrics to Monitor
- API response times
- Database connection pool
- Request rate and errors (4xx, 5xx)
- Database query latency
- Memory and CPU usage
- Disk space (PostgreSQL)
- Background worker queue depth (when implemented)

### Recommended Tools
- **Application:** Prometheus + Grafana
- **Logs:** ELK Stack or Loki
- **Uptime:** UptimeRobot, Pingdom
- **Errors:** Sentry

---

## Scaling Considerations

### Horizontal Scaling
- Backend: Stateless, can run multiple instances behind load balancer
- Frontend: Static build, use CDN
- Database: PostgreSQL read replicas for query load

### Vertical Scaling
- Database: Increase instance size for more connections/memory
- Backend: Increase memory for metrics cache size

### Performance Optimization
- Enable PostgreSQL connection pooling (pgBouncer)
- Add Redis for session management
- Move metrics to TimescaleDB for better time-series performance
- Add CDN for frontend static assets
- Implement caching layer (Redis) for frequently accessed data

---

## Backup and Disaster Recovery

### Database Backups
```bash
# Automated backup (cron)
pg_dump -h localhost -U traceforge traceforge > backup_$(date +%Y%m%d).sql

# Restore
psql -h localhost -U traceforge traceforge < backup_20261017.sql
```

### Application State
- Metrics: In-memory, lost on restart (migrate to persistent store)
- Logs/Traces: PostgreSQL (backed up)
- Configuration: Version controlled in Git

### Recovery Time Objective (RTO)
- Target: < 1 hour
- Steps: Restore database, deploy containers, verify health checks

---

## Troubleshooting

### Backend won't start
1. Check DATABASE_URL connection
2. Verify migrations applied: `alembic current`
3. Check logs: `docker-compose logs backend`
4. Verify SECRET_KEY is set

### Frontend shows API errors
1. Check NEXT_PUBLIC_API_URL is correct
2. Verify CORS origins in backend
3. Check backend is accessible from frontend network
4. Inspect browser console for errors

### Database connection issues
1. Verify PostgreSQL is running
2. Check firewall rules
3. Verify connection string format
4. Check PostgreSQL logs for authentication errors

### High memory usage
1. Check metrics store cardinality (max 1000 series)
2. Review log retention settings
3. Monitor PostgreSQL query performance
4. Consider adding connection pooling

---

## CI/CD Pipeline Example

### GitHub Actions

```yaml
name: Deploy TraceForge

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt -r requirements-test.txt
          pytest
      
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Build and push Docker images
          docker build -t registry/traceforge-backend:${{ github.sha }} ./backend
          docker push registry/traceforge-backend:${{ github.sha }}
          
          # Update deployment
          kubectl set image deployment/backend backend=registry/traceforge-backend:${{ github.sha }}
```

---

## Cost Optimization

### Free Tier Options
- **Database:** Neon (PostgreSQL), Supabase (1GB free)
- **Backend:** Fly.io (3 VMs free), Railway (5$ credit)
- **Frontend:** Vercel (unlimited), Netlify (100GB free)
- **Monitoring:** Grafana Cloud (free tier)

### Minimal Production Setup
- 1x t3.micro EC2 (backend + frontend)
- 1x db.t3.micro RDS PostgreSQL
- **Estimated:** ~$30-40/month

### Recommended Production
- 2x t3.small EC2 (backend, load balanced)
- 1x db.t3.small RDS PostgreSQL (Multi-AZ)
- CloudFront CDN for frontend
- **Estimated:** ~$100-150/month

---

## Production Readiness Checklist

- [ ] Automated tests passing
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] HTTPS enabled
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Health check endpoints working
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated
- [ ] Rollback plan documented
- [ ] On-call rotation established

---

## Support and Maintenance

### Regular Tasks
- **Daily:** Monitor error rates and response times
- **Weekly:** Review database size and clean old data
- **Monthly:** Security updates, dependency updates
- **Quarterly:** Load testing, disaster recovery drill

### Update Process
1. Review changelog
2. Test in staging environment
3. Schedule maintenance window
4. Apply database migrations
5. Deploy new version
6. Verify health checks
7. Monitor for errors
8. Roll back if issues detected

---

For questions or issues, refer to:
- Documentation: `docs/` directory
- Architecture: `docs/ARCHITECTURE.md`
- API Spec: `docs/API.md`
- Security: `docs/THREAT_MODEL.md`
