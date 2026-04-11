# BookHive API Documentation

## Overview

This document explains how the BookHive backend works.

BookHive uses a layered backend structure:

Frontend → FastAPI API → Services → Repositories → MySQL

The backend provides endpoints for authentication, books, inventory/location management, members, loans, sales, dashboard summaries, BI/reporting, settings, exports, health, and observability metrics.

---

## Architecture

### Backend Layers

- API routers handle HTTP requests and responses
- Services contain business logic
- Repositories interact with the database through SQLAlchemy ORM
- MySQL stores the application data

### Core Technologies

- FastAPI
- SQLAlchemy
- MySQL
- JWT authentication
- Pydantic validation

---

## Authentication

### Authentication Endpoints

- `POST /auth/register`
- `POST /auth/token`
- `POST /auth/logout`
- `GET /auth/me`

### Authentication Flow

1. Manager logs in using email and password
2. Server validates credentials
3. Server issues a JWT
4. JWT is stored in an HttpOnly cookie
5. Protected routes require authenticated manager access

### Authentication Notes

- All authenticated users are manager/admin users for MVP use
- Invalid or expired auth returns FastAPI `detail` responses
- JWT expiry is configured through environment variables

---

## Books

### Book Endpoints

- `GET /books`
- `POST /books`
- `GET /books/{id}`
- `PATCH /books/{id}`
- `DELETE /books/{id}`
- `GET /books/lookup`
- `PATCH /books/{book_id}/stock`
- `PATCH /books/{book_id}/location`
- `PATCH /books/{book_id}/min-threshold`

### Book Features

- create books
- search/filter books
- update book information
- delete books
- OpenLibrary ISBN lookup
- stock adjustment
- shelf location assignment
- per-book threshold updates

### Book Request Flow

1. Request comes to `/books`
2. `BookService` processes logic
3. `BookRepo` and related repos save/update records
4. Response is returned

### Search and Filtering

`GET /books` supports:

- `q`
- `title`
- `author`
- `isbn`
- `genre`
- `year_min`
- `year_max`
- `offset`
- `limit`

---

## Members

### Member Endpoints

- `POST /members`
- `GET /members`
- `GET /members/{id}`
- `PATCH /members/{id}`
- `DELETE /members/{id}`

### Member Features

- create members
- search members
- update member information
- delete members

### Member Fields

- `id`
- `name`
- `email`
- `phone_number`
- `created_at`

### Member Search Filters

`GET /members` supports:

- `name`
- `email`
- `phone_number`
- `offset`
- `limit`

---

## Loans

### Loan Endpoints

- `POST /loans`
- `GET /loans`
- `PATCH /loans/{id}/return`

### Loan Features

- create loans with due dates
- return books
- view active loans
- view due-soon loans
- view overdue loans
- view returned loans through derived status

### Loan Validation Rules

- book must exist
- member must exist
- due date cannot be in the past
- stock must be available
- overdue and due-soon filters cannot both be true at the same time

### Loan Processing Flow

1. Request comes in
2. `LoanService` validates member, book, due date, and stock
3. Inventory decreases on checkout
4. Loan is saved
5. Returning a loan sets `returned_at` and increments inventory

### Loan Status Model

Loan status is derived from dates:

- `active`
- `due_soon`
- `overdue`
- `returned`

### Loan Filters

`GET /loans` supports:

- `active_only`
- `overdue_only`
- `due_soon_only`
- `due_within_days`
- `member_id`
- `book_id`
- `offset`
- `limit`

---

## Sales

### Sales Endpoints

- `POST /sales`
- `GET /sales`

### Sales Features

- record manual sales
- optionally associate a member
- decrement stock on sale
- view sales history

### Sales Validation Rules

- book must exist
- optional member must exist if provided
- stock must be enough
- quantity must be valid

### Sales Processing Flow

1. Request comes in
2. `SaleService` validates inputs
3. Inventory decreases
4. Sale is saved

### Sales Filters

`GET /sales` supports:

- `member_id`
- `book_id`
- `offset`
- `limit`

---

## Dashboard

### Dashboard Endpoint

- `GET /dashboard/low-stock`

### Dashboard Features

- shows low-stock books
- shows out-of-stock books
- uses the configured default threshold
- includes aisle/shelf location when available

### Dashboard Purpose

This endpoint powers the operational inventory panels on the dashboard.

---

## BI Reports

### Report Endpoints

- `GET /reports/sales-trends`
- `GET /reports/checkouts-by-genre`
- `GET /reports/top-titles`
- `GET /reports/inventory-health`
- `GET /reports/export.csv`

### Report Features

- report data returned as JSON suitable for Plotly charts
- summary metrics included with report response
- timeframe/filter-based reporting
- CSV export for current BI report datasets

### Sales Trends Report

`GET /reports/sales-trends`

Supported query params:

- `days`
- `bucket` = `week` or `month`
- `metric` = `revenue` or `quantity`

### Circulation Reports

`GET /reports/checkouts-by-genre`

- supports `days`

`GET /reports/top-titles`

- supports `days`
- supports `limit`

### Inventory Health Report

`GET /reports/inventory-health`

Supported query params:

- `scope` = `all` or `attention_only`

### Report CSV Export

`GET /reports/export.csv`

Supported query params:

- `report`
- `days`
- `bucket`
- `metric`
- `limit`
- `scope`

Exportable BI datasets:

- `sales_trends`
- `checkouts_by_genre`
- `top_titles`
- `inventory_health`

---

## Settings

### Settings Endpoints

- `GET /settings/low-stock-threshold`
- `PUT /settings/low-stock-threshold`

### Settings Features

- controls the global low-stock threshold
- affects low-stock and stockout reporting behavior

---

## Raw CSV Exports

### Raw Export Endpoints

- `GET /exports/books.csv`
- `GET /exports/members.csv`
- `GET /exports/loans.csv`
- `GET /exports/sales.csv`

### Raw Export Features

- downloads base operational datasets
- intended for spreadsheet review and ad hoc analysis

### Export Notes

- loans CSV includes derived loan status values
- BI/report CSV exports are handled separately under `/reports/export.csv`

---

## Locations

### Location Endpoints

- `GET /locations`
- `POST /locations`

### Location Features

- stores aisle/shelf combinations
- supports book inventory placement

---

## Health

### Health Endpoint

- `GET /health`

### Health Check Behavior

- checks database connectivity
- returns database health information

---

## Metrics

### Metrics Endpoint

- `GET /metrics`

### Metrics Features

- request count
- error count
- error rate
- latency p95
- rolling in-memory metrics window

---

## Error Handling

BookHive currently uses FastAPI’s default error response structure, primarily through readable `detail` messages.

Examples:

- invalid credentials
- book not found
- member not found
- insufficient stock
- invalid filter combinations

---

## Security Notes

- passwords are hashed with bcrypt
- JWTs are signed using environment-configured secrets
- auth is manager-scoped for MVP
- HttpOnly cookies are used for login session handling
- protected endpoints require authenticated access
