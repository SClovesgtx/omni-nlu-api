FROM python:3.6-slim-buster

WORKDIR /usr/omni_nlu_api/

COPY ./src/requirements.txt ./
RUN pip install -r requirements.txt
RUN python -m spacy download pt_core_news_lg
RUN pip install jupyterlab

COPY ./src/ ./
COPY ./jupyter_notebooks/ ./

EXPOSE 5000

CMD ["python3", "src/api.py"]
