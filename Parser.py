n_org = 8
n_state = 16
n_action = 8
n_goto = 3

org_G[n_org]={
    "E->E+T",
    "E->E-T",
    "E->T",
    "T->T*F",
    "T->T/F",
    "T->F",
    "F->(E)",
    "F->n"
}
Action[n_state][n_action] = {
# //    n        +     -       *     /     (     )     $
    "S4", "E1", "E1", "E1", "E1", "S5", "E2", "E1",
    "E3", "S8", "S9", "E3", "E3", "E3", "E2", "ACC",
    "E5", "R3", "R3", "S11", "S12", "E5", "R3", "R3",
    "E6", "R6", "R6", "R6", "R6", "E6", "R6", "R6",
    "E6", "R8", "R8", "R8", "R8", "E6", "R8", "R8",

    # // 5
    "S4", "E1", "E1", "E1", "E1", "S5", "E2", "E1",
    "E3", "S8", "S9", "E3", "E3", "E3", "S7", "E4",
    "E6", "R7", "R7", "R7", "R7", "E6", "R7", "R7",
    "S4", "E1", "E1", "E1", "E1", "S5", "E2", "E1",
    "S4", "E1", "E1", "E1", "E1", "S5", "E2", "E1",

    # // 10
    "E5", "R1", "R1", "S11", "S12", "E5", "R1", "R1",
    "S4", "E1", "E1", "E1", "E1", "S5", "E2", "E1",
    "S4", "E1", "E1", "E1", "E1", "S5", "E2", "E1",
    "E6", "R4", "R4", "R4", "R4", "E6", "R4", "R4",
    "E6", "R5", "R5", "R5", "R5", "E6", "R5", "R5",

    # // 15
    "E5", "R2", "R2", "S11", "S12", "E5", "R2", "R2"
}
Goto[n_state][n_goto] = {
# //  E  T  F
    1, 2, 3,
    0, 0, 0,
    0, 0, 0,
    0, 0, 0,
    0, 0, 0,
    6, 2, 3,
    0, 0, 0,
    0, 0, 0,
    0, 10, 3,
    0, 15, 3,
    0, 0, 0,
    0, 0, 13,
    0, 0, 14,
    0, 0, 0,
    0, 0, 0,
    0, 0, 0
}

len = 0
etg = 0

def find_action(S, a):
    global org_G, etg, len, n_org, n_state, n_action, n_goto
    global Action
    if a =='+':
        j = 1
    elif a == '-':
        j = 2
    elif a == '*':
        j = 3
    elif a == '/':
        j = 4
    elif a == '(':
        j = 5
    elif a == ')':
        j = 6
    elif a == '$':
        j = 7
    elif a.isdigit():
        j = 0
    else:
        print("出现不匹配终结符")
        return "NU"
    print("action:(",S,",",j ,")",Action[S][j],end = ' ')
    return Action[S][j]

def find_goto(S, A):
    global Goto
    if A == 'E':
        j = 0
    elif A == 'T':
        j = 1
    else: j = 3
    print("goto:(",S,",",j,")",Goto[S][j], end=' ')
    return Goto[S][j]

class _Stack(object):

    def __init__(self):
        self.stack = []

    def push(self, data):
        """
        进栈函数
        """
        self.stack.append(data)

    def pop(self):
        """
        出栈函数，
        """
        return self.stack.pop()

    def gettop(self):
        """
        取栈顶
        """
        return self.stack[-1]
    def size(self):
        return len(self.stack)

def print_stack(ST, temp, j):
    global org_G, etg, len, n_org, n_state, n_action, n_goto
    t_ST = _Stack

    spc1 = ST.size()
    print("Symble:",end=' ')
    for i in range(0,spc1):
        t_char = ST.top()
        t_ST.push(t_char)
        ST.pop()
    for i in range(0,spc1):
        t_char = t_ST.top()
        t_ST.pop()
        print(t_char,end='')
        ST.push(t_char)
    for i in range(0,23 - spc1):
        print(' ',end='')
    print('|',end='')
    for i in range(0,20 - len(temp) + j):
        print(' ',end='')

    for i in range(j,len(temp)):
        print(temp.at(i),end='      ')

def LR(temp):
    global org_G,etg,len,n_org,n_state,n_action,n_goto
    print("2. 算法4.3 LR分析")
    print("          栈                   ",end='')
    print("                    输入",end='')
    print("     分析动作")
    State =_Stack
    Symble = _Stack
    State.push(0)
    Symble.push('-')

    i = 0
    j = 1
    while(1):
        print(j,end='')
        if j > 9: print(":", end='')
        else: print(':',end=' ')

        print_stack(Symble, temp, i)

        S = State.top()
        a = temp.at(i)

        P = find_action(S, a)
        b = P.at(0)

        if b == 'S':
            t_s = P[1:]
            s = int(t_s.c_str())
            State.push(s)
            Symble.push(a)
            if i < len - 1:
                i+=1
            print("shift ",s,end='')
        elif b == 'R':
            t_s = P[1:]
            s = int(t_s.c_str())

            reduce = org_G[s][3:]
            for i in range(0,len(reduce)):
                State.pop()
                Symble.pop()

            S = State.top()
            A = org_G[s].at(0)
            Symble.push(A)

            new_s = find_goto(S, A)
            State.push(new_s)
            print("reduce by ",org_G[s],end='')
        elif b == 'A':
            return 1
        else:
            etg = 1
            print("error",end='')
            return 0
        j+=1
        print()




