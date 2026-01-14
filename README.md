# Backend Documentation - Store Management System

This directory contains the server-side API for the Store Management System, built with **Flask** and **SQLAlchemy**.

## 🚀 Tech Stack

-   **Framework**: [Flask](https://flask.palletsprojects.com/)
-   **Database**: SQLite (Development)
-   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
-   **Authentication**: Flask-JWT-Extended
-   **Data Analysis**: Pandas (for generating sales reports)
-   **CORS**: Flask-CORS

## 📂 Project Structure

```bash
backend/
├── instance/           # Contains the SQLite database file (store.db)
├── routes/             # API Blueprints (organized by resource)
│   ├── auth.py         # Login/Register endpoints
│   ├── products.py     # Product CRUD
│   ├── sales.py        # Sales transaction processing
│   └── analytics.py    # Dashboard data endpoints
├── models.py           # Database Models (User, Product, Sale, Category)
├── app.py              # Application factory and entry point
├── seed.py             # Script to populate DB with initial data
├── requirements.txt    # Python dependencies
└── .env                # Environment variables (Secret keys, DB URI)
```

## 🛠️ Setup & Installation

### Prerequisites

-   Python 3.8+
-   pip (Python Package Installer)

### Installation

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create a Virtual Environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the Virtual Environment:
    -   **Windows**:
        ```powershell
        .\venv\Scripts\activate
        ```
    -   **Mac/Linux**:
        ```bash
        source venv/bin/activate
        ```
4.  Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Database Initialization

To set up the database and populate it with sample data (Categories, Products):

```bash
python seed.py
```

*Note: This will create a `store.db` file in the `instance/` folder.*

### Running the Server

Start the Flask development server:

```bash
python app.py
```

The API will be accessible at `http://localhost:5000`.

## 📡 API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/auth/login` | User login (returns JWT) |
| **GET** | `/api/products` | proper list of inventory |
| **POST** | `/api/sales/checkout` | Process a new sale |
| **GET** | `/api/analytics/summary` | Get dashboard stats |

*(See `routes/` python files for full endpoint details)*

## ⚙️ Configuration

Create a `.env` file in the `backend/` directory if you need to override defaults:

```env
SECRET_KEY=your_secret_key_here
SQLALCHEMY_DATABASE_URI=sqlite:///store.db
```
