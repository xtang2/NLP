from nltk.parse.corenlp import CoreNLPParser
from nltk.parse.corenlp import CoreNLPDependencyParser
from queue import Queue
import sys

parser = CoreNLPParser(url='http://localhost:9000')

dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')

parses = dep_parser.parse('What is the airspeed of an unladen swallow ?'.split())
print(parses)

dp = [[(governor, dep, dependent) for governor, dep, dependent in parse.triples()] for parse in parses]
print(dp)

#normal_parse = parser.raw_parse("What does the important inscription on the tomb of Ankhtifi, a nomarch during the early First Intermediate Periodi, describe?")

text = "Not only was the last king of the Early Dynastic Period related to the first two kings of the Old Kingdom, but the 'capital', the royal residence, remained at Ineb-Hedg, the Ancient Egyptian name for Memphis."
actual_parse = dep_parser.parse(text.split())
dp = [[(governor, dep, dependent) for governor, dep, dependent in parse.triples()] for parse in actual_parse]
for item in dp:
    print(item)
    for i in item:
        print(i)

actual_parse = parser.raw_parse(text)

actual_tree = [t for t in actual_parse][0]

#actual_tree.draw()

# doesn't work!!
def findRelatives(t, label=None, word=None):

    if label is None and word is None:
        print("please specify either the label or the word to search for")
        return None

    q = [(t,[])]

    curr = 0
    while (curr < len(q)):
        print(curr)
        (currT, trail) = q[curr]
        n = len(currT)
        children = [child for child in currT]
        newTrail = trail + [currT]
        for i in range(len(children)):
            child = children[i]
            if ((word is not None)
                and (type(child) == str)
                and child == word):
                parent = trail[-1]
                return {"trail": newTrail[:-1],
                        "siblings": [c for c in parent if c != currT]}
            elif ((label is not None)
                  and (type(child) != str)
                  and child.label() == label):
                return {"trail": newTrail, "siblings": children[:i] + children[i+1:]}
            else:
                q.append((child, newTrail))
        curr += 1




#items = findRelatives(actual_tree, label="remained")

#sibs = items["siblings"]

#print(sibs)
#for s in sibs:
#    print (s.label())
#    print (" ".join(s.leaves()))


