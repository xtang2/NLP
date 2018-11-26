from collections import defaultdict, Counter
import math

class WeightedD:

    # token is the text in the file, splitted and tokenized
    def __init__(self, tokens):
        c = Counter(tokens)
        (max_elem,max_count) = c.most_common(1)[0]

        costs = defaultdict(lambda:1)
        unplusCosts = defaultdict(int)
        for elem in c:
            curr_count = c[elem]
            factor = max_count / curr_count
            log_factor = math.log (factor)
            costs[elem] = 1 + log_factor
            unplusCosts[elem] = log_factor

        self.costs = costs
        self.unplusCosts = unplusCosts


    def ld(self, source, target):
        n = len(target)
        cols = n+1
        m = len(source)
        rows = m+1
        distance = [[0 for c in range(cols)] for r in range(rows)]
        for c in range(1, cols):
            distance[0][c] = distance[0][c-1] + self.costs[target[c-1]]
        for r in range(1, rows):
            distance[r][0] = distance[r-1][0] + 1

        for c in range(1, cols):
            for r in range(1, rows):
                insCost = distance[r][c-1] + self.costs[target[c-1]]
                delCost = distance[r-1][c] + 1
                if target[c-1] == source[r-1]:
                    subCost = distance[r-1][c-1]
                else:
                    multipliedCost = self.costs[target[c-1]]
                    subCost = distance[r-1][c-1] + multipliedCost
                distance[r][c] = min(insCost, delCost, subCost)
        return distance[rows-1][cols-1]

    # both source and target are sets
    def jd(self, source, target):
        # we want to give high weights to
        union_elems = set.union(source, target)
        inters_elems = set.intersection(source, target)

        union_cost = 0
        for elem in union_elems:
            union_cost += self.unplusCosts[elem]
        inters_cost = 0
        for elem in inters_elems:
            inters_cost += self.unplusCosts[elem]

        return (union_cost - inters_cost) / union_cost

