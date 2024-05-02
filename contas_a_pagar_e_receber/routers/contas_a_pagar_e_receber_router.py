from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import (
    ContaPagarReceber,
)
from shared.dependencies import get_db

router = APIRouter(prefix="/contas-a-pagar-e-receber")


class ContaPagarReceberResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    tipo: str  # Pagar ou Receber
    
    class Config:
        orm_mode = True


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
def criar_conta(
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest,
    db: Session = Depends(get_db),
) -> ContaPagarReceberResponse:

    contas_a_pagar_e_receber = ContaPagarReceber(
        # descricao=conta.descricao, valor=conta.valor, tipo=conta.tipo
        **conta_a_pagar_e_receber_request.model_dump()
    )

    db.add(contas_a_pagar_e_receber)
    db.commit()
    db.refresh(contas_a_pagar_e_receber)

    return contas_a_pagar_e_receber
