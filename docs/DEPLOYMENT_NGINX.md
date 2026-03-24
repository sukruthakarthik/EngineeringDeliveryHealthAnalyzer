# Deployment Guide

This guide explains how to build and deploy the Engineering Delivery Health Analyzer application.

---

## Phase 1 — Build Locally (your machine)

### 1. Build the React frontend:
```bash
cd frontend
npm install          # only needed once / when deps change
npm run build        # outputs to frontend/dist/
```

### 2. Verify the backend starts cleanly:
```bash
cd ..\backend
..\venv\Scripts\activate
uvicorn main:app --host 127.0.0.1 --port 8000
# Ctrl+C after confirming it starts
```

### 3. Bundle what to transfer
You only need these files/folders on the server:

```
/opt/edha/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env               ← JIRA credentials
│   ├── routes/
│   ├── models/
│   ├── analytics/
│   └── utils/
├── data/
│   └── issues.json
└── frontend/
    └── dist/              ← built static files only (NOT src/)
```

### 4. Create a deploy archive (PowerShell):
```powershell
$src = "D:\OneDrive - Mobileum\AI\EngineeringDeliveryHealthAnalyzer"
Compress-Archive -Path `
  "$src\backend", `
  "$src\data", `
  "$src\frontend\dist" `
  -DestinationPath "$src\edha-deploy.zip"
```

---

## Phase 2 — Server Setup (one-time, on `172.17.17.104`)

### 5. Upload and extract the archive:
```bash
scp edha-deploy.zip user@172.17.17.104:/opt/
ssh user@172.17.17.104
sudo mkdir -p /opt/edha
sudo unzip /opt/edha-deploy.zip -d /opt/edha/
```

The `dist/` folder must land at `/opt/edha/frontend/dist/` — rename if needed:
```bash
sudo mv /opt/edha/dist /opt/edha/frontend      # if unzip flattened it
```

### 6. Create Python virtualenv and install deps (server only, once):
```bash
cd /opt/edha
python3.12 -m venv venv     # Use python3.12 or higher (not python3)
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 7. Create `/opt/edha/backend/.env` (JIRA credentials):
```ini
JIRA_URL=https://your-jira-instance.atlassian.net
JIRA_USER=your@email.com
JIRA_TOKEN=your-api-token
```

### 8. Create systemd service at `/etc/systemd/system/edha.service`:
```ini
[Unit]
Description=Engineering Delivery Health Analyzer API
After=network.target

[Service]
User=nginx
WorkingDirectory=/opt/edha/backend
EnvironmentFile=/opt/edha/backend/.env
ExecStart=/opt/edha/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable edha
sudo systemctl start edha
sudo systemctl status edha
```

### 9. Generate self-signed TLS certificate:
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/edha.key \
  -out /etc/ssl/certs/edha.crt \
  -subj "/CN=172.17.17.104"
```

### 10. Create Nginx config at `/etc/nginx/conf.d/edha.conf`:
**Note:** Uses ports 8080/8443 to avoid conflicts with other apps on the server.

```nginx
server {
    listen 8080;
    server_name 172.17.17.104;
    return 301 https://$host:8443$request_uri;
}

server {
    listen 8443 ssl;
    server_name 172.17.17.104;

    ssl_certificate     /etc/ssl/certs/edha.crt;
    ssl_certificate_key /etc/ssl/private/edha.key;
    ssl_protocols       TLSv1.2 TLSv1.3;

    root /opt/edha/frontend;
    index index.html;

    location /api/ {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```
```bash
sudo vi /etc/nginx/conf.d/edha.conf  # Or: sudo nano /etc/nginx/conf.d/edha.conf
sudo nginx -t
sudo systemctl reload nginx
```

**Access the app at:** `https://172.17.17.104:8443/`

---

## Phase 3 — Subsequent Updates (your machine → server)

Each time you make changes:
```powershell
# 1. Rebuild frontend
cd frontend ; npm run build

# 2. Re-archive changed pieces
Compress-Archive -Path ".\frontend\dist", ".\backend", ".\data" `
  -DestinationPath ".\edha-deploy.zip" -Force

# 3. Upload and restart
scp edha-deploy.zip user@172.17.17.104:/opt/
ssh user@172.17.17.104 "sudo unzip -o /opt/edha-deploy.zip -d /opt/edha && sudo systemctl restart edha && sudo systemctl reload nginx"
```

# Troubleshoting
## Test if Backend and Frontend APIs are working on Nginx
```bash
# Basic curl
curl http://127.0.0.1:8000/

# From the server, test the API directly
curl http://127.0.0.1:8000/api/v1/jira/spaces

# Test through nginx from the server
curl -k https://127.0.0.1:8443/api/v1/jira/spaces


# Watch backend logs in real-time
sudo journalctl -u edha -f

# Or just see recent errors
sudo journalctl -u edha -n 50

# Check nginx error log for details
sudo tail -30 /var/log/nginx/error.log
```
