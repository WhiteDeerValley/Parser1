import os
import tkinter as tk
import tkinter.messagebox
import tkinter.font as tf
import copy
window = tk.Tk()
window.title('消除左递归')
window.minsize(500, 500)

# 转换坐标显示形式为元组
def getIndex(text, pos):
    return tuple(map(int, str.split(text.index(pos), ".")))


class Inputs:
    def __init__(self):
        print("请输入表达式，以$结尾")
        self.inputs = input()

    def current(self):                  #返回当前指向的字符
        return self.inputs[0]

    def forward(self):                  #输入串前移一位
        self.inputs = self.inputs[1:]

    def backward(self,char):            #输入串退位
        self.inputs = char + self.inputs

    def empty(self):                    #检查输入串是否空
        return True if len(self.inputs) == 0 else False

class SymbolStack:
    def __init__(self,string):
        self.stack = string

    def pop(self):                  #将最后一个元素弹出
        self.stack = self.stack[:-1]

    def top(self):                  #返回栈顶元素
        return self.stack[-1]

    def push(self,m):               #压栈m
        self.stack = self.stack+m

    def empty(self):
        return True if len(self.stack) == 0 else False

class AnalyseTable:
    def __init__(self, productions, first, follows, input_symbols, state_symbols):
        self.table = {i + j: '' for j in input_symbols for i in state_symbols}
        '''
        'standard': ['E->TA', 'A->+TA', 'A->-TA', 'A->e', 'T->FB',
                     'B->*FB', 'B->/FB', 'B->e', 'F->(E)', 'F->n']
        '''
        for p in productions['standard']:
            if p[3] in state_symbols:
                for q in first[p[0]]:
                    if q != 'ε':
                        self.table[p[0]+q] = p
            else:
                if p[3] == 'ε':
                    for q in follows[p[0]]:
                        if q != 'ε':
                            self.table[p[0]+q] = p
                else:
                    self.table[p[0]+p[3]] = p
        for i in state_symbols:
            for p in follows[i]:
                if self.table[i+p] == '':
                    self.table[i+p] = productions['synch']
        self.show_table(input_symbols, state_symbols)

    def show_table(self,input_symbols,state_symbols):
        format1 = '%-8s'
        print(format1 % '状态/符号', end='')
        for i in input_symbols:
            print(format1 % i, end='')
        print()
        for i in state_symbols:
            print(format1 % i, end='')
            for j in input_symbols:
                print(format1 % self.table[i+j],end='')
            print()

    def at(self, index):
        return self.table[index]
'''
E->E+T / E-T / T
T->T*F / T/F / F
F->(E) / num
'''


class LL1Parser:
    def __init__(self):
        self.productions = {'none': '', 'synch': 'synch'}
        self.state_symbols, self.productions['standard'] = LL1Run()
        self.input_symbols = ['(', ')', '+', '-', '*', '/', 'n', '$']
        tmp = self.productions.get('standard')
        self.first,self.follow = getFirstandFollow(tmp,self.state_symbols)
        '''
        self.follows = {'E': [')', '$'], 'A': [')', '$'], 'T': ['+', '-', ')', '$'],
                        'B': ['+', '-', ')', '$'], 'F': ['*', '/', '+', '-', ')', '$']}
        self.firsts = {'E': ['(', 'n'], 'A': ['+', '-', 'ε'], 'T': ['(', 'n'], 'B': ['*', '/', 'ε'], 'F': ['(', 'n']}

        'standard': ['E->TA', 'A->+TA', 'A->-TA', 'A->ε', 'T->FB',
                                                                       'B->*FB', 'B->/FB', 'B->e', 'F->(E)', 'F->n']}
       
        self.symbol_stack = SymbolStack('$E')

        self.table = AnalyseTable(self.productions,self.firsts,self.follows,self.input_symbols,self.state_symbols)
        self.inputs = Inputs()
        self.process()
        '''
        self.process()


    def print_a_line(self,char, info,report = '正确'):
        print('%-20s' % self.symbol_stack.stack, end='')
        print('%-32s' % self.inputs.inputs, end='')
        print('%-8s' % char,end='')
        print('%-8s' % report,end='')
        print('%-24s' % info)

    '''
        def process(self):
        while not self.inputs.empty() and not self.symbol_stack.empty():
            if self.inputs.current() in self.input_symbols or self.inputs.current().isdigit():      #是终结符
                if self.inputs.current().isdigit():     #是数字
                        self.inputs.forward()
                        while self.inputs.current().isdigit():
                            self.inputs.forward()
                        self.inputs.backward('n')           #消去数字替换成n
                if self.symbol_stack.top() in self.input_symbols:       #栈顶是终结符
                    if self.symbol_stack.top() != self.inputs.current():   #栈顶与输入不相同
                        if self.symbol_stack.top() == '$':              #栈顶元素为空
                            self.print_a_line(self.inputs.current(),'栈顶是$ 并且与当前不匹配, 输入后移', '错误')
                            self.inputs.forward()
                        else:
                            self.print_a_line(self.inputs.current(),'栈顶是终结符且与当前不匹配, 符号栈弹出元素', '错误')
                            self.symbol_stack.pop()
                    else:
                        self.print_a_line(self.inputs.current(),'栈顶符号与当前匹配，消去', '正确')
                        self.inputs.forward()
                        self.symbol_stack.pop()
                else:
                    tmp_production = self.table.at(self.symbol_stack.top() + self.inputs.current())
                    if tmp_production == self.productions['none']:          #空白产生式
                        self.print_a_line(self.inputs.current(),'空白产生式，符号后移', '错误')
                        self.inputs.forward()
                    elif tmp_production == self.productions['synch']:
                        self.print_a_line(self.inputs.current(),'同步产生式, 符号栈栈顶弹出', '错误')
                        self.symbol_stack.pop()
                    else:
                        self.print_a_line(self.inputs.current(),tmp_production)
                        adds = "".join(i for i in reversed(tmp_production[3:]) if i!='ε' )
                        self.symbol_stack.pop()
                        self.symbol_stack.push(adds)
            else:
                print('监测到非法输入，跳过该部分')
                self.inputs.forward()
        print('分析完成')
    '''

    def  process(self):
        text_output.insert('insert', '左递归', 'tag1')
        text_output.insert('insert', self.productions.get('standard'),'tag2')
        text_output.insert('insert', '\n')
        text_output.insert('insert', self.state_symbols, 'tag2')
        text_output.insert('insert', '\n')
        text_output.insert('insert', self.first, 'tag2')
        text_output.insert('insert', '\n')
        text_output.insert('insert', self.follow, 'tag2')

        print(self.productions)
        print(self.first)
        print(self.follow)



def zhijie(x,y):
    outX = []
    outY = []
    x2 = chr(ord(x)+2)
    outX.append(x)
    for p in y:    #查找产生式右部每一个公式
        if p[0] == x:  #存在直接左递归
            outX.append(x2)
            outYtmp = x2+'->'+'ε'
            outY.append(outYtmp)
            flag = 0        #记录是否存在有非左递归形式的产生式，若到最后flag仍为0，则需要在产生式中加入A->A'
            for outProductions in y:        #对右部每一个产生式进行转变
                if outProductions[0] == x:     #左递归形式
                    outYtmp = x2+'->'+outProductions[1:]+x2
                    outY.append(outYtmp)
                else:                           #非左递归形式
                    flag = 1
                    outYtmp = str(x)+'->'+outProductions+x2
                    outY.append(outYtmp)
            if flag == 0:                       #不存在非左递归形式的右部产生式
                outYtmp = str(x)+'->'+x2
                outY.append(outYtmp)
            break           #结束对是否有左递归的查找
    if len(outX) == 1:  #不存在左递归，直接返回
        for i in y:
            outytmp = str(x)+'->'+i
            outY.append(outytmp)
        return outX,outY
    else:
        return outX,outY





def LL1Run():
    text_output.delete('1.0', 'end')
    text = text_input.get('1.0', 'end')
    text_list = list(text.split('\n'))  # 一行一行的拿文法
    text_list.pop()
    state_symbol =[]
    standards = []
    if not text_list[0]:
        print(tkinter.messagebox.showerror(title='出错了！', message='输入不能为空'))
    else:
        for cfg in text_list:

            x, y = cfg.split('->')  # 将文法左右分开
            x = ''.join(x.split())  # 消除空格,x为产生式左侧
            y = ''.join(y.split())
            y2 = y.split('|')       #产生式右侧，用list存储
            if not (len(x) == 1 and x >= 'A' and x <= 'Z'):
                pos = text_input.search(x, '1.0', stopindex="end")
                result = tkinter.messagebox.showerror(title='出错了！',
                                                      message='非上下文无关文法!坐标%s' % (getIndex(text_input, pos),))
                # 返回值为：ok
                print(result)
                return 0
            else:
                tmpx,tmpy = zhijie(x, y2)
                state_symbol += tmpx
                standards += tmpy
    '''
        text_output.insert('insert','左递归','tag1')
    text_output.insert('insert',standards,'tag2')
    text_output.insert('insert','\n')
    text_output.insert('insert',state_symbol,'tag2')
    '''

    return state_symbol,standards

def getFirstandFollow(prodections,state_symbols):             #获取first集合
    resultFirst = {}                                     #存储first字典
    resultFollow = {}

    for i in state_symbols:                              #初始化字典
        resultFirst[i] = []
        resultFollow[i] = []
    resultFollow.get(state_symbols[0]).append('$')
    resultFirst = getFirst(resultFirst, prodections,state_symbols)
    resultFollow = getFollow_3(resultFollow,resultFirst,prodections,state_symbols)
    return resultFirst,resultFollow
    #resultFollow = getFollow(resultFollow, prodections,state_symbols)

#形如A->aXYZ
def getFirst_1(resultFirst, prodections,state_symbols):
    result = resultFirst
    for str in prodections:
        leftP = str.split("->")[0]
        rightP = str.split("->")[1]
        if rightP[0] not in state_symbols:
            result[leftP].append(rightP[0])
    return result

#形如A->BCD
def getFirst_2(resultFirst, prodections,state_symbols):
    result = resultFirst
    for str in prodections:
        leftP = str.split("->")[0]
        rightP = str.split("->")[1]
        if rightP[0] in state_symbols:
            result[leftP] = result.get(leftP)+result.get(rightP[0])
    return result

#循环
def getFirst_3(resultFirst, prodections,state_symbols):
    result = resultFirst
    #print(result)
    #print("#########")
    while(True):
        test = copy.deepcopy(result)
        result = getFirst_2(result, prodections, state_symbols)
        for i in state_symbols:  # 对每个非终结符，对对应的字典即first集去重
            if result.get(i) != None:
                result[i] = list(set(result.get(i)))


            if test.get(i) != None:
                test[i] = list(set(test.get(i)))


        #print("FIRST:")
        #print(result)
        if (test == result):
            break


    #result = list(set(result))          #去重
    #test = list(set(test))              #排序
    return result


def getFirst(resultFirst, prodections,state_symbols):
    result1 = getFirst_1(resultFirst,prodections,state_symbols)
    result = getFirst_3(result1,prodections,state_symbols)
    return result

def getFollow_1(resultFollow,First, prodections,state_symbols):
    FOLLOW = resultFollow
    for str in prodections:
        leftP = str.split("->")[0]
        rightP = str.split("->")[1]
        tmp = []
        for i in rightP:
            tmp.append(i)
        tmp.reverse()
        if len(tmp) > 1:  # 产生式右边不止一个字符
            tmp1 = tmp[0]
            j = 0
            if tmp[0] in state_symbols:  # 最后一个字符是非终结符号
                FOLLOW[tmp[0]] = FOLLOW.get(leftP)+FOLLOW.get(tmp[0])
            for i in tmp[1:]:
                j += 1      #j为求follow的元素的下标
                if i not in state_symbols:  # 该字符是终结符
                    tmp1 = i
                else:  # i为非终结符
                    tmp1 = tmp[j-1]         #tmp1为求follow元素后的那个元素
                    if tmp1 in state_symbols:  # i后面一个字符为非终结符
                        tmpN = j - 1  #tmpN为求follow元素后的那个元素下标
                        while tmpN >= 0:  # 后面字符可以推出空需要继续考察更后面元素是否都为空直至考察到最后一个元素
                            tmp1 = tmp[tmpN]
                            if tmp1 not in state_symbols:
                                FOLLOW[i] = FOLLOW.get(i).append(tmp1)
                                break
                            elif 'ε' not in First.get(tmp1):  # 考察元素为非终结符
                                FOLLOW[i] = FOLLOW.get(i) + First.get(tmp1)
                                break
                            else:
                                if FOLLOW.get(i)!=None:
                                    #print(FOLLOW.get(i))
                                    FOLLOW[i] = FOLLOW.get(i)+First.get(tmp1)


                                    #print(FOLLOW.get(i))
                                else:
                                    FOLLOW[i] = First.get(tmp1)
                            tmpN -= 1  # 当前考察元素仍能推出空，再往后考察
                        if tmpN == -1:  # 求follow元素后可一直都推出空
                            if FOLLOW.get(i) == None:
                                FOLLOW[i] =  FOLLOW.get(leftP)
                            elif FOLLOW.get(leftP) == None:
                                FOLLOW[i] =  FOLLOW.get(i)
                            else:   FOLLOW[i] = FOLLOW.get(i) + FOLLOW.get(leftP)
                    else:                   #如果tmp1为终结符则直接加上tmp1的follow
                        FOLLOW[i] = FOLLOW.get(i)+[tmp1]
        else:
            if tmp[0] in state_symbols:
                FOLLOW[tmp[0]] = FOLLOW.get(tmp[0]) + FOLLOW.get(leftP)
    return FOLLOW

def getFollow_3(resultFollow,First, prodections,state_symbols):
    FOLLOW = resultFollow
    while(True):
        test = copy.deepcopy(FOLLOW)
        FOLLOW = getFollow_1(FOLLOW,First,prodections,state_symbols)

        for i in state_symbols:
            if FOLLOW.get(i) != None:
                FOLLOW[i] = list(set(FOLLOW.get(i)))
                if 'ε' in FOLLOW[i]:
                    FOLLOW[i].remove('ε')
            if test.get(i) != None:
                test[i] = list(set(test.get(i)))
                if 'ε' in test[i]:
                    test[i].remove('ε')
        if test == FOLLOW:
            break
    return FOLLOW



text_input = tk.Text(window, width=80, height=16)
text_output = tk.Text(window, width=80, height=20)

ft = tf.Font(family='微软雅黑', size=12)
text_output.tag_config("tag1", background="yellow", foreground="red", font=ft)
text_output.tag_config('tag2', font=ft)
# 按钮
button = tk.Button(window, text="消除左递归", command=LL1Parser, padx=32, pady=4, bd=4)

text_input.pack()
text_output.pack()
button.pack()
window.mainloop()