Mini Inventory & Asset Management System
1. Project Name

Mini Inventory & Asset Management System
-------------------------------
2. Short Project Description

A FastAPI-based web application designed to manage inventory products, stock purchases, asset issuance, asset returns, and inventory movement history. The system helps organizations track product availability, stock levels, vendors, and asset allocation efficiently through a centralized dashboard.
-----------------------------
3. Features Implemented
Dashboard
Total Products Count
Total Stock Quantity
Low Stock Items
Issued Assets
Available Assets
Repair Items
Damaged Items
Warranty Expiring Soon
Latest Stock Movements
Product Management
Add Product
View Product List
Product Detail Page
Product Status Tracking
Unique Serial Number Support
Stock Management
Add Stock / Purchase Entry
Vendor Information
Invoice Number Tracking
Purchase Amount Tracking
Automatic Stock Quantity Update
Asset Issue Management
Issue Asset to Employee, Client, Project, or Internal Use
Stock Availability Validation
Automatic Stock Reduction
Issue History Tracking
Asset Return Management
Return Issued Assets
Condition-Based Return Handling
Stock Quantity Update
Return History Tracking
Movement History
Stock Added
Asset Issued
Asset Returned
Complete Movement Tracking
Search & Filter
Search by Product Name
Search by Brand
Search by Model Number
Search by Serial Number
Filter by Category
---------------------------------------
4. Setup Instructions
Clone Repository
git clone <repository-url>
cd inventory_management
Create Virtual Environment
python -m venv .venv
Activate Virtual Environment
Windows
.venv\Scripts\activate
Linux / Mac
source .venv/bin/activate
Install Dependencies
pip install -r requirements.txt
-----------------------------------------
5. Run Instructions

Start the FastAPI server:

uvicorn app.main:app --reload

Open the application in your browser:

http://127.0.0.1:8000
----------------------------------------
6. Test Login Details

Login functionality has not been implemented in this project.

Admin Login: Not Applicable
----------------------------------------
7. Important Notes
Database used: SQLite
Backend Framework: FastAPI
ORM: SQLAlchemy
Frontend: HTML, CSS, Bootstrap 5, Jinja2 Templates
Inventory data is stored permanently in the SQLite database.
Stock quantity automatically increases when stock is added.
Stock quantity automatically decreases when assets are issued.
Movement history is maintained for stock additions, issues, and returns.
Low stock items are highlighted based on minimum stock quantity.
Warranty expiry tracking is available through the dashboard.
The project is designed with a scalable structure for future enhancements such as authentication, employee management, vendor management, and export functionality.
