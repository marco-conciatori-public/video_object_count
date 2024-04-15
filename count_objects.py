import cv2
import ultralytics
from ultralytics import YOLO
from ultralytics.solutions import object_counter

import global_constants
from import_args import args


def count_objects_(**kwargs) -> dict:
    ultralytics.checks()

    parameters = args.import_and_check(global_constants.CONFIG_PARAMETER_PATH, **kwargs)

    # Download model in "models" folder if not present, and load it
    model_path = global_constants.MODEL_FOLDER + parameters['model_name']
    model = YOLO(model=model_path, verbose=parameters['verbose'])

    # Load video
    video_path = global_constants.DATA_FOLDER + parameters['video_name']
    print(f'video_path: {video_path}')
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f'could not open file "{video_path}"'
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f'width: {frame_width}, height: {frame_height}, fps: {fps}')

    # Classes
    # dict mapping class_id to class_name
    class_names_dict = model.names
    # class_ids of interest
    print(f'selected_classes: {parameters["selected_classes"]}')
    # class names of interest
    class_names = [class_names_dict[class_id] for class_id in parameters['selected_classes']]
    print(f'class_names: {class_names}')

    # Define region points
    half_width = int(frame_width / 2)
    # region_points = [
    #     (half_width, 0),
    #     (half_width, frame_height),
    # ]
    distance_from_center = 10
    region_points = [
        (half_width - distance_from_center, 0),
        (half_width + distance_from_center, 0),
        (half_width + distance_from_center, frame_height),
        (half_width - distance_from_center, frame_height),
    ]

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

    # Init Object Counter
    counter = object_counter.ObjectCounter()
    counter.set_args(
        view_img=False,
        reg_pts=region_points,
        classes_names=class_names_dict,
        draw_tracks=False,
    )

    while cap.isOpened():
        if parameters['verbose']:
            if cap.get(cv2.CAP_PROP_POS_FRAMES) % 30 == 0:
                print(f'\tProgress: {round(cap.get(cv2.CAP_PROP_POS_AVI_RATIO) * 100, 1)} %')
        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
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

    counts = {
        'in_counts': counter.in_counts,
        'out_counts': counter.out_counts,
        'class_wise_count': counter.class_wise_count,
    }
    print(f'in_counts: {counter.in_counts}')
    print(f'out_counts: {counter.out_counts}')
    print(f'class_wise_count: {counter.class_wise_count}')
    cap.release()
    if parameters['save_video']:
        video_writer.release()
        print(f'Video saved at: "{output_path}"')
    return counts


if __name__ == '__main__':
    counts = count_objects_()
    # IN means object moving right to letf
    # OUT means object moving left to right
