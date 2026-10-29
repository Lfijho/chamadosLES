FROM python:3.13.7-slim-bookworm
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends pandoc libreoffice-writer fonts-liberation poppler-utils && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir python-docx==1.2.0
WORKDIR /work
ENTRYPOINT ["python", "scripts/documents/build.py"]
