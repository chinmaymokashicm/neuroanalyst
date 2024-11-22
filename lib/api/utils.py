from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/{filepath}", tags=["file"])
async def get_file(filepath: str):
    """
    Stream file from filepath: usually to stream logs.
    """
    return FileResponse(filepath)