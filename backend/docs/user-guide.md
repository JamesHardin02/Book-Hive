# Book-Hive User Guide

## Overview

Book-Hive is a manager-focused bookstore/library management application that helps staff manage books, members, loans, sales, inventory, exports, and business intelligence reporting.

The system combines day-to-day operational workflows with dashboards and report tools so managers can track circulation, stock pressure, and sales trends in one place.

---

## Main Features

- Login and authentication
- Book management
- Inventory and location management
- Member management
- Loan and return tracking
- Due-soon and overdue monitoring
- Sales tracking
- Dashboard operational panels
- Business Intelligence Workspace
- Raw CSV exports
- BI report CSV exports
- Settings management

---

## Login

Managers log in using email and password.

After successful login:

- the system stores an authentication cookie
- protected pages become accessible
- logout clears the session cookie

---

## Books

The Books feature allows managers to:

- add new books
- search books
- update book information
- delete books
- adjust stock
- assign aisle/shelf location
- set minimum stock thresholds
- look up book details by ISBN
- support separate editions of the same ISBN when needed

### Book Data Includes

- ISBN
- title
- author
- genre
- year
- edition
- optional price
- optional cover image
- on-hand quantity
- threshold
- location

---

## Inventory and Locations

Inventory management allows managers to:

- increase stock
- decrease stock
- prevent stock from going below zero
- assign or change book location
- set per-book threshold values
- monitor low stock and stockout items

Locations store physical aisle/shelf placement for titles.

---

## Members

The Members feature allows managers to:

- create members
- view member details
- search members
- update member information
- delete members

### Member Data Includes

- id
- name
- email
- phone number
- created date

---

## Loans and Returns

The Loans feature allows managers to:

- create a loan
- assign a due date
- return borrowed books
- view loan status through derived states

### Loan Statuses

The system derives loan status as:

- **active**
- **due soon**
- **overdue**
- **returned**

### Returns / Loan Status Page

The Returns page supports:

- active loan review
- due-soon filtering
- overdue filtering
- returned loan visibility
- sorting and triage by due date
- returning books directly from the page

Returning a book:

- marks the loan as returned
- increments inventory back by one

---

## Sales

The Sales feature allows managers to:

- record manual book sales
- optionally associate a member
- track quantity sold
- track unit price
- view sales history

Sales are manual operational records only.
The MVP does not include payment processing or POS features.

---

## Dashboard

The Dashboard includes two major areas:

### 1. Operational Panels

These provide quick visibility into:

- stockout books
- low-stock books
- overdue loans
- due-soon loans

These panels help managers quickly identify urgent actions.

### 2. Business Intelligence Workspace

The BI Workspace lets managers build dynamic reports using interactive charts.

Managers can:

- choose a report family
- choose a chart style
- apply filters
- view summary metrics
- view an interactive Plotly chart
- export the current BI report dataset as CSV

### Report Families

The BI Workspace includes:

- **Sales Trends**
- **Circulation Metrics**
- **Inventory Health**

### Chart Styles

The BI Workspace supports live chart styles where appropriate, such as:

- donut
- column/bar
- line
- area
- timeline

Some planned chart styles may appear visually in the selector but are not active for MVP use.

---

## BI Reports

### Sales Trends

Used to analyze:

- revenue over time
- units sold over time
- weekly/monthly time buckets

### Circulation Metrics

Used to analyze:

- checkouts by genre
- top circulated titles

### Inventory Health

Used to analyze:

- stockout titles
- low-stock titles
- healthy inventory counts
- attention-only inventory views

---

## Exports

Book-Hive supports two kinds of CSV export.

### Raw Exports

From the Exports page, managers can download:

- books
- members
- loans
- sales

### BI Report Exports

From the Dashboard BI Workspace, managers can export:

- sales trends report data
- circulation report data
- inventory health report data

These BI exports reflect the current selected report and filter settings.

### Loan Export Notes

Loans CSV includes derived status values such as:

- active
- due_soon
- overdue
- returned

---

## Settings

Managers can configure the global low-stock threshold used for:

- dashboard stock panels
- inventory health reporting
- default threshold logic

---

## Notes

- Most features require the user to be logged in
- The MVP uses a manager-only access model
- The system is intended for local development/demo use
- Report data and dashboard data depend on the current database contents
- Seeded demo data can be loaded for testing and presentation use
