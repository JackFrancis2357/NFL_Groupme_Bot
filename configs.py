import os
import yaml

import logging
logger = logging.getLogger(__name__)
# Read in base configs
with open('./config/base.yaml', 'r') as file:
    try:
        Config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)

    try:
        Config["ENVIRONMENT"] = os.environ["ENVIRONMENT"]
    except KeyError:
        Config["ENVIRONMENT"] = 'local_dev'
        logger.info("os environment variable not set")

with open('config/team_mapping_jack.yaml', 'r') as file:
    try:
        team_mapping_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)
