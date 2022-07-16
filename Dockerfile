FROM python:3.10

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY . /app

WORKDIR /app
CMD ["python","-u","main.py"]