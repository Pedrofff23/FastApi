from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import extract
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import (
    ContaPagarReceber,
)
from contas_a_pagar_e_receber.models.fornecedor_cliente_model import FornecedorCliente
from contas_a_pagar_e_receber.routers.fornecedor_cliente_router import (
    FornecedorClienteResponse,
)
from shared.dependencies import get_db
from shared.exeptions import NotFound

router = APIRouter(prefix="/contas-a-pagar-e-receber")

QUANTIDADE_PERMITIDA_POR_MES = 100


class ContaPagarReceberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: int
    descricao: str
    valor: float
    tipo: str  # PAGAR, RECEBER
    data_previsao: date
    data_baixa: date | None = None
    valor_baixa: float | None = None
    esta_baixada: bool | None = None
    fornecedor: FornecedorClienteResponse | None = None


class ContaPagarReceberTipoEnum(str, Enum):
    PAGAR = "PAGAR"
    RECEBER = "RECEBER"


class ContaPagarReceberRequest(BaseModel):
    descricao: str = Field(min_length=3, max_length=30)
    valor: Decimal = Field(gt=0)
    tipo: ContaPagarReceberTipoEnum  # Pagar ou Receber
    fornecedor_cliente_id: int | None = None
    data_previsao: date


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

    valida_se_pode_registrar_novas_contas(
        db=db, conta_a_pagar_e_receber_request=conta_a_pagar_e_receber_request
    )

    contas_a_pagar_e_receber = ContaPagarReceber(
        # descricao=conta.descricao, valor=conta.valor, tipo=conta.tipo
        **conta_a_pagar_e_receber_request.model_dump()
    )

    db.add(contas_a_pagar_e_receber)
    db.commit()
    db.refresh(contas_a_pagar_e_receber)

    return contas_a_pagar_e_receber


@router.put(
    "/{id_da_conta_a_pagar_e_receber}",
    response_model=ContaPagarReceberResponse,
    status_code=200,
)
def atualizar_conta(
    id_da_conta_a_pagar_e_receber: int,
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest,
    db: Session = Depends(get_db),
) -> ContaPagarReceberResponse:
    valida_fornecedor(conta_a_pagar_e_receber_request.fornecedor_cliente_id, db)

    conta_a_pagar_e_receber = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)
    conta_a_pagar_e_receber.tipo = conta_a_pagar_e_receber_request.tipo
    conta_a_pagar_e_receber.valor = conta_a_pagar_e_receber_request.valor
    conta_a_pagar_e_receber.descricao = conta_a_pagar_e_receber_request.descricao
    conta_a_pagar_e_receber.fornecedor_cliente_id = (
        conta_a_pagar_e_receber_request.fornecedor_cliente_id
    )

    db.add(conta_a_pagar_e_receber)
    db.commit()
    db.refresh(conta_a_pagar_e_receber)
    return conta_a_pagar_e_receber


@router.post(
    "/{id_da_conta_a_pagar_e_receber}/baixar",
    response_model=ContaPagarReceberResponse,
    status_code=200,
)
def baixar_conta(
    id_da_conta_a_pagar_e_receber: int, db: Session = Depends(get_db)
) -> ContaPagarReceberResponse:
    conta_a_pagar_e_receber = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)

    if (
        conta_a_pagar_e_receber.esta_baixada
        and conta_a_pagar_e_receber.valor == conta_a_pagar_e_receber.valor_baixa
    ):
        return conta_a_pagar_e_receber

    conta_a_pagar_e_receber.data_baixa = date.today()
    conta_a_pagar_e_receber.esta_baixada = True
    conta_a_pagar_e_receber.valor_baixa = conta_a_pagar_e_receber.valor

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


def valida_fornecedor(fornecedor_cliente_id, db):
    if fornecedor_cliente_id is not None:
        conta_apagar_e_receber = db.get(FornecedorCliente, fornecedor_cliente_id)
        if conta_apagar_e_receber is None:
            raise HTTPException(
                status_code=422, detail="Esse fornecedor não existe no banco de dados"
            )


def valida_se_pode_registrar_novas_contas(
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest, db: Session
) -> None:
    if (
        recupera_numero_registros(
            db,
            conta_a_pagar_e_receber_request.data_previsao.year,
            conta_a_pagar_e_receber_request.data_previsao.month,
        )
        >= QUANTIDADE_PERMITIDA_POR_MES
    ):
        raise HTTPException(
            status_code=422, detail="Você não pode mais lançar contas para esse mês"
        )


def recupera_numero_registros(db, ano, mes) -> int:
    quantidade_de_registros = (
        db.query(ContaPagarReceber)
        .filter(extract("year", ContaPagarReceber.data_previsao) == ano)
        .filter(extract("month", ContaPagarReceber.data_previsao) == mes)
        .count()
    )

    return quantidade_de_registros
