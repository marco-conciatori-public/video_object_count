import real_counts
import count_objects


for file_name, counts in real_counts.by_file_name.items():
    print(f'\n {file_name}: {counts}')
    algorithm_counts = count_objects.count_objects_(video_name=file_name)
    for key, value in algorithm_counts.items():
        if isinstance(value, dict):
            print(f' - {key}:')
            for key2, value2 in value.items():
                print(f'   - {key2}: {value2}')
