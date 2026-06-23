from sqlalchemy import*
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Date

class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key = True,
        index = True
    )

    product_name = Column(
        String,
        nullable= False
    )

    category = Column(
        String,
        nullable = False
    )

    brand = Column(String)

    model_number = Column(String)

    serial_number = Column(
        String,
        nullable = True
    )

    product_type = Column(String)

    unit_price = Column(Float)

    current_quantity = Column(
        Integer,
        default = 0
    )

    minimum_quantity = Column(
        Integer,
        default = 0
    )

    warranty_expiry = Column(String)

    status = Column(
        String,
        default="Available"
    )

    created_at = Column(
        DateTime,
        default=datetime.now
    )

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

class StockEntry(Base):
    __tablename__ = "stock_entries"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
        )

    quantity_added = Column(Integer)

    vendor_name = Column(String)

    purchase_date = Column(Date)

    invoice_number = Column(String)

    purchase_amount = Column(Float)

    warranty_expiry = Column(Date)

    remarks = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.now
        )
    
class MovementHistory(Base):
    __tablename__ = "movement_history"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    movement_type = Column(String)

    quantity = Column(Integer)

    reference_type = Column(String)

    reference_name = Column(String)

    vendor_name = Column(String)

    invoice_number = Column(String)

    movement_date = Column(Date)

    remarks = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.now
    )    

class AssetIssue(Base):
    __tablename__ = "asset_issues"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    quantity_issued = Column(Integer)

    issued_to = Column(String)

    issue_type = Column(String)

    issue_date = Column(Date)

    expected_return_date = Column(Date)

    remarks = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.now
    )

class AssetReturn(Base):
    __tablename__ = "asset_returns"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    returned_by = Column(String)

    return_date = Column(Date)

    quantity_returned = Column(Integer)

    condition = Column(String)

    remarks = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.now
    )    