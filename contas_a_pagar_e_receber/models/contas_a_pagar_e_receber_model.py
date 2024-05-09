from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from shared.database import Base


class ContaPagarReceber(Base):
    __tablename__ = "contas_a_pagar_e_receber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(30))
    valor = Column(Numeric(scale=2))
    tipo = Column(String(30))
    data_baixa = Column(DateTime())
    valor_baixa = Column(Numeric(scale=2))
    esta_baixada = Column(Boolean, default=False)

    fornecedor_cliente_id = Column(Integer, ForeignKey("fornecedor_cliente.id"))
    fornecedor = relationship("FornecedorCliente")
