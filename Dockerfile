FROM python:3.10-slim-bullseye

WORKDIR /api/

ADD ./requirements.txt /api/requirements.txt

COPY . /api

RUN pip install -r requirements.txt
ENV PYTHONPATH=/api

ENTRYPOINT ["./run.sh]
