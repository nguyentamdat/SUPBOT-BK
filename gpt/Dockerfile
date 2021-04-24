# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Install pip requirements
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache python -m pip install -r requirements.txt
# RUN python -m pip install -r requirements.txt
# RUN python -m nltk.downloader -d /usr/share/nltk_data punkt
# RUN cp //nltk_data /usr/local/nltk_data

WORKDIR /app
COPY . /app

# Creates a non-root user and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN useradd appuser && chown -R appuser /app
RUN chown -R appuser /home
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["PYTHONPATH=./", "FLASK_APP=app.py", "flask", "run"]
