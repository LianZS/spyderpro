import numpy as np
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
import csv
import time
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pyplot as plt


def KCurveFit(x, y, rank=6, isPlot=True):
    '''
    :param x: x数据
    :param y: y数据
    :param rank: 曲线阶数
    :param isPlot: 是否进行画图
    :return: 计算正常则返回数组形式的系数，错误则返回0
    '''

    len_x = len(x)
    X0 = np.zeros((rank + 1, len_x))  # 构造X0，X0是N次方程组的矩阵表示
    for i in np.arange(rank + 1):
        for j in np.arange(len_x):
            X0[i, j] = x[j] ** (rank - i)

    # 需要用到的函数
    # np.transpose() 求转置
    # np.linalg.inv 求逆矩阵
    # np.dot() 矩阵乘积
    # np.linalg.matrix_rank 求矩阵的秩

    # 求系数 其实就是一个N次方程组求解的过程
    X = np.transpose(X0)  # X0本身已经是转置，参见公式类型
    XT = np.transpose(X)  # 求转置
    XTX = np.dot(XT, X)
    XInv = np.linalg.inv(XTX)  # 求逆矩阵 先构造方阵
    # 系数A = INV((XT*X)) * XT * Y
    Y = np.transpose(y)
    A = XInv.dot(XT).dot(Y)  # 得到系数

    # 验证参数是否正确
    if isPlot:
        # x0 = np.linspace(0,20,100)
        minx = np.min(x)
        maxx = np.max(x)
        x0 = np.arange(minx, maxx, 0.001)
        y0 = np.zeros(np.shape(x0))
        for i in np.arange(len(x0)):
            for j in np.arange(rank + 1):
                y0[i] = y0[i] + A[j] * x0[i] ** (rank - j)
        plt.figure(1)
        plt.grid(True)
        plt.plot(x, y, 'r.')
        plt.plot(x0, y0, 'b-')
        plt.show()
    print(A)
    return A


wf = open("/Volumes/Tigo/易班项目数据/非节假日交通预测模型.csv", 'a+')
w = csv.writer(wf)
w.writerow(["地区", "模型"])
for file in os.listdir("/Users/darkmoon/Project/SpyderPr/spyderpro/test/Traffic/"):
    area = file.split(".")[0]
    filetype = file.split(".")[1]
    if filetype != "csv":
        continue
    f = open("/Users/darkmoon/Project/SpyderPr/spyderpro/test/Traffic/" + file, 'r')
    r = csv.reader(f)
    data_map = dict()
    try:

        for item in r:

            ddate = item[0]
            if ddate not in data_map.keys():
                data_map[ddate] = list()
            ttime = item[1]
            rate = float(item[2])
            data_map[ddate].append({ttime: rate})
        # 日期集合
        date_index = sorted(data_map.keys())

        for ddate in date_index:
            data: list = data_map[ddate]
            if ddate>="20190821":
                break
            # 按时间排序

            sorted_data_range: list = sorted(data, key=lambda x: x.keys())
            rate_range: list = [list(item.values())[0] for item in sorted_data_range]

            # 定义x、y散点坐标
            x = [i for i in range(1, len(rate_range) + 1)]
            x = np.array(x)
            rates = rate_range
            y = np.array(rates)
            A = KCurveFit(x, y, rank=6)
            print(' 最小二乘法系数为：' + A)
            # 用3次多项式拟合
            # try:
            #     f1 = np.polyfit(x, y, 4)
            # except Exception as  e:
            #     print(area, e)
            #     continue
            # # print('f1 is :\n', f1)
            # #
            # p1 = np.poly1d(f1)
            # # # # print('p1 is :\n', p1)
            # # # w.writerow([area, str(p1)])
            # # print("%s is SUCCESS" % area)
            # # # # 也可使用yvals=np.polyval(f1, x)
            # yvals = p1(x)
            # # # 绘图
            # plot1 = plt.plot(x, y, 's', label='original values')
            # # plot2 = plt.plot(x, yvals, 'r', label='polyfit values')
            # plt.xlabel('x')
            # plt.ylabel('y')
            # plt.legend(loc=4)  # 指定legend的位置右下角
            # plt.title('polyfitting')
            # plt.show()


    except Exception as e:
        print(e)
        continue
