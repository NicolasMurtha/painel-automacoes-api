from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends
from models import Bot, Job, JobStatus, JobStatusUpdate
from pydantic import BaseModel  
from sqlmodel import SQLModel, create_engine, Session, select


engine = create_engine("sqlite:///database.db")


SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class BotCreate(BaseModel):
    name : str
    desc : str


app = FastAPI()


@app.get("/")
def read_root():
    return {"message":"Painel de automações - API online"}

@app.get("/status")
def read_status():
    return {"status":"ok"}

@app.get("/bots")
def read_bots(session: Session = Depends(get_session)):
    bots = session.exec(select(Bot)).all()

    result = []
    for bot in bots:
        result.append({
            "id": bot.id,
            "name": bot.name,
            "desc": bot.desc
        })

    return result

@app.get("/bots/{id}")
def read_bot(id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)

    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    return {
        "id": bot.id,
        "name": bot.name,
        "desc": bot.desc
    }

@app.post("/bots")
def create_bot(bot_data: BotCreate, session: Session = Depends(get_session)):
    bot = Bot(name=bot_data.name, desc=bot_data.desc)

    session.add(bot)
    session.commit()
    session.refresh(bot)

    return {
        "id": bot.id,
        "name": bot.name,
        "desc": bot.desc
    }

@app.delete("/bots/{id}")
def delete_bot(id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)

    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    bot_name = bot.name  # guarda antes de deletar

    session.delete(bot)
    session.commit()

    return {
        "status": "ok",
        "message": f"Bot {id} {bot_name} excluído com sucesso"
    }

@app.put("/bots/{id}")
def update_bot(id: int, bot_data: BotCreate, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)

    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    bot.name = bot_data.name
    bot.desc = bot_data.desc

    session.add(bot)
    session.commit()
    session.refresh(bot)

    return {
        "id": bot.id,
        "name": bot.name,
        "desc": bot.desc
    }

@app.post("/bots/{bot_id}/jobs")
def create_job(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    job = Job(bot_id=bot_id)  # status e created_at vêm do model

    session.add(job)
    session.commit()
    session.refresh(job)

    return job

@app.get("/bots/{bot_id}/jobs")
def read_jobs(bot_id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot não encontrado")

    jobs = session.exec(select(Job).where(Job.bot_id == bot_id)).all()
    return jobs

@app.get("/jobs/{job_id}")
def read_job(job_id: int, session: Session = Depends(get_session)):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    return job

@app.put("/jobs/{job_id}/status")
def update_job_status(
    job_id: int,
    payload: JobStatusUpdate,
    session: Session = Depends(get_session)
):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    job.status = payload.status

    if payload.status in {JobStatus.SUCCESS, JobStatus.ERROR}:
        job.finished_at = datetime.now(timezone.utc)

    if payload.status == JobStatus.ERROR:
        job.error_message = payload.error_message or "Erro não informado"
    else:
        job.error_message = None

    session.add(job)
    session.commit()
    session.refresh(job)

    return job