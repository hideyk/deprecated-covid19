from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# chrome_driver_path = r"C:/Users/hidey/Desktop/chromedriver.exe"
# driver = webdriver.Chrome(worldometer_corona_url)

worldometer_corona_url = r"https://www.worldometers.info/coronavirus/"
page = requests.get(worldometer_corona_url)

soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(id="main_table_countries_div")
header_object = results.find("thead")

header = []
for column in header_object.find_all('th'):
    words = column.text
    if "," in words:
        header.append(words.split(",")[0])
    else:
        new_word = re.sub(r"(\w)([A-Z])", r"\1 \2", words)
        header.append(new_word)

header.pop()

countries = results.find_all('tr')
for country in countries:
    for element in country.find_all("td"):
        print(element)
        

