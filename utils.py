import logging
import os

logs = set()
def init_log(name, level=logging.INFO):
    if (name, level) in logs:
        return
    logs.add((name, level))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    if 'SLURM_PROCID' in os.environ:
        rank = int(os.environ['SLURM_PROCID'])
        logger.addFilter(lambda record: rank == 0)
    else:
        rank = 0
    # format_str = '%(asctime)s-rk{}-%(filename)s#%(lineno)d: %(message)s'.format(rank)
    format_str = '%(asctime)s: \n%(message)s'
    formatter = logging.Formatter(format_str)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def trans_float(location):
    if isinstance(location, list):
        for idx, pos in enumerate(location):
            if type(pos) == float:
                continue
            if (pos == None) | (pos == 'N/A') | (pos == 'None'):
                pos = 0.0
            else:
                try:
                    pos = float(pos)
                except:
                    return None
            
            location[idx] = pos
    else:
        if (location == None) | (location == 'N/A') | (location == 'None'):
            location = 0.0
        location = float(location)

    return location
