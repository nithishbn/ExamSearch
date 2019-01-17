# Exam Search

ExamSearch is an application that allows Cambridge students to go through past Cambridge exam papers and search them for content to study.

Currently, ExamSearch only supports Biology 9700 Multiple Choice Papers, but support for free-response and other types of papers in Biology 9700 as well as for other subjects is on the roadmap.

## Installation

Clone the repository, and install the requirements listed below.
### Requirements
#### Python 3
Well, this is a Python project, so I guess it's expected. Make sure you get Python 3!
#### Tesseract-OCR
Follow installation instructions [here](https://github.com/tesseract-ocr/tesseract/wiki#Installation).
This is the main OCR tool used.
*Make sure to add this to the path! Otherwise, you **will** have issues.*

#### Poppler
Download the latest binary for Windows [here](http://blog.alivate.com.au/poppler-windows/).
You can find binaries for other systems with a Google search. 
For this library, you just need to extract the package and add the `bin` folder to the path.

#### PyOCR
*Python 3*
```python
pip install pyocr
```
PyOCR is necessary for the majority of the heavy lifting as it is the wrapper between tesseract-ocr and Python. Installing PyOCR also installs Pillow, which is also used.

#### PDF2Image
*Python 3*
```python
pip install pdf2image
```
If you're stuck with installing pdf2image, this is the [Github page](https://github.com/Belval/pdf2image). It details out the dependencies for pdf2image as well

#### NLTK
*Python 3*
```python
pip install nltk
```
Before you run `main.py`, make sure you download the `stopwords` corpus via 
```python 
import nltk
nltk.download('stopwords')
```
You only need to run this once before you run `main.py`.

## Usage
* First, you will need to run `scrap.py` in order to download all past Cambridge papers from, currently, the Biology section on PapaCambridge. This will allow you to proceed with the next steps.
* Grab any multiple choice pdf file path and feed it through `pdfToText(filePath)`
* run `getMultipleChoiceQuestions(filePath)` in order to, well, get the multiple choice questions
* Run `tagImage(filePath)` in order to get image tags for each question into a database
* Finally, you may run `search()` in order to search for questions!

*Happy studying!*

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

### Authors and acknowledgment
Head Developer - Nithish Narasimman

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/does-not-contain-msg.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/does-not-contain-treenuts.svg)](https://forthebadge.com)