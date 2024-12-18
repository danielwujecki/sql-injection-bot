FROM python:3.13

WORKDIR /usr/src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ app/

ENTRYPOINT ["python", "-m", "app"]
CMD [ "--config", "config.yaml" ]
