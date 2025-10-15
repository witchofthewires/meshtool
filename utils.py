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
    logger_initialize_msg(logger, "BASE", log_level)

    return logger

def logger_initialize_msg(logger, name, log_level):
    print("HI THERE", log_level, type(log_level))
    log_level_str  = logging.getLevelName(log_level) if type(log_level) == int else log_level
    logger.debug(f"Initialized [{name}] log handler at severity '{log_level_str}'")

def rightnow():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
