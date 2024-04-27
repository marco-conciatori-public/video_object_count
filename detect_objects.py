from ultralytics import YOLO

import utils
import global_constants
from import_args import args


def detect_objects_(**kwargs):
    parameters = args.import_and_check(global_constants.CONFIG_PARAMETER_PATH, **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = global_constants.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])

    # Load video
    video_path = global_constants.DATA_FOLDER + parameters['video_folder'] + 'argo_1.mp4'

    # Device (cpu or gpu)
    device = utils.get_available_device(verbose=parameters['verbose'])

    if parameters['verbose']:
        print(f'video_path: {video_path}')
        print(f'device: {device}')
        print(f'model: {parameters["model_name"]}')

    results = model(
        source=video_path,
        device=device,
        save=parameters['save_video'],
        # show=True,
        project=global_constants.OUTPUT_FOLDER + 'detections/',
    )


if __name__ == '__main__':
    detect_objects_()
