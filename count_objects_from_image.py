from pathlib import Path
from ultralytics import YOLO

import global_constants
from import_args import args


def count_objects_(**kwargs) -> dict:

    parameters = args.import_and_check(global_constants.CONFIG_PARAMETER_PATH, **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = global_constants.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])
    # parameters['verbose'] = True
    # Load image
    image_path = global_constants.DATA_FOLDER + parameters['file_folder'] + parameters['file_name']

    # Classes
    # dict mapping class_id to class_name
    class_names_dict = model.names
    # print(class_names_dict)
    if parameters['verbose']:
        print(f'image_path: {image_path}')
        print(f'selected_classes: {parameters["selected_classes"]}')
        # class names of interest
        selected_class_names = [class_names_dict[class_id] for class_id in parameters['selected_classes']]
        print(f'selected_class_names: {selected_class_names}')

    if parameters['save_media']:
        output_path = (global_constants.OUTPUT_FOLDER + 'counting_result_' +
                       parameters['file_folder'] + parameters['file_name'])
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    results = model(image_path, classes=parameters['selected_classes'])

    object_counts = {}
    for class_id in parameters['selected_classes']:
        object_counts[class_names_dict[class_id]] = 0
    for class_id in results[0].boxes.cls:
        class_id = int(class_id.item())
        class_name = class_names_dict[class_id]
        object_counts[class_name] += 1
    if parameters['verbose']:
        print(f'object_counts: {object_counts}')
    return object_counts


if __name__ == '__main__':
    counts = count_objects_()
