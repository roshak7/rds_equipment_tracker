from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from models import get_db_connection
from notifications import NotificationSystem

def init_scheduler():
    scheduler = BackgroundScheduler()
    notification_system = NotificationSystem()

    def check_notifications():
        with get_db_connection() as conn:
            notification_system.check_return_dates(conn)
            notification_system.check_maintenance_dates(conn)

    # Запускаем проверку каждый день в 9:00
    scheduler.add_job(
        check_notifications,
        trigger=CronTrigger(hour=9, minute=0),
        id='daily_notifications',
        name='Ежедневные проверки уведомлений',
        replace_existing=True
    )

    scheduler.start()
    return scheduler 