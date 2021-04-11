FROM python:3.6-slim-buster

WORKDIR /usr/omni_nlu_api/

RUN mkdir src
COPY ./src/requirements.txt ./src
RUN pip install -r ./src/requirements.txt
RUN python -m spacy download pt_core_news_lg
RUN python -m nltk.downloader rslp
RUN pip install jupyterlab

COPY ./src/ ./src/
RUN mkdir jupyter_notebooks
COPY ./jupyter_notebooks/ ./jupyter_notebooks/

EXPOSE 5000

CMD ["python3", "src/run.py"]
