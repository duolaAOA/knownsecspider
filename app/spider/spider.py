# -*-coding:utf-8 -*-

import logging
import threading

from requests_html import HTMLSession, HTMLResponse

from app import args
from app.spider.threadpool import ThreadPool


class Spider(object):
    """
    sina.com.cn Spider
    """

    def __init__(self, db):
        self.url = args.url
        self.depth = args.depth
        self.keyword = args.keyword
        self.db = db
        self.analysed_url = {}
        self.url_visiting = {}
        self.url_keyword = {}
        self.lock = threading.Lock()
        self.rlock = threading.RLock()
        self._session = HTMLSession()
        self._thread_pool = ThreadPool(args.thread, fn=self.analyse)
        self._thread_pool.sumbit((args.url, 0))
        logging.debug('start Spider url={} keyword={} depth={}'.format(self.url, self.keyword, self.keyword, self.depth))

    def analyse(self, task):
        """
        get html response
        :param task:   (url, level)
        :return:
        """
        url, level = task
        if not self.is_visited(url, level):
            logging.debug('get task {} which has been visited. Please check mutex use right or not'.format(task))
            return
        try:
            response = self._session.get(url)
            logging.debug('GET {}'.format(url))

        except Exception as e:
            logging.error("requests error %s" % e)
        else:
            content_type = self.content_type(response)
            if '/html' in content_type:
                has_key = self.has_keyword(response)
                if has_key:
                    try:
                        self.lock.acquire()
                        self.url_keyword[url] = level
                        logging.info('url {} with keyword={}'.format(url, self.keyword))
                    except Exception as e:
                        logging.error(e)
                    finally:
                        self.lock.release()
                links = self.extract_link(response)
                self.submit_links2queue(links, level + 1)
            else:
                logging.warning('url {} Content-Type={} not supported'.format(url, content_type))
        finally:
            self.add_url2analysed(url, level)

    def is_visited(self, url, level):
        # 判断urk是否抓取过
        flag = False
        try:
            self.lock.acquire()
            if url not in self.url_visiting and url not in self.analysed_url:
                self.url_visiting[url] = level
                flag = True
        except Exception as e:
            pass
        finally:
            self.lock.release()
        return flag

    def content_type(self, r: HTMLResponse) -> str:
        # 网页类型
        return r.headers.get('Content-Type', '')

    def has_keyword(self, r):
        # 是否含关键词
        text = ""
        try:
            text = r.html.text
        except Exception as e:
            logging.error(e)

        if self.keyword in text:
            logging.debug('{} in url {}'.format(self.keyword, r.url))
            return True
        else:
            logging.debug('{} not in url {}'.format(self.keyword, r.url))
            return False

    def submit_links2queue(self, links, level):
        """
        向队列中添加新任务
        :param links: 本次爬取页面中的所有链接
        :param level: 本次页面所处深度
        :return:
        """
        if level > self.depth:
            logging.debug('links {} beyond max_depth={}'.format(links, level))
            return
        for link in links:
            if link.startswith(self.url):  # 只搜索同一个域下的内容
                if link not in self.url_visiting and link not in self.analysed_url:
                    # 提交到队列中
                    self._thread_pool.sumbit((link, level))

    def add_url2analysed(self, url, level):
        """
        将 url 加入到已经分析的 url 字典中
        :param url:
        :return:
        """
        try:
            self.lock.acquire()
            # 先加到 analysed_url 再从 url_visiting 删除，防止重复爬取
            self.analysed_url[url] = level
            del self.url_visiting[url]
        except Exception as e:
            logging.error(e)
        finally:
            self.lock.release()
            logging.info('finish url {} in level {}'.format(url, level))

    def extract_link(self, r: HTMLResponse):
        """
        提取 html 中的链接，需要分析相对链接和绝对链接
        :return:
        """
        relative_links = r.html.links - r.html.absolute_links
        all_links = r.html.absolute_links | self.relative2absolute(relative_links, r.html.base_url)
        logging.info('links {} in url {}'.format(all_links, r.url))
        return all_links

    def relative2absolute(self, relative_links, base_url):
        """
        将相对链接拼接成绝对链接
        :param relative_links:
        :param base_url:
        :return:
        """
        return {base_url + x for x in relative_links}

    def has_finished(self):
        """
        查询当前爬虫任务是否已经完成
        :return:
        """
        f = self._thread_pool.is_over()
        if not f:
            self.persist2db()
            return f
        return f

    def persist2db(self):
        """
        将 url 持久化到 sqlite db
        :return:
        """
        with self.rlock:
            self.rlock.acquire()
            t = self.url_keyword
            self.url_keyword = {}

        for url in t:
            content = self._session.get(url).content.decode("utf8", "ignore")
            self.db.insert(self.keyword, url, content)

    def progress(self) -> tuple:
        """
        反馈进度消息
        :return:
        """
        return self._thread_pool.progress()

    def add_url_with_keyword(self, url, level):
        """
        发现页面包含关键字的 url
        :param url:
        :param level:
        :return:
        """
        with self.rlock:
            self.url_keyword[url] = level
        logging.info('url {} with keyword={}'.format(url, self.keyword))