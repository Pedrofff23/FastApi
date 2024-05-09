import uvicorn
from fastapi import FastAPI

from contas_a_pagar_e_receber.routers import (
    contas_a_pagar_e_receber_router,
    fornecedor_cliente_router,
    fornecedor_cliente_vs_contas_router,
)
from shared.exeptions import NotFound
from shared.exeptions_handler import not_found_exception_handler

app = FastAPI()

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

tags_metadata = [
    {"name": "Contas", "description": "Contas para pagar ou receber"},
    {"name": "Fornecedor", "description": "Fornecedor/cliente"}
]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/")
def hello_world() -> str:
    return {"Hello": "World"}


app.include_router(contas_a_pagar_e_receber_router.router,tags=['Contas'])
app.include_router(fornecedor_cliente_router.router,tags=["Fornecedor"])
app.include_router(fornecedor_cliente_vs_contas_router.router,tags=["Fornecedor"])
app.add_exception_handler(NotFound, not_found_exception_handler)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
