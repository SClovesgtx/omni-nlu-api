FROM python:3.6-slim-buster

WORKDIR /usr/omni_nlu_api/

RUN apt-get update && apt-get install -y apt-transport-https

RUN mkdir src
COPY ./src/requirements.txt ./src

RUN pip install -r ./src/requirements.txt
RUN python -m spacy download pt_core_news_lg
RUN python -m nltk.downloader rslp
RUN jupyter nbextension install --py jupyter_tabnine
RUN jupyter nbextension enable --py jupyter_tabnine
RUN jupyter serverextension enable --py jupyter_tabnine

# graphviz is required by prefect[viz]==0.14.12
RUN apt-get -y install graphviz

COPY ./src/ ./src/
RUN mkdir jupyter_notebooks
COPY ./jupyter_notebooks/ ./jupyter_notebooks/

EXPOSE 5000

CMD ["python3", "src/run.py"]
