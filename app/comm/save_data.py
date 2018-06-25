# -*-coding:utf-8 -*-
import os
import sqlite3
import logging


class SqliteBase:
    """
    数据库操作
    """
    def __init__(self, dbfile):
        # 初始化
        self.dbfile = dbfile    # 数据库名
        self.make_dir()     # 创建文件夹
        self.conn = sqlite3.connect(dbfile)
        self.c = self.conn.cursor()
        self.table_name = 'spider'
        self.create_table()

    def batch_insert(self, data: list):
        """
        批处理
        """
        try:
            self.c.executemany(
                '''INSERT INTO {table_name} (keyword, url, content) VALUES (?, ?, ?)'''.format(table_name=self.table_name), data)
            logging.info('batch insert {} into {} {} items'.format(data, self.table_name, len(data)))
            self.conn.commit()
        except:
            self.conn.rollback()
            logging.error("insert fail!")

    def insert(self, keyword, url, content):
        """
        插入单条数据
        如果数据格式不符合要求则不会执行插入操作
        :param data:
        :return:
        """
        data = (keyword, url, content)
        try:
            self.c.execute(
                '''INSERT INTO {table_name} (keyword, url, content) VALUES (?, ?, ?)'''.
                    format(table_name=self.table_name), data)
            logging.info('insert {} into {}'.format(url, self.table_name))
            self.conn.commit()
        except sqlite3.OperationalError:
            self.conn.rollback()
        logging.info('insert {} failed'.format(url))

    def make_dir(self):
        """
        创建文件夹
        """
        abspath = os.path.abspath(self.dbfile)
        pardir = abspath.rsplit(os.sep, 1)[0]
        if not os.path.exists(pardir):
            logging.debug('{} not exists'.format(pardir))
            os.makedirs(pardir, exist_ok=True)
            logging.debug('make dir {}'.format(pardir))
        else:
            logging.debug('{} exists'.format(pardir))

    def create_table(self):
        """
        创建数据表
        """
        result = self.c.execute('''SELECT name FROM sqlite_master WHERE name=? AND type="table"''', (self.table_name, ))
        if result.fetchall():
            logging.debug('table {} exists')
        else:
            logging.debug('table {} not exists'.format(self.table_name))
            self.c.execute(
                '''CREATE TABLE IF NOT EXISTS {table_name} (id INT PRIMARY KEY, keyword TEXT, url TEXT, content TEXT)'''.format
                (table_name=self.table_name))
            logging.info('create table {}'.format(self.table_name))



