import copy
import argparse


def update_config(default_parameter_dict: dict) -> dict:
    parser = argparse.ArgumentParser()
    for key in default_parameter_dict:
        value = default_parameter_dict[key]
        if isinstance(value, list):
            parser.add_argument(f'--{key}', dest=key, type=type(value), nargs='*')
        # elif isinstance(value, dict):
        #     continue
        else:
            parser.add_argument(f'--{key}', dest=key, type=type(value))

    parser.add_argument('-f', required=False, type=str)
    updated_parameter_dict = copy.deepcopy(default_parameter_dict)
    args = parser.parse_args()
    args_dict = vars(args)
    for key in args_dict:
        if args_dict[key] is not None:
            updated_parameter_dict[key] = args_dict[key]

    return updated_parameter_dict
