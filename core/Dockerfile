FROM python:3.8-slim AS builder
WORKDIR /app
RUN python -m venv .venv  && \
.venv/bin/pip install --no-cache-dir -U pip setuptools wheel
COPY requirements.txt .
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt && \
.venv/bin/python -m nltk.downloader -d .venv/nltk_data punkt && \
find /app/.venv \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+

FROM python:3.8-slim
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
RUN apt-get update && \
apt-get install --no-install-recommends ffmpeg libsm6 libxext6 -y
COPY --from=builder /app /app
COPY . .
EXPOSE 5000
CMD [ "python", "app.py" ]