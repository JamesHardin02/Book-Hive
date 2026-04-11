# Book-Hive API Documentation

## Overview

This document explains how the backend of Book‑Hive works.

## Architecture

The system follows this structure:

Frontend → API → Services → Repositories → Database

- API handles requests
- Services handle logic
- Repositories talk to the database

---

## Authentication

### Authentication Endpoints

- POST /auth/register
- POST /auth/token
- POST /auth/logout
- GET /auth/me

### Authentication Flow

1. User logs in
2. Server creates a token
3. Token is stored in a cookie
4. Protected routes require authentication

---

## Books

### Book Endpoints

- GET /books
- POST /books
- GET /books/{id}
- PATCH /books/{id}
- DELETE /books/{id}

### Book Features

- create books
- search books
- update books
- delete books

### Book Request Flow

1. Request comes to /books
2. BookService processes logic
3. BookRepo saves to database
4. Response is returned

---

## Members

### Member Endpoints

- POST /members
- GET /members
- GET /members/{id}
- PATCH /members/{id}
- DELETE /members/{id}

### Member Request Flow

1. Request goes to API
2. MemberService processes it
3. MemberRepo accesses database

---

## Loans

### Loan Endpoints

- POST /loans
- GET /loans
- PATCH /loans/{id}/return

### Loan Validation Rules

- book must exist
- member must exist
- stock must be available

### Loan Processing Flow

1. Request comes in
2. LoanService checks rules
3. Inventory is updated
4. Loan is saved

---

## Sales

### Sales Endpoints

- POST /sales
- GET /sales

### Sales Validation Rules

- stock must be enough
- book must exist

### Sales Processing Flow

1. Request comes in
2. SaleService processes it
3. Inventory decreases
4. Sale is saved

---

## Dashboard

### Dashboard Endpoint

- GET /dashboard/low-stock

### Dashboard Features

- shows low‑stock books
- shows out‑of‑stock books

---

## Settings

### Settings Endpoints

- GET /settings/low-stock-threshold
- PUT /settings/low-stock-threshold

### Settings Features

- controls low‑stock threshold

---

## Exports

### Export Endpoints

- GET /exports/books.csv
- GET /exports/members.csv
- GET /exports/loans.csv
- GET /exports/sales.csv

### Export Features

- downloads CSV files

---

## Health

### Health Endpoint

- GET /health

### Health Check Behavior

- checks if database is working
