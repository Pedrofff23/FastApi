from decimal import Decimal
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/contas-a-pagar-e-receber")


class ContaPagarReceberResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    tipo: str  # Pagar ou Receber


class ContaPagarReceberRequest(BaseModel):
    descricao: str
    valor: Decimal
    tipo: str  # Pagar ou Receber


@router.get("", response_model=List[ContaPagarReceberResponse])
def listar_contas():
    return [
        ContaPagarReceberResponse(
            id=1, descricao="Conta de Luz", valor=100.00, tipo="Pagar"
        ),
        ContaPagarReceberResponse(
            id=2, descricao="Conta de Água", valor=50.00, tipo="Pagar"
        ),
    ]


@router.post("", response_model=ContaPagarReceberResponse, status_code=201)
def criar_conta(conta: ContaPagarReceberRequest):
    return ContaPagarReceberResponse(
        id=3, descricao=conta.descricao, valor=conta.valor, tipo=conta.tipo
    )
