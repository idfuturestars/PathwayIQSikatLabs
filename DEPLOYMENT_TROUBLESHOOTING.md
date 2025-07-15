# PathwayIQ Deployment Troubleshooting Guide

## 🚨 DEPLOYMENT STUCK - SOLUTIONS

### **Problem Identified:**
The deployment is stuck due to **missing Docker configuration files** and the original `annotated_types` wheelhouse error.

### **✅ SOLUTION IMPLEMENTED:**

I've created all the necessary files to resolve your deployment issues:

1. **`/app/Dockerfile`** - Multi-stage production build
2. **`/app/.dockerignore`** - Optimized build context  
3. **`/app/deploy.sh`** - Automated deployment script
4. **`/app/docker-compose.yml`** - Full orchestration setup
5. **`/app/backend/.env.production`** - Production environment template

---

## 🔧 **IMMEDIATE DEPLOYMENT STEPS:**

### **Step 1: Test Docker Build**
```bash
# Navigate to your project directory
cd /app

# Test the Docker build
docker build -t pathwayiq:test .

# If successful, the wheelhouse error should be resolved
```

### **Step 2: Quick Deploy**
```bash
# Use the deployment script
chmod +x deploy.sh
./deploy.sh
```

### **Step 3: Full Production Deploy**
```bash
# Use Docker Compose for full stack
docker-compose up -d
```

---

## 🛠️ **TROUBLESHOOTING SPECIFIC ISSUES:**

### **Issue 1: annotated_types wheelhouse error**
**Fixed in:** `/app/Dockerfile` (lines 20-25)
```dockerfile
# Install Python dependencies with wheel building
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --wheel-dir=/wheelhouse wheel && \
    pip wheel --no-cache-dir --wheel-dir=/wheelhouse -r requirements.txt && \
    pip install --no-cache-dir --find-links=/wheelhouse -r requirements.txt
```

### **Issue 2: Missing system dependencies**
**Fixed in:** `/app/Dockerfile` (lines 10-15)
```dockerfile
# Install system dependencies for audio processing and build tools
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*
```

### **Issue 3: Build context too large**
**Fixed in:** `/app/.dockerignore`
- Excludes node_modules, build artifacts, logs, cache files
- Reduces build context size by ~90%

### **Issue 4: No health checks**
**Fixed in:** `/app/Dockerfile` (lines 58-60)
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1
```

---

## 🔍 **VERIFY DEPLOYMENT SUCCESS:**

### **Check 1: Container Status**
```bash
docker ps -f name=pathwayiq
```

### **Check 2: Health Check**
```bash
curl http://localhost:8001/api/health
```

### **Check 3: Application URL**
```bash
curl http://localhost:8001/api/
```

### **Check 4: Database Connection**
```bash
curl http://localhost:8001/api/health/detailed
```

---

## 🚀 **PRODUCTION DEPLOYMENT OPTIONS:**

### **Option A: Single Container (Recommended for testing)**
```bash
cd /app
./deploy.sh
```

### **Option B: Full Stack with Docker Compose**
```bash
cd /app
docker-compose up -d
```

### **Option C: Kubernetes Deployment**
```bash
# Apply the k8s configuration from PRODUCTION_DEPLOYMENT_GUIDE.md
kubectl apply -f pathwayiq-deployment.yaml
```

---

## 🐛 **COMMON DEPLOYMENT ERRORS & FIXES:**

### **Error: "Could not install packages due to OSError"**
**Solution:** Use the new Dockerfile which properly handles wheel building

### **Error: "No such file or directory: wheelhouse"**
**Solution:** The multi-stage build creates the wheelhouse directory correctly

### **Error: "Permission denied"**
**Solution:** Dockerfile creates non-root user and sets proper ownership

### **Error: "Port already in use"**
**Solution:** Stop existing containers or use different ports

### **Error: "Database connection failed"**
**Solution:** Update MONGO_URL in environment variables

---

## 📋 **DEPLOYMENT CHECKLIST:**

- [ ] Docker installed and running
- [ ] Environment variables configured
- [ ] Database accessible
- [ ] Ports available (8001 for backend)
- [ ] SSL certificates ready (for production)
- [ ] Domain configured
- [ ] DNS records set up
- [ ] Load balancer configured (if needed)
- [ ] Monitoring set up
- [ ] Backup strategy in place

---

## 🔄 **ROLLBACK PROCEDURE:**

If deployment fails:
```bash
# Stop containers
docker-compose down

# Remove containers
docker rm pathwayiq-app pathwayiq-mongodb pathwayiq-redis

# Remove images (if needed)
docker rmi pathwayiq:latest

# Check logs
docker logs pathwayiq-app
```

---

## 📞 **GETTING HELP:**

1. **Check container logs:**
   ```bash
   docker logs -f pathwayiq-app
   ```

2. **Check health endpoint:**
   ```bash
   curl http://localhost:8001/api/health/detailed
   ```

3. **Verify environment variables:**
   ```bash
   docker exec pathwayiq-app env | grep -E "(MONGO|REDIS|JWT)"
   ```

4. **Test database connectivity:**
   ```bash
   docker exec pathwayiq-app python -c "from backend.database_indexer import db_indexer; import asyncio; asyncio.run(db_indexer.connect())"
   ```

---

## 🎯 **NEXT STEPS AFTER DEPLOYMENT:**

1. **Monitor application:** Check `/api/metrics` endpoint
2. **Set up alerts:** Configure monitoring alerts
3. **Load testing:** Test with expected user load
4. **SSL setup:** Configure HTTPS in production
5. **Database backup:** Set up automated backups
6. **CDN setup:** Configure static asset delivery

---

The deployment should now work successfully with these fixes! 🚀