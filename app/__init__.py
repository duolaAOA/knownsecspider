# -*-coding:utf-8 -*-

import os
import sys
import logging
from app.commands import parse


def logging_config(logfile, level):
    """
    配置日志
    :param logfile:
    :return:
    """
    loglevel = {1: logging.DEBUG,
                2: logging.INFO,
                3: logging.WARNING,
                4: logging.ERROR,
                5: logging.CRITICAL}

    abspath = os.path.abspath(logfile)
    pardir = abspath.rsplit(os.sep, 1)[0]
    if not os.path.exists(pardir):
        os.makedirs(pardir, exist_ok=True)
    logging.basicConfig(filename=abspath, level=loglevel.get(level, logging.INFO), filemode='w',
                        format='%(asctime)s %(levelname)s %(threadName)s "%(module)s.%(filename)s.%(funcName)s:'
                               '%(lineno)d":%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('config logging finished.')
    logging.getLogger().setLevel(loglevel.get(level, logging.INFO))
    print('爬虫日志保存在 {} 中'.format(logfile))


parser = parse.Parse()
args = parser.get_args()
logging_config(args.logfile, args.loglevel)
logging.debug('Argument input: {}'.format(sys.argv[1:]))
logging.debug('url={} logfile={} loglevel={} testself={} thread={} dbfile={} keyword={} depth={}'.format(args.url,
                                                                                                         args.logfile,
                                                                                                         args.loglevel,
                                                                                                         args.testself,
                                                                                                         args.thread,
                                                                                                         args.dbfile,
                                                                                                         args.keyword,
                                                                                                         args.depth))
