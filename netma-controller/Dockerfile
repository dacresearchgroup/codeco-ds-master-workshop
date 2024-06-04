# Author: Panagiotis Karamolegkos (UPRC)

FROM python:3.10

WORKDIR /app

# Get the files to be used in the container
COPY netma-controller/netma-controller.py .
COPY netma-controller/netma-crd.yaml .
COPY generation/traffic_generator.py /app
COPY generation/test_gen.py /app
COPY generation/requirements.txt /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# This will be the default value for the environment variable
ENV DATA_PATH="/app/config.json"

CMD ["python", "-u", "netma-controller.py"]