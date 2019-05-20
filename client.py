import ast
import io
import os

import requests
from PIL import Image


def search():
    server = "http://167.99.99.14/"
    dirname = os.path.dirname(os.path.abspath(__file__))
    print(dirname)
    while True:
        query = input("Query: ")
        if query == "quit":
            break
        r = requests.post(server, {"query": query})
        # print(r.status_code)

        if r.status_code == 200:
            # print(r.content)
            content = dict(ast.literal_eval(bytes.decode(r.content)))
            # print(content)
            if content['error'] == -1:
                print("Error!")
            else:
                values = list(set(content['data']))
                for val in values:
                    # print(val)
                    img = requests.post(server + "getImage", {"imgPath": val})
                    if img.status_code == 200:
                        # print(type(img.content))
                        imgToShow = Image.open(io.BytesIO(img.content))
                        imgToShow.show()
                    else:
                        # print(img.status_code)
                        print("Image not available")
                    q = input("wait: ")
                    if q == "quit":
                        break
        else:
            print("There has been an error: \'{}\'".format(r.status_code))
    input()



if __name__ == "__main__":
    search()
