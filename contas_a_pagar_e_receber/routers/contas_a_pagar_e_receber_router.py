from decimal import Decimal
from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import (
    ContaPagarReceber,
)
from shared.dependencies import get_db
from shared.exeptions import NotFound

router = APIRouter(prefix="/contas-a-pagar-e-receber")


class ContaPagarReceberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: int
    descricao: str
    valor: float
    tipo: str  # Pagar ou Receber


class ContaPagarReceberTipoEnum(str, Enum):
    PAGAR = "PAGAR"
    RECEBER = "RECEBER"


class ContaPagarReceberRequest(BaseModel):
    descricao: str = Field(min_length=3, max_length=30)
    valor: Decimal = Field(gt=0)
    tipo: ContaPagarReceberTipoEnum  # Pagar ou Receber
    fornecedor_cliente_id: int | None = None


@router.get("", response_model=List[ContaPagarReceberResponse])
def listar_contas(db: Session = Depends(get_db)) -> List[ContaPagarReceberResponse]:
    return db.query(ContaPagarReceber).all()


@router.get("/{id}", response_model=ContaPagarReceberResponse)
def listar_uma_contas(
    id: int, db: Session = Depends(get_db)
) -> List[ContaPagarReceberResponse]:

    return busca_conta_por_id(id, db)


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


@router.put("/{id}", response_model=ContaPagarReceberResponse, status_code=200)
def atualizar_conta(
    id: int,
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest,
    db: Session = Depends(get_db),
) -> ContaPagarReceberResponse:

    conta_a_pagar_e_receber = busca_conta_por_id(id, db)

    conta_a_pagar_e_receber.tipo = conta_a_pagar_e_receber_request.tipo
    conta_a_pagar_e_receber.descricao = conta_a_pagar_e_receber_request.descricao
    conta_a_pagar_e_receber.valor = conta_a_pagar_e_receber_request.valor

    db.add(conta_a_pagar_e_receber)
    db.commit()
    db.refresh(conta_a_pagar_e_receber)

    return conta_a_pagar_e_receber


@router.delete("/{id}", status_code=204)
def deletar_conta(
    id: int,
    db: Session = Depends(get_db),
) -> None:
    conta_a_pagar_e_receber = busca_conta_por_id(id, db)

    db.delete(conta_a_pagar_e_receber)
    db.commit()


def busca_conta_por_id(id: int, db: Session) -> ContaPagarReceber:
    conta_a_pagar_e_receber = db.get(ContaPagarReceber, id)

    if conta_a_pagar_e_receber is None:
        raise NotFound("Conta a Pagar e receber")

    return conta_a_pagar_e_receber
