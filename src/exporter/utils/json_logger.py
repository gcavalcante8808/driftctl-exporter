import json_logging
import logging
import sys


json_logging.init_non_web(enable_json=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
