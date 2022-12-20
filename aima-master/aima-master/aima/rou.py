from utils import *


class BayesNet:
    "Bayesian network containing only boolean-variable nodes."

    def __init__(self, node_specs=[]):
        "nodes must be ordered with parents before children."
        update(self, nodes=[], vars=[])
        for node_spec in node_specs:
            self.add(node_spec)

    def add(self, node_spec):
        """Add a node to the net. Its parents must already be in the
        net, and its variable must not."""
        node = BayesNode(*node_spec)
        assert node.variable not in self.vars
        assert every(lambda parent: parent in self.vars, node.parents)
        self.nodes.append(node)
        self.vars.append(node.variable)
        for parent in node.parents:
            self.variable_node(parent).children.append(node)

    def variable_node(self, var):
        """Return the node for the variable named var.
        >>> burglary.variable_node('Burglary').variable
        'Burglary'"""
        for n in self.nodes:
            if n.variable == var:
                return n
        raise Exception("No such variable: %s" % var)

    def variable_values(self, var):
        "Return the domain of var."
        return [True, False]

    def __repr__(self):
        return 'BayesNet(%r)' % self.nodes

class BayesNode:
    """A conditional probability distribution for a boolean variable,
    P(X | parents). Part of a BayesNet."""

    def __init__(self, X, parents, cpt):
        """X is a variable name, and parents a sequence of variable
        names or a space-separated string.  cpt, the conditional
        probability table, takes one of these forms:

        * A number, the unconditional probability P(X=true). You can
          use this form when there are no parents.

        * A dict {v: p, ...}, the conditional probability distribution
          P(X=true | parent=v) = p. When there's just one parent.

        * A dict {(v1, v2, ...): p, ...}, the distribution P(X=true |
          parent1=v1, parent2=v2, ...) = p. Each key must have as many
          values as there are parents. You can use this form always;
          the first two are just conveniences.

        In all cases the probability of X being false is left implicit,
        since it follows from P(X=true).

        >>> X = BayesNode('X', '', 0.2)
        >>> Y = BayesNode('Y', 'P', {T: 0.2, F: 0.7})
        >>> Z = BayesNode('Z', 'P Q',
        ...    {(T, T): 0.2, (T, F): 0.3, (F, T): 0.5, (F, F): 0.7})
        """
        if isinstance(parents, str): parents = parents.split()

        # We store the table always in the third form above.
        if isinstance(cpt, (float, int)): # no parents, 0-tuple
            cpt = {(): cpt}
        elif isinstance(cpt, dict):
            if cpt and isinstance(cpt.keys()[0], bool): # one parent, 1-tuple
                cpt = dict(((v,), p) for v, p in cpt.items())

        assert isinstance(cpt, dict)
        for vs, p in cpt.items():
            assert isinstance(vs, tuple) and len(vs) == len(parents)
            assert every(lambda v: isinstance(v, bool), vs)
            assert 0 <= p <= 1

        update(self, variable=X, parents=parents, cpt=cpt, children=[])

    def p(self, value, event):
        assert isinstance(value, bool)
        ptrue = self.cpt[event_values(event, self.parents)]
        return if_(value, ptrue, 1 - ptrue)

    def sample(self, event):
        """Sample from the distribution for this variable conditioned
        on event's values for parent_vars. That is, return True/False
        at random according with the conditional probability given the
        parents."""
        return probability(self.p(True, event))

    def __repr__(self):
        return repr((self.variable, ' '.join(self.parents)))

# Burglary example [Fig. 14.2]

T, F = True, False
