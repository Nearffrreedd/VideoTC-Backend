from datetime import date
from fastapi import Query
from sqlalchemy.orm import Session
from typing import Optional

@app.get("/sales/")
def get_sales(
    product_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Sales)

    if product_id:
        query = query.filter(Sales.product_id == product_id)

    if start_date:
        query = query.filter(Sales.date >= start_date)

    if end_date:
        query = query.filter(Sales.date <= end_date)

    result = query.all()
    return result
