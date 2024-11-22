from fastapi import APIRouter

router = APIRouter()

@router.get("/all/", tags=["process", "image"])
async def get_all_processes():
    return {"message": "Get all processes"}

@router.get("/{image_id}/", tags=["process", "image"])
async def get_process_by_id(image_id: str):
    return {"message": f"Get process by id {image_id}"}

@router.get("/search/filter/", tags=["process", "image"])
async def search_processes_by_filter(filters: dict = {}):
    return {"message": f"Search processes with filters {filters}"}

@router.get("/search/keyword/", tags=["process", "image"])
async def search_processes_by_keyword(keyword: str = ""):
    return {"message": f"Search processes with keyword {keyword}"}

# ==================================================================================================

@router.post("/create/", tags=["process", "image"])
async def create_process():
    return {"message": "Create process"}

@router.put("/{image_id}/update/", tags=["process", "image"])
async def update_process(image_id: str):
    return {"message": f"Update process with id {image_id}"}

@router.delete("/{image_id}/delete/", tags=["process", "image"])
async def delete_process(image_id: str):
    return {"message": f"Delete process with id {image_id}"}