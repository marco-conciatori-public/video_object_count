import yaml


def read_config(yaml_path) -> dict:
    with open(yaml_path) as f:
        parameter_dict = yaml.safe_load(f)

    return parameter_dict
