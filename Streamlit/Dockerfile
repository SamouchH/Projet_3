FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

COPY requirements.txt /dependencies/requirements.txt
RUN pip install --no-cache-dir -r /dependencies/requirements.txt

COPY . .

EXPOSE 8501

CMD streamlit run "Home.py" --server.port=8501 --server.address=0.0.0.0 --server.runOnSave=true