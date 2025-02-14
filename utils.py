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
        raise ValueError(f'Invalid region_points type: {region_type}. Only "vertical_line" and "rectangle" are allowed.')
    return region_points
