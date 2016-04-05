__author__ = 'Priyanka'
import sys,re

OPERATORS = ['^', '=>', '~', '|']
VARCOUNT = 0
GOALS = set()
QNUM=0
facts=[]


class KnowledgeBase:
    def __init__(self, initial_exprs = []):
        self.exprs = {}
        for expr in initial_exprs:
            self.tell(expr)

    def tell(self, expr):
        self.setPredicateIndex(expr, expr)

    def ask(self, query):
        return FOL_BC_ask(self, query)

    def display(self):
        for key in self.exprs.keys():
            print key,':',self.exprs[key]

    def setPredicateIndex(self, mainExpr, innerExpr):
        if isPredicate(innerExpr):
            if innerExpr.op in self.exprs:
                if mainExpr not in self.exprs[innerExpr.op]:
                    self.exprs[innerExpr.op].append(mainExpr)
            else:
                self.exprs[innerExpr.op] = [mainExpr]

        elif innerExpr.op == '~':
            self.setPredicateIndex(mainExpr, innerExpr.args[0])

        else:
            #print "mainExpr:",mainExpr
            #print "innerExpr:",innerExpr.args[1]
            self.setPredicateIndex(mainExpr, innerExpr.args[0])
            self.setPredicateIndex(mainExpr, innerExpr.args[1])

    def fetchRulesForGoal(self, goal):
        try:
            predicate = self.getPredicate(goal)
            if predicate in self.exprs:
                return self.exprs[predicate]
        except IndexError:
            allExprs = []
            for key in self.exprs.keys():
                allExprs += self.exprs[key]
            return list(set(allExprs))

    def getPredicate(self, goal):
        if isPredicate(goal):
            return goal.op
        else:
            return self.getPredicate(goal.args[0])



class Expression:
    def __init__(self, op, args = []):
        self.op = op
        self.args = map(convertToExpr, args)

    def display(self):
        print("op:",self.op)
        print("args:",self.args)

    def __hash__(self):
        return hash(self.op) ^ hash(tuple(self.args))

    def __repr__(self):
        if len(self.args) == 0:
            return self.op

        elif self.op not in OPERATORS:
            args = str(self.args[0])
            for arg in self.args[1:]:
                args = args + ', ' + str(arg)
            return self.op + '(' + args + ')'

        elif self.op == '~':
            if self.args[0].op not in OPERATORS:
                return '~' + str(self.args[0])
            else:
                return '~' + '(' + str(self.args[0]) + ')'

        else:
            stringRepr = ''
            if self.args[0].op in OPERATORS:
                stringRepr = '(' + str(self.args[0]) + ')'
            else:
                stringRepr = str(self.args[0])
            stringRepr += ' ' + self.op + ' '

            if self.args[1].op in OPERATORS:
                stringRepr += '(' + str(self.args[1]) + ')'
            else:
                stringRepr += str(self.args[1])
            return stringRepr

    def __eq__(self, other):
        return isinstance(other, Expression) and self.op == other.op and self.args == other.args



def convertToExpr(item):
    if isinstance(item, Expression):
        return item

    if '=>' in item:
        pos = item.index('=>')
        lhs,rhs = item[:pos],item[pos + 1:]
        expr = Expression('=>', [lhs, rhs])
        return expr

    elif '^' in item:
        pos = item.index('^')
        first,second = item[:pos],item[pos + 1:]
        expr = Expression('^', [first, second])
        return expr

    elif '~' in item:
        pos = item.index('~')
        expr = Expression('~', [item[pos + 1:]])
        return expr

    elif isinstance(item, str):
        return Expression(item)

    if len(item) == 1:
        return convertToExpr(item[0])

    simpleExpr = Expression(item[0], item[1:][0])
    return simpleExpr


def isPredicate(expr):
    if expr.op[0] != '~':
        return expr.op not in OPERATORS and expr.op[0].isupper()
    else:
        return expr.op not in OPERATORS and expr.op[1].isupper()


def isVariable(item):
    return isinstance(item, Expression) and item.op.islower() and item.args == []


def Unify(x, y, subst = {}):
    if subst is None:
        return None

    elif x == y:
        return subst

    elif isVariable(x):
        return Unify_Var(x, y, subst)

    elif isVariable(y):
        return Unify_Var(y, x, subst)

    elif isinstance(x, Expression) and isinstance(y, Expression):
        return Unify(x.args, y.args, Unify(x.op, y.op, subst))

    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        return Unify(x[1:], y[1:], Unify(x[0], y[0], subst))

    else:
        return None


def Unify_Var(var, x, subst):
    if var in subst:
        return Unify(subst[var], x, subst)

    newSubst = subst.copy()
    newSubst[var] = x
    return newSubst



def standardizeVars(expr, stdVars = None):
    global VARCOUNT

    if stdVars is None:
        stdVars = {}

    if not isinstance(expr, Expression):

        return expr

    if isVariable(expr):
        if expr in stdVars:
            return stdVars[expr]
        else:
            newVar = Expression('z_' + str(VARCOUNT))
            VARCOUNT += 1
            stdVars[expr] = newVar
            return newVar
    else:
        return Expression(expr.op, (standardizeVars(arg, stdVars) for arg in expr.args))


def substitute(theta, expr):
    assert isinstance(expr, Expression)

    if isVariable(expr):
        if expr in theta:
            #print "PRIYANKA:",expr,theta[expr]
            return theta[expr]
        else:
            return expr
    else:
        return Expression(expr.op, (substitute(theta, arg) for arg in expr.args))


def expandBrackets(expr):
    if expr.op in ['^', '|']:
        arg1 = expandBrackets(expr.args[0])
        arg2 = expandBrackets(expr.args[1])
        #print arg1,arg2
        #raw_input()
        return Expression(expr.op, [arg1, arg2])

    else:
        return expr


def seperateExpr(expr):
    if expr.op == '=>':
        #print expandBrackets(expr.args[0]), expr.args[1]
        #print expr.op
        #print expr.args,"\n"
        return expandBrackets(expr.args[0]), expr.args[1]
    else:
        return [], expr


def FOL_BC_and(KB, goals, theta):
    #print goals
    if theta is None:
        pass

    elif isinstance(goals, list) and len(goals) == 0:
        yield theta

    else:
        if goals.op == '^':
            first = goals.args[0]
            rest = goals.args[1]

            if first.op == '^':
                while not isPredicate(first):
                    rest = Expression('^', [first.args[1], rest])
                    first = first.args[0]
        else:
            first = goals
            rest = []

        for theta1 in FOL_BC_or(KB, substitute(theta, first), theta):
            for theta2 in FOL_BC_and(KB, rest, theta1):
                yield theta2


def FOL_BC_or(KB, goal, theta):
    if goal in GOALS:
        #print "loop:",goal
        return

    GOALS.add(goal)

    #print "\n GOALS:",GOALS

    temp=''
    temp=str(goal)
    #print "1:",goal
    #temp=temp.split()
    if 'z_' in temp:
        s = re.sub('z_\d+','_', temp)
        s="Ask: "+s
        #f=open('output.txt','a+')
        #f.write(s + '\n')
        #f.close()
        #print "Ask:",s

    else:
        temp="Ask: "+temp
        #f=open('output.txt','a+')
        #f.write(temp+ '\n')
        #f.close()
        #print "Ask:",temp


    #print "2 fetchRulesForGoal:",KB.fetchRulesForGoal(goal)
    #print KB.fetchRulesForGoal(goal),substitute(theta,goal),goal

        #GOALS.remove(goal)

    #if str(substitute(theta,goal)) in str(KB.fetchRulesForGoal(goal)):
    #print substitute(theta,goal),facts
    if str(substitute(theta,goal)) in facts:
        #print 'Ask:',substitute(theta,goal)
        #print "True:",goal
        f=open('output.txt','a+')
        f.write("Ask: "+str(substitute(theta,goal)) + '\n')
        f.write("True: "+str(substitute(theta,goal)) + '\n')
        f.close()


    for rule in KB.fetchRulesForGoal(goal):

            ##STRTTTTT
        stdRule = standardizeVars(rule)
        lhs, rhs = seperateExpr(stdRule)
        #print "3",lhs,rhs,goal,substitute(theta,goal)
        #print "2.5:",rule
        R=str(rhs)
        R=R[:R.index('(')]
        #print str(rhs),str(goal)
        G=str(goal)
        G=G[:G.index('(')]
        #print "R:",R,G
        #print rhs,goal

        if R==G and str(substitute(theta,goal)) not in facts:
            #t=str(goal)
            t= str(substitute(theta,goal))
            t = re.sub('z_\d+','_', t)
            t= re.sub('\([a-z]\)','(_)', t)
            #print t
            t = re.sub('\([a-z]','(_', t)
            t = re.sub(',\s[a-z]',', _', t)
            #print t
            #t="Ask: "+t
            #print substitute(theta,goal)
            f=open('output.txt','a+')
            f.write("Ask: "+t + '\n')
            f.close()
            #print "Ask2: ",t

            #print "Ask:",substitute(theta,goal)

        #if lhs!=[]:
            #print "Ask:",goal

        if lhs==[] and str(substitute(theta,goal)) not in facts:
            temp_goal=str(goal)
            start_goal=temp_goal.index('(')
            end_goal=temp_goal.index(')')
            clue=temp_goal[start_goal+1:end_goal]
                #print clue[0]

            temp_goal1=str(substitute(theta,goal))
            start_goal1=temp_goal1.index('(')
            end_goal1=temp_goal1.index(')')
            clue1=temp_goal1[start_goal+1:end_goal]
                #print clue1[0]
            #or str(rhs)!=substitute(theta,goal)

            if str(rhs)!=str(goal) and not clue.islower():
                f=open('output.txt','a+')
                f.write("False: "+str(goal)+ '\n')
                #print "False2: ",str(goal)
                f.close()
                    #GOALS.remove(goal)

            elif str(rhs)!=str(substitute(theta,goal)) and clue1[0].isupper() and str(str(substitute(theta,goal))) not in str(KB.fetchRulesForGoal(goal)):
                    #print "Ask: ",goal
                f=open('output.txt','a+')
                f.write("False: "+str(substitute(theta,goal))+ '\n')

                f.close()
                #print "False: ",str(substitute(theta,goal))

        unify_sol = Unify(rhs, goal, theta)
        #print "Map:",unify_sol


        for theta1 in FOL_BC_and(KB, lhs, Unify(rhs, goal, theta)):

            if goal in GOALS and str(substitute(theta,goal)) not in facts:

                temp="True: "+str(substitute(theta1,goal))
                f=open('output.txt','a+')
                f.write(str(temp) + '\n')
                f.close()
                #print "True4:",substitute(theta1, goal)

                GOALS.remove(goal)
            else:
                GOALS.remove(goal)

            yield theta1




def FOL_BC_ask(KB, query):
    return FOL_BC_or(KB, query, {})


def parse(s):
    s = '(' + s + ')'
    s = s.replace('(', ' ( ')
    s = s.replace(')', ' ) ')
    s = s.replace(',', ' ')

    s = s.replace('|', ' | ')
    s = s.replace('&&', ' ^ ')
    s = s.replace('~', ' ~ ')
    s = s.replace('=>', ' => ')

    tokens = s.split()
    #print tokens,"\n"
    return readTokenList(tokens)


def readTokenList(List):
    first = List.pop(0)

    if first == '(':
        newSentence = []
        while List[0] != ')':
            newSentence.append(readTokenList(List))
        List.pop(0)
        return newSentence
    else:
        return first


def printOutputFile(result):
    with open('output.txt','a+') as outputFile:
        outputFile.write(result + '\n')
    #print QNUM

def setOutputFile():
    outputFile = open('output.txt','w')
    outputFile.close()


def main():
    global VARCOUNT, GOALS,QNUM,facts
    queries = []
    rules = []


    with open(sys.argv[-1]) as f:
    #with open("input.txt") as f:
        queryCount = 1
        goal = f.next().strip()
        temp=goal.split("&& ")
        l= len(temp)
        QNUM=l

        i=0
        while i < l :
            #print temp[i]

            queries.append(temp[i])
            i += 1

        KBcount = int(f.next().strip())
        while KBcount > 0:
            expr = f.next().strip()

            if "=>" not in expr:
                facts.append(expr)

            rules.append(expr)


            KBcount -= 1

    KB = KnowledgeBase(map(convertToExpr,map(parse,rules)))
    #KB.display()
    #raw_input()


    setOutputFile()
    j=0
    finalFlag=True
    if(len(queries)==1):
        Q = convertToExpr(parse(queries[0]))
        j=j+1
        GOALS.clear()
        VARCOUNT = 0
        flag = False
        for ans in KB.ask(Q):
            flag = True
            break
        if j==QNUM:
            if flag:
            #print "True"
            #raw_input()
                printOutputFile('True')
            else:
            #print "False"
            #raw_input()
                printOutputFile('False')
    else:
        for i in range(len(queries)):
            Q = convertToExpr(parse(queries[i]))
            j=j+1
            GOALS.clear()
            VARCOUNT = 0
            flag = False


            for ans in KB.ask(Q):
                flag = True
                finalFlag=finalFlag^flag
                break
            if j==QNUM:
                if finalFlag:
                #print "True"
                #raw_input()
                    printOutputFile('True')
                else:
                #print "False"
                #raw_input()
                    printOutputFile('False')


if __name__ == '__main__':
    main()