# -*-coding:utf-8 -*-

import argparse


class Parse:
    """
    解析命令行参数
    """

    def __init__(self):
        # 初始化
        self.args = None
        self._parse()

    def _parse(self):
        """
        解析参数
        :return:
        """
        parser = argparse.ArgumentParser(description='Sina.com.cn Crawl Spider')
        parser.add_argument('-u', dest='url', default='http://www.sina.com.cn/', metavar='sina.com.cn',
                            type=str, help='输入待爬取url')
        parser.add_argument('-d', dest='depth', default=3, metavar='5', type=int, help='爬取最大深度')
        parser.add_argument('-f', dest='logfile', default='./log/spider.log', metavar='log.txt', type=str,
                            help='日志文件')
        parser.add_argument('-l', dest='loglevel', default=2, metavar='[1,5]', type=int, help='日志等级')
        parser.add_argument('--testself', dest='testself', action='store_const', const=True, default=False, help='自测')
        parser.add_argument('-thread', dest='thread', default=10, metavar='10', type=int, help='线程池大小')
        parser.add_argument('-dbfile', dest='dbfile', metavar='./spider.db', default='spider.db', type=str,
                            help='sqlite3存储')
        parser.add_argument('--key', dest='keyword', default='世界杯', metavar='keyword', type=str, help='搜索关键字')
        parser.add_argument('-flush', dest='flush', default=1, metavar='10', type=int, help='间隔N秒刷新')
        parser.add_argument('--version', action='version', version='1.0')
        self.args = parser.parse_args()

    def get_args(self):
        return self.args

