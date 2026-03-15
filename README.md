# GÜDLFT — Regional Booking Application
### Python Testing & QA Project | OpenClassrooms

A lightweight Flask application for managing regional strength competition registrations.
This repository is a QA fork of the original OpenClassrooms prototype, rebuilt with full
test coverage, bug fixes, and performance verification.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Running the Application](#running-the-application)
4. [Project Structure](#project-structure)
5. [Running Tests](#running-tests)
   - [All Tests](#all-tests)
   - [Unit Tests](#unit-tests)
   - [Integration Tests](#integration-tests)
   - [Functional Tests (Selenium)](#functional-tests-selenium)
   - [Performance Tests (Locust)](#performance-tests-locust)
6. [Test Coverage](#test-coverage)
7. [Known Limitations](#known-limitations)
8. [Branch Strategy](#branch-strategy)

---

## Project Overview

This project implements Phase 1 bug fixes and Phase 2 features for the GÜDLFT regional
booking platform, following a TDD (Test-Driven Development) approach.

**Stack:**
- Python 3.x
- Flask (microframework)
- JSON files for data storage (`clubs.json`, `competitions.json`)
- pytest + pytest-cov (unit and integration tests)
- Selenium WebDriver (functional/browser tests)
- Locust (performance tests)

**Phases completed:**
- Phase 1: Bug fixes — login crash, booking validation, points deduction, past competition blocking
- Phase 2: Public points display board, performance verification

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/SiRipo92/Python_Testing.git
cd Python_Testing
git checkout QA
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify data files exist

The application requires two JSON data files at the project root:

- `clubs.json` — list of clubs with email and points
- `competitions.json` — list of competitions with dates and available places

Example `clubs.json`:
```json
{
    "clubs": [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
        {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
    ]
}
```

Example `competitions.json`:
```json
{
    "competitions": [
        {"name": "Spring Festival", "date": "2030-03-27 10:00:00", "numberOfPlaces": "25"},
        {"name": "Fall Classic", "date": "2030-10-22 13:30:00", "numberOfPlaces": "13"}
    ]
}
```

---

## Running the Application

```bash
python server.py
```

Or using Flask CLI:

```bash
flask --app server run
```

The app will be available at `http://127.0.0.1:5000`

---

## Project Structure

```
Python_Testing/
├── server.py                        # Main Flask application
├── clubs.json                       # Club data (email, name, points)
├── competitions.json                # Competition data (name, date, places)
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # pytest configuration
├── templates/
│   ├── index.html                   # Login page
│   ├── welcome.html                 # Summary/dashboard page
│   ├── booking.html                 # Booking form page
│   └── points-board.html            # Public points board
├── tests/
│   ├── conftest.py                  # Shared fixtures (mock data, mock_client, make_booking)
│   ├── unit/
│   │   ├── test_login.py            # Login route tests
│   │   ├── test_booking.py          # Booking and validation tests
│   │   ├── test_points_board.py     # Points board route tests
│   │   └── test_loading.py          # Data loading function tests
│   ├── integration/
│   │   └── test_integration.py      # Full user journey tests
│   ├── functional/
│   │   └── test_functional.py       # Selenium browser tests
│   ├── performance/
│   │   └── locustfile.py            # Locust load tests
│   └── reports/
│       ├── htmlcov/                 # HTML coverage report (generated)
│       └── Locust_*.html            # Locust performance report (generated)
└── .github/
    └── ISSUE_TEMPLATE/
        ├── bug_report.yml
        ├── feature_request.yml
        └── improvement.yml
```

---

## Running Tests

### All Tests

Run the full test suite (unit + integration + functional):

```bash
pytest -v
```

Run with live logging output:

```bash
pytest -v -s
```

---

### Unit Tests

Unit tests cover individual routes and functions in isolation using mock data.
They never touch `clubs.json` or `competitions.json`.

**Run all unit tests:**
```bash
pytest tests/unit/ -v
```

**Run a specific test file:**
```bash
pytest tests/unit/test_login.py -v
pytest tests/unit/test_booking.py -v
pytest tests/unit/test_points_board.py -v
pytest tests/unit/test_loading.py -v
```

**Test classes and what they cover:**

| File | Class | What it tests |
|---|---|---|
| test_login.py | TestLogin | Valid/invalid email login, redirect behaviour |
| test_booking.py | TestPurchasePlaces | Competition place deduction after booking |
| test_booking.py | TestPurchaseValidation | Points cap, 12-place cap, availability cap |
| test_booking.py | TestBookRoute | book() route, past competition blocking, unknown data |
| test_points_board.py | TestPointsBoard | Public access, data display, privacy, empty state |
| test_loading.py | TestDataLoading | FileNotFoundError handling for JSON loading |

---

### Integration Tests

Integration tests verify that multiple routes work correctly together in sequence,
simulating a complete user session.

**Run integration tests:**
```bash
pytest tests/integration/ -v -s
```

**What is tested:**

Full booking journey across 6 routes in a single session:
1. `GET /pointsBoard` — verify initial points before booking
2. `POST /showSummary` — login with valid email
3. `GET /book/<competition>/<club>` — access booking page
4. `POST /purchasePlaces` — book 3 places
5. `GET /logout` — logout
6. `GET /pointsBoard` — verify points board reflects deduction

> **Note:** Integration tests use a `reset_server_data` fixture (`autouse=True`) defined
> at the top of the integration test file. This resets mock data before each test
> without affecting the unit test suite.

---

### Functional Tests (Selenium)

Functional tests use Selenium WebDriver to test real browser interactions
against a live Flask server. Chrome runs in headless mode — no window opens.

**Prerequisites:**
- Google Chrome installed
- No manual ChromeDriver installation needed — Selenium 4.6+ manages this automatically

**Important:** Do NOT start the Flask server manually before running functional tests.
The `app_server` fixture starts Flask on port 5002 automatically.

**Run functional tests:**
```bash
pytest tests/functional/ -v -s
```

**What is tested:**

| Test | Type | Description |
|---|---|---|
| test_index_page_loads | Happy | Homepage renders login form |
| test_valid_login_loads_summary | Happy | Valid email loads welcome page |
| test_booking_flow | Happy | Login → Book Places → submit → confirmation |
| test_points_board_loads_without_login | Happy | Public access to points board |
| test_unknown_email_shows_error | Sad | Error message shown for unknown email |
| test_booking_attempt_insufficient_points | Sad | Blocked when points insufficient |
| test_booking_attempt_more_than_12_places | Sad | Blocked when exceeds 12-place cap |

---

### Performance Tests (Locust)

Performance tests simulate multiple simultaneous users to verify response times
meet the specification requirements.

**Specification requirements:**
- Maximum **5 seconds** to load any page
- Maximum **2 seconds** for point balance updates
- Default: **6 simultaneous users**

**Important:** Do NOT start the Flask server manually before running Locust.
The locustfile starts its own server on port 5002 with factory data injected.

**Factory data used:**
- 500 fake clubs (simulates production scale dataset)
- 100 fake competitions

> Factory data is only used for performance tests. Unit and integration tests
> always use controlled mock data from `conftest.py` fixtures.

---

**Option A — Web UI (recommended):**

```bash
locust -f tests/performance/locustfile.py --host=http://localhost:5002
```

Then open `http://localhost:8089` and enter:
- Number of users: `6`
- Spawn rate: `1`
- Click **Start swarming**

**Option B — Headless (terminal only):**

```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:5002 \
  --users 6 \
  --spawn-rate 1 \
  --run-time 60s \
  --headless \
  --csv=tests/performance/results
```

**Verified performance results:**

| Route | 50th percentile | 95th percentile | Max | Requirement |
|---|---|---|---|---|
| GET /pointsBoard | 5ms | 9ms | 110ms | < 5000ms ✅ |
| POST /showSummary | 7ms | 25ms | 110ms | < 5000ms ✅ |

Tested with 500 clubs and 100 competitions, 6 users, over 8+ minutes.
**0 failures recorded.**

Full Locust report available in `tests/reports/`.

---

## Test Coverage

Coverage is configured in `pytest.ini` and outputs to `tests/reports/htmlcov/`.

```bash
pytest tests/unit/ tests/integration/ --cov=server --cov-report=html:tests/reports/htmlcov
```

Open `tests/reports/htmlcov/index.html` in a browser to view the full report.

**Current coverage: 99%** (72 statements, 1 missing)

---

## Known Limitations

| # | Limitation | Notes |
|---|---|---|
| Data persistence | Updates stored in memory only — lost on server restart | JSON write-back or database needed for production |
| Max 12 reservations tracking | No mechanism to track cumulative bookings per club across sessions | Requires database logging |
| Email format validation | No regex validation on email input | Improvement branch identified |
| Logout session | No session management — logout simply redirects to index | Known architectural constraint of stateless design |

---

## Branch Strategy

| Branch type | Naming convention | Purpose |
|---|---|---|
| Bug fix | `fix/descriptive-name` | One bug per branch |
| Feature | `feature/descriptive-name` | One feature per branch |
| Improvement | `improvement/descriptive-name` | Refactoring, PEP8, etc. |
| Tests | `tests/type` | Test suite additions |
| QA | `QA` | Working deliverable — all fix/feature branches merge here |
| master | `master` | Original broken code — protected, never modified |

All pull requests target the `QA` branch.
`master` is branch-protected and contains the original OpenClassrooms code for reference.

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Locust Documentation](https://docs.locust.io/)
- [Coverage Documentation](https://coverage.readthedocs.io/)
- [OpenClassrooms Original Repo](https://github.com/OpenClassrooms-Student-Center/Python_Testing)