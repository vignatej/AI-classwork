#Bayesian Networks
import random
import numpy as np
from collections import defaultdict
from functools import reduce

class BayesNet:
    def __init__(self, node_specs=None):
        self.nodes = []
        self.variables = []
        node_specs = node_specs or []
        for node_spec in node_specs:
            self.add(node_spec)

    def add(self, node_spec):
        node = BayesNode(*node_spec)
        assert node.variable not in self.variables
        assert all((parent in self.variables) for parent in node.parents)
        self.nodes.append(node)
        self.variables.append(node.variable)
        for parent in node.parents:
            self.variable_node(parent).children.append(node)

    def variable_node(self, var):
        for n in self.nodes:
            if n.variable == var:
                return n
        raise Exception("No such variable: {}".format(var))

    def variable_values(self, var):
        return [True, False]

    def __repr__(self):
        return 'BayesNet({0!r})'.format(self.nodes)

class BayesNode:

    def __init__(self, X, parents, cpt):
        if isinstance(parents, str):
            parents = parents.split()

        if isinstance(cpt, (float, int)):
            cpt = {(): cpt}
        elif isinstance(cpt, dict):
            if cpt and isinstance(list(cpt.keys())[0], bool):
                cpt = {(v,): p for v, p in cpt.items()}

        assert isinstance(cpt, dict)
        for vs, p in cpt.items():
            assert isinstance(vs, tuple) and len(vs) == len(parents)
            assert all(isinstance(v, bool) for v in vs)
            assert 0 <= p <= 1

        self.variable = X
        self.parents = parents
        self.cpt = cpt
        self.children = []

    def p(self, value, event):
        assert isinstance(value, bool)
        ptrue = self.cpt[event_values(event, self.parents)]
        return ptrue if value else 1 - ptrue

    def sample(self, event):
        return probability(self.p(True, event))

    def __repr__(self):
        return repr((self.variable, ' '.join(self.parents)))

def event_values(event, variables):
    if isinstance(event, tuple) and len(event) == len(variables):
        return event
    else:
        return tuple([event[var] for var in variables])

def probability(p):
    return p > random.uniform(0.0, 1.0)


def elimination_ask(X, e, bn):

    assert X not in e, "Query variable must be distinct from evidence"
    factors = []
    for var in reversed(bn.variables):
        factors.append(make_factor(var, e, bn))
        if is_hidden(var, X, e):
            factors = sum_out(var, factors, bn)
    return pointwise_product(factors, bn).normalize()


def is_hidden(var, X, e):
    return var != X and var not in e


def make_factor(var, e, bn):
    node = bn.variable_node(var)
    variables = [X for X in [var] + node.parents if X not in e]
    cpt = {event_values(e1, variables): node.p(e1[var], e1)
           for e1 in all_events(variables, bn, e)}
    return Factor(variables, cpt)


def pointwise_product(factors, bn):
    return reduce(lambda f, g: f.pointwise_product(g, bn), factors)


def sum_out(var, factors, bn):
    result, var_factors = [], []
    for f in factors:
        (var_factors if var in f.variables else result).append(f)
    result.append(pointwise_product(var_factors, bn).sum_out(var, bn))
    return result


class Factor:
    def __init__(self, variables, cpt):
        self.variables = variables
        self.cpt = cpt

    def pointwise_product(self, other, bn):
        variables = list(set(self.variables) | set(other.variables))
        cpt = {event_values(e, variables): self.p(e) * other.p(e) for e in all_events(variables, bn, {})}
        return Factor(variables, cpt)

    def sum_out(self, var, bn):
        variables = [X for X in self.variables if X != var]
        cpt = {event_values(e, variables): sum(self.p(extend(e, var, val)) for val in bn.variable_values(var))
               for e in all_events(variables, bn, {})}
        return Factor(variables, cpt)

    def normalize(self):
        assert len(self.variables) == 1
        return ProbDist(self.variables[0], {k: v for ((k,), v) in self.cpt.items()})

    def p(self, e):
        return self.cpt[event_values(e, self.variables)]


def all_events(variables, bn, e):
    if not variables:
        yield e
    else:
        X, rest = variables[0], variables[1:]
        for e1 in all_events(rest, bn, e):
            for x in bn.variable_values(X):
                yield extend(e1, X, x)

def extend(s, var, val):
    return {**s, var: val}

class ProbDist:
    def __init__(self, var_name='?', freq=None):
        self.prob = {}
        self.var_name = var_name
        self.values = []
        if freq:
            for (v, p) in freq.items():
                self[v] = p
            self.normalize()

    def __getitem__(self, val):
        try:
            return self.prob[val]
        except KeyError:
            return 0

    def __setitem__(self, val, p):
        if val not in self.values:
            self.values.append(val)
        self.prob[val] = p

    def normalize(self):
        total = sum(self.prob.values())
        if not np.isclose(total, 1.0):
            for val in self.prob:
                self.prob[val] /= total
        return self

    def show_approx(self, numfmt='{:.3g}'):
        return ', '.join([('{}: ' + numfmt).format(v, p) for (v, p) in sorted(self.prob.items())])

    def __repr__(self):
        return "P({})".format(self.var_name)


T, F = True, False

burglary = BayesNet([('Burglary', '', 0.001),
                     ('Earthquake', '', 0.002),
                     ('Alarm', 'Burglary Earthquake',
                      {(T, T): 0.95, (T, F): 0.94, (F, T): 0.29, (F, F): 0.001}),
                     ('JohnCalls', 'Alarm', {T: 0.90, F: 0.05}),
                     ('MaryCalls', 'Alarm', {T: 0.70, F: 0.01})])

if __name__ == '__main__':
    # a) P(John Calls | Burglary, Earthquake)
    print("a) P(John Calls | Burglary, Earthquake)")
    print(elimination_ask('JohnCalls', dict(Burglary=T, Earthquake=T), burglary).show_approx())
    # b) P(Alarm | Burglary)
    print("b) P(Alarm | Burglary)")
    print(elimination_ask('Alarm', dict(Burglary=T), burglary).show_approx())
    # c) P(Earthquake | Mary Calls)
    print("c) P(Earthquake | Mary Calls)")
    print(elimination_ask('Earthquake', dict(MaryCalls=T), burglary).show_approx())
    # d) P(Burglary | Alarm)
    print("d) P(Burglary | Alarm)")
    print(elimination_ask('Burglary', dict(Alarm=T), burglary).show_approx())

    # Through appropriate queries, verify whether John Calls is
    # conditionally independent to Mary Calls
    # given that the Alarm goes off.
    if(elimination_ask('JohnCalls', dict(Alarm=T, MaryCalls=T), burglary).show_approx() == elimination_ask('JohnCalls', dict(Alarm=T, MaryCalls=F), burglary).show_approx()):
        print("John Calls is conditionally independent to Mary Calls given that the Alarm goes off.")
    else:
        print("John Calls is not conditionally independent to Mary Calls given that the Alarm goes off.")