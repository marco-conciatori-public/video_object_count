import ultralytics
import numpy as np
import supervision as sv
from ultralytics import YOLO

import config
import global_constants


ultralytics.checks()
print('supervision.__version__:', sv.__version__)


model_path = global_constants.model_folder + config.model_name
model = YOLO(model=model_path, verbose=config.verbose)
model.fuse()

video_path = global_constants.data_folder + config.video_name
print(video_path)

# dict mapping class_id to class_name
class_names_dict = model.model.names
# class_ids of interest
print(f'selected_classes: {config.selected_classes}')
# class names of interest
class_names = [class_names_dict[class_id] for class_id in config.selected_classes]
print(f'class_names: {class_names}')

# settings
# LINE_START = sv.Point(50, 1500)
# LINE_END = sv.Point(3840-50, 1500)
output_path = global_constants.output_folder + 'counting_result_' + config.video_name

sv.VideoInfo.from_video_path(video_path)

# create BYTETracker instance
byte_tracker = sv.ByteTrack(track_thresh=0.25, track_buffer=30, match_thresh=0.8, frame_rate=30)
# create VideoInfo instance
video_info = sv.VideoInfo.from_video_path(video_path)
# create frame generator
generator = sv.get_video_frames_generator(video_path)
# create instance of BoxAnnotator
box_annotator = sv.BoxAnnotator(thickness=4, text_thickness=4, text_scale=2)


# define call back function to be used in video processing
def callback(frame: np.ndarray, index: int) -> np.ndarray:
    # model prediction on single frame and conversion to supervision Detections
    results = model(frame, verbose=config.verbose)[0]
    detections = sv.Detections.from_ultralytics(results)
    # only consider class id from selected_classes define above
    detections = detections[np.isin(detections.class_id, config.selected_classes)]
    # tracking detections
    detections = byte_tracker.update_with_detections(detections)
    labels = [
        f"#{tracker_id} {class_names_dict[class_id]} {confidence:0.2f}"
        for confidence, class_id, tracker_id
        in zip(detections.confidence, detections.class_id, detections.tracker_id)
    ]
    annotated_frame = box_annotator.annotate(
        scene=frame.copy(),
        detections=detections,
        labels=labels)

    # return frame with box annotated result
    return annotated_frame


# process the whole video
sv.process_video(source_path=video_path, target_path=output_path, callback=callback)
