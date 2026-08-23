# 🚆 IRCTC Journey Redesign

> **From booking a train to planning the entire journey.**

IRCTC Journey Redesign is a conceptual redesign of the railway booking experience focused on the **complete passenger journey**: train selection, first-mile and last-mile connectivity, travel time, estimated cost, and journey recommendations.



## 🎯 The Problem

A passenger's journey doesn't start at the railway station:

**Home → First-Mile Transport → Railway Station → Train → Destination Station → Last-Mile Transport → Final Destination**

Traditional railway booking primarily focuses on the train segment. Passengers must separately determine how to reach the departure station, which local transport to use, the complete travel time and cost, and whether a train is convenient when the entire journey is considered.

> **Booking a train is only one part of planning a journey.**

## 💡 What Is This Project?

This full-stack prototype combines railway journey planning with first-mile and last-mile connectivity. It brings together:

**Train Search + Filtering + Journey Planning + First-Mile Connectivity + Last-Mile Connectivity + Fare Estimation + Recommendations**

## 🧭 User Flow

```text
Homepage
    ↓
Enter Source & Destination
    ↓
Search Trains
    ↓
Filter & Compare Train Options
    ↓
Select a Train
    ↓
Choose First-Mile and Last-Mile Connectivity
    ↓
Journey Planning & Recommendation
    ↓
Journey Summary
    ↓
Confirm & Save Journey
```

## 🏗️ System Architecture

```text
React + Vite UI
        ↓ Fetch API / HTTP
Starlette JSON API
        ↓
Routes → Pydantic Schemas → Services → Providers
        ↓                         ↓
SQLite / PostgreSQL       Synthetic CSV Data
```

The backend is organized into routes, schemas, services, providers, and database adapters. The CSV provider supplies reproducible synthetic train, station, route, and transport data.

## 🗄️ Database & Data Architecture

### SQLite

SQLite is the default database for local development:

```env
DATABASE_URL=sqlite:///./ircts.db
```

### PostgreSQL

PostgreSQL is supported through SQLAlchemy and `psycopg`:

```env
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

### Synthetic CSV Data

- `backend/data/trains.csv`
- `backend/data/stations.csv`
- `backend/data/routes.csv`
- `backend/data/transport_options.csv`

Synthetic data keeps the prototype reproducible, easy to run locally, independent of private railway systems, and consistent to test.

## 🔄 Data Flow

```text
User → React Frontend → Fetch API → Starlette API
     → Routes → Pydantic Schemas → Services
     → Journey, Transport, Fare, and Recommendation Logic
     → CSV Provider / Future External API Providers
```

## 🛠️ Technology Stack

### Frontend

- React
- Vite
- React DOM
- React Router DOM
- Tailwind CSS
- Lucide React
- JavaScript with JSX
- CSS
- Fetch API
- Browser `localStorage`

The frontend handles user interaction, train search, filtering, journey selection, connectivity display, recommendations, confirmation, saved journeys, and client-side authentication token storage.

### Backend

- Python 3.11+
- Starlette
- Uvicorn
- Pydantic
- SQLAlchemy
- SQLite
- PostgreSQL
- `psycopg`
- HTTPX
- `python-dotenv`

The backend provides API routes, validation, journey planning, transport options, fare estimation, recommendations, authentication, and database/provider integration.

### Authentication & Security

- Custom HMAC-based authentication
- PBKDF2-SHA256 password hashing
- Authentication tokens stored client-side using browser `localStorage`

### Testing & Development Tools

- Python virtual environment
- pip
- pytest
- pytest-asyncio
- AnyIO
- Node.js
- npm
- Vite development server
- PostCSS
- Tailwind CSS


## 📁 Project Structure

```text
irctc_journey_redesign/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── providers/
│   │   ├── database/
│   │   ├── models/
│   │   └── utils/
│   ├── data/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── services/api.js
│   │   └── styles.css
│   ├── public/
│   ├── package.json
│   └── .env.example
└── README.md
```

Important backend directories are `routes`, `schemas`, `services`, `providers`, `database`, `models`, `utils`, `data`, and `tests`. The main frontend entry point is `frontend/src/main.jsx`; the frontend API client is `frontend/src/services/api.js`.

## 🤖 How Codex Was Used

Codex was used as an AI-assisted coding and debugging tool to accelerate implementation. It helped generate code, create and modify React components, implement backend routes, connect frontend and backend APIs, debug runtime and integration errors, refactor code, improve implementations, work through data-flow issues, and refine UI functionality. The product direction and architecture were determined during development.

## ⚙️ Step-by-Step Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/RadhaDintyala/irctc_journey_redesign.git
cd railx
```

### 2. Install Python

Install **Python 3.11 or newer** and verify it:

```bash
python --version
```

### 3. Create and Activate the Backend Virtual Environment

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```


### 4. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Backend Environment Variables

```powershell
Copy-Item .env.example .env
```

Default configuration:

```env
DEMO_MODE=true
DATABASE_URL=sqlite:///./ircts.db
FRONTEND_ORIGIN=http://localhost:5173
MAPS_API_KEY=
TRANSIT_API_KEY=
CAB_API_KEY=
```

The application runs in demo mode with SQLite and synthetic CSV data without external API keys.

### 6. Start the Backend

Run this from the `backend` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend URL: `http://localhost:8000`
Health check: `http://localhost:8000/api/health`

### 7. Install Node.js

Install **Node.js 18 or newer** and verify it:

```bash
node --version
npm --version
```

### 8. Install Frontend Dependencies

Open a second terminal:

```bash
cd frontend
npm install
```

### 9. Configure Frontend Environment Variables

```powershell
Copy-Item .env.example .env
```

Default configuration:

```env
VITE_API_URL=http://localhost:8000
```

### 10. Start the Frontend

Run this from the `frontend` directory:

```bash
npm run dev
```

Frontend URL: `http://localhost:5173`

### 11. Run the Application

Keep both services running and open:

```text
http://localhost:5173
```

## 🧪 Backend Tests

Run tests from the `backend` directory:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
```

The test suite covers health, train search, journey planning, transport recommendations, estimated fare status, invalid coordinates, train filters, and transport filters.

## 📦 Production Frontend Build

Run these commands from the `frontend` directory:

```bash
npm run build
npm run preview
```

`npm run build` must be executed inside `frontend`, while `pytest` must be executed inside `backend`.

## 🗃️ Database Configuration

SQLite is recommended for local development:

```env
DATABASE_URL=sqlite:///./ircts.db
```

For PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

When PostgreSQL is configured, SQLAlchemy and `psycopg` are used for database access. The application can continue using CSV-backed demo data where applicable if PostgreSQL is unavailable.

## 🚀 Future Scope

A production version could integrate live IRCTC/train availability, real-time train status, live railway fares, public transport APIs, maps and routing services, traffic information, dynamic fare estimation, GPS-based station detection, accessibility-aware recommendations, disruption alerts, and integrated payments.

## ⚠️ Current Limitations

This is a synthetic prototype. It does not provide live IRCTC booking, live train availability, live railway fares, live government railway data, live transport provider data, or real-money transactions.

## 📌 Project Summary

```text
Traditional Experience
Search Train → Book Ticket

Proposed Experience
Plan Journey → Find Train → Compare Options → Reach Station
→ Take Train → Leave Destination Station → Reach Final Destination
```

**IRCTC Journey Redesign turns a train booking into a complete journey-planning experience.**
