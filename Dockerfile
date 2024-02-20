FROM python:3.11-slim
WORKDIR /opt/app
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt
COPY bot.py /opt/app
CMD ["python", "./bot.py"]