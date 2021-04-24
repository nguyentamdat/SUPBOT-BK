FROM pytorch/pytorch

RUN apt-get update
RUN cp requirements.txt .
RUN --mount=type=cache, target=/root/.cache pip install -r requirements.txt


CMD [ "PYTHONPATH=./", "FLASK_APP=app.py", "flask", "run" ]