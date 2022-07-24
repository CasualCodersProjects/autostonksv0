FROM python:3.10-slim
WORKDIR /app
RUN pip3 install -U pip pipenv
COPY . /app
RUN pipenv install --system
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]