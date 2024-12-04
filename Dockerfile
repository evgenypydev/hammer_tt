FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /backend
COPY poetry.lock pyproject.toml /backend/
RUN pip install -U pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root
COPY . ./
COPY ../.env ./.env
EXPOSE 8000
ENTRYPOINT [ "bash", "-c", "./entrypoint.sh"]