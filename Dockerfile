FROM dockerhub.yuhuofei.cn/xianggui_service:latest

WORKDIR /

COPY ./ /xianggui_service

WORKDIR xianggui_service

RUN (pip install -r requirement.txt -i https://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com)

# CMD ["sh", "-c", "echo yes | python manage.py collectstatic && python manage.py migrate && bash run_celery.sh && uwsgi --http=:8888 --wsgi-file=pywe_django/wsgi.py --processes=2 --threads=2 && bash mkdoc.sh"]

CMD ["sh", "-c", "echo yes | python manage.py collectstatic && python manage.py migrate && uwsgi --http=:8900 --wsgi-file=pywe_django/wsgi.py --processes=2 --threads=2"]

EXPOSE 8900