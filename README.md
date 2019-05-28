# Exam Search

ExamSearch is a website that allows Cambridge students to go through past Cambridge exam papers and search them for content to study.

Currently, ExamSearch only supports Biology 9700 Multiple Choice Papers, but support for free-response and other types of papers in Biology 9700 as well as for other subjects is on the roadmap.

## Installation
### Note
**It is important to note that the following instructions for installation are simply for creating your own instance of the server**
A working copy of this project can be found at [my website](http://www.nithishnarasimman.com)

If you'd like your own version of the parser, continue following the directions.
Clone the repository, and install the requirements listed below.
### Requirements
#### Python 3
Well, this is a Python project, so I guess it's expected for you have to Python. Make sure you get Python 3!
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
* First, you will need to run `initializeDirectories()` from `main.py` in order to download all past Cambridge papers from, currently, the Biology section on PapaCambridge. This will allow you to proceed with the next steps.
* Grab any multiple choice pdf file path and feed it through `pdfToText(filePath)`
* run `getMultipleChoiceQuestions(filePath)` in order to, well, get the multiple choice questions
* Run `tagImage(filePath)` in order to get image tags for each question into a database
* Finally, you may run `search()` in order to search for questions! `search()` has been moved to the `app/routes.py` because it is part of the website search algorithm now

*Happy studying!*

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Road Map
Currently, Exam Search is able to parse a majority of Biology 9700 Multiple Choice papers.
### Planned features
* Expand Exam Search to all Biology 9700 papers
* Expand Exam Search to other subjects like A Level History
* Pull up the mark scheme alongside the question
* Index the Biology textbook and pull up relevant paragraphs from the text to be used to answer the question
    * This feature is the end goal for Exam Search at least for Biology 9700
* Work on UI/Create a good-looking application
For further details, visit this page for the [complete roadmap](https://app.gitkraken.com/glo/board/XEfNTzlDSQAP5w8i).

### Authors and acknowledgment
Head Developer - Nithish Narasimman<br>


[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/does-not-contain-msg.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/does-not-contain-treenuts.svg)](https://forthebadge.com)