# Environment Setup Guide

## Security Notice
**⚠️ IMPORTANT**: API keys and sensitive credentials are not committed to this repository for security reasons.

## Required Environment Variables

### Backend Configuration (`backend/.env`)

Copy `backend/.env.template` to `backend/.env` and configure the following:

#### AI Service API Keys
- **OPENAI_API_KEY**: Required for content generation and speech-to-text
  - Get from: https://platform.openai.com/api-keys
  - Used for: GPT-4 content generation, Whisper speech-to-text, think-aloud analysis

- **CLAUDE_API_KEY**: Required for advanced AI features  
  - Get from: https://console.anthropic.com/
  - Used for: Alternative content generation, emotional intelligence analysis

- **GEMINI_API_KEY**: Required for multi-provider AI support
  - Get from: https://makersuite.google.com/app/apikey
  - Used for: Google's AI capabilities, content generation diversity

#### OAuth Integration (Optional)
- **GOOGLE_CLIENT_ID** & **GOOGLE_CLIENT_SECRET**: For Google OAuth
- **GITHUB_CLIENT_ID** & **GITHUB_CLIENT_SECRET**: For GitHub OAuth

#### Database & Infrastructure
- **MONGO_URL**: MongoDB connection string (default: `mongodb://localhost:27017`)
- **DB_NAME**: Database name (default: `idfs_pathwayiq_database`)
- **REDIS_URL**: Redis connection string (default: `redis://localhost:6379`)
- **JWT_SECRET**: JWT signing secret (generate a secure random string)

### Frontend Configuration (`frontend/.env`)

The frontend `.env` is auto-configured for the current deployment but can be customized:

```
REACT_APP_BACKEND_URL=<your-backend-url>
WDS_SOCKET_PORT=443
```

## Quick Setup

1. **Copy template files:**
   ```bash
   cp backend/.env.template backend/.env
   ```

2. **Add your API keys to `backend/.env`**

3. **Install dependencies:**
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend  
   cd frontend && yarn install
   ```

4. **Start services:**
   ```bash
   sudo supervisorctl restart all
   ```

## Feature Requirements by API Key

### Core Features (No API keys needed)
- ✅ User authentication and registration
- ✅ Basic navigation and UI
- ✅ User profiles and settings

### Speech-to-Text Features
- **Required**: OPENAI_API_KEY
- Features: Think-aloud assessments, voice recording, speech analysis

### AI Content Generation  
- **Required**: OPENAI_API_KEY
- **Optional**: CLAUDE_API_KEY, GEMINI_API_KEY (for provider diversity)
- Features: Quiz generation, lesson plans, explanations, practice problems

### Advanced AI Features
- **Required**: OPENAI_API_KEY + CLAUDE_API_KEY
- Features: Enhanced emotional intelligence, advanced personalization

### Social Authentication
- **Optional**: GOOGLE_CLIENT_ID, GITHUB_CLIENT_ID
- Features: OAuth login options

## Security Best Practices

1. **Never commit `.env` files** - They are in `.gitignore`
2. **Use environment-specific files** - Different keys for dev/staging/prod
3. **Rotate API keys regularly** - Especially for production
4. **Use minimal permissions** - Only grant necessary API scopes
5. **Monitor API usage** - Track costs and usage limits

## Troubleshooting

### API Key Issues
- Verify keys are correctly formatted (no extra spaces/quotes)
- Check API key permissions and quotas
- Ensure keys are active and not expired

### Database Issues  
- Verify MongoDB is running: `sudo systemctl status mongod`
- Check connection string format
- Ensure database permissions

### Service Issues
- Check logs: `sudo supervisorctl tail -f backend`
- Restart services: `sudo supervisorctl restart all`
- Verify environment loading: Check backend logs for "Environment loaded"