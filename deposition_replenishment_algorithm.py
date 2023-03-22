import math
import time

def positive(x):
    if x > 0:
        return x
    else:
        return 0


def II(x):
    if x:
        return 1
    else:
        return 0


class DepositionReplenishmentAlgorithm():
    def __init__(self, T, c, b, h, beta, L, m, n, np, lamda):
        self.T = T
        self.c = c
        self.b = b
        self.h = h
        self.beta = beta
        self.L = L
        self.m = m
        self.n = n
        self.np = np
        self.lamda = lamda
        print('T:', T)
        print('c:', c)
        print('b:', b)
        print('h:', h)
        print('beta:', beta)
        print('L:', L)
        print('m:', m)
        print('n:', n)
        print('n\':', np)
        print('lamda:', lamda)


    def run(self, d):
        print('d:', d)
        u = {}
        q_star = {}
        min_v = {}
        for t in range(1, self.T+1):  # for all decision periods t
            print(f'########t={t}########')
            u[t] = {}
            p = self.n + self.np + 1
            v_sum = 0
            while True:  # for all product-demand pair p>=n+np+1
                # print(f'  ####p={p}####')
                if p <= self.m:
                    # tp_star, v = self.argmin_v_1(p, t)
                    tp_star, v = self.argmin_v_3(p, t)
                    # print(f'    p<=m={self.m},tp_star={tp_star},v={v}')
                else:
                    tp_star, v = self.argmin_v_2(p, t)
                    # print(f'    p>m={self.m},tp_star={tp_star},v={v}')
                u[t][p] = 1 - II(tp_star > 0)
                if u[t][p] == 0:
                    print(f'    u[{t}]={u[t]}, break loop')
                    print(f'    v[{t}]sum={v_sum}')
                    min_v[t] = v_sum
                    break
                else:
                    v_sum += v
                p = p + 1
            sum = 0
            for p in u[t]:
                sum += u[t][p]
            q_star[t] = sum
            # update system status m, n, n'
            if (t-self.L) in q_star:
                q = q_star[t-self.L]
            else:
                q = 0
            m = self.m
            self.m = positive(self.m + d[t] - q)
            self.n = positive(self.n - m - d[t] + q)
            npt = 0
            for i in range(t-self.L+1, t+1):
                if i in q_star:
                    npt += q_star[i]
            self.np = npt
            print(
                f'  q{t}*={sum},d{t}={d[t]},m={self.m},n={self.n},n\'={self.np}')
        return q_star, min_v

    def v(self, p, t, tp):
        if tp + self.L <= self.T - t:
            sum1 = 0
            for k in range(0, self.T-t+1):
                temp = self.Pr(p, k) * (self.c*(self.beta**tp)+II(tp+self.L < k)
                                        * self.H1(tp, k)+II(tp+self.L > k)*self.B(tp, k))
                sum1 += temp
            sum2 = 0
            for k in range(0, self.T-t+1):
                temp = self.Pr(p, k)
                sum2 += temp
            result = sum1 + (1-sum2)*self.H2(tp, t)
            return result
        else:
            sum = 0
            for k in range(0, self.T-t+1):
                betasum = 0
                for i in range(1, self.T-t-k+1):
                    betasum += self.beta**(i-1)
                sum += self.Pr(p, k) * (self.c * self.beta **
                                        tp + self.b * betasum)
            return sum

    def Pr(self, p_input, k):
        p = p_input - self.m
        e = math.exp(1)
        if k == 0:
            result = (self.lamda**p) * (e**(-self.lamda)) / math.factorial(p)
        else:
            if k > 0:
                result = (self.lamda*(k+1))**p * \
                    (e**(-self.lamda*(k+1))) / \
                    math.factorial(p) * (1-e**(-self.lamda))
            else:
                result = 0
                print('[Pr]warning')
        return result

    def B(self, tp, k):
        sum = 0
        for i in range(1, tp+self.L-k+1):
            sum += self.beta**(i-1)
        return self.b*sum

    def H1(self, tp, k):
        sum = 0
        for i in range(1, k-tp-self.L+1):
            sum += self.beta**(i-1)
        return sum*self.h

    def H2(self, tp, t):
        sum = 0
        for i in range(1, self.T-t+1-tp-self.L+1):
            sum += self.beta**(i-1)
        return self.h*sum

    def argmin_v_1(self, p, t):
        v_min = float('inf')
        tp_star = -1
        for tp in range(0, self.T-t+1+1):
            v = self.v(p, t, tp)
            if v < v_min:
                v_min = v
                tp_star = tp
        return tp_star, v_min

    def argmin_v_2(self, p, t):
        v_a = self.v(p, t, 0)
        v_b = self.v(p, t, self.T - t + 1)
        if v_a < v_b:
            return 0, v_a
        else:
            return self.T - t + 1, v_b

    def argmin_v_3(self, p, t):
        k = 0
        pr = 1
        v_min = float('inf')
        tp_star = -1
        for tp in range(0, self.T-t+1+1):
            if tp+self.L <= self.T-t:
                v = self.v_3_1(p, t, tp)
            else:
                v = self.v_3_2(p, t, tp)
            if v < v_min:
                v_min = v
                tp_star = tp
        return tp_star, v_min

    def v_3_1(self, p, t, tp):
        betasum = 0
        for i in range(1, tp+self.L+1):
            betasum += self.beta**(i-1)
        result = self.c * self.beta**tp + self.b * betasum
        return result

    def v_3_2(self, p, t, tp):
        betasum = 0
        for i in range(1, self.T-t+1+1):
            betasum += self.beta**(i-1)
        result = self.c * self.beta**tp + self.b * betasum
        return result


if __name__ == '__main__':
    T = 10
    c = 0.2
    b = 1
    h = 0.5
    beta = 0.8
    L = 3
    m = 0
    n = 0
    np = 0
    lamda = 1
    d = [0, 1, 0, 4, 1, 3, 3, 1, 1, 1, 1]
    start = time.perf_counter() # 返回系统运行时间
    algo = DepositionReplenishmentAlgorithm(
        T, c, b, h, beta, L, m, n, np, lamda)
    q_list, min_v = algo.run(d)
    

    end = time.perf_counter()
    print(f'用时：{end-start:.4f}s')
    print('q:', q_list.values())
    print('v:', min_v.values())

    sum_v = 0
    for k in min_v:
        sum_v += min_v[k]
    print(f'V_sum = {sum_v:.2f}')
