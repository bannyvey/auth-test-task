from fastapi import APIRouter, Depends
from .auth import router as auth_router
from .admin import router as admin_router
from ..di.dependencies import require_admin

router= APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(admin_router, dependencies=[Depends(require_admin)])