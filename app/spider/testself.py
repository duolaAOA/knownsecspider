# -*-coding:utf-8 -*-

from app.spider import spider
from app.comm import save_data
from app import args


class TestSelf(spider.Spider):
    """
    程序自测
    """

    def __init__(self):
        print('程序自测')
        db = save_data.SqliteBase(dbfile='test.db')
        super(TestSelf, self).__init__(db=db)


TestSelf()
