# -*-coding:utf-8 -*-

import logging
import threading
from queue import Queue


class ThreadPool(object):
    """
    线程池
    """

    def __init__(self, num, fn, size=2000):
        """
        :param num: 任务数
        :param size: 队列大小
        """
        self.num = num
        self.fn = fn
        self.task_queue = Queue(size)
        self.pool = []
        self.__create_thread_pool()
        self._task_num = 0
        self._task_over = 0
        self.lock = threading.Lock()

        logging.debug("The thread pool size： {}".format(self.num))

    def __create_thread_pool(self):
        # 创建线程池
        self.pool.extend([WorkManage(self.task_queue, self.fn, self.task_finish_callback) for _ in range(self.num)])

    def sumbit(self, task):
        """
        添加任务队列
        :param task: url 与 level
        :return:
        """
        self.lock.acquire()
        self._task_num += 1
        logging.debug('{}:  new task {}'.format(self._task_num, task))
        self.lock.release()
        self.task_queue.put(task)

    def wait(self):
        logging.debug("Waiting task thread!")
        # 等待线程完成
        while len(self.pool):
            t = self.pool.pop()
            # 等待线程结束
            if t.is_alive():
                t.join()

    def is_over(self):
        """
        判断任务完成与否
        :return:
        """
        f = self._task_num > 0 and self._task_num == self._task_over
        if f:
            logging.debug('The task queue is over!!')
        return f

    def task_finish_callback(self):
        """
        线程每完成一个任务就回调该函数
        :return:
        """
        self.lock.acquire()
        self._task_over += 1
        logging.debug('finish No.{} task'.format(self._task_over))
        self.lock.release()

    def progress(self) -> tuple:
        """
        进度
        """
        return self._task_over, self._task_num


class WorkManage(threading.Thread):
    """
    工作线程
    """
    def __init__(self, task_queue, fn, callback=None):
        self.fn = fn
        self.callback = callback
        threading.Thread.__init__(self)
        self.run_flag = True
        self.daemon = True
        self.task_queue = task_queue
        self.start()
        logging.debug('New worker {} create'.format(self.name))

    def run(self):
        logging.debug('worker thread {} start main loop'.format(self.name))
        while self.run_flag:
            # 从工作队列中获取一个任务
            task = self.task_queue.get()
            logging.debug('worker thread {} get task {}'.format(self.name, task))
            self.fn(task)
            if self.callback is not None:
                self.callback()
            logging.info('worker thread {} finish task {}'.format(self.name, task))
        logging.debug('worker thread {} exit main loop'.format(self.name))

    def stop(self):
        """
        退出
        :return:
        """
        self.run_flag = False
        logging.info('worker thread run_flag={}', self.run_flag)