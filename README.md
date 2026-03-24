# Engineering Delivery Health Analyzer

A real-time dashboard that analyzes engineering work items from JIRA and surfaces delivery risks, bottleneck patterns, and RAG-based health scores.

## 🚀 Features

- **Health Scoring**: Weighted composite scores based on status, priority, and age
- **RAG Classification**: Red/Amber/Green status indicators (Red < 50, Amber 50-74, Green ≥ 75)
- **Bottleneck Detection**: Automatically identifies blocked or stalled issues
- **Workload Distribution**: Priority-based workload visualization
- **JIRA Integration**: Sync issues directly from JIRA by space, project, or fix version
- **Multi-Space Support**: Track multiple product areas (configurable per deployment)

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+ (tested with 3.11 and 3.12)
- **JIRA Account** with API token
- **JIRA Access**: Must have read permissions for the projects you want to track

## 🔑 JIRA Credentials Setup

### 1. Generate Your JIRA API Token

1. Log in to your JIRA instance (e.g., `https://yourcompany.atlassian.net`)
2. Go to **Account Settings** → **Security** → **API tokens**
3. Click **Create API token**
4. Give it a name (e.g., "EDHA Dashboard")
5. Copy the generated token (you won't see it again!)

### 2. Configure Backend Credentials

Create `backend/.env` with your credentials:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```ini
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_api_token_here
```

⚠️ **IMPORTANT**: Never commit real credentials! The `.env` file is already in `.gitignore`.

### 3. Configure Frontend (Development Only)

The frontend `.env.local` is already configured for local development:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

For production deployments, `.env.production` uses relative URLs automatically.

## 🛠️ Local Development Setup

### 1. Configure Your Projects

**Edit `config/projects.json`** to add your JIRA projects and spaces:

```json
{
  "projects": {
    "Your Space Display Name": "JIRAKEY",
    "Another Product 2.0": "PROJ2"
  },
  "contributors": {
    "Your Space Display Name": ["Developer Name 1", "Developer Name 2"],
    "Another Product 2.0": ["Developer Name 3"]
  }
}
```

**Important:**
- **Space Name** (key): The display name shown in the UI dropdown and filters
- **Project Key** (value): Your JIRA project key/ID (e.g., "TSITE", "VPE2")
- **Contributors** (optional): List of assignee names for each space

**Example:**
```json
{
  "projects": {
    "TSA-SITE": "TSITE",
    "Voice Policy Engine 2.0": "VPE2"
  },
  "contributors": {
    "TSA-SITE": ["John Doe", "Jane Smith"]
  }
}
```

Both backend and frontend automatically load from this single file - no code changes needed!

**For detailed configuration guide:** See [`docs/PROJECT_CONFIGURATION.md`](docs/PROJECT_CONFIGURATION.md)

**If your project names are sensitive:** Keep your real config in `config/projects.json.backup` and commit the anonymized version.

### 2. Backend Setup

```bash
# 1. Navigate to project root
cd EngineeringDeliveryHealthAnalyzer

# 2. Create Python virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Create .env file (see "JIRA Credentials Setup" above)

# 5. Start the backend server
uvicorn main:app --reload --port 8000
```

Backend API will be available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🌐 Production Deployment

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for complete deployment instructions including:

- Building for production
- Nginx configuration
- Systemd service setup
- SSL/TLS certificate generation
- Multi-server deployment

Quick production build:
```bash
cd frontend
npm run build  # Outputs to frontend/dist/
```

## 📊 Architecture

```
┌──────────────┐      HTTPS      ┌──────────┐
│   Browser    │ ────────────▶   │  Nginx   │
│              │                  │  :8443   │
└──────────────┘                  └────┬─────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────┐   ┌─────────────┐   ┌──────────────┐
            │   Static     │   │   FastAPI   │   │     JIRA     │
            │   Files      │   │   Backend   │   │     API      │
            │ (React SPA)  │   │   :8000     │   │              │
            └──────────────┘   └─────────────┘   └──────────────┘
```

## 🗂️ Project Structure

```
EngineeringDeliveryHealthAnalyzer/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Template for credentials
│   ├── routes/                # API endpoints
│   ├── models/                # Pydantic models
│   ├── analytics/             # Scoring, RAG, bottleneck logic
│   └── utils/                 # Project mapping utilities
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/            # API hooks
│   │   ├── types/            # TypeScript interfaces
│   │   └── utils/            # Helper functions
│   ├── .env.local            # Dev environment (localhost)
│   ├── .env.production       # Prod environment (relative URLs)
│   └── .env.example          # Template
├── data/
│   └── issues.json           # Mock/cached issue data
├── docs/
│   ├── API_REFERENCE.md      # API documentation
│   └── DEPLOYMENT.md         # Production deployment guide
└── README.md                 # This file
```

## 🔒 Security Notes

**Files that should NEVER be committed:**
- `backend/.env` (contains JIRA API token)
- `frontend/.env.local` (may contain local credentials)
- Any file with real API tokens or passwords

**Protected by `.gitignore`:**
- `backend/.env`
- `frontend/.env.local`
- `venv/`
- `node_modules/`
- `dist/`

**Safe to commit:**
- `.env.example` files (templates with placeholders)
- `.env.production` (uses relative URLs, no credentials)

## 📖 API Documentation

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/jira/spaces` | List available spaces and their JIRA project keys |
| `GET /api/v1/jira/sync` | Sync issues from JIRA (params: `space`, `project`, `fix_version`) |
| `GET /api/v1/health-score` | Get health scores for all issues |
| `GET /api/v1/health-score/by-release` | Health scores grouped by release |
| `GET /api/v1/health-score/summary` | RAG summary (no issue details) |
| `GET /api/v1/bottlenecks` | List of bottleneck issues |
| `GET /api/v1/workload` | Workload distribution by priority |

Full API documentation: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. **Do not commit real JIRA credentials**
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📝 License

Internal project for Mobileum. Not for public distribution.

## 🆘 Troubleshooting

### "Error loading spaces: Failed to fetch"

**Cause**: Frontend can't reach the backend API.

**Solutions**:
1. Check backend is running: `curl http://localhost:8000/`
2. Verify CORS settings allow your frontend URL
3. For production: Ensure nginx is proxying `/api/` correctly

### "401 Unauthorized" from JIRA

**Cause**: Invalid JIRA credentials or expired API token.

**Solutions**:
1. Verify JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN in `backend/.env`
2. Generate a new API token
3. Check you have permissions for the JIRA projects

### Backend won't start: "ModuleNotFoundError"

**Cause**: Missing Python dependencies.

**Solution**:
```bash
pip install -r backend/requirements.txt
```

### Frontend build fails

**Cause**: Missing node modules.

**Solution**:
```bash
cd frontend
npm install
npm run build
```

## 📞 Support

For issues or questions, contact the development team or open an issue in the repository.
