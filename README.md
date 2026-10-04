# Hospital Appointment System (local version)

Patients browse doctors, see real-time free slots and book without queueing. Admins manage doctors,
weekly schedules and the day's appointments.

- **Backend:** Python, FastAPI, SQLAlchemy 2 (async), SQLite (local), JWT auth
- **Frontend:** React 18 + Vite + React Router
- **Cloud deployment:** intentionally *not* included yet.

## 1. Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.10 or newer | `python --version` (or `python3 --version`) |
| Node.js (includes npm) | 18 or newer | `node --version` |

## 2. Run the backend (terminal 1)

A virtual environment is recommended so packages stay isolated from your system Python.

**Windows (PowerShell)**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1        # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
python -m scripts.seed            # demo data
uvicorn app.main:app --reload
```
(On Windows cmd.exe use `.venv\Scripts\activate.bat` instead.)

**macOS / Linux**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.seed
uvicorn app.main:app --reload
```

API is now on http://localhost:8000 - interactive docs at http://localhost:8000/docs.
The SQLite file `backend/hospital.db` is created automatically. Delete it to reset all data.

## 3. Run the frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to the backend, so no CORS setup is needed.

## 4. Demo accounts (created by the seed script - local only)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@hospital.com | Admin@123 |
| Patient | patient@hospital.com | Patient@123 |

You can also sign up as a new patient on the site.

**Try it:** open the site -> pick a doctor -> choose a date -> click a slot -> log in as the patient
-> confirm. Then log in as admin -> *Admin* -> view that day's appointments, mark complete or cancel.

## 5. Run the tests

```bash
cd backend            # venv active
pip install -r requirements-dev.txt
pytest
```

## 6. Project structure

```
hospital-appointment-system/
├── backend/
│   ├── app/
│   │   ├── main.py                 # app factory, middleware, router wiring
│   │   ├── core/                   # config (env), security (JWT/bcrypt), exceptions, logging
│   │   ├── db/                     # engine/session, Base + mixins, UTC datetime type
│   │   ├── models/                 # SQLAlchemy tables: user, doctor(+schedule), appointment
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── repositories/           # all database queries (one class per aggregate)
│   │   ├── services/               # business rules: auth, doctors, availability, booking
│   │   │   └── slots.py            # pure slot generation (unit-tested, no I/O)
│   │   ├── events/publisher.py     # domain events (currently logged) - hook for notifications later
│   │   └── api/
│   │       ├── deps.py             # auth guards + dependency wiring
│   │       └── v1/                 # versioned routers: auth, doctors, appointments, health
│   ├── scripts/                    # seed.py (demo data), create_admin.py
│   ├── tests/
│   └── requirements*.txt, .env.example
└── frontend/
    └── src/
        ├── api/                    # one module per backend resource + shared fetch client
        ├── context/AuthContext.jsx # login state
        ├── components/             # Navbar, ProtectedRoute, DoctorPicker, Alert
        ├── pages/                  # Doctors, DoctorDetail, Login, Register, MyAppointments, Admin/
        ├── lib/format.js           # date/time helpers (clinic timezone)
        └── config.js               # API base, clinic timezone
```

**Request flow:** `endpoint (api/v1) -> service -> repository -> database`.
Endpoints only parse/validate HTTP; services hold the rules; repositories hold SQL. Each layer can be
changed or tested on its own.

## 7. How double-booking is prevented

1. Availability = doctor's weekly schedule split into slots, minus booked slots, minus the past.
2. Booking re-checks the slot on the server (never trusts the client).
3. A partial unique index on `(doctor_id, start_time)` for non-cancelled appointments is the final
   guarantee: if two people click at the same instant, one gets HTTP 409.

## 8. Adding a feature (example: prescriptions)

1. `models/prescription.py` (+ import in `models/__init__.py`)
2. `schemas/prescription.py`
3. `repositories/prescription.py`
4. `services/prescriptions.py` (rules, permissions)
5. `api/v1/endpoints/prescriptions.py`, then include it in `api/v1/router.py`
6. Frontend: `api/prescriptions.js`, a page in `pages/`, a route in `App.jsx`
7. A test in `backend/tests/`

## 9. Known limitations / suggested next steps

- Tables are created automatically (`AUTO_CREATE_TABLES`). Add **Alembic migrations** before real data.
- Registration creates patients only; admins come from `seed.py` / `create_admin.py`.
  A "doctor" login role exists in the API but isn't linked to a doctor profile yet.
- No email/SMS notifications yet - booking events are logged by `events/publisher.py`.
- Rescheduling, rate limiting, refresh tokens and an audit log are natural next features.
- Change `JWT_SECRET` (see `backend/.env.example`) for anything beyond local use.
