# 💳 Credit Approval System (Assignment)

This is a backend system for credit approval using historical customer and loan data. Built using **Django**, **Django REST Framework**, **PostgreSQL**, and **Celery**. It ingests past data, supports loan eligibility checking, and handles real-time loan processing.

---

## 📦 Tech Stack

- **Backend**: Django 4.x, Django REST Framework
- **Database**: PostgreSQL
- **Task Queue**: Celery
- **Broker**: Redis
- **Containerization**: Docker & Docker Compose
- **Data Ingestion**: Background task using Celery

---

## ⚙️ Features

### ✅ API Endpoints

#### 1. `/register`
- **Registers a new customer**
- Approved credit limit = `36 × monthly_income` (rounded to nearest lakh)

#### 2. `/check-eligibility`
- **Checks customer’s loan eligibility** based on credit score
- Considers:
  - Past on-time EMI payments
  - Loan count
  - Current year loan activity
  - Current debt vs approved limit
  - Interest rate thresholds

#### 3. `/create-loan`
- **Creates new loan if eligible**
- Calculates monthly EMI using compound interest

#### 4. `/view-loan/<loan_id>`
- **Get loan details + customer details**

#### 5. `/view-loans/<customer_id>`
- **Get all loans for a specific customer**

---

## 📁 Project Structure

```

Assignment/
│
├── cas/              # Main Django project
│   └── celery.py     # Celery app configuration
│
├── capp/             # Django app containing logic
│   ├── models.py     # Customer & Loan models
│   ├── views.py      # API views
│   ├── urls.py       # API routing
│   ├── tasks.py      # Celery tasks for data ingestion
│   └── serializers.py# DRF serializers
│
├── Dockerfile.web    # Dockerfile for Django web service
├── Dockerfile.celery # Dockerfile for Celery worker
├── docker-compose.yml
├── customer\_data.xlsx
├── loan\_data.xlsx
└── requirements.txt

````

---

## 🐳 Running Locally (Dockerized)

### 1️⃣ Clone the Repo
```bash
git clone https://github.com/SatvickShekhawat31/Assignment.git
cd Assignment
````

### 2️⃣ Start All Services

```bash
docker compose up --build --detach
```

This will start:

* Django web server
* PostgreSQL DB
* Redis broker
* Celery worker

### 3️⃣ Run Initial Migrations

```bash
docker compose exec web python manage.py migrate
```

---

## 🧠 Credit Score Logic

Credit score is evaluated on a scale of 0 to 100 considering:

* On-time EMI payments
* Number of past loans
* Loan activity this year
* Total approved vs current debt

**Loan approval logic is based on score:**

| Score Range | Approval Condition             | Interest Rate     |
| ----------- | ------------------------------ | ----------------- |
| > 50        | Approve directly               | As given          |
| 30-50       | Approve if interest rate ≥ 12% | Correct if needed |
| 10-30       | Approve if interest rate ≥ 16% | Correct if needed |
| < 10        | Reject                         | —                 |

Also, if current EMIs > 50% of monthly salary → reject.

If interest rate doesn’t match allowed slab, return a `corrected_interest_rate`.

---

## 📊 EMI Calculation

Compound Interest Formula used:

```
EMI = [P × R × (1+R)^N] / [(1+R)^N – 1]
Where:
P = Principal (Loan Amount)
R = Monthly Interest Rate (Annual Rate / 12 / 100)
N = Tenure (in months)
```

---

## 📂 Input Files

Place the following in the root directory:

* `customer_data.xlsx` — initial customer data
* `loan_data.xlsx` — historical loan data

These are ingested by Celery background tasks.

---

## 🧪 Bonus Points

✅ Writing unit tests in `capp/tests.py` is optional but appreciated.

---

## 🚀 Deployment Instructions

* Requires Docker & Docker Compose
* All services run with one command:

```bash
docker compose up --build --detach
```

---

## 👤 Author

**Satvick Shekhawat**

* 📧 [manushekhawat3@gmail.com](mailto:manushekhawat3@gmail.com)
* 🔗 [LinkedIn](https://www.linkedin.com/in/satvick-shekhawat-01450925a/)
* 📍 Jhujhailla, Bijnor, Uttar Pradesh, India

---

## 📄 License

This project is provided for internship assignment purposes only. Not intended for commercial use.

````

---
