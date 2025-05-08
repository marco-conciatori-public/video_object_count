import cv2
from pathlib import Path

from import_args import args
import global_constants as gc


def convert_(**kwargs):
    file_counter = 0
    error_counter = 0

    parameters = args.import_and_check(gc.CONFIG_PARAMETER_PATH, **kwargs)
    media_path = gc.DATA_FOLDER + parameters['file_folder']
    print(f'{media_path=}')
    save_folder_path = media_path + 'images/'
    print(f'{save_folder_path=}')
    Path(save_folder_path).mkdir(exist_ok=True)
    for video_path in Path(media_path).rglob(f'*.{gc.VIDEO_FORMAT}'):
        # print(f'\t{video_path=}')
        video_name = video_path.name
        video_file_path = media_path + video_name
        # print(f'\t{video_file_path=}')
        if parameters["verbose"]:
            print(f'\tfile number {file_counter}: "{video_name}"')

        try:
            cap = cv2.VideoCapture(video_file_path)
            assert cap.isOpened(), f'could not open file "{video_path}"'
            success, im0 = cap.read()
            assert success, f'could not read first frame of video "{video_path}".'
            # print(f'\t{video_name=}')
            video_name_without_extention = video_path.stem
            # print(f'\t{video_name_without_extention=}')
            image_name = video_name_without_extention + '.' + gc.IMAGE_FORMAT
            save_file_path = save_folder_path + image_name
            # print(f'\t{save_file_path=}')
            cv2.imwrite(filename=save_file_path, img=im0)
            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            print(e)
            print(f'\tskipping file "{video_path}"')
            error_counter += 1
            try:
                cap.release()
            except:
                pass
            cv2.destroyAllWindows()

        file_counter += 1
        # print('\t--------------------------------------------------')

    print(f'Found {file_counter} videos.')
    if error_counter > 0:
        print(f'Encountered {error_counter} errors.')
    print(f'Generated {file_counter - error_counter} images.')


if __name__ == '__main__':
    convert_()
