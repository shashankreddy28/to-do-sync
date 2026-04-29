import logging
import logging.config as conf

def setup_logging(name):

    conf.fileConfig('logging.conf')
    logger = logging.getLogger(name)
    
    return logger