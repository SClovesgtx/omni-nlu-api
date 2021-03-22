FROM python:3.6-slim-buster

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
RUN python -m spacy download pt_core_news_lg
RUN pip install jupyterlab
COPY ./ ./

EXPOSE 5000
CMD ["python3", "api.py"]
