from spyderpro.data_requests.Internetdata.mobilekeyword import MobileKeyWord
from spyderpro.function.keyword_function.parent import Parent

from setting import *


class MobileKey(Parent):
    brand_dic = {'苹果': 1, 'QEDIRS': 2, '飞利浦': 3, '尼比鲁': 4, '语信': 5, '富可视': 6, '首云': 7, '小米': 8, '艾优尼': 9, '康柏': 10,
                 'dolphin': 11, '华为': 12, 'I-MOBILE': 13, 'CherryMobile': 14, '康尔': 15, '帷幄': 16, 'OTT': 17, '鲜米': 18,
                 '全志': 19, '基伍': 20, '魔百盒': 21, '乡米': 22, 'Bmobile': 23, '欧沃': 24, '中国移动': 25, 'LG': 26, '乐丰': 27,
                 '先锋': 28, '泰捷': 29, '海尔': 30, '海思': 31, '台电': 32, '格力': 33, 'RK2928SDK': 34, '金星数码': 35, '松下': 36,
                 '斐讯': 37, '宏碁': 38, '广信': 39, '锤子': 40, '安博盒子': 41, 'MTK': 42, 'maxtron': 43, '米蓝': 44, 'Innjoo': 45,
                 '优购': 46, '魅族': 47, '夏普': 48, 'GENERIC': 49, '虾米': 50, '索尼爱立信': 51, 'imobile': 52, '晨星': 53, '百立丰': 54,
                 '海派贵族': 55, 'Cherry Mobile': 56, 'MBX': 57, 'leimin': 58, 'QMOBILE': 59, '酷比魔方': 60, 'HTC': 61,
                 '爱派尔': 62, 'TCL': 63, '糯米': 64, 'imoo': 65, 'Blu': 66, 'vivo': 67, '安卓': 68, 'Advan': 69, '朵唯': 70,
                 '戴尔': 71, '美格': 72, 'ZUK': 73, '爱我': 74, '康佳': 75, '沃普丰': 76, '爱迪生': 77, 'ALPS': 78, 'L1E': 79,
                 '欧奇': 80, '诺基亚': 81, 'SOFTWINNERS': 82, '领歌': 83, 'E派': 84, '瑞芯微': 85, '小辣椒': 86, 'BIGNOX': 87,
                 'bigsamsung': 88, '宇飞来': 89, '闻泰': 90, '西门子': 91, '一加': 92, '天宏时代': 93, 'CMDC': 94, 'Ipro': 95,
                 '阿尔卡特': 96, 'LNV-LENOVO': 97, '英菲克': 98, '青橙': 99, '亿通': 100, '酷乐视': 101, 'ivvi': 102, '金立': 103,
                 '白米': 104, '传奇': 105, '昂达': 106, '邦华': 107, '至尊宝': 108, '普耐尔': 109, '摩托罗拉': 110, 'OPPO': 111,
                 'MICROMAX': 112, '卡美欧': 113, 'PANTECH': 114, '碟米': 115, 'Bluboo': 116, 'E人E本': 117, '安博': 118,
                 '小米盒子': 119, '奇酷': 120, 'Micromax': 121, '本为': 122, '创维': 123, '酷派': 124, '英特尔': 125, '夏新': 126,
                 '美图': 127, '世纪天元': 128, '唯比': 129, 'TCT': 130, '开博尔': 131, '领英': 132, 'Lovme': 133, '亿格瑞': 134,
                 '暴风': 135, 'Videocon': 136, '贝尔丰': 137, '拓百纳': 138, '智镁': 139, 'Karbonn': 140, '聆韵': 141, '迪优美特': 142,
                 '蓝魔': 143, '欧亚信': 144, 'MI': 145, 'SUGAR': 146, '德赛': 147, '锋影': 148, '天敏': 149, '亚马逊': 150, '诺迅': 151,
                 '大显': 152, 'QCOM': 153, '誉品': 154, '海信': 155, '京瓷': 156, 'MOOKA': 157, 'YUSU': 158, '小天才': 159,
                 '魔盒': 160, '华硕': 161, '忆典': 162, 'Intex': 163, '酷比': 164, '大麦盒子': 165, 'DATC': 166, '奥洛斯': 167,
                 '海美迪': 168, '西米': 169, '优酷': 170, 'ADVAN': 171, '谷歌': 172, 'BAIDU': 173, '联想': 174, '黑莓': 175,
                 '赛博宇华': 176, 'LGE': 177, '维图': 178, 'INTEX': 179, 'CHINA TELECOM': 180, 'Azumi': 181, 'Omate': 182,
                 '唯米': 183, 'Blackview': 184, '酷米': 185, '乐视': 186, 'DOOGEE': 187, '蓝博兴': 188, 'LETV': 189, 'PPTV': 190,
                 '中兴': 191, 'XOLO': 192, '德卡诺': 193, 'bignox': 194, '声丽': 195, 'QMobile': 196, '极米': 197, '读书郎': 198,
                 '波导': 199, '欧博信': 200, '索尼': 201, '诺亚信': 202, '酷珀': 203, '天语': 204, 'LAVA': 205, '宇龙酷派': 206,
                 '三星': 207, '优米': 208, '步步高': 209, '天猫': 210, '纽曼': 211, '努比亚': 212, '长虹': 213}
    system_dic = {'Android+5.1.1': 1, 'Android+4.4.4': 2, 'Android6.0.1': 3, 'Android+6.0': 4, 'Android7.1.2': 5,
                  'Android+4.2.1': 6, 'Android7.1.1': 7, 'Android+4.0.4': 8, 'Android+5.0.2': 9, 'Android+4.1.1': 10,
                  'Android+4.3': 11, 'Android+6.0.1': 12, 'Android+5.0': 13, 'Android5.1': 14, 'Android5.0.2': 15,
                  'Android+4.0.3': 16, 'Android+2.3.6': 17, 'Android+2.3.4': 18, 'Android+2.3.7': 19,
                  'Android+4.4.2': 20, 'Android7': 21, 'Android+4.1.2': 22, 'Android4.4.2': 23, 'Android+5.1': 24,
                  'Android6.0': 25, 'Android4.4.4': 26, 'Android+4.2.2': 27, 'Android+2.3.5': 28, 'Android8.0.0': 29,
                  'Android+7.0': 30, 'Android5.1.1': 31}
    operator_dic = {
        '中国移动': 1,
        '中国联通': 2,
        '中国电信': 3,
        '其他': 4
    }
    network_dic = {
        '5G': 0,
        'WIFI': 1,
        '4G': 2,
        '3G': 3,
        '2G': 4,
        '其他': 5,
    }

    def request_mobile_type_rate(self, year: int, startmonth: int = None, endmonth: int = None,platform=2):
        """
        获取某个时段的中国境内各手机机型的占有率

        :param year:
        :param startmonth:
        :param endmonth:
        :return:
         platform=2表示安卓手机，1表示苹果

        """
        mobile = MobileKeyWord()
        result = mobile.get_mobile_type_rate(year=year, startmonth=startmonth, endmonth=endmonth, platform=platform)
        return result

    def request_mobile_brand_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        """
        2014年开始,获取某时段中国境内各手机品牌占用率
        :param year:
        :param startmonth:
        :param endmonth:
        :return:
        platform=2表示安卓手机，1表示苹果
        """
        mobile = MobileKeyWord()
        result = mobile.get_mobile_brand_rate(year=year, startmonth=startmonth, endmonth=endmonth)

        return list(result)

    def request_mobile_system_rate(self, year: int, startmonth: int = None, endmonth: int = None,platform=2):
        """
        获取某时段中国境内各手机系统版本占用率
        :param year: 201x
        :param startmonth:1<=x<12
        :param endmonth:  x<=12
        :return:
        """
        mobile = MobileKeyWord()
        result = mobile.get_mobile_system_rate(year=year, startmonth=startmonth, endmonth=endmonth,platform=platform)
        return result

    def request_mobile_operator_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        """
        获取某时段中国境内各手机运营商占用率
        :param year:
        :param startmonth:
        :param endmonth:
        :return:
        """
        mobile = MobileKeyWord()
        result = mobile.get_mobile_operator_rate(year=year, startmonth=startmonth, endmonth=endmonth)

        return result

    def request_mobile_network_rate(self, year: int, startmonth: int = None, endmonth: int = None):
        """
        获取某时段中国境内各手机网络占用率
        :param year:
        :param startmonth:
        :param endmonth:
        :return:
        """
        mobile = MobileKeyWord()
        result = mobile.get_mobile_network_rate(year=year, startmonth=startmonth, endmonth=endmonth)

        return result
