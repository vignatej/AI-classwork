import random
def close(a,b):
    return a-0.01<=b<=a+0.01
def norm(w):
    tot=sum([i for i in w.values()])
    for i in w:
        w[i]=w[i]/tot
    return w
class ProbDict:
    def __init__(self, name: str, dic: dict = None):
        self.name=name
        self.prob={}
        if dic:
            for i,v in dic.items():
                self[i]=v
            self.normalize()
    def __getitem__(self,key):
        return self.prob[key]
    def __setitem__(self,key,val):
        self.prob[key] = val
    def normalize(self):
        total = sum(self.prob.values())
        if not close(1,total):
            for i in self.prob.keys():
                self.prob[i]/=total 
        return self
    def __str__(self) -> str:
        return "name: "+self.name+"  |||| prob table : "+str(self.prob)
# P = ProbDict('Flip')
#p[True]=10
# print(P[True])



def event_values(event,values):
    if isinstance(event,tuple): return event
    return tuple([event[i] for i in values])
# print(event_values({'A':10,'B':3,"C":10},['B','A']))

class BayesNode:
    #prob talble sh be like{(p1,p2):val}
    def __init__(self,name: str,parents: list[str],prob_table: dict) -> None:
        self.name=name
        self.parents=parents
        self.prob_table=prob_table
        self.children=[]
    def p(self,TorF:bool,event: dict):
        a=event_values(event,self.parents)
        ans = self.prob_table[a]
        return ans if TorF else 1-ans

class BayesNetwork:
    def __init__(self, node_spec) -> None:
        self.nodes=[]
        self.variables=[]
        for node in node_spec:
            self.add(node)
    def add(self, node_spec):
        n = BayesNode(*node_spec)
        self.nodes.append(n)
        self.variables.append(n.name)
        for par in n.parents:
            self.var_node(par).children.append(n.name)

    def var_node(self, name):
        for i in self.nodes:
            if i.name == name:
                return i
    def __str__(self) -> str:
        return "nodes: "+str(self.variables)
def enumeration_ask(X,e,bn):
    Q=ProbDict(X)
    for i in [True,False]:
        Q[i] =  enumerate_all(bn.variables,{**e,X:i},bn)
    return Q.normalize()
    
def enumerate_all(vars,e,bn):
    if not vars : return 1
    first = vars[0]
    first_node = bn.var_node(first)
    if first in e:
        return first_node.p(e[first],e)*enumerate_all(vars[1:],e,bn)
    s=0
    s+=first_node.p(True, e)*enumerate_all(vars[1:],{**e,first:True},bn)
    s+=first_node.p(False, e)*enumerate_all(vars[1:],{**e,first:False},bn)
    return s


burglary = BayesNetwork([('Burglary', [], {():0.001}),
                     ('Earthquake', [],{():0.002}),
                     ('Alarm', ['Burglary','Earthquake'],
                      {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001}),
                     ('JohnCalls', ['Alarm'], {(True,): 0.90, (False,): 0.05}),
                     ('MaryCalls', ['Alarm'], {(True,): 0.70, (False,): 0.01})])

print(enumeration_ask('Burglary',{'MaryCalls':True,'JohnCalls':True},burglary))


text_expl = BayesNetwork(
    [
        ('Cloudy',[],{():0.5}),
        ('Sprinkler',['Cloudy'],{(True,):0.1,(False,):0.5}),
        ('Rain',['Cloudy'],{(True,):0.8,(False,):0.2}),
        ('WetGrass',['Sprinkler','Rain'],{(True,True):0.99,(True,False):0.9,(False,True):0.9,(False,False):0.0})
    ]
)




def priorSampling(bn: BayesNetwork):
    x={}
    for i in bn.variables:
        a=random.random()
        node = bn.var_node(i)
        b=node.p(True,x)
        x[i] = True if a<b else False
    return x

#dict={}
# for i in range(10000):
#     a=priorSampling(burglary)
#     dict[tuple(a.values())]=dict.get(tuple(a.values()),0)+1
# print(dict)

def rejection_sampling(X,e,bn,N):
    dict={}
    while N>0:
        a=priorSampling(bn)
        exc=0
        for i in e:
            if a[i]!=e[i]:
                ecx=1
                break
        if exc==1: 
            continue
        N=N-1
        dict[event_values(a,X)]=dict.get(event_values(a,X),0)+1
    return norm(dict)
print(rejection_sampling(('Burglary',),{'MaryCalls':True,'JohnCalls':True},burglary,100000))


def weightedSample(bn: BayesNetwork,e:dict):
    w=1
    X={}
    for n in bn.variables:
        node = bn.var_node(n)
        if n in e:
            w=w*node.p(e[n],X)
            X[n] = e[n]
        else:
            a=random.random()
            b=node.p(True,X)
            X[n] = True if a<b else False
    return X,w
def likelihoodWeighiting(X,e,bn,N):
    dict={}
    for i in range(N):
        a,b=weightedSample(bn,e)
        dict[event_values(a,X)] = dict.get(event_values(a,X),0)+b
    return norm(dict)


print(likelihoodWeighiting(('Burglary',),{'MaryCalls':True,'JohnCalls':True},burglary,100000))



def markov_blanket_prob(bn: BayesNetwork,n,dict):
    node = bn.var_node(n)
    all=set()
    all.add(n)
    for i in node.parents:
        all.add(i)
    child=[]
    for i in node.children:
        all.add(i)
        child.append(i)
    for i in child:
        c=bn.var_node(i)
        for j in c.parents:
            all.add(j)
    prod=1
    for i in all:
        i_n=bn.var_node(i)
        prod*=i_n.p(dict[i],dict)
    return prod







def gibbs(X,e,bn: BayesNetwork,N):
    ne=[]
    final={}
    for i in bn.variables:
        if i not in e: 
            ne.append(i)
    dict=e
    for i in ne:
        a=random.random()
        node=bn.var_node(i)
        b=node.p(True,dict)
        if a<b: 
            dict[i]=True
        else:
            dict[i]=False
    final[event_values(dict,X)] = final.get(event_values(dict,X),0)+1
    for j in range(N):
        for ne_var in ne:
            a=random.random()
            node=bn.var_node(ne_var)
            # pr=node.p(True,dict)
            # if a<pr:
            #     dict[ne_var] = True
            # else:
            #     dict[ne_var] = False
            mbv=markov_blanket_prob(bn,ne_var,dict)
            if a<mbv:
                dict[ne_var]=True
            else:
                dict[ne_var]=False
            final[event_values(dict,X)] = final.get(event_values(dict,X),0)+mbv
    return norm(final)
print(gibbs(('Burglary',),{'MaryCalls':True,'JohnCalls':True},burglary,100000))
