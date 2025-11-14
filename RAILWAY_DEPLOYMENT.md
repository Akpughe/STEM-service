# Railway Deployment Guide

This guide explains how to deploy the STEM Service API to Railway.

## 🚂 Quick Deployment

### Prerequisites
- Railway account (sign up at [railway.app](https://railway.app))
- GitHub repository connected to Railway
- Required API keys (Wolfram Alpha, Groq)

### Deployment Steps

1. **Create New Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository and branch: `claude/analyze-codebase-011CUoSNWxgJbkGSwTNeKsMK`

2. **Railway Auto-Detection**
   - Railway will automatically detect the `Dockerfile`
   - No additional configuration needed for build

3. **Configure Environment Variables**

   Go to your project → Variables tab and add:

   ```bash
   # Required - Groq Configuration (for math reasoning with openai/gpt-oss-120b)
   # Get your API key from: https://console.groq.com
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   GROQ_MAX_COMPLETION_TOKENS=8192

   # Required - Wolfram Alpha Configuration
   WOLFRAM_APP_ID=your_wolfram_app_id_here

   # Optional - OpenAI Configuration (fallback only, not required)
   # OPENAI_API_KEY=your_openai_api_key_here
   # OPENAI_MODEL=gpt-4o
   # OPENAI_MAX_TOKENS=4096

   # Optional - Server Configuration (Railway sets PORT automatically)
   # PORT is automatically provided by Railway
   # DEBUG=false
   # LOG_LEVEL=INFO

   # Optional - Wolfram API URLs (defaults work fine)
   # WOLFRAM_LLM_API_URL=https://www.wolframalpha.com/api/v1/llm-api
   # WOLFRAM_FULL_RESULTS_API_URL=https://api.wolframalpha.com/v2/query
   # WOLFRAM_SHOW_STEPS_API_URL=https://api.wolframalpha.com/v2/query
   # WOLFRAM_LANGUAGE_API_URL=https://api.wolframalpha.com/v1/query

   # Optional - Redis (if you add Redis service)
   # REDIS_URL=redis://host:port
   # REDIS_TTL=3600

   # Optional - CORS Configuration
   # CORS_ORIGINS=https://your-frontend.com,https://another-domain.com
   ```

4. **Deploy**
   - Railway will automatically build and deploy
   - Wait for deployment to complete (usually 2-5 minutes)
   - Check the logs for any errors

5. **Get Your API URL**
   - Go to Settings tab
   - Find "Domains" section
   - Railway provides a URL like: `https://your-app.up.railway.app`
   - This is your API base URL

## 🎯 Port Configuration

The application automatically detects the correct port:

- **Local Development**: Port 8000
- **Railway**: Automatically uses Railway's PORT environment variable
- **Custom**: Set PORT or SERVER_PORT environment variable

No manual port configuration needed! Railway will automatically set the PORT variable, and the app will use it.

## ✅ Verify Deployment

### Health Check

```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "STEM Service",
  "timestamp": "2025-11-04T20:00:00Z"
}
```

### Test API

```bash
curl -X POST https://your-app.up.railway.app/api/v1/math/solve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2 + 2?",
    "format": "latex",
    "show_steps": true
  }'
```

### View API Documentation

Visit:
- Interactive docs: `https://your-app.up.railway.app/docs`
- Alternative docs: `https://your-app.up.railway.app/redoc`

## 🐛 Troubleshooting

### Issue: Build Failed - Package Not Found

**Error:** `Package 'libgl1-mesa-glx' has no installation candidate`

**Solution:** ✅ Already fixed! The Dockerfile now uses `libgl1` instead.

### Issue: Import Error - Cannot import 'GenericAlias'

**Error:** `ImportError: cannot import name 'GenericAlias' from 'types'`

**Solution:** ✅ Already fixed! The conflicting `types/` directory has been removed.

### Issue: Application Won't Start

**Check logs:**
1. Go to Railway project
2. Click on your service
3. Click "View Logs"
4. Look for error messages

**Common causes:**
- Missing environment variables (especially `GROQ_API_KEY` and `WOLFRAM_APP_ID`)
- Invalid API keys
- Network/firewall issues

### Issue: Port Already in Use

**Solution:** Railway handles ports automatically. If you see this error:
- Ensure you're not setting PORT manually to 8000
- Let Railway set the PORT environment variable
- The app will automatically use Railway's port

### Issue: Groq API Errors / Math Queries Failing

**Error:** API requests work locally but fail in Railway deployment

**Symptoms:**
- Queries that worked in local testing fail in production
- Missing or empty responses from `/api/v1/math/solve`
- Logs show Groq-related errors

**Solution:** This is usually caused by missing Groq environment variables.

**Required variables:**
1. Go to Railway Dashboard → Your Project → Variables
2. Add the following:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   GROQ_MAX_COMPLETION_TOKENS=8192
   ```
3. Get your Groq API key from: https://console.groq.com
4. Railway will automatically redeploy after adding variables
5. Check logs to verify successful deployment

**To verify it's working:**
```bash
curl -X POST https://your-app.up.railway.app/api/v1/math/solve \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the derivative of x^3 + 2x^2 + 5?", "show_steps": true}'
```

### Issue: CORS Errors

**Solution:** Add your frontend domains to CORS_ORIGINS:

```bash
CORS_ORIGINS=https://your-frontend.com,https://another-domain.com
```

Or update in code:
```python
# config/settings.py
cors_origins: List[str] = Field(
    default=[
        "http://localhost:3000",
        "https://your-frontend.com",
        "https://your-production-domain.com"
    ],
    description="Allowed CORS origins"
)
```

### Issue: API Timeout

**Solution:** Increase Railway's timeout:
1. Go to Settings → Deployment
2. Increase "Timeout" value (default is usually 300 seconds)
3. Redeploy

For the application code, you can also adjust timeouts in client code:
```typescript
const response = await fetch(url, {
  signal: AbortSignal.timeout(120000) // 2 minute timeout
});
```

### Issue: Memory Errors

**Solution:** Upgrade Railway plan or optimize memory usage:
1. Check current memory usage in Railway metrics
2. Consider upgrading to a paid plan for more memory
3. Optimize your code to use less memory

### Issue: Redis Connection Failed

**If using Redis:**
1. Add Redis service in Railway
2. Copy the Redis URL from the Redis service
3. Add to environment variables: `REDIS_URL=redis://...`

**If not using Redis:**
- The app works fine without Redis (it's optional for caching)
- You can safely ignore Redis connection warnings

## 📊 Monitoring

### View Logs

```bash
# Real-time logs
railway logs

# Or in the Railway dashboard
# Project → Service → Logs tab
```

### Metrics

Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic
- Request count

Access in: Project → Metrics tab

## 🔒 Security Best Practices

1. **API Keys**
   - Never commit API keys to Git
   - Use Railway's environment variables
   - Rotate keys regularly

2. **CORS Configuration**
   - Only allow trusted domains
   - Don't use `*` (allow all) in production

3. **Rate Limiting**
   - Consider adding rate limiting for production
   - Railway has built-in DDoS protection

4. **HTTPS**
   - Railway provides HTTPS automatically
   - All traffic is encrypted

## 💰 Cost Considerations

**Free Tier:**
- $5 free credit per month
- Sufficient for development/testing
- Sleeps after inactivity

**Hobby Plan ($5/month):**
- Fixed monthly cost
- No sleep time
- Better for production

**Pro Plan (usage-based):**
- Pay for what you use
- Higher limits
- Priority support

## 🔄 Continuous Deployment

Railway automatically redeploys when you push to GitHub:

1. Push changes to your branch:
   ```bash
   git push origin claude/analyze-codebase-011CUoSNWxgJbkGSwTNeKsMK
   ```

2. Railway detects the push
3. Automatic rebuild and deployment
4. Check logs to verify success

## 📱 Custom Domain

To use your own domain:

1. Go to Settings → Domains
2. Click "Add Domain"
3. Enter your domain (e.g., `api.yourdomain.com`)
4. Add the CNAME record to your DNS provider:
   - Type: CNAME
   - Name: api (or your subdomain)
   - Value: (provided by Railway)
5. Wait for DNS propagation (5-60 minutes)
6. Railway will automatically provision SSL certificate

## 🚀 Performance Tips

1. **Enable HTTP/2**
   - Automatically enabled by Railway

2. **Use Compression**
   - Already enabled in FastAPI by default

3. **Optimize Response Size**
   - Use `format="plaintext"` for smaller responses
   - Enable `include_educational=false` if not needed

4. **Cache Responses**
   - Add Redis for caching
   - Cache common queries

5. **Monitor Response Times**
   - Check Railway metrics
   - Optimize slow endpoints

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [API Documentation](./API_DOCUMENTATION.md)
- [Test Suite](./TEST_README.md)
- [Testing Guide](./TESTING_GUIDE.md)

## 🆘 Support

If you encounter issues:

1. Check Railway logs first
2. Review this troubleshooting guide
3. Check Railway's status page: [status.railway.app](https://status.railway.app)
4. Contact Railway support: [railway.app/help](https://railway.app/help)

## ✅ Deployment Checklist

Before deploying:

- [ ] All environment variables configured
- [ ] API keys are valid
- [ ] CORS origins include your frontend domain
- [ ] Tested locally with `docker build` and `docker run`
- [ ] Reviewed Railway logs after deployment
- [ ] Tested health endpoint
- [ ] Tested a sample API call
- [ ] Verified API documentation loads
- [ ] Configured custom domain (optional)
- [ ] Set up monitoring/alerts (optional)

---

**Your API is now deployed and ready to use!** 🎉

Access your API at: `https://your-app.up.railway.app`

**API Endpoints:**
- Health: `GET /health`
- Solve: `POST /api/v1/math/solve`
- Solve Image: `POST /api/v1/math/solve-image`
- Plot: `POST /api/v1/math/plot`
- Docs: `GET /docs`
