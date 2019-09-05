import numpy as np
import csv
import os
import matplotlib.pyplot as plt

# wf = open("/Volumes/Tigo/易班项目数据/非节假日模型.csv", 'a+')
# w = csv.writer(wf)
# w.writerow(["地区", "模型"])


f = open("/Volumes/Tigo/易班项目数据/非重大节日预测模型训练数据/深圳野生动物园.csv", 'r',encoding="gbk")
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

    date_time_range.append(date_time)
    data.append(data_map[date_time])
    # 定义x、y散点坐标
x = [i for i in range(1, len(data) + 1)]
x = np.array(x)
num = data
y = np.array(num)
# 用3次多项式拟合
f1 = np.polyfit(x, y, 3)

# print('f1 is :\n', f1)

p1 = np.poly1d(f1)
# # print('p1 is :\n', p1)
# w.writerow([area, str(p1)])
# # 也可使用yvals=np.polyval(f1, x)
yvals = p1(x)
# # 绘图
plot1 = plt.plot(x, y, 's', label='original values')
plot2 = plt.plot(x, yvals, 'r', label='polyfit values')
plt.xlabel('x')
plt.ylabel('y')
plt.legend(loc=4)  # 指定legend的位置右下角
plt.title('polyfitting')
plt.show()
print(p1)