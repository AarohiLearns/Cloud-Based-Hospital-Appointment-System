#!/bin/bash
# ================================================================
# Hospital Appointment System - EC2 Setup Script
# Run this ONCE after connecting to your EC2 instance.
# It installs everything and starts the backend automatically.
# ================================================================

echo "=========================================="
echo "  Hospital Appointment System - EC2 Setup"
echo "=========================================="

# 1. Update system and install Python & Git
echo ""
echo "[Step 1/6] Installing Python and Git..."
sudo apt update -y && sudo apt install -y python3 python3-pip python3-venv git

# 2. Clone the project from GitHub
echo ""
echo "[Step 2/6] Downloading project from GitHub..."
cd /home/ubuntu
if [ -d "Cloud-Based-Hospital-Appointment-System" ]; then
    echo "Project folder already exists. Pulling latest code..."
    cd Cloud-Based-Hospital-Appointment-System
    git pull
else
    git clone https://github.com/AarohiLearns/Cloud-Based-Hospital-Appointment-System.git
    cd Cloud-Based-Hospital-Appointment-System
fi

# 3. Set up Python virtual environment and install packages
echo ""
echo "[Step 3/6] Setting up Python and installing packages..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create database and seed demo data
echo ""
echo "[Step 4/6] Creating database with demo doctors and accounts..."
python3 -m scripts.seed

# 5. Create systemd service (runs FastAPI 24/7 in background)
echo ""
echo "[Step 5/6] Setting up background service..."
sudo bash -c 'cat > /etc/systemd/system/hospital.service << EOF
[Unit]
Description=Hospital Appointment System Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Cloud-Based-Hospital-Appointment-System/backend
ExecStart=/home/ubuntu/Cloud-Based-Hospital-Appointment-System/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment=CORS_ORIGINS=*

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable hospital
sudo systemctl start hospital

# 6. Verify everything is working
echo ""
echo "[Step 6/6] Verifying server is running..."
sleep 3
if sudo systemctl is-active --quiet hospital; then
    echo ""
    echo "=========================================="
    echo "  SUCCESS! Your backend is now LIVE!"
    echo "=========================================="
    echo ""
    echo "  Your API is running at:"
    echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
    echo ""
    echo "  API Docs (Swagger):"
    echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
    echo ""
    echo "  Admin Login: admin@hospital.com / Admin@123"
    echo "  Patient Login: patient@hospital.com / Patient@123"
    echo ""
    echo "  COPY THE IP ADDRESS ABOVE AND SEND IT TO ME!"
    echo "=========================================="
else
    echo "Something went wrong. Checking logs..."
    sudo journalctl -u hospital --no-pager -n 20
fi
