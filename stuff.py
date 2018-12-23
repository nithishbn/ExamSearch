from PIL import Image
import sys

import pyocr
import pyocr.builders

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'libtesseract'

langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))
lang = langs[0]
print("Will use lang '%s'" % (lang))
# number = 0


# txt = tool.image_to_string(
#     Image.open('xd-1.png'),
#     lang=lang,
#     builder=pyocr.builders.TextBuilder()
# )
# print(txt)
# print("end")
# word_boxes = tool.image_to_string(
#     Image.open('xd-1.png'),
#     lang="eng",
#     builder=pyocr.builders.WordBoxBuilder()
# )
# for i in range(1, 2):
img = "test.jpg"
line_and_word_boxes = tool.image_to_string(
    Image.open(img), lang=lang,
    builder=pyocr.builders.LineBoxBuilder()
)
# print(line)
for line in line_and_word_boxes:
    print(line.content)
print("---------------------------------------------------------------------")
