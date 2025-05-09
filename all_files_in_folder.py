import json
from pathlib import Path

from import_args import args
import global_constants as gc
import count_objects_from_video
import count_objects_from_image


def all_files_in_folder_(**kwargs) -> dict:
    file_counter = 0
    parameters = args.import_and_check(gc.CONFIG_PARAMETER_PATH, **kwargs)
    media_path = gc.DATA_FOLDER + parameters['file_folder']
    media_format = gc.IMAGE_FORMAT
    if parameters['input_type'] == 'video':
        media_format = gc.VIDEO_FORMAT
    count_by_file = {}
    total_count = {}
    for file_path in Path(media_path).rglob(f'*.{media_format}'):
        parameters['file_name'] = file_path.name
        if parameters['input_type'] == 'video':
            predicted_counts = count_objects_from_video.count_objects_(**parameters)
        elif parameters['input_type'] == 'image':
            predicted_counts = count_objects_from_image.count_objects_(**parameters)
        if parameters["verbose"]:
            print(f'file number {file_counter} ("{file_path.name}")')
            if not parameters['output_on_file']:
                print(f'\tpredicted_counts: {predicted_counts}')
                print('--------------------------------------------------')
        file_counter += 1
        count_by_file[file_path.name] = predicted_counts
        for class_name in predicted_counts:
            if class_name not in total_count:
                total_count[class_name] = 0
            total_count[class_name] += predicted_counts[class_name]
        # print(f'\tcount_by_file: {count_by_file}')
        # print(f'\ttotal_count: {total_count}')
    if parameters['output_on_file']:
        output_path = gc.OUTPUT_FOLDER + 'counting_result_' + parameters['file_folder']
        Path(output_path).mkdir(parents=True, exist_ok=True)
        with open(output_path + 'total_count.json', 'w') as json_file:
            json.dump(total_count, json_file)
        with open(output_path + 'count_by_file.json', 'w') as json_file:
            json.dump(count_by_file, json_file)
    return total_count


if __name__ == '__main__':
    object_count_dict = all_files_in_folder_()
