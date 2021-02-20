FROM python:3.6

WORKDIR /usr/src/app

COPY ./ ./
RUN pip install -r requirements.txt
# RUN pip install --upgrade setuptools
# RUN pip install https://github.com/explosion/spacy-models/releases//tag/pt_core_news_lg-3.0.0
RUN python -m spacy download pt_core_news_lg

COPY . .

EXPOSE 5000
CMD ["python", "api.py"]
