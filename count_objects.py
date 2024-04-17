from ultralytics import YOLO
from ultralytics.solutions import object_counter
import cv2

import global_constants
import utils
from import_args import args


def count_objects_(**kwargs) -> dict:
    parameters = args.import_and_check(global_constants.CONFIG_PARAMETER_PATH, **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = global_constants.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])

    # Load video
    video_path = global_constants.DATA_FOLDER + parameters['video_name']

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f'could not open file "{video_path}"'
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Classes
    # dict mapping class_id to class_name
    class_names_dict = model.names
    # class names of interest
    class_names = [class_names_dict[class_id] for class_id in parameters['selected_classes']]
    if parameters['verbose']:
        print(f'video_path: {video_path}')
        print(f'width: {frame_width}, height: {frame_height}, fps: {fps}')
        print(f'selected_classes: {parameters["selected_classes"]}')
        print(f'class_names: {class_names}')

    if parameters['save_video']:
        # Video writer
        output_path = global_constants.OUTPUT_FOLDER + 'counting_result_' + parameters['video_name']
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
        view_img=False,
        reg_pts=region_points,
        classes_names=class_names_dict,
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
    object_counts = {
        'right_to_left': counter.in_counts,
        'left_to_right': counter.out_counts,
        'class_wise_count': {class_name: {'right_to_left': 0, 'left_to_right': 0} for class_name in counter.class_wise_count},
    }
    for class_name in counter.class_wise_count:
        object_counts['class_wise_count'][class_name]['right_to_left'] = counter.class_wise_count[class_name]['in']
        object_counts['class_wise_count'][class_name]['left_to_right'] = counter.class_wise_count[class_name]['out']
    if parameters['verbose']:
        print(f'in_counts: {counter.in_counts}')
        print(f'out_counts: {counter.out_counts}')
        print(f'class_wise_count: {counter.class_wise_count}')
    cap.release()
    # cv2.destroyAllWindows()
    if parameters['save_video']:
        video_writer.release()
        if parameters['verbose']:
            print(f'Video saved at: "{output_path}"')
    return object_counts


if __name__ == '__main__':
    # IN means object moving right to left
    # OUT means object moving left to right
    counts = count_objects_()
