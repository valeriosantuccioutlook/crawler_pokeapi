FROM mcr.microsoft.com/vscode/devcontainers/python:3.9

WORKDIR /workspace

RUN apt-get update \ 
    && apt install -y dos2unix python3 python3-pip git openssh-client \
    && pip3 install pip-tools

COPY . /workspace
RUN pip install fastapi uvicorn pip-tools sqlalchemy requests aenum aiohttp
RUN pip install psycopg2-binary
RUN pip install psycopg2

RUN pip install  python-magic pylance

# CMD [ "uvicorn", "crawler_api.main:app", "--host", "0.0.0.0", "--port", "80" ]
# CMD [ "sleep", "infinity" ]
