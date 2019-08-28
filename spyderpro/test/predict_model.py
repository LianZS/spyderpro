import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
from random import randrange
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.api import tsa
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller

# def generate_data(start_date, end_date):
#     df = pd.DataFrame([300 + i * 30 + randrange(50) for i in range(31)], columns=['income'],
#                       index=pd.date_range(start_date, end_date, freq='D'))
#
#     return df
#
#
# data = generate_data('20170601', '20170602')
# # 这里要将数据类型转换为‘float64’
# data['income'] = data['income'].astype('float64')
# # 绘制时序图
# data.plot()
# plt.show()
# # 绘制自相关图
# plot_acf(data).show()
f = open("/Volumes/Tigo/易班项目数据/FILE/乐山大佛风景区.csv")
r = csv.reader(f)
data_map = dict()
for item in r:
    ddate = item[0]
    num = int(item[1])
    data_map[ddate] = num

date_index = sorted(data_map.keys())
data = list()  # 数据
date_time_range = list()
for date_time in date_index:
    ddate = date_time.split(" ")[0]
    # 元旦等重大节假日不分析，先分析一个月的情况
    if ddate == "2017-01-01":
        continue
    if ddate == "2017-01-09":
        break
    date_time_range.append(date_time)
    data.append(data_map[date_time])
print(date_time_range)
df = pd.DataFrame(data, columns=['num'], index=date_time_range)
df['num'] = df['num'].astype('int32')
df.plot()
plt.show()
# # # 绘制自相关图
plot_acf(df).show()
# 差分–转换为平稳序列
# 默认1阶差分
data_diff = df.diff().dropna()
# 对数据进行差分后得到 自相关图和 偏相关图
data_diff.plot()
plt.show()
plot_acf(data_diff).show()
plot_pacf(data_diff).show()
##返回值依次为：adf, pvalue p值， usedlag, nobs, critical values临界值 , icbest, regresults, resstore
##一阶差分后的序列的时序图在均值附近比较平稳的波动， 自相关性有很强的短期相关性， 单位根检验 p值小于 0.05 ，所以说一阶差分后的序列是平稳序列
# 原始序列的检验结果为： (-9.450203372703733, 4.638339901271695e-16, 35, 7164, {'1%': -3.43126312739421, '5%': -2.8619435304007217, '10%': -2.5669847951004168}, 82184.47562744557)
print('原始序列的检验结果为：', adfuller(df["num"]))
adf = acorr_ljungbox(data_diff, lags=1)  ##返回统计量和 p 值
# 差分序列的ADF 检验结果为：(array([4223.28247679]), array([0.]))
# 一阶差分后的序列的时序图在均值附近比较平稳的波动， 自相关性有很强的短期相关性， 单位根检验 p值小于 0.05 ，所以说一阶差分后的序列是平稳序列
print(adf)
# 对模型进行定阶
pmax = int(len(data_diff) / 10)  # 一般阶数不超过 length /10
qmax = int(len(data_diff) / 10)
bic_matrix = []
for p in range(pmax + 1):
    temp = []
    for q in range(qmax + 1):
        try:
            temp.append(ARIMA(df, (p, 1, q)).fit().bic)
        except:
            temp.append(None)
        bic_matrix.append(temp)

bic_matrix = pd.DataFrame(bic_matrix)  # 将其转换成Dataframe 数据结构
p, q = bic_matrix.stack().idxmin()  # 先使用stack 展平， 然后使用 idxmin 找出最小值的位置
result = 'BIC 最小的p值 和 q 值：%s,%s' % (p, q)
f = open("/home/result.txt", "a+")
f.write(result)
f.close()
print(u'BIC 最小的p值 和 q 值：%s,%s' % (p, q))  # BIC 最小的p值 和 q 值：0,1
# 所以可以建立ARIMA 模型，ARIMA(0,1,1)
model = ARIMA(data, (p, 1, q)).fit()
model.summary2()  # 生成一份模型报告
model.forecast(5)  # 为未来5天进行预测， 返回预测结果， 标准误差， 和置信区间
