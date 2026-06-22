# 🛡️ MetricGuard — AIOps Anomaly Detection Platform

![Status](https://img.shields.io/badge/Status-Completed_v1.0-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-19-61dafb?style=for-the-badge&logo=react)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?style=for-the-badge&logo=docker)
MetricGuard is an AI-powered, real-time system monitoring and anomaly detection platform built for intelligent IT operations (AIOps). It collects live system metrics and application logs, transmits them to a centralized backend API, and applies a dual-model machine learning pipeline (Isolation Forest + LSTM Autoencoder) to detect both instant point anomalies and long-term temporal behavior anomalies — all presented through a modern, real-time React dashboard.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Real-time Metric Collection** | Monitors CPU, RAM, Disk usage, network I/O, and process counts via a lightweight agent |
| **Application Log Monitoring** | Watches log files for new entries, parses them into structured JSON, and forwards to the backend |
| **Dual ML Anomaly Detection** | Isolation Forest for point anomalies + LSTM Autoencoder for temporal sequence anomalies |
| **Log Anomaly Detection** | TF-IDF vectorization + Isolation Forest model for detecting anomalous log patterns |
| **Root Cause Analysis (RCA)** | Automated RCA classification with ML-based root cause breakdown |
| **Metric-Log Correlation** | Correlates metric spikes with concurrent log anomalies for unified insights |
| **Incident Management** | Auto-generated incidents with severity scoring, deduplication, and lifecycle tracking |
| **Smart Recommendations** | Knowledge-base-driven remediation suggestions for each incident type |
| **Real-time Alerting** | Live alert stream with configurable thresholds and priority levels |
| **Automated PDF Reports** | One-click PDF report generation with direct browser download |
| **Historical Knowledge Base** | Stores resolved incidents as searchable knowledge for future reference |
| **Unified Dashboard** | Modern React + Vite frontend with real-time data visualization |
| **Docker Deployment** | Full one-command Docker Compose deployment for all services |

---

## 📂 Project Structure

```text
MetricGuard/
│
├── src/                              # Backend source code
│   ├── app/                          # FastAPI core application
│   │   ├── main.py                   # Application entry point with lifespan management
│   │   ├── database.py               # SQLAlchemy engine, session, and TiDB Cloud connection
│   │   ├── models.py                 # ORM models (Metric, Anomaly, Log, etc.)
│   │   ├── schemas.py                # Pydantic request/response schemas
│   │   ├── crud.py                   # Database CRUD operations
│   │   ├── ml_service.py             # ML model loading & inference service
│   │   └── routers/                  # API route handlers
│   │       ├── metrics.py            # POST/GET /metrics/
│   │       ├── anomalies.py          # GET /anomalies/
│   │       ├── logs.py               # POST/GET /logs/
│   │       └── ml.py                 # ML inference & RCA endpoints
│   │
│   └── backend/                      # Extended backend modules
│       ├── routes/                   # Additional API routes
│       │   ├── correlation_routes.py # GET /correlations/latest
│       │   ├── incident_routes.py    # CRUD /incidents/
│       │   ├── log_anomaly_routes.py # GET /log-anomalies
│       │   └── report_routes.py      # POST /reports/generate, GET /reports/download
│       ├── alerting/                 # Real-time alert engine
│       ├── api/                      # Alert REST API routes
│       ├── jobs/                     # Background scheduler (correlation analysis)
│       ├── knowledge_base/           # Historical incident knowledge base
│       ├── models/                   # Extended ORM models
│       ├── recommendation_engine/    # Smart remediation suggestion engine
│       ├── report_generator/         # PDF report generation (ReportLab)
│       ├── schemas/                  # Extended Pydantic schemas
│       ├── service_impact/           # Service impact analysis
│       ├── services/                 # Log anomaly detection service
│       ├── tests/                    # Backend unit tests
│       ├── utils/                    # Utility functions
│       └── requirements.txt          # Backend Python dependencies
│
├── frontend/                         # React + Vite dashboard
│   └── src/
│       ├── App.jsx                   # Main application with tab navigation
│       ├── index.css                 # Global styles and design system
│       ├── services/
│       │   └── api.js                # Axios-based API client
│       └── components/
│           ├── MetricCards.jsx        # Live CPU/RAM/Disk metric cards
│           ├── MetricsChart.jsx       # Resource trend line charts
│           ├── MetricAnomalies.jsx    # Metric anomaly feed
│           ├── LogAnomalies.jsx       # Log anomaly feed
│           ├── CorrelationPanel.jsx   # Metric-log correlation insights
│           ├── RCAView.jsx            # Root cause analysis breakdown
│           ├── LiveAlerts.jsx         # Real-time alert stream
│           ├── IncidentTable.jsx      # Active incident management table
│           ├── RecommendationPanel.jsx # Smart remediation suggestions
│           ├── ReportsPanel.jsx       # PDF report generation & download
│           └── KnowledgeBasePanel.jsx # Historical knowledge base viewer
│
├── agent/                            # Production monitoring agent
│   ├── main.py                       # Agent entry point
│   ├── collector.py                  # System metric collection (psutil)
│   ├── sender.py                     # HTTP sender to backend
│   ├── log_collector.py              # Log file monitoring (watchdog + pygtail)
│   ├── log_parser.py                 # Structured log parsing
│   └── config.yaml                   # Agent runtime configuration
│
├── models/                           # Pre-trained ML model weights
│   ├── isolation_forest/             # Isolation Forest model + scaler
│   ├── encoder/                      # LSTM Autoencoder model + scaler
│   └── isolation_forest_log/         # Log anomaly Isolation Forest model
│
├── docker/                           # Docker configuration
│   ├── docker-compose.yml            # Full orchestration (backend, frontend, agent, demo)
│   ├── Dockerfile.backend            # Backend API container
│   ├── Dockerfile.frontend           # Frontend Vite container
│   └── Dockerfile.monitoring         # Agent container
│
├── tests/                            # Test suites
│   ├── test_api.py                   # API endpoint tests
│   ├── test_alerting.py              # Alerting system tests
│   ├── test_correlation.py           # Correlation engine tests
│   ├── test_incident_management.py   # Incident management tests
│   ├── test_service_impact.py        # Service impact tests
│   ├── test_recommendation_engine.py # Recommendation engine tests
│   ├── test_integration.py           # End-to-end integration tests
│   └── testing/                      # Anomaly simulation & stress tests
│
├── scripts/                          # Automation & utility scripts
│   ├── start_with_logs.ps1           # Docker startup with file logging
│   ├── demo_start.ps1                # Local demo environment startup
│   ├── demo_generator.py             # Demo data generator (metrics + logs)
│   └── seed_demo_data.py             # Database seeding script
│
├── docs/                             # Documentation
│   ├── deployment/                   # Deployment guides
│   └── legacy_monitoring/            # Legacy monitoring docs (deprecated)
│
├── .env                              # Environment variables (DB credentials, etc.)
└── README.md                         # This file
```

---

## 🧠 ML Model Architecture

MetricGuard uses a dual-model pipeline for comprehensive anomaly detection:

### 1. Isolation Forest (Point Anomaly Detection)
- **Purpose:** Detects instantaneous metric spikes and outliers
- **Features:** CPU usage, RAM usage, Disk usage (normalized)
- **Output:** Binary anomaly classification + anomaly score
- **Location:** `models/isolation_forest/`

### 2. LSTM Autoencoder (Temporal Anomaly Detection)
- **Purpose:** Detects long-term behavioral drift and temporal patterns
- **Architecture:** Sequence-to-sequence autoencoder with reconstruction error scoring
- **Features:** Multivariate time-series windows
- **Output:** Reconstruction error threshold-based anomaly detection
- **Location:** `models/encoder/`

### 3. Log Anomaly Isolation Forest
- **Purpose:** Detects unusual log message patterns
- **Preprocessing:** TF-IDF vectorization of log messages
- **Output:** Anomaly classification with confidence score
- **Location:** `models/isolation_forest_log/`

> [!IMPORTANT]
> ML model weights are excluded from version control due to file size.
> Download them from: https://drive.google.com/drive/folders/1tqSjdgNn7fHwVl4YJHjdnZwWyd2xUHLK?usp=sharing
>
> Place the downloaded files inside the appropriate subdirectories under `models/`.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/metrics/` | Ingest system metrics from the agent |
| `GET` | `/metrics/` | Retrieve stored metrics with pagination |
| `GET` | `/anomalies/` | Retrieve detected metric anomalies |
| `POST` | `/logs/` | Ingest structured application logs |
| `GET` | `/logs/` | Retrieve stored logs with filtering |
| `GET` | `/log-anomalies` | Run ML inference on recent logs, return anomalies |
| `GET` | `/ml/rca/stats` | Root cause analysis statistics |
| `GET` | `/correlations/latest` | Latest metric-log correlation results |
| `GET` | `/incidents/` | List incidents with pagination |
| `GET` | `/incidents/{id}/recommendations` | Smart remediation suggestions |
| `GET` | `/alerts` | Retrieve real-time alerts |
| `POST` | `/reports/generate` | Generate PDF incident report |
| `GET` | `/reports/download/{id}` | Download generated report |
| `GET` | `/reports/` | List all generated reports |
| `GET` | `/health` | System health check (API + database) |

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+ and npm
- **Docker** & Docker Compose (for containerized deployment)
- **TiDB Cloud** or MySQL database instance

---

### Option 1: Docker Deployment (Recommended)

The simplest way to run the entire platform with a single command.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Siddharth-Pattanshetty/MetricGuard.git
cd MetricGuard
```

#### Step 2: Download ML Models

Download the pre-trained model files from [Google Drive](https://drive.google.com/drive/folders/1tqSjdgNn7fHwVl4YJHjdnZwWyd2xUHLK?usp=sharing) and place them inside the appropriate subdirectories under `models/`.

#### Step 3: Configure Environment Variables

Create a `.env` file in the project root with your database credentials:

```env
DB_HOST=your_tidb_host
DB_PORT=4000
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=metricguard
DB_SSL_CA=/path/to/ca.pem
```

#### Step 4: Run with Docker Compose

```powershell
# Standard run
docker compose -f docker/docker-compose.yml up --build

# Or with log file output (saves to logs/docker_logs.txt)
.\scripts\start_with_logs.ps1
```

This starts **all four services**:
| Container | Port | Service |
|-----------|------|---------|
| `metricguard-backend` | `8000` | FastAPI Backend API |
| `metricguard-frontend` | `5173` | React Dashboard |
| `metricguard-agent` | — | System Metric & Log Collector |
| `metricguard-demo-generator` | — | Automated Demo Data Generator |

#### Step 5: Access the Dashboard

Open your browser and navigate to: **http://localhost:5173**

---

### Option 2: Local Development Setup

#### Step 1: Clone and Install Backend

```powershell
git clone https://github.com/Siddharth-Pattanshetty/MetricGuard.git
cd MetricGuard

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install backend dependencies
pip install -r src/backend/requirements.txt
pip install -r docs/legacy_monitoring/requirements.txt
```

#### Step 2: Download ML Models

Same as Docker Step 2 above.

#### Step 3: Configure `.env`

Same as Docker Step 3 above.

#### Step 4: Start the Backend API

```powershell
$env:PYTHONPATH = "src"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Step 5: Start the Frontend

```powershell
cd frontend
npm install
npm run dev
```

#### Step 6: Start the Monitoring Agent

```powershell
python agent/main.py
```

#### Step 7 (Optional): Generate Demo Data

```powershell
python scripts/demo_generator.py
```

---

## 🖥️ Dashboard Tabs

### 1. System Overview
- Real-time CPU, RAM, and Disk metric cards with live values
- Resource trend analysis charts with historical data
- ML Root Cause Analysis breakdown
- Live alert stream with severity indicators

### 2. Anomalies Feed
- Side-by-side Metric Anomalies and Log Anomalies feeds
- Each anomaly shows timestamp, severity, anomaly score, and root cause
- Metric-Log Correlation Insights panel linking metric spikes to log events

### 3. Incident Room
- Active incident table with severity, status, and root cause
- Smart Remediation Suggestions panel powered by the recommendation engine
- Incident lifecycle management (open, acknowledged, resolved)

### 4. Automated Reports
- Select an incident and generate a PDF report with one click
- PDF is automatically downloaded to your browser
- Historical report log for previously generated reports

---

## 🧪 Testing

MetricGuard includes comprehensive test suites:

```powershell
# Set PYTHONPATH first
$env:PYTHONPATH = "src"

# Run all tests
python -m pytest tests/ -v

# Specific test suites
python -m pytest tests/test_api.py -v                      # API endpoint tests
python -m pytest tests/test_alerting.py -v                  # Alerting system tests
python -m pytest tests/test_correlation.py -v               # Correlation engine tests
python -m pytest tests/test_incident_management.py -v       # Incident management tests
python -m pytest tests/test_service_impact.py -v            # Service impact tests
python -m pytest tests/test_recommendation_engine.py -v     # Recommendation engine tests
python -m pytest tests/test_integration.py -v               # End-to-end integration tests
python -m pytest tests/testing/anomaly_test.py -v           # Anomaly simulation tests
```

---

## 📌 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python, FastAPI, Uvicorn, SQLAlchemy, Pydantic |
| **Frontend** | React 19, Vite, Axios, Recharts |
| **Database** | TiDB Cloud (MySQL-compatible), SQLAlchemy ORM |
| **ML/AI** | scikit-learn (Isolation Forest), TensorFlow/Keras (LSTM Autoencoder), pandas, NumPy |
| **Monitoring** | psutil, watchdog, pygtail |
| **Reports** | ReportLab (PDF generation) |
| **Scheduling** | APScheduler (background correlation jobs) |
| **Containerization** | Docker, Docker Compose |
| **Testing** | pytest, httpx |

---

## 📄 License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Siddharth Pattanshetty** — [GitHub](https://github.com/Siddharth-Pattanshetty)

---

<p align="center">
  <b>MetricGuard</b> — Intelligent AIOps for Modern Infrastructure<br/>
  <sub>Built with FastAPI, React, TensorFlow, and scikit-learn</sub>
</p>