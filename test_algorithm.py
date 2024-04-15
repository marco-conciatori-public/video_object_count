import warnings

import utils
import true_counts
import count_objects


true_counts_dict = true_counts.by_file_name
for file_name, counts in true_counts_dict.items():
    print(f'{file_name}: {counts}')

    # suppress warnings
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=RuntimeWarning)
        predicted_counts = count_objects.count_objects_(video_name=file_name, verbose=False)
    print(f'predicted_counts: {predicted_counts}')
    print(f'true_counts: {counts}')
    utils.show_difference_dicts(true=counts, predicted=predicted_counts)
    print('--------------------------------------------------')
    print()

