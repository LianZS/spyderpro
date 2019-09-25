from typing import List
from spyderpro.function.keywordfunction.parent import Parent

from spyderpro.data_requests.Internetdata.keyword import KeyWord, BaiduKeyWordObject


class SearchKeyword(Parent):

    def baidu_browser_keyword_frequency(self, keyword: str, baidu: bool = True,
                                        pc: bool = True, modile: bool = True) -> BaiduKeyWordObject:
        """
        获取百度浏览器关键词搜索频率
        :param keyword:关键词
        :param baidu:是否使用百度引擎
        :param weixin:是否使用微信搜索

        :param pc:是否获取pc端数据
        :param modile:是否移动端水
        :return:[KeyWordObject,KeyWordObject]
        """
        browser = KeyWord()
        result = browser.baidu_get_keyword_search_index(keyword=keyword)

        try:
            return result
        except Exception:
            return None

    def wechat_browser_keyword_frequency(self, keword, startdate, enddate):
        browser = KeyWord()
        self.type_check(startdate, int)
        self.type_check(enddate, int)
        result = browser.wechat_get_keyword_search_index(keyword=keword, startDate=startdate, endDate=enddate)
        return result

    def sougou_browser_keyword_frequency(self, keword, startdate, enddate):
        browser = KeyWord()
        self.type_check(startdate, int)
        self.type_check(enddate, int)
        result = browser.sougou_get_keyword_search_index(keyword=keword, startDate=startdate, endDate=enddate)
        return result

    def alibaba_goods_purchased_frequency(self, keyword: str, pur1688flag: bool = True, taobaoflag: bool = True,
                                          supplyflag: bool = True) -> dict:
        # **************该功能目前有bug**************

        """
        获取淘宝，1688某商品用户采购总数量，返回一年的数据

        :param keyword:
        :param pur1688flag:
        :param taobaoflag:
        :param supplyflag:
        :return:
        """
        browser = KeyWord()
        result = browser.get_alibaba_keyword_buy_index(keyword=keyword)
        return result

    def key_check(self, keyword) -> str:
        """
        由于部分关键词有问题，需要做修改才能查询
        :param keyword:
        :return:
        """
        if "中国民俗文化村" in keyword:
            return "中国民俗文化村"
        if "荔枝公园" in keyword:
            return "荔枝公园"
        if "小梅沙" in keyword:
            return "小梅沙"
        if "南昆山" in keyword:
            return "南昆山"
        if "立园" in keyword:
            return "立园"
        if "锦江温泉" in keyword:
            return "锦江温泉"
        if "曹溪温泉" in keyword:
            return "曹溪温泉"
        if "肇庆星湖" in keyword:
            return "肇庆星湖"
        if "海陵岛" in keyword:
            return "海陵岛"
        if "玄武山" in keyword:
            return "玄武山"
        if "南澳岛" in keyword:
            return "南澳岛"
        if "榕江" in keyword:
            return "榕江"
        if "金沙湾" in keyword:
            return "金沙湾"
        if "绿岛" in keyword:
            return "绿岛"
        if "分界洲岛" in keyword:
            return "分界洲岛"
        if "南湾猴岛" in keyword:
            return "南湾猴岛"
        if "清水湾" in keyword:
            return "清水湾"
        if "呀诺达" in keyword:
            return "呀诺达"
        if "槟榔谷" in keyword:
            return "槟榔谷"
        if "龙湾温泉" in keyword:
            return "龙湾温泉"
        if "瑶里古镇" in keyword:
            return "瑶里古镇"
        if "明月山温泉" in keyword:
            return "明月山温泉"
        if "龙虎山" in keyword:
            return "龙虎山"
        if "法门寺" in keyword:
            return "法门寺"
        if "恒山" in keyword:
            return "恒山"
        if "皇城相府" in keyword:
            return "皇城相府"
        if "响沙湾" in keyword:
            return "响沙湾"
        if "水洞沟" in keyword:
            return "水洞沟"
        if "广宗" in keyword:
            return "广宗"
        if "喀喇沁亲王府" in keyword:
            return "喀喇沁亲王府"
        if "阿斯哈图" in keyword:
            return "阿斯哈图石林"
        if "格根塔拉草原" in keyword:
            return "格根塔拉草原"
        if "阿尔山" in keyword:
            return "阿尔山"
        if "嘉峪关长城" in keyword:
            return "嘉峪关长城"
        if "鸣沙山月牙泉" in keyword:
            return "鸣沙山月牙泉"
        if "松鸣岩" in keyword:
            return "松鸣岩"
        if "官鹅沟" in keyword:
            return "官鹅沟"
        if "武威文庙" in keyword:
            return "孔庙"
        if "神州" in keyword:
            return "神州"
        if "景泰黄河石林" in keyword:
            return "景泰黄河石林"
        if "麦积山" in keyword:
            return "麦积山"
        if "贵清山" in keyword:
            return "贵清山"
        if "龟兹" in keyword:
            return "龟兹"
        if "金沙滩" in keyword:
            return "金沙滩"
        if "天山天池" in keyword:
            return "天山天池"
        if "新疆兵团" in keyword:
            return "新疆兵团"
        if "锡伯" in keyword:
            return "锡伯"
        if "那拉提" in keyword:
            return  "那拉提"
        if "吐鲁番葡萄沟" in keyword:
            return "吐鲁番葡萄沟"
        if "青海湖" in keyword:
            return "青海湖"
        if "嶂石岩" in keyword:
            return "嶂石岩"
        if "文化艺术中心" in keyword:
            return "文化艺术中心"
        if "金山岭长城" in keyword:
            return "金山岭长城"
        if "白草畔" in keyword:
            return "白草畔"
        if "南岳衡山" in keyword:
            return "南岳衡山"
        if "任弼时" in keyword:
            return "任弼时"
        if "岳阳楼" in keyword:
            return "岳阳楼"
        if "宝峰湖" in keyword:
            return "宝峰湖"
        if "黄龙洞" in keyword:
            return "黄龙洞"
        if "桃花源" in keyword:
            return "桃花源"

        if "湄江" in keyword:
            return "湄江"
        if "神农顶" in keyword:
            return "神农顶"
        if "神农架" in keyword:
            return "神农架"
        if "车溪民俗风景区" in keyword:
            return "车溪民俗风景区"
        if "神农溪" in keyword:
            return "神农溪"
        if "沙湖" in keyword:
            return "沙湖"
        if "沙坡头" in keyword:
            return "沙坡头"
        if "泸山" in keyword:
            return "泸山"
        if "灵山" in keyword:
            return "灵山"

        if "翠云廊" in keyword:
            return "翠云廊"
        if "乐山大佛" in keyword:
            return "乐山大佛"
        if "峨眉山" in keyword:
            return "峨眉山"
        if "中国死海" in keyword:
            return "中国死海"
        if "四姑娘山" in keyword:
            return "四姑娘山"

        if "三江" in keyword:
            return "三江"
        if "海螺沟" in keyword:
            return "海螺沟"
        if "阆中古城" in keyword:
            return "阆中古城"
        if "西山" in keyword:
            return "西山"
        if "蒙顶山" in keyword:
            return "蒙顶山"
        if "世界地质公园" in keyword:
            return "世界地质公园"
        if "七曲山" in keyword:
            return "七曲山"
        if "窦圌山" in keyword:
            return "窦圌山"
        if "龙宫" in keyword:
            return "龙宫"
        if "黄果树大瀑布" in keyword:
            return "黄果树大瀑布"
        if "贵州百里杜鹃" in keyword:
            return "贵州百里杜鹃"
        if "竹海" in keyword:
            return "竹海"
        if "南雁荡山" in keyword:
            return "南雁荡山"
        if "长屿硐天" in keyword:
            return "长屿硐天"
        if "石门" in keyword:
            return "石门"
        if "江南长城" in keyword:
            return "江南长城"
        if "黄山" in keyword:
            return "黄山"
        if "绩溪龙川" in keyword:
            return "绩溪龙川"
        if "天柱山" in keyword:
            return "天柱山"
        if "石台牯牛降" in keyword:
            return "石台牯牛降"
        if "九华山" in keyword:
            return "九华山"
        if "马仁奇峰" in keyword:
            return "马仁奇峰"
        if "王稼祥" in keyword:
            return "王稼祥"
        if "天堂寨" in keyword:
            return "天堂寨"
        if "万佛湖" in keyword:
            return "万佛湖"
        if "阜阳" in keyword:
            return "阜阳"
        if "八里河" in keyword:
            return "八里河"
        if "孟庙" in keyword:
            return "孟庙"
        if "明故城" in keyword:
            return "明故城"
        if "东昌湖" in keyword:
            return "东昌湖"
        if "蒙山国家森林公园" in keyword:
            return "蒙山国家森林公园"
        if "蒙山" in keyword:
            return "蒙山"
        if "泰山" in keyword:
            return "泰山"
        if "刘公岛" in keyword:
            return "刘公岛"
        if "赤山" in keyword:
            return "赤山"
        if "十梅庵" in keyword:
            return "十梅庵"
        if "千山" in keyword:
            return "千山"
        if "兴城海滨" in keyword:
            return "兴城海滨"
        if "龙湾海滨" in keyword:
            return "龙湾海滨"
        if "北普陀山" in keyword:
            return "北普陀山"
        if "清河" in keyword:
            return "清河"
        if "棒棰岛" in keyword:
            return "棒棰岛"
        if "巴松措" in keyword:
            return "巴松措"
        if "和顺" in keyword:
            return "和顺"
        if "腾冲" in keyword:
            return "腾冲"

        if "莫里" in keyword:
            return "莫里"
        if "秀山" in keyword:
            return "秀山"
        if "世界第一高桥" in keyword:
            return "世界第一高桥"
        if "鸡公山" in keyword:
            return "鸡公山"
        if "南街村" in keyword:
            return "南街村"
        if "濮阳绿色庄园" in keyword:
            return "濮阳绿色庄园"
        if "芒砀山" in keyword:
            return "芒砀山"
        if "包公祠" in keyword:
            return "包公祠"
        if "嵖岈山" in keyword:
            return "嵖岈山"
        if "白帝城" in keyword:
            return "白帝城"
        if "独秀峰" in keyword:
            return "独秀峰"
        if "八寨沟" in keyword:
            return "八寨沟"
        if "桂平西山" in keyword:
            return "桂平西山"
        if "容县" in keyword:
            return "容县"
        if "鹿峰山" in keyword:
            return "鹿峰山"
        if "龙母庙" in keyword:
            return "龙母庙"
        if "三平" in keyword:
            return "三平"
        if "福建土楼" in keyword:
            return "福建土楼"
        if "南普陀" in keyword:
            return "南普陀"
        if "三坊七巷" in keyword:
            return "三坊七巷"
        if "奥林匹克体育中心" in keyword:
            return "奥林匹克体育中心"
        if "铜山" in keyword:
            return "铜山"
        if "红梅公园" in keyword:
            return "红梅公园"

        if "金山湖" in keyword:
            return "金山湖"
        if "连岛" in keyword:
            return "连岛"
        if "淮海战役烈士" in keyword:
            return "淮海战役纪念塔"
        if "狼山" in keyword:
            return "狼山"
        if "太湖" in keyword:
            return "太湖"
        if "中华麋鹿园" in keyword:
            return "江苏大丰麋鹿国家级自然保护区"
        if "大庆铁人王" in keyword:
            return "铁人纪念馆"
        if "火山口" in keyword:
            return "火山口"
        if "向海" in keyword:
            return "向海"
        if "查干湖" in keyword:
            return "查干湖"
        if "龙湾" in keyword:
            return "龙湾"
        if "杨靖宇" in keyword:
            return "杨靖宇"
        if "伪满皇宫" in keyword:
            return "伪满皇宫"
        if "松花湖" in keyword:
            return "松花湖"
        if "六鼎山" in keyword:
            return "六鼎山"
        if "嵩山" in keyword:
            return "嵩山"
        if "张家界武陵源" in keyword:
            return "张家界武陵源"
        if "中山陵园" in keyword:
            return "钟山"
        if "明孝陵" in keyword:
            return "明孝陵"
        if "同里古镇" in keyword:
            return "同里古镇"
        if "花果山" in keyword:
            return "花果山"
        if "暖泉古镇" in keyword:
            return "暖泉古镇"
        if "庙香山" in keyword:
            return "庙香山滑雪场"
        if "幸福梅林" in keyword:
            return "幸福梅林"
        if "朝天门" in keyword:
            return "朝天门"
        if "朝天门" in keyword:
            return "朝天门"
        if "朝天门" in keyword:
            return "朝天门"
        if "朝天门" in keyword:
            return "朝天门"
        if "朝天门" in keyword:
            return "朝天门"
        if "朝天门" in keyword:
            return "朝天门"
        if "朝天门" in keyword:
            return "朝天门"
        if "朝天门" in keyword:
            return "朝天门"



        return keyword
