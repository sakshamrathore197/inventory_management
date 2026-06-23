from fastapi import FastAPI,Request,Depends,Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime,date,timedelta
from sqlalchemy import or_


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
            "latest_movements": latest_movements
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
        product = models.Product(
        product_name=product_name,
        category=category,
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
        url="/",
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
