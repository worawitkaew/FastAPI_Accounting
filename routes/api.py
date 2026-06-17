from fastapi import APIRouter

from .utility import login

api_router = APIRouter()

pre_route = "pre_route"


api_router.include_router(
	login.router,
	tags=["pre_route_tags"],
	prefix=f"/{pre_route}",
)

