import ast
import io
import os

import requests
from PIL import Image


def search():
    server = "http://167.99.99.14:5000/"
    dirname = os.path.dirname(os.path.abspath(__file__))
    print(dirname)
    query = ""
    while True:
        query = input("Query: ")
        r = requests.post(server, {"query": query})
        # print(r.status_code)
        print(r.content)
        content = ast.literal_eval(bytes.decode(r.content))
        print(list(content))
        for val in content:
            print(val)
            img = requests.post(server + "getImage", {"imgPath": val})

            if img.status_code == 200:
                print(type(img.content))
                imgToShow = Image.open(io.BytesIO(img.content))
                imgToShow.show()
            else:
                print(img.status_code)
                print("Image not available")
            input("wait: ")
        if query == "quit":
            break


if __name__ == "__main__":
    search()
