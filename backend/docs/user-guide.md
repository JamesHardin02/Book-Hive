# Book-Hive User Guide

## Overview

Book-Hive is a bookstore/library management application that helps staff manage books, members, loans, sales, inventory, and reports.

## Main Features

- Login and authentication
- Book management
- Member management
- Loan tracking
- Sales tracking
- Inventory and low-stock monitoring
- CSV exports
- Settings management

## How to Use the System

### Login

Users log in using their email and password. After successful login, the system stores an authentication cookie and allows access to protected pages.

### Books

The Books feature allows users to:

- add new books
- search books
- update book information
- delete books
- adjust stock
- assign shelf location
- set minimum stock thresholds
- look up book details by ISBN

### Members

The Members feature allows users to:

- create members
- view member details
- search members
- update member information
- delete members

### Loans

The Loans feature allows users to:

- create a loan
- view active, overdue, or due-soon loans
- return borrowed books

### Sales

The Sales feature allows users to:

- record book sales
- view sales history
- filter sales by member or book

### Dashboard

The Dashboard shows:

- low-stock books
- stockout books
- threshold-based inventory alerts

### Locations

The Locations feature stores aisle and shelf information for books.

### Exports

Users can export:

- books
- members
- loans
- sales
  as CSV files.

### Settings

Users can configure the global low-stock threshold used by the dashboard.

## Notes

- Most features require the user to be logged in.
- Admin-only routes may require additional permissions.
