# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 15:40:21 2023

@author: Yue
"""

import pandas as pd

def estimate_lambda(df_sales, resample='d'):
    df_sales['date'] = pd.to_datetime(df_sales['下单时间'])
    # 以日期作为索引
    df_sales = df_sales.set_index('date')
    # 取其中一种产品，按日求和得到各字段每日总和
    daily_sales_sum = df_sales[df_sales['ProductName']=='中长款无毛领羽绒服'].resample(resample).sum(numeric_only=True)
    # 每日销量总和的均值即为需求到达率
    daily_sales_sales_avg = daily_sales_sum['销量'].mean()
    return daily_sales_sales_avg

def estimate_c_L(df_purchase):
    df_purchase['date'] = pd.to_datetime(df_purchase['下单日期'])
    # 以日期作为索引
    df_purchase = df_purchase.set_index('date')
    # 取其中一种产品
    product = df_purchase[df_purchase['ProductName']=='中长款无毛领羽绒服']
    c = (product['单价'] * product['采购数量']).sum() / product['采购数量'].sum()
    # L为每日平均提前期的加权平均，权重为当日采购数量
    L = (product['提前期'] * product['采购数量']).sum() / product['采购数量'].sum()
    return c, L

if __name__ == '__main__':
    df_sales = pd.read_csv('销量表(1).csv', encoding='gbk')
    daily_sales_sales_avg = estimate_lambda(df_sales)
    print('需求到达率:', daily_sales_sales_avg)

    df_purchase = pd.read_csv('完整供应表(1).csv', encoding='gbk')
    c, L = estimate_c_L(df_purchase)
    print('采购成本:', c)
    print('提前期:', L)
