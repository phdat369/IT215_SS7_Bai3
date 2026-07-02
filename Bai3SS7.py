from fastapi import FastAPI, status, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from fastapi.responses import JSONResponse
products_db = [
    {"id": 101, "name": "Bàn phím cơ", "stock": 5, "price": 1200000.0},
    {"id": 102, "name": "Chuột Gaming", "stock": 2, "price": 600000.0}
]
orders_db = []
class BaseReponse(BaseModel):
    status_code: int
    message: str
    data: Optional[Any]
    error: Optional[str]
    time_stamp: str
    path: str
def create_response(req, status_code: str, message: str, data = None, error = None):
    return BaseReponse(
        status_code=status_code,
        message= message,
        data = data,
        error = error,
        time_stamp=datetime.now().isoformat(),
        path = req.url.path
    )
app = FastAPI()
@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    response = create_response(request,exc.status_code, "Failed",error=exc.detail)
    return JSONResponse(
        status_code = exc.status_code,
        content = response.dict()
    )
@app.get("/products_db")
def get_products_db(req: Request):
    return create_response(req,status.HTTP_200_OK,"Succes",products_db)
@app.post("/orders")
def add_order(req: Request,id_input: int, quantity: int):
    check_id = next((pro for pro in products_db if pro["id"] == id_input),None)
    if check_id:
        if quantity <= 0:
            raise HTTPException (
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số lượng mua phải lớn hơn 0"
            )
        if quantity > check_id["stock"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sản phẩm không đủ số lượng trong kho"
            )
        check_id["stock"] -= quantity
        buy_product = {
            "id": id_input,
            "name": check_id["name"],
            "quantity": quantity
        }
        orders_db.append(buy_product)
        return create_response(req,status.HTTP_201_CREATED,"Success",orders_db)
    else: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ID not Found"
        )