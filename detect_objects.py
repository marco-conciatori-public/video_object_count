from ultralytics import YOLO

import utils
from import_args import args
import global_constants as gc


def detect_objects_(**kwargs):
    parameters = args.import_and_check(gc.CONFIG_PARAMETER_PATH, **kwargs)
    video_name = 'argo_1.mp4'

    # Download model in "models" folder if not present, and load it
    model_path = gc.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])

    # Load video
    video_path = gc.DATA_FOLDER + parameters['video_folder'] + video_name

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
        project=gc.OUTPUT_FOLDER + 'detections/',
    )


if __name__ == '__main__':
    detect_objects_()
