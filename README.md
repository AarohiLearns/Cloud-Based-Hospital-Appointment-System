# Cloud Based Hospital Appointment System

A cloud-native, full-stack hospital outpatient appointment scheduling system. Patients browse doctors, view real-time open 30-minute consultation slots, and book appointments without physical queues. Hospital administrators manage doctor profiles, shift schedules, and patient appointments.

Deployed live on **Amazon Web Services (AWS)** within the **AWS Free Tier** using an **Amazon EC2 `t3.micro`** instance in the **Asia Pacific (Sydney) region (`ap-southeast-2`)**.

---

## 🌐 Live Cloud Deployment & Demo

* **Live Web Application:** [http://13.210.205.45:8000](http://13.210.205.45:8000)
* **Interactive API Docs (Swagger UI):** [http://13.210.205.45:8000/docs](http://13.210.205.45:8000/docs)
* **AWS Public DNS:** `ec2-13-210-205-45.ap-southeast-2.compute.amazonaws.com`
* **🎥 Project Demonstration Video:** [Watch Demo Video](https://drive.google.com) *(Add Drive or YouTube link here)*

---

## ⚡ Key Architectural Features

1. **Unified Single-Server Deployment:**
   * The production React 18 Single Page Application (SPA) bundle is mounted directly into FastAPI (`app/static/`).
   * Serving both the frontend and REST API on **Port 8000** eliminates Cross-Origin Resource Sharing (CORS) errors, prevents HTTPS/HTTP mixed-content browser blocking, and operates at **₹0 extra domain cost**.

2. **Dynamic 30-Minute Slot Calculation:**
   * Pure mathematical slot-generation logic (`app/services/slots.py`) takes a doctor's shift window and steps through it in 30-minute intervals (`cursor += step`).
   * Slots are converted to standard UTC to prevent timezone inconsistencies across clients.

3. **Atomic Double-Booking Prevention (Partial Unique Index):**
   * Enforces a database-level partial unique index:
     ```python
     Index(
         "uq_appointment_active_slot",
         "doctor_id", "start_time",
         unique=True,
         sqlite_where=text("status <> 'cancelled'")
     )
     ```
   * If two patients confirm the exact same slot at the same millisecond, the database engine accepts the first and rejects the second with an **HTTP 409 Conflict** error. Cancelled appointments are automatically excluded so slots can be re-booked.

4. **24/7 Cloud Process Supervision (`systemd`):**
   * Registered as a Linux background daemon (`hospital.service`) on Amazon Linux 2023.
   * Runs continuously without an active terminal session and automatically recovers upon system reboots or process crashes (`Restart=always`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, React Router |
| **Backend** | Python 3.11, FastAPI, Uvicorn (ASGI) |
| **Database & ORM** | SQLite, SQLAlchemy 2.0 (Async), aiosqlite |
| **Security** | JWT (JSON Web Tokens), Bcrypt password hashing, Role-Based Access Control (RBAC) |
| **Cloud (AWS)** | Amazon EC2 (`t3.micro`), Amazon Linux 2023, AWS Security Groups (Ports 8000 & 22), Amazon EBS |
| **Process Management** | Linux `systemd` daemon (`hospital.service`) |

---

## 👥 Demo Accounts

The database comes pre-seeded with initial accounts for testing:

| Role | Email | Password | Access / Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@hospital.com` | `Admin@123` | View all appointments, manage doctor shifts, add doctors |
| **Patient** | `patient@hospital.com` | `Patient@123` | Browse doctors, view real-time open slots, book & cancel appointments |

*Visitors can also self-register as a new patient on the website.*

---

## 💻 Local Development Setup

### 1. Prerequisites
* Python 3.10+ (Python 3.11 recommended)
* Node.js 18+ (with npm)

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m scripts.seed            # Seeds demo doctors and accounts
uvicorn app.main:app --reload --port 8000
```
Backend API will be running on `http://localhost:8000` (Docs: `http://localhost:8000/docs`).

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend development server will open on `http://localhost:5173`.

---

## 🚀 Cloud Deployment (AWS EC2)

The project includes an automated deployment shell script (`deploy_ec2.sh`) for Amazon Linux 2023 / Ubuntu:

```bash
# 1. Connect to your EC2 instance via SSH or EC2 Instance Connect
# 2. Run the deployment script:
bash deploy_ec2.sh
```

The script automatically:
1. Installs Python 3.11, pip, and Git.
2. Clones the repository.
3. Creates a virtual environment and installs Python dependencies.
4. Seeds the SQLite database (`hospital.db`).
5. Configures and starts the `hospital.service` systemd daemon on Port 8000.

---

## 📂 Project Structure

```text
hospital-appointment-system/
│
├── deploy_ec2.sh                  # Automated AWS EC2 setup and deployment script
├── backend/                       # Python FastAPI backend & static bundle
│   ├── app/
│   │   ├── main.py                # FastAPI entry point, static mount, CORS
│   │   ├── core/                  # Security (JWT, bcrypt), config, exceptions
│   │   ├── db/                    # SQLAlchemy async session, Base metadata
│   │   ├── models/                # Database models (User, Doctor, Appointment)
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── repositories/          # Isolated database query logic
│   │   ├── services/              # Business logic (slots.py, availability, booking)
│   │   ├── api/v1/endpoints/      # API routes (auth, doctors, appointments, health)
│   │   └── static/                # Compiled React SPA (served on Port 8000)
│   ├── scripts/                   # seed.py (initial demo data)
│   └── requirements.txt
│
└── frontend/                      # React 18 source code
    └── src/
        ├── pages/                 # Doctors, DoctorDetail, MyAppointments, Admin, Login
        ├── components/            # Navbar, ProtectedRoute, Alert
        └── api/                   # API client helper modules
```

---

## 🔒 Security & Privacy Notice
* Passwords are never stored in plaintext; all user credentials use salted `bcrypt` hashes.
* Stateless JWT authentication is signed using secret HMAC-SHA256 tokens with automatic expiration.
* Sensitive files (`.env`, private keys `*.pem`, local database files) are strictly excluded via `.gitignore`.
