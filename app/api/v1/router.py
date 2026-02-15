from fastapi import APIRouter

from app.api.v1.endpoints.executors import router as executors_router
from app.api.v1.endpoints.handling_units import router as handling_units_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.inventory import router as inventory_router
from app.api.v1.endpoints.locations import router as locations_router
from app.api.v1.endpoints.materials import router as materials_router
from app.api.v1.endpoints.missions import router as missions_router
from app.api.v1.endpoints.movements import router as movements_router
from app.api.v1.endpoints.operators import router as operators_router
from app.api.v1.endpoints.requests import router as requests_router
from app.api.v1.endpoints.rules import router as rules_router
from app.api.v1.endpoints.vehicles import router as vehicles_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(operators_router, tags=["Operator"])
api_router.include_router(executors_router, tags=["Executor"])
api_router.include_router(vehicles_router, tags=["Vehicle"])
api_router.include_router(locations_router, tags=["Location"])
api_router.include_router(materials_router, tags=["Material"])
api_router.include_router(handling_units_router, tags=["Handling Unit"])
api_router.include_router(inventory_router, tags=["Inventory"])
api_router.include_router(missions_router, tags=["Mission"])
api_router.include_router(requests_router, tags=["Request"])
api_router.include_router(movements_router, tags=["Movement"])
api_router.include_router(rules_router, tags=["Rules"])
