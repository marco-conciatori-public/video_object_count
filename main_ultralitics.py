import ultralytics
import numpy as np
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
output_path = global_constants.output_folder + 'counting_result_' + config.video_name

