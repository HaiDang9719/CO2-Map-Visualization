FROM python:3.9-slim

WORKDIR /var/opt/geographic-information-system/backend

COPY . .

RUN apt-get update && apt-get install -y build-essential
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

EXPOSE 5000
