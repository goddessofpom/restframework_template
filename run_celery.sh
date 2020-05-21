#!/bin/sh

#celery multi start -A pywe_django demo -B -l info -f logs/demo.log -Q demo -n demo

celery multi start beat -A pywe_django -B -l info -f /var/.../logs/celery_beat.log
#celery multi start -A pywe_django beat -B -l info -f logs/celery_beat.log