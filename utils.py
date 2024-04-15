def show_difference_dicts(true: dict, predicted: dict, level=0):
    for key in true.keys():
        print('  ' * level + key)
        value1 = true[key]
        value2 = predicted[key]
        if isinstance(value1, dict):
            show_difference_dicts(value1, value2)
        else:
            print('  ' * (level + 1) + 'true:' + str(value1))
            print('  ' * (level + 1) + 'predicted:' + str(value2))
