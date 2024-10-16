FROM python:3.9-slim

WORKDIR /app

# Добавляем изображения в контейнер
COPY ./images /app/images

# Устанавливаем Flask
RUN pip install flask

# flask app (optional)
COPY ./app.py /app/app.py

CMD ["python", "/app/app.py"]
