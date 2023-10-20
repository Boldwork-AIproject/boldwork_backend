from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.models import Customer, User

router = APIRouter()

# `user` 매개변수는 `User` 타입입니다.
@router.get("/info")
async def get_customers(
    user: User = Depends(get_current_user),  # `user` 매개변수는 `User` 타입입니다.
    name: str = None,  # `name` 매개변수는 `str` 타입입니다.
    search: str = None,  # `search` 매개변수는 `str` 타입입니다.
):
    """상담사가 관리하는 고객정보"""

    # 상담사 조회
    if not user.is_admin:  # `user` 매개변수는 `User` 타입입니다.
        raise HTTPException(status_code=401, detail="관리자만 접근할 수 있습니다.")

    # 고객 목록 조회
    customers = await Customer.filter(  # `customers` 변수는 `list` 타입입니다.
        author=user,  # `user` 매개변수는 `User` 타입입니다.
        name=name,  # `name` 매개변수는 `str` 타입입니다.
        search=search,  # `search` 매개변수는 `str` 타입입니다.
    ).all()

    # 응답 생성
    return JSONResponse({
        "code": 200,
        "message": "Search successful",
        "page": customers.page,  # `page` 속성은 `int` 타입입니다.
        "size": customers.per_page,  # `size` 속성은 `int` 타입입니다.
        "totalPage": customers.pages,
        "totalCount": customers.total,
        "data": customers.items,  # `items` 속성은 `list` 타입입니다.
    })

# `customer_id` 매개변수는 `int` 타입입니다.
@router.get("/info/{customer_id}")
async def get_customer(
    customer_id: int,  # `customer_id` 매개변수는 `int` 타입입니다.
    user: User = Depends(get_current_user),  # `user` 매개변수는 `User` 타입입니다.
):
    """상담사가 관리하는 고객정보"""

    # 상담사 조회
    if not user.is_admin:  # `user` 매개변수는 `User` 타입입니다.
        raise HTTPException(status_code=401, detail="관리자만 접근할 수 있습니다.")

    # 고객 정보 조회
    customer = await Customer.get(customer_id)  # `customer` 변수는 `Customer` 타입입니다.

    # 고객이 존재하지 않으면 오류
    if not customer:
        raise HTTPException(status_code=404, detail="고객이 존재하지 않습니다.")

    # 응답 생성
    return JSONResponse({
        "code": 200,
        "message": "Customer Information Retrieved",
        "data": customer,  # `customer` 변수는 `Customer` 타입입니다.
    })