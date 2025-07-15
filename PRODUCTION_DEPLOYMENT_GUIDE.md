# PathwayIQ Production Deployment Guide

## 🚀 Production Environment Setup

### 1. MongoDB Production Setup

```bash
# MongoDB Atlas (Recommended)
# Create a MongoDB Atlas cluster
# Get connection string: mongodb+srv://username:password@cluster.mongodb.net/pathwayiq_production

# Or MongoDB on-premises
# Install MongoDB Community Edition
# Configure replica set for high availability
# Set up authentication and SSL
```

### 2. Redis Production Setup

```bash
# Redis Cloud (Recommended)
# Get Redis connection string: redis://username:password@redis-server:6379

# Or Redis on-premises
# Install Redis
# Configure persistence (AOF + RDB)
# Set up clustering for high availability
# Configure authentication
```

### 3. SSL/TLS Configuration

```nginx
# Nginx configuration for SSL termination
server {
    listen 443 ssl http2;
    server_name pathwayiq.com www.pathwayiq.com;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Frontend (React build)
    location / {
        root /var/www/pathwayiq/build;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    }
    
    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. Load Balancer Configuration

```yaml
# HAProxy configuration
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog

frontend pathwayiq_frontend
    bind *:80
    bind *:443 ssl crt /path/to/ssl/cert.pem
    redirect scheme https if !{ ssl_fc }
    default_backend pathwayiq_backend

backend pathwayiq_backend
    balance roundrobin
    server app1 127.0.0.1:8001 check
    server app2 127.0.0.1:8002 check
    server app3 127.0.0.1:8003 check
```

### 5. CDN Configuration

```javascript
// CloudFlare or AWS CloudFront settings
const cdnConfig = {
    origin: 'https://pathwayiq.com',
    cacheBehaviors: {
        '/static/*': {
            ttl: 31536000, // 1 year
            compress: true
        },
        '/api/*': {
            ttl: 0, // No caching for API
            headers: ['Authorization', 'Content-Type']
        }
    },
    gzipCompression: true,
    brotliCompression: true
};
```

### 6. Docker Production Setup

```dockerfile
# Multi-stage build for production
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

FROM python:3.11-slim AS backend-build
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

FROM python:3.11-slim AS production
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY --from=backend-build /app/backend /app/backend
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy frontend build
COPY --from=frontend-build /app/frontend/build /app/frontend/build

# Create non-root user
RUN useradd -m -u 1000 pathwayiq
USER pathwayiq

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

EXPOSE 8001
CMD ["python", "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 7. Kubernetes Deployment

```yaml
# pathwayiq-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pathwayiq-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pathwayiq
  template:
    metadata:
      labels:
        app: pathwayiq
    spec:
      containers:
      - name: pathwayiq
        image: pathwayiq:latest
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: pathwayiq-secrets
              key: mongo-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: pathwayiq-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: pathwayiq-service
spec:
  selector:
    app: pathwayiq
  ports:
  - port: 80
    targetPort: 8001
  type: LoadBalancer
```

### 8. Monitoring Setup

```yaml
# Prometheus monitoring
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'pathwayiq'
      static_configs:
      - targets: ['pathwayiq-service:80']
      metrics_path: '/api/metrics'
      scrape_interval: 5s
```

### 9. Database Backup Strategy

```bash
#!/bin/bash
# MongoDB backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/pathwayiq/$DATE"

# Create backup
mongodump --uri="$MONGO_URL" --out="$BACKUP_DIR"

# Compress backup
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR.tar.gz" s3://pathwayiq-backups/

# Clean up old backups (keep last 7 days)
find /backups/pathwayiq -name "*.tar.gz" -mtime +7 -delete
```

### 10. Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Security headers implemented
- [ ] Rate limiting enabled
- [ ] API keys secured in environment variables
- [ ] Database authentication configured
- [ ] Redis authentication enabled
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] Logging configured (no sensitive data)
- [ ] Monitoring alerts set up
- [ ] Backup strategy implemented
- [ ] Access controls configured

### 11. Performance Optimization

```python
# Production uvicorn settings
uvicorn_config = {
    "host": "0.0.0.0",
    "port": 8001,
    "workers": 4,  # CPU cores
    "worker_class": "uvicorn.workers.UvicornWorker",
    "max_requests": 1000,
    "max_requests_jitter": 100,
    "timeout": 30,
    "keepalive": 2,
    "limit_concurrency": 1000,
    "limit_max_requests": 10000
}
```

### 12. Environment Variables Template

```bash
# Copy to .env.production and update values
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pathwayiq_production
DB_NAME=pathwayiq_production

# Redis
REDIS_URL=redis://username:password@redis-server:6379
REDIS_PASSWORD=your-redis-password

# Security
JWT_SECRET=your-256-bit-secret-key
CORS_ORIGINS=https://pathwayiq.com,https://www.pathwayiq.com,https://app.pathwayiq.com

# AI Services
OPENAI_API_KEY=your-production-openai-key
CLAUDE_API_KEY=your-production-claude-key
GEMINI_API_KEY=your-production-gemini-key

# OAuth
GOOGLE_CLIENT_ID=your-production-google-client-id
GOOGLE_CLIENT_SECRET=your-production-google-client-secret
GITHUB_CLIENT_ID=your-production-github-client-id
GITHUB_CLIENT_SECRET=your-production-github-client-secret

# Monitoring
MONITORING_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Performance
CACHE_TTL=3600
SESSION_TIMEOUT=7200
MAX_CONNECTIONS=100
```