# -*-coding:utf-8 -*-

import time
import logging

from app import args
from app.spider import spider
from app.comm import save_data
from app.spider import testself


def main():
    if args.testself:
        crawl = testself.TestSelf()
    else:
        db = save_data.SqliteBase(args.dbfile)
        crawl = spider.Spider(db=db)
    print('开始爬取 {} ......\n'.format(args.url))
    sleep_time = args.flush
    # 定时刷新
    while not crawl.has_finished():
        print(end='\n\r')
        finish, total = crawl.progress()
        time.sleep(sleep_time)
        print('已完成：{} 已发现：{}'.format(finish, total), end='', flush=True)

    finish, total = crawl.progress()
    print('\r已完成：{} 已发现：{}'.format(finish, total), end='', flush=True)
    print('\nfinish')
    logging.debug('spider exit')


if __name__ == '__main__':
    main()