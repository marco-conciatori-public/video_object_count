def show_difference_dicts(d1: dict, d2: dict, level=0):
    for key in d1.keys():
        value1 = d1[key]
        value2 = d2[key]
        if isinstance(value1, dict):
            show_difference_dicts(value1, value2)
        else:
            print(f'{key}: {value1} vs {value2}')

    return True