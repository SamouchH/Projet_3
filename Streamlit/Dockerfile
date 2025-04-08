FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

RUN apt-get update && apt-get install -y libgl1

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . .

EXPOSE 8501
EXPOSE 4000

CMD streamlit run "Home.py" --server.port=8501 --server.address=0.0.0.0 --server.runOnSave=true