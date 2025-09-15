# 🚆 OptiRail: AI-Driven Train Scheduling System for Kochi Metro


An intelligent decision-support platform built with Python and Django to automate and optimize the daily train induction and scheduling process for Kochi Metro Rail Limited (KMRL).

<img width="400" height="227.5" alt="image" src="https://github.com/user-attachments/assets/f00e1e11-b8d4-4838-a0c6-2807431a8fec" />



## 📜 About The Project

Kochi Metro's nightly scheduling process is a complex, time-sensitive manual task. Supervisors have a two-hour window to reconcile six different data streams—from fitness certificates to mileage logs—to decide which trains run the next day. This process is error-prone, inefficient, and not scalable for KMRL's planned fleet expansion.

Our solution is a centralized AI platform that transforms this manual task into an automated, data-driven, and predictive operation. It integrates all critical data, uses a machine learning model to generate an optimized daily roster, and provides staff with an interactive dashboard for complete operational oversight.

---
## ✨ Key Features

* **🤖 AI-Powered Ranking:** A multi-objective optimization algorithm that balances mileage, maintenance, branding, and more to generate an intelligent daily rank list.
* **🖥️ Interactive Dashboard:** A visual overview of the entire fleet with color-coded status ribbons, search, and sorting capabilities.
* **📄 AI Document Intelligence:** Automatically reads and validates data from uploaded fitness certificates and job cards using OCR technology.
* **🤔 "What-If" Simulation:** A powerful tool for supervisors to instantly model the impact of unexpected train faults on the daily schedule.
* **🔐 Role-Based Access Control (RBAC):** Secure, granular permissions for different user roles (e.g., a cleaner can only edit cleaning data).
* **📊 One-Click Reporting:** Instantly generate and download the daily induction list as a formal CSV report.
* **💬 AI Chatbot:** An integrated chatbot for staff to get instant answers about train availability and status.

---

## 🛠️ Technology Stack

* **Backend:** Python, Django Framework
* **Frontend:** Django Templates, HTML, CSS, JavaScript, Bootstrap 5
* **Database:** PostgreSQL (Production), SQLite3 (Development)
* **API:** Django REST Framework (DRF)
* **Deployment:** Docker, Gunicorn, Nginx



---
## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing.

### Prerequisites

* Python 3.10+
* Pip (Python Package Installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser to access the admin panel:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **(Optional) Seed the database with sample data:**
    ```bash
    python manage.py seed_trains
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

---
## 📖 Usage

* **Main Application:** `http://127.0.0.1:8000/`
* **Admin Panel:** `http://127.0.0.1:8000/admin/`

### Demo Credentials

You can log in with different roles to see the permission system in action. The role is assigned based on the username.

| Username    | Role                 |
| ----------- | -------------------- |
| `admin`     | Administrator        |
| `officer`   | Metro Officer        |
| `operator`  | Train Operator       |
| `maintenance`| Maintenance Worker |
| `cleaner`   | Cleaner              |

---
## 📈 Future Scope

* **Full Mobile App:** Develop the Flutter mobile app and connect it to the Django REST Framework API.
* **Real-Time IoT Integration:** Integrate with on-train sensors for live fitness and mileage data.
* **Deeper Predictive Analytics:** Enhance the ML model to predict component failure rates and optimize spare parts inventory.
