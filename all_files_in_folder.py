import json
from pathlib import Path

import count_objects
from import_args import args
import global_constants as gc
import count_objects_from_images


def all_files_in_folder_(**kwargs) -> dict:
    file_counter = 0
    parameters = args.import_and_check(gc.CONFIG_PARAMETER_PATH, **kwargs)
    local_verbose = parameters['verbose']
    parameters['verbose'] = False
    media_path = gc.DATA_FOLDER + parameters['media_folder']
    format = gc.IMAGE_FORMAT
    if parameters['input_type'] == 'video':
        format = gc.VIDEO_FORMAT
    total_count = {}
    for file_path in Path(media_path).rglob(f'*.{format}'):
        parameters['media_name'] = file_path.name
        if parameters['input_type'] == 'video':
            predicted_counts = count_objects.count_objects_(**parameters)
        elif parameters['input_type'] == 'image':
            predicted_counts = count_objects_from_images.count_objects_(**parameters)
        if local_verbose:
            print(f'file number {file_counter} ("{file_path.name}")')
            if not parameters['output_on_file']:
                print(f'\tpredicted_counts: {predicted_counts}')
                print('--------------------------------------------------')
        file_counter += 1
        total_count[file_path.name] = predicted_counts

    if parameters['output_on_file']:
        output_path = gc.OUTPUT_FOLDER + 'counting_result_' + parameters['media_folder']
        Path(output_path).mkdir(parents=True, exist_ok=True)
        with open(output_path + 'Total_counts.json', 'w') as json_file:
            json.dump(total_count, json_file)
    return total_count


if __name__ == '__main__':
    object_count_dict = all_files_in_folder_()
