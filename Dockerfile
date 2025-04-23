FROM python:3.9.21 as python-base

RUN mkdir er_extractor
WORKDIR  /er_extractor
COPY . /app
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install 
COPY . .
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
