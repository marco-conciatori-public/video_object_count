import cv2
from pathlib import Path
from ultralytics import YOLO
from ultralytics.solutions import object_counter

import utils
from import_args import args
import global_constants as gc


def count_objects_(**kwargs) -> dict:
    # IN means object moving right to left
    # OUT means object moving left to right

    parameters = args.import_and_check(gc.CONFIG_PARAMETER_PATH, **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = gc.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])

    # Load video
    video_path = gc.DATA_FOLDER + parameters['video_folder'] + parameters['video_name']
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f'could not open file "{video_path}"'
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Classes
    # dict mapping class_id to class_name
    class_names_dict = model.names
    # print(class_names_dict)
    # exit()
    if parameters['verbose']:
        print(f'video_path: {video_path}')
        print(f'width: {frame_width}, height: {frame_height}, fps: {fps}')
        print(f'selected_classes: {parameters["selected_classes"]}')
        # class names of interest
        selected_class_names = [class_names_dict[class_id] for class_id in parameters['selected_classes']]
        print(f'selected_class_names: {selected_class_names}')

    if parameters['save_video']:
        # Video writer
        output_path = (gc.OUTPUT_FOLDER + 'counting_result_' + parameters['video_folder'] + parameters['video_name'])
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fourcc_code = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            output_path,
            fourcc_code,
            fps,
            (frame_width, frame_height),
        )

    region_points = utils.define_region_points(
        region_type=parameters['region_type'],
        frame_width=frame_width,
        frame_height=frame_height,
        x_distance_from_center=parameters['x_distance_from_center'],
    )

    # Init Object Counter
    counter = object_counter.ObjectCounter()
    counter.set_args(
        classes_names=class_names_dict,
        reg_pts=region_points,
        view_img=False,
        draw_tracks=False,
        line_dist_thresh=parameters['line_dist_thresh'],
        # cls_txtdisplay_gap=parameters['cls_txtdisplay_gap'],
    )
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    while cap.isOpened():
        if parameters['verbose']:
            if cap.get(cv2.CAP_PROP_POS_FRAMES) % 30 == 0:
                print(f'\tProgress: {round(cap.get(cv2.CAP_PROP_POS_FRAMES) / total_frames * 100, 1)} %')
        success, im0 = cap.read()
        if not success:
            print(f'\tProgress: {round(cap.get(cv2.CAP_PROP_POS_FRAMES) / total_frames * 100, 1)} %')
            # print("Video frame is empty or video processing has been successfully completed.")
            break

        tracks = model.track(
            source=im0,
            persist=True,
            classes=parameters['selected_classes'],
            # tracker='bytetrack.yaml',
            verbose=False,
        )

        im0 = counter.start_counting(im0, tracks)
        if parameters['save_video']:
            video_writer.write(im0)

    # convert 'in' and 'out' counts to 'right_to_left' and 'left_to_right' counts
    object_counts = {}
    for class_name in parameters['selected_classes']:
        object_counts[class_names_dict[class_name]] = 0
    for class_name in counter.class_wise_count:
        count_by_class = counter.class_wise_count[class_name]
        object_counts[class_name] = count_by_class['OUT'] + count_by_class['IN']
    if parameters['verbose']:
        print(f'object_counts: {object_counts}')
    cap.release()
    cv2.destroyAllWindows()
    if parameters['save_video']:
        video_writer.release()
        if parameters['verbose']:
            print(f'Video saved at: "{output_path}"')
    return object_counts


if __name__ == '__main__':
    counts = count_objects_()
