FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /backend

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY backend/ .

# Add entrypoint that runs migrations/collectstatic
COPY entrypoint.sh /backend/entrypoint.sh
RUN chmod +x /backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/backend/entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]