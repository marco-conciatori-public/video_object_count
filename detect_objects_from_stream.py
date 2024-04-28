import cv2
from ultralytics import YOLO

import utils
import global_constants
from import_args import args


def detect_objects_from_stream_(**kwargs):
    parameters = args.import_and_check(global_constants.CONFIG_PARAMETER_PATH, **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = global_constants.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])

    # Device (cpu or gpu)
    device = utils.get_available_device(verbose=parameters['verbose'])
    if parameters['verbose']:
        print(f'model: {parameters["model_name"]}')

    window_name = 'YOLO Detections'
    cv2.namedWindow(window_name)
    results = model(
        source=0,
        device=device,
        save=False,
        stream=True,
        show=False,
        stream_buffer=False,
        # vid_stride=2,
        project=global_constants.OUTPUT_FOLDER + 'stream/',
    )

    for result in results:
        key = cv2.waitKey(20)
        cv2.imshow(window_name, result.plot())
        if key == 27:  # exit on ESC
            break

    cv2.destroyWindow(window_name)


if __name__ == '__main__':
    detect_objects_from_stream_()
