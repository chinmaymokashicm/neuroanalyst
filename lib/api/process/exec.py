from fastapi import APIRouter

router = APIRouter()

@router.get("/all/", tags=["process", "exec"])
async def get_all_execs():
    return {"message": "Get all execs"}

@router.get("/{exec_id}/", tags=["process", "exec"])
async def get_exec_by_id(exec_id: str):
    return {"message": f"Get exec by id {exec_id}"}

@router.get("/search/filter/", tags=["process", "exec"])
async def search_execs_by_filter(filters: dict = {}):
    return {"message": f"Search execs with filters {filters}"}

@router.get("/search/keyword/", tags=["process", "exec"])
async def search_execs_by_keyword(keyword: str = ""):
    return {"message": f"Search execs with keyword {keyword}"}

# ==================================================================================================

@router.post("/create/", tags=["process", "exec"])
async def create_exec():
    return {"message": "Create exec"}

@router.put("/{exec_id}/update/", tags=["process", "exec"])
async def update_exec(exec_id: str):
    return {"message": f"Update exec with id {exec_id}"}

@router.delete("/{exec_id}/delete/", tags=["process", "exec"])
async def delete_exec(exec_id: str):
    return {"message": f"Delete exec with id {exec_id}"}

# ==================================================================================================

@router.get("/{exec_id}/status/", tags=["process", "exec"])
async def get_exec_status(exec_id: str):
    return {"message": f"Get status of exec with id {exec_id}"}