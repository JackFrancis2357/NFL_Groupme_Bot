import yaml

# Read in base configs
with open('./config/base.yaml', 'r') as file:
    try:
        base_configs = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(e)