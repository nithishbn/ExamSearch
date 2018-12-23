import os
import re

import requests
from bs4 import BeautifulSoup
dirname = os.path.dirname(__file__)

def scrap(url, year, month, paper):
    data = requests.get(url, stream=True)
    if data.status_code != 200:
        print("error :(")
    if not os.path.exists(year):
        os.makedirs(year)
    if not os.path.exists(os.path.join(dirname, "{}/{}".format(year, month))):
        os.makedirs("{}/{}".format(year, month))
    with open(os.path.join(dirname, "{year}/{month}/{paper}.pdf".format(year=year, month=month, paper=paper)),
              "wb") as file:
        file.write(data.content)


def run():
    baseUrl = "https://pastpapers.papacambridge.com/?dir=Cambridge%20International%20Examinations%20%28CIE%29%2FAS%20and%20A%20Level%2FBiology%20%289700%29"
    domain = "https://pastpapers.papacambridge.com/"
    directory = requests.get(baseUrl)
    soup = BeautifulSoup(directory.content, "html.parser")
    aTags = list(soup.find_all('a', class_="clearfix", href=True))
    newList = list()
    for i in range(len(aTags) - 4, len(aTags) - 2):  # len(aTags) - 2
        dirThing = aTags[i]['href']
        monthDir = requests.get(domain + dirThing)
        soup = BeautifulSoup(monthDir.content, "html.parser")
        fileTags = list(soup.find_all('a', class_="clearfix", href=True))
        for j in range(1, len(fileTags)):
            tag = fileTags[j]
            file = tag['href']
            thing = "{file}".format(file=file)[12::]
            print(thing)
            matches = re.findall("(?:Biology%20%289700%29//)([0-9].+?)%20(.+[A-z])//(.+).pdf", thing)
            if len(matches) == 0:
                matches = re.findall("(?:Biology%20%289700%29//)([0-9].+?)-(.+[A-z])//(.+).pdf", thing)
            # print(matches)
            if matches is not None and len(matches) != 0:
                print(matches)
                matches = matches[0]
                year = matches[0]
                month = matches[1]
                paper = matches[2]
                scrap("{domain}/{file}".format(domain=domain, file=thing), year, month, paper)