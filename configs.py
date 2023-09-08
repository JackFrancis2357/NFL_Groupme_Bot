import logging
import os

import yaml

logger = logging.getLogger(__name__)
# Read in base configs
with open("./config/base.yaml", "r") as file:
    try:
        base_config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.info(e)

with open("config/team_mapping.yaml", "r") as file:
    try:
        team_mapping_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.info(e)

with open("config/user_params.yaml", "r") as file:
    try:
        user_params_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.info(e)

with open("config/user_teams.yaml", "r") as file:
    try:
        user_teams_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.info(e)

try:
    base_config["ENVIRONMENT"] = os.environ["ENVIRONMENT"]
except KeyError:
    base_config["ENVIRONMENT"] = "local_dev"
    logger.info("os environment variable not set")

Config = {**base_config, **team_mapping_configs, **user_params_configs, **user_teams_configs}
