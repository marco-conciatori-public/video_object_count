import torch
import warnings


def show_difference_dicts(true: dict, predicted: dict, level=0):
    for key in true.keys():
        print('  ' * level + key)
        value1 = true[key]
        try:
            value2 = predicted[key]
        except KeyError:
            value2 = 0
        if isinstance(value1, dict):
            show_difference_dicts(true=value1, predicted=value2, level=level + 1)
        else:
            print('  ' * (level + 1) + 'true:' + str(value1))
            print('  ' * (level + 1) + 'predicted:' + str(value2))


def define_region_points(region_type: str,
                         frame_width: int,
                         frame_height: int,
                         x_distance_from_center: int = None,
                         ) -> list[tuple[int, int]]:
    # Define region points
    half_width = int(frame_width / 2)
    if region_type == 'vertical_line':
        region_points = [
            (half_width, 0),
            (half_width, frame_height),
        ]
    elif region_type == 'rectangle':
        assert x_distance_from_center is not None, 'x_distance_from_center must be provided for region_type=rectangle'
        assert x_distance_from_center > 0, 'x_distance_from_center must be greater than 0'
        assert x_distance_from_center < half_width, 'x_distance_from_center must be less than half_width'
        region_points = [
            (half_width - x_distance_from_center, 0),
            (half_width + x_distance_from_center, 0),
            (half_width + x_distance_from_center, frame_height),
            (half_width - x_distance_from_center, frame_height),
        ]
    else:
        raise ValueError(f'Invalid region_points type: {region_type}')
    return region_points


def get_available_device(verbose: int = 0) -> torch.device:
    if not torch.cuda.is_available():
        warnings.warn('GPU not found, using CPU')
        device = torch.device('cpu')
    else:
        device = torch.device('cuda:0')

    if verbose >= 1:
        print(f'Device: {device}')

    return device
