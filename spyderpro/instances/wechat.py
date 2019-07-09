class WechatPublic_Info:
    """
    name:公众号
    pid:微信号
    articles:文章列表
    """
    __slots__ = ['page', 'name', 'pid', 'articles']

    def __init__(self, page, name, public_pid, articlelist):
        self.page = page
        self.name = name
        self.pid = public_pid
        self.articles = articlelist


class WechatSituation:
    """
    公众号的详细数据：平均阅读量，最高阅读量，平均点赞，最高点赞等

    "头条平均阅读量": average_read,
     "最高阅读量": hight_read,
     "头条平均点赞数": average_like,

     "最高点赞数": hight_like,"发文数":count_article,
     "fans_num":粉丝数，
     "历史数据":data
    """
    __slots__ = ['average_read', 'hight_read', 'average_like', 'hight_like', 'count_article', 'fans_num', 'data']

    def __init__(self, average_read, hight_read, average_like, hight_like, count_article, fans_num, data):
        self.average_read = average_read
        self.hight_read = hight_read
        self.average_like = average_like
        self.hight_like = hight_like
        self.count_article = count_article
        self.fans_num = fans_num
        self.data = data


class ArticleInfo:
    """
    文章相关历史数据，比如阅读量等
    """
    __slots__ = ['read_num_total', 'like_num_total', 'date']

    def __init__(self, read_num_total, like_num_total, date):
        self.read_num_total = read_num_total
        self.like_num_total = like_num_total
        self.date = date


class ArticleKeyWord:
    """获取关键词列表
    "keyword":关键词,
    "value":热度
    """

    __slots__ = ['keyword', 'value']

    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value
