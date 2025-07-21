# Invoice Tracker

Welcome to the **Invoice Tracker API**, a backend solution built with **FastAPI** This project is designed to help businesses and individuals manage their invoices, clients, items, and payments seamlessly. With a focus on clean architecture, security, and scalability, this API provides all the necessary endpoints to keep your financial records organized and accessible.

This project is an excellent demonstration of building a RESTful API with Python's FastAPI framework, integrating with **PostgreSQL** (via **SQLAlchemy** and **Alembic**), and implementing **secure authentication** using **JWT** and **Bcrypt**

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)

## Features

- **User Authentication**: Secure user registration and login with JWT-based authentication.
- **Client Management**: Create, read, update, and delete (CRUD) operations for client records.
- **Item Management**: Manage items associated with invoices via CRUD operations.
- **Invoice Management**: Generate, update, and delete invoices with detailed records.
- **Payment Tracking**: Track payments linked to invoices with full CRUD support.
- **Database Integration**: Utilizes PostgreSQL with SQLAlchemy for robust data management.
- **Error Handling**: Comprehensive error handling for HTTP, database, and validation errors.
- **Logging**: Integrated logging for debugging and monitoring database operations.

## Technologies Used

- **Python**: Core programming language.
- **FastAPI**: High-performance web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **PostgreSQL**: Relational database for data storage.
- **PyJWT**: JSON Web Token implementation for secure authentication.
- **Pydantic**: Data validation and settings management.
- **Alembic**: Database migration tool.
- **Uvicorn**: ASGI server for running the application.
- **Passlib**: Password hashing for secure user authentication.

For a complete list of dependencies, see the [requirements.txt](#installation) file.

## Prerequisites

- Python 3.9+
- PostgreSQL database
- Git
- Virtualenv (optional but recommended)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/YousofDev/Invoice-Tracker.git
   cd Invoice-Tracker
   ```

2. **Set Up a Virtual Environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the project root and add the following:

   ```bash
   DATABASE_URL=postgresql://username:password@localhost:5432/invoice_tracker
   SECRET_KEY=your-secret-key-for-jwt
   ```

5. **Set Up the Database**:
   Run database migrations using Alembic:
   ```bash
   alembic upgrade head
   ```

## Running the Application

1. Start the FastAPI application with Uvicorn:

   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API at `http://localhost:8000`. The interactive API documentation is available at `http://localhost:8000/docs`.

## API Endpoints

The API is organized into several routers, each handling specific resources:

### Authentication (`/auth`)

- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Authenticate a user and return a JWT token.
- `GET /auth/profile`: Retrieve the authenticated user's profile (requires authentication).

### Users (`/users`)

- `GET /users`: List all users with pagination.
- `GET /users/{id}`: Retrieve a specific user by ID.

### Clients (`/clients`)

- `GET /clients`: List all clients with pagination.
- `POST /clients`: Create a new client.
- `GET /clients/{id}`: Retrieve a specific client by ID.
- `PUT /clients/{id}`: Update a client.
- `DELETE /clients/{id}`: Delete a client.

### Items (`/items`)

- `GET /items`: List all items with pagination.
- `POST /items`: Create a new item.
- `GET /items/{id}`: Retrieve a specific item by ID.
- `PUT /items/{id}`: Update an item.
- `DELETE /items/{id}`: Delete an item.

### Invoices (`/invoices`)

- `GET /invoices`: List all invoices with pagination.
- `POST /invoices`: Create a new invoice.
- `GET /invoices/{id}`: Retrieve a specific invoice by ID.
- `PUT /invoices/{id}`: Update an invoice.
- `DELETE /invoices/{id}`: Delete an invoice.

### Payments (`/payments`)

- `GET /payments`: List all payments with pagination.
- `POST /payments`: Create a new payment.
- `GET /payments/{id}`: Retrieve a specific payment by ID.
- `PUT /payments/{id}`: Update a payment.
- `DELETE /payments/{id}`: Delete a payment.

## Project Structure

```
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routers.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── client/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routers.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── invoice/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routers.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── item/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routers.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── payment/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routers.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── security.py
│   │   ├── constants.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── .env.example
├── requirements.txt
├── README.md
```
