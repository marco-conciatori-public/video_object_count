import os

from import_args import from_yaml, from_command_line, from_function_arguments


def import_and_check(yaml_path, **kwargs) -> dict:
    max_iterations = 5
    level_up = 0
    parameter_dict = None
    while parameter_dict is None:
        try:
            parameter_dict = from_yaml.read_config(yaml_path)
        except FileNotFoundError:
            if level_up == max_iterations:
                raise
            level_up += 1
            os.chdir("..")

    # command line arguments have priority over yaml arguments
    parameter_dict = from_command_line.update_config(parameter_dict)
    # function arguments have priority over yaml and command line arguments
    parameter_dict = from_function_arguments.update_config(parameter_dict, **kwargs)
    if parameter_dict['save_annotated_video']:
        assert parameter_dict['video_output_path'] is not None, \
            'if "save_annotated_video" is True, "video_output_path" must be provided.'

    return parameter_dict
