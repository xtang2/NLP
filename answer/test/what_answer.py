from nltk.parse.corenlp import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser
from stanfordcorenlp import StanfordCoreNLP
from queue import Queue
import sys

text = "Egyptians in this era worshipped their Pharaoh as a god, believing that he ensured the annual flooding of the Nile that was necessary for their crops."

nlp = StanfordCoreNLP("http://localhost", port=9000, timeout=30000)

parser = CoreNLPParser(url='http://localhost:9000')
parse = parser.raw_parse(text)
depparse = nlp.dependency_parse(text)
print(depparse)

# strategy for who, what questions:
# look for NP be NP, match either of them and return the unmatched one
# this assumes that the question doesn't come in the form of NP,NP,blah! (that might be for later)


keyphrase = "worshipped"

t = [t for t in parse][0]

def getAll(label,t):
    if type(t) == str:
        return []
    elems = []
    for subtree in t:
        if type(subtree) != str and subtree.label() == label:
            elems.append(subtree)
        elems += getAll(label,subtree)
    return elems

allS = getAll("S", t)
for item in allS:
    print(" ".join(item.leaves()))

t.draw()

def what_answer(keyphrase, t):
    for toplevel in t:
        if toplevel.label() == "S":
            for components in toplevel:
                if components.label() == "VP":
                    print(components)
                    npchildren = [c for c in components if c.label() == "NP"]
                    if len(npchildren) == 0:
                        continue
                    else:
                        return npchildren[0]

def what_answer_s(keyphrase, t):
    for s in getAll("S", t)[::-1]:
       for components in s:
           if keyphrase in components.leaves():
               if components.label() == "VP":
                   print(components)
                   npchildren = [c for c in components if c.label() == "NP"]
                   if len(npchildren) == 0:
                       continue
                   else:
                       return npchildren[0]


result = what_answer_s(keyphrase, t)
print(" ".join(result.leaves()))

