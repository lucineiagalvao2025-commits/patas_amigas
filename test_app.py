import os
from datetime import date, timedelta

# Usa um banco SQLite separado, em memória, para os testes.
os.environ["DATABASE_URL"] = "sqlite://"

from app import app, db, Tutor, Pet


def setup_function():
    with app.app_context():
        db.drop_all()
        db.create_all()


def teardown_function():
    with app.app_context():
        db.session.remove()
        db.drop_all()


def criar_tutor():
    tutor = Tutor(nome="Tutor Teste", telefone="11999999999")
    db.session.add(tutor)
    db.session.commit()
    return tutor.id


def test_pagina_inicial():
    with app.test_client() as client:
        resposta = client.get("/")
        assert resposta.status_code == 200


def test_cadastro_de_tutor():
    with app.test_client() as client:
        resposta = client.post(
            "/tutores",
            data={"nome": "Tutor Teste", "telefone": "11999999999"},
            follow_redirects=True
        )
        assert resposta.status_code == 200
        assert Tutor.query.filter_by(nome="Tutor Teste").first() is not None


def test_validacao_de_peso():
    with app.app_context():
        tutor_id = criar_tutor()

    with app.test_client() as client:
        resposta = client.post(
            "/pets",
            data={
                "nome": "Rex",
                "especie": "Cachorro",
                "tutor_id": str(tutor_id),
                "peso": "-2"
            },
            follow_redirects=True
        )

        assert resposta.status_code == 200
        assert "O peso do pet deve ser maior que zero.".encode() in resposta.data

    with app.app_context():
        assert Pet.query.count() == 0


def test_data_de_nascimento_futura():
    with app.app_context():
        tutor_id = criar_tutor()

    data_futura = (date.today() + timedelta(days=30)).isoformat()

    with app.test_client() as client:
        resposta = client.post(
            "/pets",
            data={
                "nome": "Rex",
                "especie": "Cachorro",
                "tutor_id": str(tutor_id),
                "data_nascimento": data_futura,
                "peso": "5"
            },
            follow_redirects=True
        )

        assert resposta.status_code == 200
        assert "A data de nascimento".encode() in resposta.data
        assert "futura".encode() in resposta.data

    with app.app_context():
        assert Pet.query.count() == 0

def test_agendamento_sem_data():
    with app.test_client() as client:
        resposta = client.post(
            "/agendamentos",
            data={
                "pet_id": "",
                "veterinario_id": "",
                "servico_id": "",
                "data_hora": ""
            },
            follow_redirects=True
        )

        assert resposta.status_code == 200
        assert "Informe a data e o horário do agendamento.".encode() in resposta.data
