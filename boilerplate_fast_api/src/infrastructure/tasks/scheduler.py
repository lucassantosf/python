import logging
from apscheduler.schedulers.background import BackgroundScheduler
from src.infrastructure.tasks.post_tasks import generate_scheduled_fake_post

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    # Adicionar nosso job engatilhado para executar a cada 1 minuto
    scheduler.add_job(
        func=generate_scheduled_fake_post,
        trigger="interval",
        minutes=1,
        id="generate_cron_fake_post_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler iniciado: Job para criar posts automatizado a cada 1 min.")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler parado.")
