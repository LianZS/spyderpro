from .celeryconfig import app

@app.task(queue='Internet')
def keyword_rate(keyword):
    print(keyword)
    """
    获取浏览器关键词搜索频率

    """
    pass


@app.task(queue='Internet')
def monitoring_mobile_type_rate():
    """
    获取某个时段的中国境内各手机机型的占有率"""
    print("start")
    pass


@app.task(queue='Internet')
def monitoring_mobile_brand_rate():
    """
    获取某时段中国境内各手机品牌占用率

    """
    pass


@app.task(queue='Internet')
def monitoring_mobile_system_rate():
    """
    获取某时段中国境内各手机系统版本占用率
    """

    pass


@app.task(queue='Internet')
def monitoring_mobile_operator_rate():
    """获取某时段中国境内各手机运营商占用率"""
    pass


@app.task(queue='Internet')
def monitoring_mobile_network_rate():
    """获取某时段中国境内各手机网络占用率"""
    pass
