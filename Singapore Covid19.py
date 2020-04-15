from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from elasticsearch import Elasticsearch, helpers
from datetime import datetime, timedelta

host = "localhost"
es = Elasticsearch([{'host': host, 'port': 9200}])
es_index = "sg_covid"
es.indices.delete(index=es_index, ignore=[400, 404])

covidsg_path = r"https://co.vid19.sg/singapore/cases/search"
page = requests.get(covidsg_path)

soup = BeautifulSoup(page.content, 'html.parser')
headers = soup.findAll("th")
cases = soup.findAll("tr")

header_names = []
for header in headers:
    if header.text == 'Patient':
        continue
    header_names.append(header.text)

counter = 0
documents = []
local_time = timedelta(hours=8)

for case in cases:
    counter+=1
    attributes = case.findAll("td")
    record = []
    if counter == 1:
        continue
    for attribute in attributes:
        att = attribute.text
        att = att.replace("\n", "").strip()
        if "year" and "old" in att.lower():
            continue
        if att == "-":
            att = None
        record.append(att)
    record[0] = int(record[0]) if record[0] else None
    record[1] = int(record[1]) if record[1] else None
    record[7] = int(record[7]) if record[7] else None
    record[8] = int(record[8]) if record[8] else None
    record[9] = datetime.strptime(record[9].replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""), "%d, %b %Y") if record[9] else None
    record[10] = datetime.strptime(record[10].replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""), "%d, %b %Y") if record[10] else None
    record[11] = datetime.strptime(record[11].replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""), "%d, %b %Y") if record[11] else None
    document = dict(zip(header_names, record))
    document["_index"] = es_index
    documents.append(document)

helpers.bulk(es, documents, chunk_size=1000, request_timeout=200)