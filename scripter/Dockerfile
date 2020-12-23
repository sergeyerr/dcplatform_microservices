FROM python:3.7
WORKDIR /code
RUN python -m pip install --upgrade pip
RUN pip install Jinja2 flask flask-cors
COPY . .
ENTRYPOINT ["python", "main.py"]
