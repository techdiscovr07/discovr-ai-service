"""
Background tasks API endpoints
"""
from fastapi import APIRouter, HTTPException
from app.celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter()

@router.get("/")
async def list_tasks():
    """List background tasks (stub)"""
    return {"tasks": []}

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """Get the status and result of a background task"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
        
    return response
