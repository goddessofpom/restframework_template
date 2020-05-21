from django.db.models import Q

from celery import shared_task
from libs.sms import SMSSender
from .celery import app
import datetime


# 测试 #
@app.task
def demo_task():
    print("hello world 2")
    return True


@shared_task
def demo_minutes_task():
    print("hello world 1")
    demo_task.delay()
    return True
# - - #


# 异步任务 #
@app.task
def demo_async():
    return True

# - - #

# 定时任务 #
@shared_task
def beat_demo():
    return True