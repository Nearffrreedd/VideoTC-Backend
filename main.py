# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import database as models
from database import SessionLocal, engine

# 自动创建数据库表（首次运行时生效）
models.Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例（必须叫 app！）
app = FastAPI(title="VideoTC Backend", description="电商销量数据 API")

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应替换为你的前端域名，如 ["https://your-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库会话依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 健康检查接口
@app.get("/")
def read_root():
    return {"status": "OK", "message": "VideoTC Backend is running!"}

# ====== 销量数据 API ======

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

@app.get("/sales/", summary="查询销量记录（可按日期筛选）")
def read_sales(date_filter: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Sale)
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, "%Y-%m-%d").date()
            query = query.filter(models.Sale.date == date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式必须为 YYYY-MM-DD")
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
    if date_str
