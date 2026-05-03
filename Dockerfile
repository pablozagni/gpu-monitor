FROM python:3.11-slim
RUN pip install flask
WORKDIR /app
COPY app.py .
COPY index.html .
CMD ["python", "app.py"]
