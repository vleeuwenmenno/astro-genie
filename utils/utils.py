
import os


def formatExposureTime(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours}h {minutes}m {seconds}s"

def calculateExposureTimes(dates:list, object_path:str):
    total_lights = 0
    total_exposure_time = 0
    light_frames = []

    for date in dates:
        lights_path = os.path.join(object_path, date)

        # Handle inconsistent folder names
        possible_folders = ["Lights", "lights", "Light"]
        lights_folder = next(
            (f for f in possible_folders if os.path.isdir(os.path.join(lights_path, f))), None
        )

        if lights_folder:
            lights_folder_path = os.path.join(lights_path, lights_folder)
            if os.path.isdir(lights_folder_path):
                # Check for sub-folders with exposure seconds
                sub_folders = [
                    name for name in os.listdir(lights_folder_path)
                    if os.path.isdir(os.path.join(lights_folder_path, name))
                ]

                if sub_folders:
                    for sub_folder in sub_folders:
                        try:
                            exposure_seconds = float(sub_folder)
                        except ValueError:
                            continue

                        sub_folder_path = os.path.join(lights_folder_path, sub_folder)
                        light_files = [
                            os.path.join(sub_folder_path, name)
                            for name in os.listdir(sub_folder_path)
                            if os.path.isfile(os.path.join(sub_folder_path, name))
                        ]
                        light_frames.extend(light_files)
                        total_lights += len(light_files)
                        total_exposure_time += len(light_files) * exposure_seconds
                else:
                    light_files = [
                        name
                        for name in os.listdir(lights_folder_path)
                        if os.path.isfile(os.path.join(lights_folder_path, name))
                    ]
                    total_lights += len(light_files)
                    light_frames.extend(light_files)

    return total_lights, total_exposure_time, light_frames