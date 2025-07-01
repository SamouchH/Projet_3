FROM python:3.11-slim

WORKDIR /home/app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

ENV PYTHONPATH="${PYTHONPATH}:/home/app"

CMD ["pytest"]