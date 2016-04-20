__author__ = 'Priyanka'
from collections import OrderedDict
import re
import copy
import sys

decision_nodes=[]
class Net:
    def __init__(self, bn):
        """
        Initialize the network; read and parse the given file.
        Args:
            fname:  Name of the file containing the data.
        """
        self.permutationsmemo = {}
        self.net = {}
        for b in bn:
            self._parse(b,bn[b])
            #print b,bn[b],len(bn[b])

    def _parse(self, var,prob):
        if len(prob) == 1 :
            self.net[var]={
                'parents': [],
                'children': [],
                'prob': float(prob[0]),
                'condprob': {}
            }
        else:
            match = re.match(r'(.*) \| (.*)', var)
            vars, parents = match.group(1).strip(), match.group(2).split()
            #print vars,parents,type(parents)
            for p in parents:
                #print p,"priyanka"
                self.net[p]['children'].append(vars)
            self.net[vars] = {
                'parents': parents,
                'children': [],
                'prob': -1,
                'condprob': {}
            }
            # table rows/distributions
            for probline in prob:
                match=probline.split(' ')
                #print match
                p=float(match[0])
                temp_truth=[]
                for m in match[1:]:
                    temp_truth.append(m)

                truth = tuple(True if x == '+' else False for x in temp_truth)
                #print len(truth),truth
                self.net[vars]['condprob'][truth] = p
    def display(self):
        for key in self.net.keys():
            print key,':',self.net[key]
    def parents(self,Y):
        parent_list=[]
        for p in self.net[Y]['parents']:
            parent_list.append(p)
        return parent_list
    def normalize(self, dist):

        return tuple(x * 1/(sum(dist)) for x in dist)
    def assignprob(self,X,net):
        for key in self.net.keys():
            if X==key:
                self.net[key]['prob']=0.5
        return net

    def toposort(self):
        variables = list(self.net.keys())
        variables.sort()
        s = set()   # used to mark variables
        l = []
        while len(s) < len(variables):
            for v in variables:
                if v not in s and all(x in s for x in self.net[v]['parents']):
                    # add the variable `v` into the set `s` iff
                    # all parents of `v` are already in `s`.
                    s.add(v)
                    l.append(v)
        return l
    def querygiven(self, Y, e):
        # Y has no parents
        if self.net[Y]['prob'] != -1:
            prob = self.net[Y]['prob'] if e[Y] else 1 - self.net[Y]['prob']

        # Y has at least 1 parent
        else:
            # get the value of parents of Y
            parents = tuple(e[p] for p in self.net[Y]['parents'])

            # query for prob of Y = y
            prob = self.net[Y]['condprob'][parents] if e[Y] else 1 - self.net[Y]['condprob'][parents]
        return prob

    def enum_ask(self, X, e):
        dist = []
        for x in [False, True]:
            # make a copy of the evidence set
            e = copy.deepcopy(e)

            # extend e with value of X
            e[X] = x

            # topological sort
            variables = self.toposort()

            # enumerate
            dist.append(self.enum_all(variables, e))

        # normalize & return
        return self.normalize(dist)
    def enum_all(self, variables, e):
        if len(variables) == 0:
            return 1.0
        Y = variables[0]
        if Y in e:
            ret = self.querygiven(Y, e) * self.enum_all(variables[1:], e)
        else:
            probs = []
            e2 = copy.deepcopy(e)
            for y in [True, False]:
                e2[Y] = y
                probs.append(self.querygiven(Y, e2) * self.enum_all(variables[1:], e2))
            ret = sum(probs)

        """print("%-14s | %-20s = %.8f" % (
                ' '.join(variables),
                ' '.join('%s=%s' % (v, 't' if e[v] else 'f') for v in e),
                ret
            ))
        """
        return ret

def printOutputFile(result):
    with open('output.txt','a+') as outputFile:
        outputFile.write(str(result)+'\n')



def setOutputFile():
    outputFile = open('output.txt','w')
    outputFile.close()

def query(bn,queries):
    net = Net(bn)
    #net.display()
    #print "\n\n"
    #queryGiven check
    #a=net.querygiven('LeakIdea',{'LeakIdea':True,'NightDefense':False})
    #print a

    #reading query
    for q in queries:
        if '|' in q: #Conditional Probability
            match = re.match(r'P\((.*)\|(.*)\)', q)
            X=match.group(1).strip()[:-4]
            Xvalue=match.group(1).strip()[-1:]
            if Xvalue=='+':
                Xval=True
            else:
                Xval=False
            e = match.group(2).strip().split(', ')
            #print e
            edict = dict((x[:-4], True if x[-1:] == '+' else False) for x in e)

            dist = net.enum_ask(X, edict)

            """for prob, x in zip(dist, [False, True]):
                print("P(%s = %s | %s) = %.4f" %
                        (X,
                        't' if x else 'f',
                        ', '.join('%s = %s' % tuple(v.split('=')) for v in e),
                        prob))
            """
            #Write to output file
            for prob, x in zip(dist, [False, True]):
                if Xval==x:
                    return prob
                    #printOutputFile("%.2f" %prob)

        elif ',' in q: #Joint Probility
            match=q[q.index('(')+1:q.index(')')]
            JProb=match.split(', ')
            #print JProb
            edict = dict((x[:-4], True if x[-1:] == '+' else False) for x in JProb)
            #print edict
            edict_new=dict()
            jProbValue=1
            for x in JProb:
                if not net.parents(x[:-4]):  #No parents
                    dist=net.enum_ask(x[:-4],{})
                    #print dist
                else:
                    parent=net.parents(x[:-4])
                    for p in parent:
                        if p in edict.keys():
                            #print p,x,"Priy"
                            edict_new[p]=edict[p]
                            #print edict_new,"New"
                            dist=net.enum_ask(x[:-4],edict_new)
                            #print dist
                        else:
                            dist=net.enum_ask(x[:-4],{})
                            #print dist

                Xvalue=x[-1:]
                #print Xvalue
                if Xvalue=="+":
                    xval=True
                else:
                    xval=False
                for prob,x1 in zip(dist,[False,True]):
                    if xval==x1:
                        prob=round(prob, 2)
                        #print prob,x
                        jProbValue=jProbValue*prob
            #print ("%.2f" %jProbValue), "final"
            return jProbValue
            #printOutputFile("%.2f" %jProbValue)

        else: # marginal Probabillity
            match=q[q.index('(')+1:q.index(')')]
            X=match[:-4]
            Xvalue=match[-1:]
            if Xvalue=='+':
                Xval=True
            else:
                Xval=False
            edict = dict((match[:-4], True if x[-1:] == '+' else False) for x in match)
            dist = net.enum_ask(X, edict)
            for prob, x in zip(dist, [False, True]):
                if Xval==x:
                    return prob
                    #printOutputFile("%.2f" %prob)

def getTruthValue(parent_list,t):
    #parent_list=[(0.37500000000000006, False), (0.625, True)]
    for i in parent_list:
        #print i[1]
        #print i
        if t=='+' and i[1]==True:
            return float(i[0])
        if t=='-' and i[1]==False:
            return float(i[0])
    return
#getTruthValue([1,2,3],'-')

def expected_utility(bn,utility,eu):

    net = Net(bn)
    for e in eu:
        if '|' not in e and ',' not in e: #Marginal Probability for EU
            match = re.match(r'EU\((.*)\)', e)
            X=match.group(1).strip()[:-4]

            Xvalue=match.group(1).strip()[-1:]
            net.assignprob(X,net)
            #net.display()

            #Find parents of utility nodes
            utilList= utility.keys()[0].split('| ')[1]

            parent_utility=utilList.rstrip('\n').split(' ')

            #Find probability of parent nodes
            e = match.group(1).strip().split(', ')
            #print e
            parent_prob=OrderedDict()

            for p in parent_utility:
                if p!='':
                    edict = dict((x[:-4], True if x[-1:] == '+' else False) for x in e)
                    dist = net.enum_ask(p, edict)
                    #print dist
                    parent_prob[p]=zip(dist, [False, True])

            #Calculate EU value
            #print parent_prob
            #print utility
            utility_value=utility.values()[0]
            #print utility_value
            euValue=0
            euVal=0
            for u in utility_value:
                #print u
                temp=[]
                for i in u.split(' '):
                    temp.append(i)
                    #print i
                #print temp
                for i in range(len(temp)):
                    if i==1:
                        euValue=int(temp[0])*getTruthValue(parent_prob.values()[0],temp[i])
                    if i==2:
                        #print getTruthValue(parent_prob.values()[1],temp[i])
                        #if getTruthValue(parent_prob.values()[1],temp[i])!=None:
                        euValue=euValue*getTruthValue(parent_prob.values()[1],temp[i])
                    if i==3:
                        euValue=euValue*getTruthValue(parent_prob.values()[2],temp[i])
                euVal+=euValue
            #print "\n Final",round(euValue),round(euVal)
            #printOutputFile("%.f" %euVal)
            return euVal
                #euValue=euValue+int(u_temp[0])

                #print parent_prob.values()[0][1][0]
                #print euValue
                #for p in parent_prob:
                    #euValue=euValue+int(u_temp[0])*()

        elif '|' in e: #Conditional Probability for EU
            match = re.match(r'EU\((.*)\)', e)
            X=match.group(1).strip().split(" | ")
            #print X

            Xvalue=match.group(1).strip()[-1:]
            net.assignprob(X,net)

            #Find parents of utility nodes
            utilList= utility.keys()[0].split('| ')[1]

            parent_utility=utilList.rstrip('\n').split(' ')

            #Find probability of parent nodes
            e = match.group(1).strip().split(', ')
            parent_prob=OrderedDict()

            for p in parent_utility:
                if p!='':
                    edict = dict((x[:-4], True if x[-1:] == '+' else False) for x in X)
                    dist = net.enum_ask(p, edict)
                    #print dist
                    parent_prob[p]=zip(dist, [False, True])

            #Calculate EU value
            #print parent_prob
            #print utility
            utility_value=utility.values()[0]
            #print utility_value
            euValue=0
            euVal=0
            for u in utility_value:
                #print u
                temp=[]
                for i in u.split(' '):
                    temp.append(i)
                    #print i
                #print temp
                for i in range(len(temp)):
                    if i==1:
                        euValue=int(temp[0])*getTruthValue(parent_prob.values()[0],temp[i])
                    if i==2:
                        euValue=euValue*getTruthValue(parent_prob.values()[1],temp[i])
                    if i==3:
                        euValue=euValue*getTruthValue(parent_prob.values()[2],temp[i])
                euVal+=euValue
            #print "\n Final",round(euValue),round(euVal)
            #printOutputFile("%.f" %euVal)
            return euVal

        elif ',' in e: #joint prob for EU
            match = re.match(r'EU\((.*)\)', e)
            X=match.group(1).strip().split(", ")


            Xvalue=match.group(1).strip()[-1:]
            net.assignprob(X,net)

            #Find parents of utility nodes
            utilList= utility.keys()[0].split('| ')[1]

            parent_utility=utilList.rstrip('\n').split(' ')

            #Find probability of parent nodes
            e = match.group(1).strip().split(', ')
            parent_prob=OrderedDict()

            for p in parent_utility:
                if p!='':
                    edict = dict((x[:-4], True if x[-1:] == '+' else False) for x in X)

                    dist = net.enum_ask(p, edict)
                    #print dist,"Dist"
                    if p in decision_nodes:
                        for x in X:
                            if x[:-4] == p:
                                xvalue=x[-1:]
                                if xvalue=="+":
                                    parent_prob[p]=zip((0,1),[False, True])
                                else:
                                    parent_prob[p]=zip((1,0),[False, True])


                    else:
                        parent_prob[p]=zip(dist, [False, True])

                    #print parent_prob
            #Calculate EU value
            #print parent_prob
            #print utility
            utility_value=utility.values()[0]
            #print utility_value
            euValue=0
            euVal=0
            for u in utility_value:

                temp=[]
                for i in u.split(' '):
                    temp.append(i)
                    #print i

                for i in range(len(temp)):
                    if i==1:
                        euValue=int(temp[0])*getTruthValue(parent_prob.values()[0],temp[i])
                    if i==2:
                        euValue=euValue*getTruthValue(parent_prob.values()[1],temp[i])
                    if i==3:
                        euValue=euValue*getTruthValue(parent_prob.values()[2],temp[i])
                euVal+=euValue
            #print "\n Final",round(euVal)
            #printOutputFile("%.f" %euVal)
            return euVal

    return

def maximum_expected_utility(meu,bn,utility):

    for m in meu:
        if '|' not in m and ',' not in m:
            m_positive_list=[]
            m_negative_list=[]
            index=m.find(')')
            mout=m[:index]+" = +"+m[index:]
            m_positive_list.append(mout[1:])
            meu1= expected_utility(bn,utility,m_positive_list)
            #print meu1
            mout=m[:index]+" = -"+m[index:]
            m_negative_list.append(mout[1:])
            meu2= expected_utility(bn,utility,m_negative_list)




            if(meu1>meu2):
                printOutputFile("+ "+"%.f" %meu1)
                #return meu1
            else:
                printOutputFile("- "+"%.f" %meu2)
                #return meu2

        #meu2=expected_utility(bn,utility,mlist[1])
        #print meu1,meu2
        elif '|' in m:
            m_positive_list=[]
            m_negative_list=[]
            index=m.find('|')
            mout=m[:index]+" = +"+m[index:]
            m_positive_list.append(mout[1:])
            print m_positive_list
            meu1= expected_utility(bn,utility,m_positive_list)
            #print meu1
            mout=m[:index]+" = -"+m[index:]
            m_negative_list.append(mout[1:])
            meu2= expected_utility(bn,utility,m_negative_list)
            if(meu1>meu2):
                printOutputFile("+ "+"%.f" %meu1)
                #return meu1
            else:
                printOutputFile("- "+"%.f" %meu2)
                #return meu2
        elif ',' in m:
            index=m.find('(')
            mout=m[index+1:m.index(')')]
            mout=mout.split(",")
            meu=[]
            meu1=[]
            if len(mout)==2:
                meu1.append("EU("+mout[0]+" = +,"+mout[1]+" = +)")
                meu.append(expected_utility(bn,utility,meu1))
                meu1=[]
                meu1.append("EU("+mout[0]+" = +,"+mout[1]+" = -)")
                meu.append(expected_utility(bn,utility,meu1))
                meu1=[]
                meu1.append("EU("+mout[0]+" = -,"+mout[1]+" = +)")
                meu.append(expected_utility(bn,utility,meu1))
                meu1=[]
                meu1.append("EU("+mout[0]+" = 1,"+mout[1]+" = -)")
                meu.append(expected_utility(bn,utility,meu1))
                meu1=[]
                #print meu,max(meu),meu.index(max(meu))
                if meu.index(max(meu))==0:
                    printOutputFile("+ + "+"%.f" %max(meu))
                elif meu.index(max(meu))==1:
                    printOutputFile("+ - "+"%.f" %max(meu))
                elif meu.index(max(meu))==2:
                    printOutputFile("- + "+"%.f" %max(meu))
                elif meu.index(max(meu))==3:
                    printOutputFile("- - "+"%.f" %max(meu))

            else:
                printOutputFile("- "+"10")
            #print m
    return

def main():
    queries=[]
    eu=[]
    meu=[]
    bn=OrderedDict()
    utility=OrderedDict()


    setOutputFile()
    with open(sys.argv[-1]) as f:
    #with open("sample01.txt") as f:
        i=f.read()
    i=i+"\n**"

    big=i.split("******\n")

    bnList=big[1].rstrip("\n").split("\n")
    bnList.append("***")
    val=[]
    for b in bnList:
        #print b
        if b=="":
            continue

        if b[0].isdigit() or b=="decision":
            val.append(b.rstrip('\n'))
        elif b[0].isalpha():
            key=b.rstrip('\n')
        if b.rstrip('\n')=="***":
            bn[key]=val
            val=[]

    for b in bn:
        if bn[b]==['decision']:
            bn[b]=['0.5']
            decision_nodes.append(b)



            #bn.pop(b, None)

    if len(big)>2:
        utilityList=big[2].split("\n")
        val=[]

        for u in utilityList:
            if u=="**":
                utility[key]=val
            elif u[0].isalpha():
                key=u
            else:
                val.append(u.rstrip('\n'))


    #print "Bayesian Network \n",bn,"\n\n\n", utility

    queriesList=big[0].split("\n")
    for q in queriesList:
        if q.startswith("P("):
            q_list=[]
            q_list.append(q)
            #print q_list
            prob1=float(query(bn,q_list))
            #print prob1
            printOutputFile("%.2f" %prob1)
            queries.append(q.rstrip('\n'))
        elif q.startswith("EU("):
            e_list=[]
            e_list.append(q)
            #print q_list
            prob2=float(expected_utility(bn,utility,e_list))

            printOutputFile("%.f" %prob2)
            eu.append(q.rstrip('\n'))
        elif q.startswith("MEU("):
            m_list=[]
            m_list.append(q)
            #print q_list
            maximum_expected_utility(m_list,bn,utility)

            #printOutputFile("%.f" %prob3)
            meu.append(q.rstrip('\n'))




    #query(bn,queries)

    """ if eu!=[]:

        expected_utility(bn,utility,eu)

    if meu!=[]:
        maximum_expected_utility(meu,bn,utility)
    """

if __name__=='__main__':
    main()
