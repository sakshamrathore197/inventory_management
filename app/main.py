from fastapi import FastAPI,Request,Depends,Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime,date,timedelta
from sqlalchemy import or_
import csv
from io import StringIO
from fastapi.responses import StreamingResponse


from app.database import engine,Base
from app.database import get_db


from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(
    directory="app/templates"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

@app.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    # Total Products
    total_products = db.query(
        models.Product
    ).count()

    # Total Stock Quantity
    products = db.query(
        models.Product
    ).all()

    total_stock = sum(
        product.current_quantity
        for product in products
    )

    # Low Stock Items
    low_stock = db.query(
        models.Product
    ).filter(
        models.Product.current_quantity <=
        models.Product.minimum_quantity
    ).count()

    # Issued Assets
    issued_assets = db.query(
        models.Product
    ).filter(
        models.Product.status == "Issued"
    ).count()

    # Available Assets
    available_assets = db.query(
        models.Product
    ).filter(
        models.Product.status == "Available"
    ).count()

    # Repair Items
    repair_items = db.query(
        models.Product
    ).filter(
        models.Product.status == "In Repair"
    ).count()

    # Damaged Items
    damaged_items = db.query(
        models.Product
    ).filter(
        models.Product.status == "Damaged"
    ).count()

    #low stock product
    low_stock_products = db.query(
    models.Product
    ).filter(
    models.Product.current_quantity
    <=
    models.Product.minimum_quantity
    ).all()

    # Warranty Expiring Within 30 Days
    today = date.today()

    expiry_date = today + timedelta(days=30)

    warranty_expiring = db.query(
        models.Product
    ).filter(
        models.Product.warranty_expiry != None,
        models.Product.warranty_expiry <= expiry_date,
        models.Product.warranty_expiry >= today
    ).count()

    # Latest Movements
    latest_movements = db.query(
        models.MovementHistory
    ).order_by(
        models.MovementHistory.created_at.desc()
    ).limit(10).all()

    #latest record
    latest_products = db.query(
    models.Product
    ).order_by(
    models.Product.created_at.desc()
    ).limit(5).all()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_products": total_products,
            "total_stock": total_stock,
            "low_stock": low_stock,
            "issued_assets": issued_assets,
            "available_assets": available_assets,
            "repair_items": repair_items,
            "damaged_items": damaged_items,
            "warranty_expiring": warranty_expiring,
            "latest_movements": latest_movements,
            "low_stock_products": low_stock_products,
            "latest_products": latest_products
        }
    )
#ADD PRODUCT
@app.get("/products/add")
def add_product_page(
    request: Request
):
    return templates.TemplateResponse(
        "add_product.html",
        {
            "request": request
        }
    )


@app.post("/products/add")
def save_product(
    request: Request,
    product_name: str = Form(...),
    category: str = Form(...),
    brand: str = Form(None),
    model_number: str = Form(None),
    serial_number: str = Form(None),
    product_type: str = Form(None),
    unit_price: float = Form(0),
    current_quantity: int = Form(0),
    minimum_quantity: int = Form(0),
    warranty_expiry: str = Form(None),

    db: Session = Depends(get_db)
):

    # Product Name Validation
    if not product_name.strip():
        return templates.TemplateResponse(
            "add_product.html",
            {
                "request": request,
                "error": "Product Name is required"
            }
        )

    # Category Validation
    if not category.strip():
        return templates.TemplateResponse(
            "add_product.html",
            {
                "request": request,
                "error": "Category is required"
            }
        )

    # Duplicate Product Check
    existing_product = db.query(
        models.Product
    ).filter(
        models.Product.product_name == product_name
    ).first()

    if existing_product:
        return templates.TemplateResponse(
            "add_product.html",
            {
                "request": request,
                "error": "Product already exists"
            }
        )

    # Quantity Validation
    if current_quantity < 0:
        return templates.TemplateResponse(
            "add_product.html",
            {
                "request": request,
                "error": "Current Quantity cannot be negative"
            }
        )

    if minimum_quantity < 0:
        return templates.TemplateResponse(
            "add_product.html",
            {
                "request": request,
                "error": "Minimum Quantity cannot be negative"
            }
        )

    # Price Validation
    if unit_price < 0:
        return templates.TemplateResponse(
            "add_product.html",
            {
                "request": request,
                "error": "Unit Price cannot be negative"
            }
        )

    # Create Product
    product = models.Product(
        product_name=product_name.strip(),
        category=category.strip(),
        brand=brand,
        model_number=model_number,
        serial_number=serial_number,
        product_type=product_type,
        unit_price=unit_price,
        current_quantity=current_quantity,
        minimum_quantity=minimum_quantity,
        warranty_expiry=warranty_expiry
    )

    db.add(product)
    db.commit()

    return RedirectResponse(
        url="/products",
        status_code=303
    )

#PRODUCT LIST
@app.get("/products")
def product_list(
    request: Request,
    search: str = "",
    category: str = "",
    db: Session = Depends(get_db)
):

    query = db.query(models.Product)

    if search:

        query = query.filter(
            or_(
                models.Product.product_name.ilike(f"%{search}%"),
                models.Product.brand.ilike(f"%{search}%"),
                models.Product.model_number.ilike(f"%{search}%"),
                models.Product.serial_number.ilike(f"%{search}%")
            )
        )

    if category:

        query = query.filter(
            models.Product.category == category
        )

    products = query.all()

    return templates.TemplateResponse(
        "product_list.html",
        {
            "request": request,
            "products": products,
            "search": search
        }
    )


#PRODUCT DETAILS
@app.get("/products/{product_id}")
def product_detail(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()

    movements = db.query(
    models.MovementHistory
    ).filter(
    models.MovementHistory.product_id == product_id
    ).all()

    return templates.TemplateResponse(
        "product_detail.html",
        {
            "request": request,
            "product": product,
            "movements": movements
        }
    )

#ADD STOCK
@app.get("/stock/add")
def add_stock_page(
    request: Request,
    db: Session = Depends(get_db)
):

    products = db.query(
        models.Product
    ).all()

    return templates.TemplateResponse(
        "add_stock.html",
        {
            "request": request,
            "products": products
        }
    )

@app.post("/stock/add")
def add_stock(
    product_id: int = Form(...),
    quantity_added: int = Form(...),
    vendor_name: str = Form(None),
    purchase_date: date = Form(None),
    invoice_number: str = Form(None),
    purchase_amount: float = Form(0),
    remarks: str = Form(None),

    db: Session = Depends(get_db)
):
    product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()
      
    stock = models.StockEntry(
        product_id=product_id,
        quantity_added=quantity_added,
        vendor_name=vendor_name,
        purchase_date=purchase_date,
        invoice_number=invoice_number,
        purchase_amount=purchase_amount,
        remarks=remarks
    )

    movement = models.MovementHistory(
        product_id=product_id,
        movement_type="Stock Added",
        quantity=quantity_added,
        reference_type="Purchase",
        reference_name=vendor_name,
        vendor_name=vendor_name,
        invoice_number=invoice_number,
        movement_date=purchase_date,
        remarks=remarks
        )

    db.add(movement)
    db.add(stock)

    product.current_quantity += quantity_added



    db.commit()

    return RedirectResponse(
        "/products",
        status_code=303
    )    


#ISSUE
@app.get("/issue")
def issue_page(
    request: Request,
    db: Session = Depends(get_db)
):

    products = db.query(
        models.Product
    ).all()

    return templates.TemplateResponse(
        "issue_asset.html",
        {
            "request": request,
            "products": products
        }
    )

@app.post("/issue")
def issue_asset(
    product_id: int = Form(...),
    quantity_issued: int = Form(...),
    issued_to: str = Form(...),
    issue_type: str = Form(...),
    issue_date: date = Form(...),
    expected_return_date: date = Form(None),
    remarks: str = Form(None),

    db: Session = Depends(get_db)
):
     product = db.query(
    models.Product
    ).filter(
    models.Product.id == product_id
    ).first()
     if quantity_issued > product.current_quantity:
          return {
        "error": "Insufficient stock available"
        }
     issue = models.AssetIssue(
          product_id=product_id,
          quantity_issued=quantity_issued,
          issued_to=issued_to,
          issue_type=issue_type,
          issue_date=issue_date,
          expected_return_date=expected_return_date,
          remarks=remarks
          )
     db.add(issue)
     product.current_quantity -= quantity_issued
     product.status = "Issued"
     movement = models.MovementHistory(
          product_id=product_id,
          movement_type="Issued",
          quantity=quantity_issued,
          reference_type=issue_type,
          reference_name=issued_to,
          movement_date=issue_date,
          remarks=remarks
          )
     db.add(movement)
     db.commit()
     return RedirectResponse(
          "/products",
          status_code=303
          )


#RETURN
@app.get("/return")
def return_page(
    request: Request,
    db: Session = Depends(get_db)
):

    products = db.query(
        models.Product
    ).all()

    return templates.TemplateResponse(
        "return_asset.html",
        {
            "request": request,
            "products": products
        }
    )

@app.post("/return")
def return_asset(
    product_id: int = Form(...),
    returned_by: str = Form(...),
    return_date: date = Form(...),
    quantity_returned: int = Form(...),
    condition: str = Form(...),
    remarks: str = Form(None),

    db: Session = Depends(get_db)
):
     product = db.query(
    models.Product
    ).filter(
    models.Product.id == product_id
    ).first()
     
     asset_return = models.AssetReturn(
     product_id=product_id,
     returned_by=returned_by,
     return_date=return_date,
     quantity_returned=quantity_returned,
     condition=condition,
     remarks=remarks
    )
     db.add(asset_return)

     if condition == "Good":
          product.current_quantity += quantity_returned
          product.status = "Available"
     elif condition == "Repair Required":
          product.status = "In Repair"
     elif condition == "Lost":
          product.status = "Retired"  

     movement = models.MovementHistory(
     product_id=product_id,
     movement_type="Returned",
     quantity=quantity_returned,
     reference_type="Return",
     reference_name=returned_by,
     movement_date=return_date,
     remarks=condition
    )
     db.add(movement)    

     db.commit()
     return RedirectResponse(
    "/products",
    status_code=303
    )    


#REPORT
@app.get("/reports")
def reports(
    request: Request,
    keyword: str = "",
    category: str = "",
    status: str = "",
    date_from: str = "",
    date_to: str = "",
    db: Session = Depends(get_db)
):

    query = db.query(models.Product)

    if keyword:
        query = query.filter(
            models.Product.product_name.ilike(
                f"%{keyword}%"
            )
        )

    if category:
        query = query.filter(
            models.Product.category == category
        )

    if status:
        query = query.filter(
            models.Product.status == status
        )

    if date_from:
        query = query.filter(
            models.Product.created_at >= date_from
        )

    if date_to:
        query = query.filter(
            models.Product.created_at <= date_to
        )    


    products = query.all()

    return templates.TemplateResponse(
        "reports.html",
        {
            "request": request,
            "products": products,
            "keyword": keyword,
            "category": category,
            "status": status

        }
    )

#EXPORT-CSV
@app.get("/export-csv")
def export_csv(
    db: Session = Depends(get_db)
):

    products = db.query(
        models.Product
    ).all()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Product Name",
        "Category",
        "Brand",
        "Quantity",
        "Minimum Quantity",
        "Status"
    ])

    for product in products:

        writer.writerow([
            product.id,
            product.product_name,
            product.category,
            product.brand,
            product.current_quantity,
            product.minimum_quantity,
            product.status
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=inventory_report.csv"
        }
    )

#edit-product
@app.get("/products/edit/{product_id}")
def edit_product_page(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()

    return templates.TemplateResponse(
        "edit_product.html",
        {
            "request": request,
            "product": product
        }
    )

#Delete-product
@app.get("/products/edit/{product_id}")
def edit_product_page(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()

    return templates.TemplateResponse(
        "edit_product.html",
        {
            "request": request,
            "product": product
        }
    )

@app.post("/products/edit/{product_id}")
def update_product(
    product_id: int,
    product_name: str = Form(...),
    category: str = Form(...),
    brand: str = Form(None),

    db: Session = Depends(get_db)
):

    product = db.query(
        models.Product
    ).filter(
        models.Product.id == product_id
    ).first()

    product.product_name = product_name
    product.category = category
    product.brand = brand

    db.commit()

    return RedirectResponse(
        "/products",
        status_code=303
    )
