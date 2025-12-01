# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import database as models
from database import SessionLocal, engine

# 自动创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VideoTC Backend", description="电商销量数据 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "OK", "message": "VideoTC Backend is running!"}

@app.post("/sales/", summary="创建销量记录")
def create_sale(
    product_id: str,
    date_str: str,
    sales: int,
    db: Session = Depends(get_db)
):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式必须为 YYYY-MM-DD")
    
    db_sale = models.Sale(product_id=product_id, date=date_obj, sales=sales)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return {
        "id": db_sale.id,
        "product_id": db_sale.product_id,
        "date": str(db_sale.date),
        "sales": db_sale.sales
    }

@app.get("/sales/", summary="查询销量记录（支持产品ID、日期范围筛选）")
def read_sales(
    product_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Sale)

    if product_id:
        query = query.filter(models.Sale.product_id == product_id)

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(models.Sale.date >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date 格式必须为 YYYY-MM-DD")

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(models.Sale.date <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="end_date 格式必须为 YYYY-MM-DD")

    results = query.all()
    return [
        {
            "id": r.id,
            "product_id": r.product_id,
            "date": str(r.date),
            "sales": r.sales
        }
        for r in results
    ]

@app.put("/sales/{sale_id}", summary="更新销量记录")
def update_sale(
    sale_id: int,
    product_id: str = None,
    date_str: str = None,
    sales: int = None,
    db: Session = Depends(get_db)
):
    db_sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="记录未找到")
    
    if product_id is not None:
        db_sale.product_id = product_id
    if date_str is not None:
        try:
            db_sale.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式必须为 YYYY-MM-DD")
    if sales is not None:
        db_sale.sales = sales

    db.commit()
    db.refresh(db_sale)
    return {
        "id": db_sale.id,
        "product_id": db_sale.product_id,
        "date": str(db_sale.date),
        "sales": db_sale.sales
    }

@app.delete("/sales/{sale_id}", summary="删除销量记录")
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="记录未找到")
    db.delete(db_sale)
    db.commit()
    return {"message": "删除成功"}