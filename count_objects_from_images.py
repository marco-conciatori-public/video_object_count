from pathlib import Path
from ultralytics import YOLO

import global_constants
from import_args import args


def count_objects_(**kwargs) -> dict:

    parameters = args.import_and_check(global_constants.CONFIG_PARAMETER_PATH, **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = global_constants.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path)
    parameters['verbose'] = True
    # Load image
    image_path = global_constants.DATA_FOLDER + parameters['media_folder'] + parameters['media_name']

    # Classes
    # dict mapping class_id to class_name
    class_names_dict = model.names
    print(class_names_dict)
    # exit()
    if parameters['verbose']:
        print(f'image_path: {image_path}')
        print(f'selected_classes: {parameters["selected_classes"]}')
        # class names of interest
        selected_class_names = [class_names_dict[class_id] for class_id in parameters['selected_classes']]
        print(f'selected_class_names: {selected_class_names}')

    if parameters['save_media']:
        # Image writer
        output_path = (global_constants.OUTPUT_FOLDER + 'counting_result_' +
                       parameters['media_folder'] + parameters['media_name'])
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    results = model(image_path)
    print('_____________________________________________________________')
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        if parameters['verbose']:
            print(f'boxes: {boxes}')

    print('_____________________________________________________________')

    # if parameters['save_media']:
    #     result.save(filename="result.jpg")  # save to disk
    #     if parameters['verbose']:
    #         print(f'Image saved at: "{output_path}"')
    #
    # object_counts = {
    #     'class_wise_count': {class_name: {'right_to_left': 0, 'left_to_right': 0} for class_name in counter.class_wise_count},
    # }
    # for class_name in counter.class_wise_count:
    #     object_counts['class_wise_count'][class_name] = counter.class_wise_count[class_name]
    # if parameters['verbose']:
    #     print(f'class_wise_count: {counter.class_wise_count}')

    # return object_counts


if __name__ == '__main__':
    counts = count_objects_()
