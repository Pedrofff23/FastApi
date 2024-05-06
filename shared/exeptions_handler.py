from fastapi import Request
from fastapi.responses import JSONResponse

from shared.exeptions import NotFound


async def not_found_exception_handler(_, exc: NotFound):
    return JSONResponse(
        status_code=404,
        content={"message": f"{exc.name} não encontrado(a)"},
    )
