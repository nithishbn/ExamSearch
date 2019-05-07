from distutils.core import setup
import py2exe
setup(console=['examsearch.py'], requires=['requests', 'Pillow'])