# Mini Inventory & Asset Management System

## Project Description

A web-based Inventory and Asset Management System developed using FastAPI, SQLAlchemy, SQLite, HTML, CSS, Bootstrap, and Jinja2 Templates.

The application helps manage products, stock entries, asset issuance, asset returns, inventory tracking, reporting, and CSV export.

## Features

* Dashboard
* Product Management
* Add Product
* Edit Product
* Delete Product
* Product Details
* Add Stock
* Issue Asset
* Return Asset
* Movement History
* Low Stock Alerts
* Warranty Alerts
* Reports
* Search and Filters
* CSV Export
* Validation Handling

## Technology Used

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Jinja2
* HTML
* CSS
* Bootstrap

## Setup Instructions

```bash
git clone <repository_url>
cd inventory_management
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Instructions

```bash
uvicorn app.main:app --reload
```

## Database

SQLite database is automatically created.

## Known Limitations

* No user authentication
* No Excel export
* No PDF export

## Future Improvements

* Authentication
* Role Management
* Excel Export
* PDF Reports
* Email Notifications
