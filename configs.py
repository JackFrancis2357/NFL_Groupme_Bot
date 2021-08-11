import yaml

# Read in base configs
with open('/Users/jackfrancis/Documents/GitHub/NFL_Groupme_Bot/config/base.yaml', 'r') as file:
    try:
        base_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)