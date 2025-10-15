import logging
import datetime

def logging_setup(logger_name, log_level=logging.ERROR, filename='meshtool.log'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s [%(process)d] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    log_level_str  = logging.getLevelName(log_level)
    logger.debug(f"Initialized console log handler at severity '{log_level_str}'")

    return logger

def rightnow():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
