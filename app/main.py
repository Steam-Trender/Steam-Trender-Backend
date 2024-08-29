import asyncio
import threading
from datetime import date

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from app.db import SessionLocal, init_db
from app.routes import init_routes
from services.db_service import db_service
from services.mail_service import mail_service
from services.scraper_service import scraper_service

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3030",
    "http://steamtrender.com",
    "https://steamtrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def update_db(f):
    async with SessionLocal() as db:
        await db_service.update_db(ddate=f, db=db)


def schedule_update_data_job(loop):
    def process():
        current_date = date.today()
        filename = current_date.strftime("%Y_%m_%d")
        scraper_service.scrap(filename=filename)
        mail_service.send_alert_report()
        asyncio.run_coroutine_threadsafe(update_db(current_date), loop)

    threading.Thread(target=process).start()


scheduler = BackgroundScheduler(
    timezone=pytz.timezone("Europe/Moscow"),
)


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    current_date = date.today()
    await init_db()
    extra_update = False
    async with SessionLocal() as db:
        await db_service.seed_db(db=db)
        last_update = await db_service.get_last_update(session=db)
        if (last_update.date - current_date).days > config.MAX_UPDATES_DELTA:
            extra_update = True
    if extra_update:
        schedule_update_data_job(loop)
    scheduler.add_job(
        lambda: schedule_update_data_job(loop),
        trigger=CronTrigger(day="10", hour="20", minute="0"),
        id="update_data_job",
        replace_existing=True,
    )
    scheduler.start()
    mail_service.send_alert_up()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


init_routes(app)
