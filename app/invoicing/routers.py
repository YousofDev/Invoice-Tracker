from fastapi import APIRouter

router = APIRouter()


@router.get("/invoices")
def get_all_invoices():
    return {"message": "all invoices"}
