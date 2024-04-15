import copy
import warnings


def update_config(default_parameter_dict: dict, **kwargs) -> dict:
    updated_parameter_dict = copy.deepcopy(default_parameter_dict)
    for key in kwargs:
        try:
            updated_parameter_dict[key] = kwargs[key]
        except KeyError:
            warnings.warn(f'Parameter "{key}" not found in the config file. Only parameters in the config file are '
                          f'valid arguments. The parameter "{key}" will be ignored.')

    return updated_parameter_dict
