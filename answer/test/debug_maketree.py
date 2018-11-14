from nltk.parse.corenlp import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser
from stanfordcorenlp import StanfordCoreNLP
from queue import Queue
import sys

text = input()

nlp = StanfordCoreNLP("http://localhost", port=9000, timeout=30000)

parser = CoreNLPParser(url='http://localhost:9000')
parse = parser.raw_parse(text)

t = [t for t in parse][0]
t.draw()
