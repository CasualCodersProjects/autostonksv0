FROM python:3.10-bullseye

WORKDIR /app

# update pip and install pipenv
RUN pip3 install --upgrade pip pipenv

COPY . .

RUN chmod +x entrypoint.sh

RUN pipenv install --system

ENTRYPOINT [ "./entrypoint.sh" ]