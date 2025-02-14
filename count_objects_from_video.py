import cv2
from pathlib import Path
from ultralytics import YOLO
from ultralytics.solutions import object_counter

import utils
from import_args import args


def count_objects(**kwargs) -> dict:
    """
    Count objects in a video using a YOLO model.
    :param kwargs:
        video_path: str, path to video file.
        model_folder: str, path to folder containing YOLO model.
        model_name: str, name of YOLO model.
        selected_classes: list, list of class_ids of classes to count.
        region_type: str, type of region to count objects in, only accepts 'rectangle' and 'vertical_line'
        x_distance_from_center: int, distance from center of frame to define region.
        line_dist_thresh: int, distance from line to count object.
        save_annotated_video: bool, whether to save video with yolo detections.
        video_output_path: str, path to save video with object counts, only required if 'save_annotated_video' is True.
        verbose: bool, whether to print information.

    :return:
        dict mapping class_name to count of objects of that class in the video.
        Es. {'person': 1, 'bicycle': 1, 'car': 0, 'motorcycle': 0, 'bus': 0}

    """
    parameters = args.import_and_check(yaml_path='config.yaml', **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = parameters['model_folder'] + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])

    # Load video
    video_path = parameters['video_path']
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f'could not open file "{video_path}"'
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Classes
    # dict mapping class_id to class_name
    class_names_dict = model.names

    selected_class_names_dict = {}
    for class_id in parameters['selected_classes']:
        selected_class_names_dict[class_id] = class_names_dict[class_id]
    selected_class_names = [class_names_dict[class_id] for class_id in parameters['selected_classes']]

    if parameters['verbose']:
        print(f'video_path: {video_path}')
        print(f'width: {frame_width}, height: {frame_height}, fps: {fps}')
        print(f'selected_classes: {parameters["selected_classes"]}')
        # class names of interest
        print(f'selected_class_names: {selected_class_names}')

    if parameters['save_annotated_video']:
        video_output_path = parameters['video_output_path']
        # Video writer
        Path(video_output_path).parent.mkdir(parents=True, exist_ok=True)
        fourcc_code = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            video_output_path,
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
        classes_names=selected_class_names_dict,
        reg_pts=region_points,
        view_img=False,
        draw_tracks=False,
        line_dist_thresh=parameters['line_dist_thresh'],
    )
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    while cap.isOpened():
        if parameters['verbose']:
            if cap.get(cv2.CAP_PROP_POS_FRAMES) % 30 == 0:
                print(f'\tProgress: {round(cap.get(cv2.CAP_PROP_POS_FRAMES) / total_frames * 100, 1)} %')
        success, im0 = cap.read()
        if not success:
            if parameters['verbose']:
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
        if parameters['save_annotated_video']:
            video_writer.write(im0)

    # convert 'in' and 'out' counts to 'right_to_left' and 'left_to_right' counts
    object_counts = {}
    for class_id in parameters['selected_classes']:
        class_name = class_names_dict[class_id]
        object_counts[class_name] = 0
    for short_class_name in counter.class_wise_count:
        count_by_class = counter.class_wise_count[short_class_name]
        complete_class_name = None
        for selected_class_name in selected_class_names:
            if short_class_name in selected_class_name:
                complete_class_name = selected_class_name
                break
        assert complete_class_name is not None, \
            f'could not find complete class name from shortened class name "{short_class_name}".'
        object_counts[complete_class_name] = count_by_class['out'] + count_by_class['in']
    if parameters['verbose']:
        print(f'object_counts: {object_counts}')
    cap.release()
    cv2.destroyAllWindows()
    if parameters['save_annotated_video']:
        video_writer.release()
        if parameters['verbose']:
            print(f'Video saved at: "{video_output_path}"')
    return object_counts


if __name__ == '__main__':
    counts = count_objects()
