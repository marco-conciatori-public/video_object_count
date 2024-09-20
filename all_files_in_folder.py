import json
from pathlib import Path

import count_objects
from import_args import args
import global_constants as gc


def all_files_in_folder_(**kwargs) -> dict:
    file_counter = 0
    parameters = args.import_and_check(gc.CONFIG_PARAMETER_PATH, **kwargs)
    local_verbose = parameters['verbose']
    parameters['verbose'] = False
    video_path = gc.DATA_FOLDER + parameters['video_folder']
    total_count = {}
    for file_path in Path(video_path).rglob(f'*.{gc.VIDEO_FORMAT}'):
        parameters['video_name'] = file_path.name
        predicted_counts = count_objects.count_objects_(**parameters)
        if local_verbose:
            if not parameters['output_on_file']:
                print(f'file number {file_counter} ("{file_path.name}")')
                print(f'\tpredicted_counts: {predicted_counts}')
                print('--------------------------------------------------')
        file_counter += 1
        total_count[file_path.name] = predicted_counts

    if parameters['output_on_file']:
        output_path = gc.OUTPUT_FOLDER + 'counting_result_' + parameters['video_folder']
        Path(output_path).mkdir(parents=True, exist_ok=True)
        with open(output_path + 'Total_counts.json', 'w') as json_file:
            json.dump(total_count, json_file)
    return total_count


if __name__ == '__main__':
    object_count_dict = all_files_in_folder_()
