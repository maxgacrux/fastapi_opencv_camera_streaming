FROM python:3.8
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apt update -y && apt install -y \
libsm6 \
libxext6 \
libxrender-dev
RUN apt-get install -y ffmpeg
COPY ./ /code
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

