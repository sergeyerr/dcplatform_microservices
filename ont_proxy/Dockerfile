FROM python:3.7
WORKDIR /code
RUN python -m pip install --upgrade pip
RUN pip install flask flask-cors
COPY . .
ENTRYPOINT ["python", "main.py"]
