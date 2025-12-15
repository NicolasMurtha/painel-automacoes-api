# Painel de Automações – Backend API

API backend desenvolvida em Python utilizando FastAPI e SQLModel para gerenciamento de automações (bots) e execuções (jobs).

## Tecnologias
- Python
- FastAPI
- SQLModel
- SQLite
- Pydantic

## Funcionalidades
- CRUD de Bots
- Criação e acompanhamento de Jobs
- Atualização de status de Jobs
- API REST com documentação automática

## Como rodar o projeto

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload