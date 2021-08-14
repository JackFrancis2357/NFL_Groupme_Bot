import yaml

# Read in base configs
with open('./config/base.yaml', 'r') as file:
    try:
        base_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)

with open('./config/team_mapping.yaml', 'r') as file:
    try:
        team_mapping_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)