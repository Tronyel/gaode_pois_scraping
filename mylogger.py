
'''
该日志类可以把不同级别的日志输出到不同的日志文件中
'''

import os
import sys
import time
import logging
import inspect

handlers = {logging.NOTSET: "./logs/poilog-notset.log",
            logging.DEBUG: "./logs/poilog-debug.log",
            logging.INFO: "./logs/poilog-info.log",
            logging.WARNING: "./logs/poilog-warning.log",
            logging.ERROR: "./logs/poilog-error.log",
            logging.CRITICAL: "./logs/poilog-critical.log"}


def createHandlers():
    logLevels = handlers.keys()
    for level in logLevels:
        path = os.path.abspath(handlers[level])
        if not os.path.exists(path):
            f = open(path, 'a')
            f.close()
        handlers[level] = logging.FileHandler(path)


# 加载模块时创建全局变量
createHandlers()


class LogObject(object):
    def printfNow(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __init__(self, level=logging.NOTSET):
        self.__loggers = {}
        logLevels = handlers.keys()
        for level in logLevels:
            logger = logging.getLogger(str(level))
            # 如果不指定level，获得的handler似乎是同一个handler?
            logger.addHandler(handlers[level])
            logger.setLevel(level)
            self.__loggers.update({level: logger})

    def getLogMessage(self, level, message):
        frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[
            2]
        '''日志格式：[时间] [类型] [记录代码] 信息'''
        return "[%s] [%s] [%s - %s - %s] %s" % (self.printfNow(), level, filename, lineNo, functionName, message)

    def info(self, message):
        message = self.getLogMessage("info", message)
        self.__loggers[logging.INFO].info(message)

    def error(self, message):
        message = self.getLogMessage("error", message)
        self.__loggers[logging.ERROR].error(message)

    def warning(self, message):
        message = self.getLogMessage("warning", message)
        self.__loggers[logging.WARNING].warning(message)

    def debug(self, message):
        message = self.getLogMessage("debug", message)
        self.__loggers[logging.DEBUG].debug(message)

    def critical(self, message):
        message = self.getLogMessage("critical", message)
        self.__loggers[logging.CRITICAL].critical(message)


if __name__ == "__main__":
    logger = LogObject()
    logger.debug("debug")
    # logger = LogObject()
    logger.info("info")
    # logger = LogObject()
    logger.warning("warning")
    # logger = LogObject()
    logger.error("error")
    # logger = LogObject()
    logger.critical("critical")
