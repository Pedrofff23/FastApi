
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from shared.database import Base
from shared.dependencies import get_db

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test/test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_deve_listar_contas_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Conta de Luz", "valor": 100.00, "tipo": "PAGAR"},
    )
    client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Conta de Água", "valor": 50.00, "tipo": "PAGAR"},
    )

    response = client.get("/contas-a-pagar-e-receber/")
    assert response.status_code == 200

    print(response.json())

    assert response.json() == [
        {"id": 1, "descricao": "Conta de Luz", "valor": 100.00, "tipo": "PAGAR"},
        {"id": 2, "descricao": "Conta de Água", "valor": 50.00, "tipo": "PAGAR"},
    ]


def test_deve_pegar_por_id():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Conta de Internet", "valor": 100.0, "tipo": "PAGAR"},
    )

    id_da_conta = response.json()["id"]

    response_get = client.get(
        f"/contas-a-pagar-e-receber/{id_da_conta}",
    )

    assert response_get.status_code == 200
    assert response_get.json()["valor"] == 100.0
    assert response_get.json()["tipo"] == "PAGAR"


def test_deve_retornar_nao_encontrado_para_id_nao_existente():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response_get = client.get(
        "/contas-a-pagar-e-receber/100",
    )

    assert response_get.status_code == 404


def test_deve_criar_conta_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    nova_conta = {"descricao": "Conta de Internet", "valor": 200.0, "tipo": "PAGAR"}

    nova_conta_copy = nova_conta.copy()

    nova_conta_copy["id"] = 1

    response = client.post(
        "/contas-a-pagar-e-receber",
        json=nova_conta,
    )
    assert response.status_code == 201
    assert response.json() == nova_conta_copy

    # assert response.json()["descricao"] == nova_conta["descricao"]


# TDD - Test Driven Development


def test_deve_atualizar_conta_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Conta de Internet", "valor": 200.0, "tipo": "PAGAR"},
    )

    id_da_conta = response.json()["id"]

    response_put = client.put(
        f"/contas-a-pagar-e-receber/{id_da_conta}",
        json={"descricao": "Conta de Internet", "valor": 111.0, "tipo": "PAGAR"},
    )

    assert response_put.status_code == 200
    assert response_put.json()["valor"] == 111.0


def test_deve_retornar_nao_encontrado_para_id_nao_existente_na_atualizacao():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response_put = client.put(
        "/contas-a-pagar-e-receber/100",
        json={"descricao": "Conta de Internet", "valor": 111.0, "tipo": "PAGAR"},
    )

    assert response_put.status_code == 404


def test_deve_remover_conta_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Conta de Internet", "valor": 200.0, "tipo": "PAGAR"},
    )

    id_da_conta = response.json()["id"]

    response_put = client.delete(
        f"/contas-a-pagar-e-receber/{id_da_conta}",
    )

    assert response_put.status_code == 204


def test_deve_retornar_nao_encontrado_para_id_nao_existente_na_remocao():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response_put = client.delete(
        "/contas-a-pagar-e-receber/100",
    )

    assert response_put.status_code == 404


def test_deve_retornar_erro_quando_exceder_a_descricao_ou_for_menor_que_o_necessario():
    response = client.post(
        "/contas-a-pagar-e-receber",
        json={
            "descricao": "0123456789012345678901234567890111",
            "valor": 200.0,
            "tipo": "PAGAR",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "descricao"]

    response = client.post(
        "/contas-a-pagar-e-receber",
        json={
            "descricao": "12",
            "valor": 200.0,
            "tipo": "PAGAR",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "descricao"]


def test_deve_retornar_erro_quando_valor_for_zero_ou_menor():
    response = client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Teste", "valor": 0, "tipo": "PAGAR"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "valor"]

    response = client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Teste", "valor": -1, "tipo": "PAGAR"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "valor"]


def test_deve_retornar_erro_quando_tipo_for_invalido():
    response = client.post(
        "/contas-a-pagar-e-receber",
        json={"descricao": "Teste", "valor": 100, "tipo": "TESTE"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "tipo"]
