from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_deve_listar_contas_a_pagar_e_receber():
    response = client.get("/contas-a-pagar-e-receber/")
    assert response.status_code == 200

    print(response.json())

    assert response.json() == [
        {"id": 1, "descricao": "Conta de Luz", "valor": 100.00, "tipo": "Pagar"},
        {"id": 2, "descricao": "Conta de Água", "valor": 50.00, "tipo": "Pagar"},
    ]


def test_deve_criar_conta_a_pagar_e_receber():
    nova_conta = {"descricao": "Conta de Internet", "valor": 200.0, "tipo": "Pagar"}
    
    nova_conta_copy = nova_conta.copy()
    
    nova_conta_copy["id"] = 3
    
    response = client.post(
        "/contas-a-pagar-e-receber",
        json=nova_conta,
    )
    assert response.status_code == 201
    assert response.json() == nova_conta_copy

    # assert response.json()["descricao"] == nova_conta["descricao"]

