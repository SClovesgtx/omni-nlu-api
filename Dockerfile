FROM python:3.6

WORKDIR /usr/src/app

COPY ./ ./
RUN pip install -r requirements.txt
RUN python -m spacy download pt_core_news_lg

COPY . .

EXPOSE 5000
CMD ["python", "api.py"]
