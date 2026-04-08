# Book-Hive API Documentation

## Overview
This document explains how the backend of Book-Hive works.

## Architecture
The system follows this structure:

Frontend → API → Services → Repositories → Database

- API handles requests
- Services handle logic
- Repositories talk to the database

## Authentication

The system uses login with a token stored in cookies.

### Endpoints
- POST /auth/register
- POST /auth/token
- POST /auth/logout
- GET /auth/me

### How it works
1. User logs in
2. Server creates a token
3. Token is stored in cookie
4. Protected routes require authentication


## Books

### Endpoints
- GET /books
- POST /books
- GET /books/{id}
- PATCH /books/{id}
- DELETE /books/{id}

### What it does
- create books
- search books
- update books
- delete books

### Flow
1. Request comes to /books
2. BookService processes logic
3. BookRepo saves to database
4. Response is returned


## Members

### Endpoints
- POST /members
- GET /members
- GET /members/{id}
- PATCH /members/{id}
- DELETE /members/{id}

### Flow
1. Request goes to API
2. MemberService processes it
3. MemberRepo accesses database


## Loans

### Endpoints
- POST /loans
- GET /loans
- PATCH /loans/{id}/return

### Rules
- book must exist
- member must exist
- stock must be available

### Flow
1. Request comes in
2. LoanService checks rules
3. Inventory is updated
4. Loan is saved


## Sales

### Endpoints
- POST /sales
- GET /sales

### Rules
- stock must be enough
- book must exist

### Flow
1. Request comes in
2. SaleService processes it
3. Inventory decreases
4. Sale is saved


## Dashboard

### Endpoint
- GET /dashboard/low-stock

### What it does
- shows low stock books
- shows out of stock books


## Settings

### Endpoints
- GET /settings/low-stock-threshold
- PUT /settings/low-stock-threshold

### What it does
- controls low stock threshold


## Exports

### Endpoints
- GET /exports/books.csv
- GET /exports/members.csv
- GET /exports/loans.csv
- GET /exports/sales.csv

### What it does
- downloads CSV files


## Health

### Endpoint
- GET /health

### What it does
- checks if database is working


