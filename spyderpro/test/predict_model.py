import numpy as np
import csv
import os
import matplotlib.pyplot as plt

wf = open("/Volumes/Tigo/易班项目数据/节假日模型.csv", 'a+')
w = csv.writer(wf)
# w.writerow(["地区", "模型"])
for file in os.listdir("/Volumes/Tigo/易班项目数据/预测模型训练数据2/"):
    area = file.split(".")[0]
    filetype = file.split(".")[1]
    if filetype != "csv":
        continue
    f = open("/Volumes/Tigo/易班项目数据/预测模型训练数据2/" + file, 'r')
    r = csv.reader(f)
    data_map = dict()
    try:
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
            if ddate <= "2018-09-30":
                continue
            if ddate == "2018-10-02":
                break
            date_time_range.append(date_time)
            data.append(data_map[date_time])
        # 定义x、y散点坐标
        x = [i for i in range(1, len(data) + 1)]
        x = np.array(x)
        num = data
        y = np.array(num)
        # 用3次多项式拟合
        try:
            f1 = np.polyfit(x, y, 3)
        except Exception:
            print(area )
            continue
    except Exception:
        print(file)
        continue
    # print('f1 is :\n', f1)

    p1 = np.poly1d(f1)
    # # print('p1 is :\n', p1)
    w.writerow([area, str(p1)])
    print("%s is SUCCESS" % area)
    # # 也可使用yvals=np.polyval(f1, x)
    # yvals = p1(x)
    # # 绘图
    # plot1 = plt.plot(x, y, 's', label='original values')
    # plot2 = plt.plot(x, yvals, 'r', label='polyfit values')
    # plt.xlabel('x')
    # plt.ylabel('y')
    # plt.legend(loc=4)  # 指定legend的位置右下角
    # plt.title('polyfitting')
    # plt.show()
