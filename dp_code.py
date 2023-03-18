# -*- coding: UTF-8 -*-

import math
import itertools as it
from scipy.stats import poisson
import numpy as np
# import copy
from bidict import bidict
from tqdm import trange
import time


class DpPlanner():
    def __init__(self, T, b, h, beta, lamda, c, L):
        self.start = time.perf_counter()  # 返回系统运行时间
        print('DpPlanner Initializing...')
        self.T = T
        self.b = b
        self.h = h
        self.beta = beta
        self.lamda = lamda
        self.c = c
        self.L = L
        self.P = []
        self.qMax = int(poisson.ppf(0.99, lamda * L))
        print("qMax =", self.qMax)
        self.M = self.qMax * 2
        for j in range(self.qMax+1):
            self.P.append(self.poisson_prob(j, lamda, L))

        self.f_lookuptable = {}
        self.state_space = bidict({})  # key: state_id, value: state

        # 构造x_1t, x_2t, ..., x_Lt
        xn = list(it.product(range(self.qMax + 1), repeat=L))
        print('Constructing State Space...')
        # 构造状态空间
        state_id = 0
        for x0 in trange(-self.M, self.M+1):
            for i in range(len(xn)):
                xt = (x0, ) + xn[i]  # tuple
                self.state_space[state_id] = xt
                state_id = state_id + 1
                for qt in range(self.qMax+1):
                    f_value = self.f(xt, qt)
                    self.f_lookuptable[xt + (qt, )] = f_value
        print('state_space:', len(self.state_space))
        print('(2M+1)*(qMax+1)^L:', (2*self.M+1)*(self.qMax+1)**L)

        self.N = len(self.state_space)
        self.V = float('inf') * np.ones([self.N, T], dtype=float)  # N行T列
        # N行T+1列，最后一列全为0
        self.V = np.hstack((self.V, np.zeros([self.N, 1], dtype=float)))
        self.q = np.zeros([self.N, T], dtype=int)
        self.state_next_link = -1 * \
            np.ones([self.N, T], dtype=int)  # 初始化为-1表示未赋值
        print('DpPlanner Initialized.')

    def dp(self, d):
        for t in trange(self.T-1, -1, -1):  # 从后往前递推
            for i in range(len(self.state_space)):  # 遍历状态空间
                xt = self.state_space[i]
                best_q = -1
                best_V = float('inf')
                best_next = -2  # -2表示此状态无后继状态可用
                for qt in range(0, self.qMax+1):  # 遍历决策
                    # 构造t+1时刻状态
                    x_next = list(xt)
                    x_next[0] = xt[0] + xt[1] - d[t]
                    x_next[1:self.L] = xt[2:self.L+1]
                    x_next[self.L] = qt
                    # 判断这个状态是否在状态空间内，若不在则抛弃
                    if(tuple(x_next) not in self.state_space.inverse):
                        continue
                    # 取t+1时刻状态id
                    id_next = self.state_space.inverse[tuple(x_next)]
                    # 取t+1时刻最小总代价
                    V_next = self.V[id_next][t+1]
                    temp_V = self.get_f(xt, qt) + V_next
                    if(temp_V < best_V):  # 寻找当前状态下的最优决策
                        best_V = temp_V
                        best_q = qt
                        best_next = id_next
                self.V[i][t] = best_V  # 填入矩阵
                self.q[i][t] = best_q  # 填入矩阵
                self.state_next_link[i][t] = best_next

        initial_state = tuple([0 for i in range(self.L+1)])
        initial_state_id = self.state_space.inverse[initial_state]

        q_list = []

        next_state_id = initial_state_id
        for t in range(0, self.T):
            print(
                f't={t}, state={self.state_space[next_state_id]}, V={self.V[next_state_id][t]:.2f}, q={self.q[next_state_id][t]}, d={d[t]}')
            q_list.append(self.q[next_state_id][t])
            next_state_id = self.state_next_link[next_state_id][t]
        print('q:', q_list)

        self.end = time.perf_counter()
        print('\n用时：{:.4f}s'.format(self.end-self.start))
        return q_list

    def poisson_prob(self, j, l, L):
        prob = (l * L)**j * math.exp(-l * L) / math.factorial(j)
        return prob

    def Eh(self, x):
        result = 0.0
        for j in range(self.qMax):
            temp = self.h * (x[0]+x[1]-j) * self.P[j]
            if(temp > 0):
                result += temp
        return result

    def Eb(self, x):
        result = 0.0
        for j in range(self.qMax):
            temp = self.b * (j-x[0]-x[1]) * self.P[j]
            if(temp > 0):
                result += temp
        return result

    def f(self, x, q):
        cqt = self.c * q
        holding_cost = self.Eh(x)
        backlog_cost = self.Eb(x)
        ret = cqt + holding_cost + backlog_cost
        return ret

    def get_f(self, x, q):
        return self.f_lookuptable[x + (q, )]


if __name__ == '__main__':
    # 1 输入参数
    T = 15
    c = 0.2
    b = 1.0
    h = 0.5
    L = 2
    beta = 0.8
    lamda = 2
    # M = 10
    d = np.random.poisson(lamda, T)
    print("d:", d)
    planner = DpPlanner(T, b, h, beta, lamda, c, L)
    planner.dp(d)
