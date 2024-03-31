import os
from glob import glob
import re
import json
import random
import numpy as np


def get_filelists(folder):
    filelists = {}
    folder_done = []
    folders_to_remove = []
    # append just annotated folders
    for o in folder:
        if 'birdrecorder-old' in o or 'birdrecorder-new' in o:
            annotated_folders_list = glob(o + "/*_done")  # just using hand annotated files
            # annotated_folders_list = glob(o + "/*") # using all files
            for annotated_folder in annotated_folders_list:
                folder_done.append(annotated_folder)
            folders_to_remove.append(o)
    folder = [o for o in folder if o not in folders_to_remove]
    # FIXME: Other Datasets

    for o in folder_done:
        if not os.path.isdir(o + '/Annotations'):  # for original Annotations
            # if not os.path.isdir(o + '/Annotations_corr'):  # for corrected Annotations
            print("Error: source annotation folder %s cannot be opened\n" % o)
            exit(1)
        try:
            filelists[o] = sorted(
                [f for f in os.listdir(o + '/Annotations') if (re.search("\.json$", f) is not None)])
        except:
            print("Error: Could not get annotations from %s\n" % o)
            exit(1)
    return filelists


def get_template(single_class, cocofolder):
    if single_class and cocofolder != "":
        template = json.load(
            open(os.path.abspath(os.path.dirname(__file__)) + '/template_birds_single-class_coco.json'))
    elif single_class and cocofolder == "":
        template = json.load(
            open(os.path.abspath(os.path.dirname(__file__)) + '/template_birds_single-class_no-coco.json'))
    elif not single_class and cocofolder != "":
        template = json.load(
            open(os.path.abspath(os.path.dirname(__file__)) + '/template_birds_3-class_coco.json'))
    elif not single_class and cocofolder == "":
        template = json.load(
            open(os.path.abspath(os.path.dirname(__file__)) + '/template_birds_3-class_no-coco.json'))
    return template


def get_frameid_and_date(o, f):
    if 'birdrecorder-old' in o:  # for selecting old birdrecorder data or other datasets
        # frame_id = int(re.search("([0-9]*)\.json", f)[1])
        frame_id = re.search("([0-9]{8})_([0-9]{6})_([0-9]{5})", f)  # our id consists of date + time + id
        frame_id = frame_id.group(1) + frame_id.group(2) + frame_id.group(3)
        date = frame_id[:8]
    elif 'birdrecorder-new' in o:  # for selecting old birdrecorder data or other datasets
        pattern = re.compile(r'snap_run(\d+)_(setup23_|)cam(\d+)_cap(\d+)_(\d{6}|\d{8})T(\d{6})Z(_static|)\.json')
        match = pattern.match(f)
        if match:
            run_num = match.group(1).zfill(6)
            cam_num = match.group(2)
            cap_num = match.group(3).zfill(10)
            date = match.group(4)
            time = match.group(5)
        frame_id = run_num + cam_num + cap_num + date + time

    elif 'sod4sb' in o:  # small-object-detection-for-spotting-birds dataset
        frame_id = re.search("([0-9]{3})_([0-9]{5})", f)
        frame_id = frame_id.group(1) + frame_id.group(2)
        date = frame_id[:3]
    else:
        print("Can't find Dataset!")
    return frame_id, date


def get_jdata(o, f, use_corr=False):
    if use_corr:  # using the corrected annotations
        jdata = json.load(open(o + '/Annotations_corr/' + f))  # for original Annotations
    else:
        jdata = json.load(open(o + '/Annotations/' + f))  # for corrected Annotations

    return jdata


def get_size_category(width, height):
    categories = ["tiny", "small", "medium", "large"]
    weights = [0.6, 0.2, 0.1, 0.1]  # Beispielgewichtung - ändere sie nach Bedarf an
    category = random.choices(categories, weights=weights, k=1)[0]  # FIXME
    return category


def within_X_percent(dictionary, current_class, categories, percentage=0.05):
    """
    Check if all values in the dictionary are within a specified percentage deviation from the first value.

    Args:
        dictionary (dict): The input dictionary with string keys and numeric values.
        current_class (str): The current annotation class.
        percentage (float): The percentage deviation allowed for all values in the dictionary.
                            It should be a decimal number between 0 and 1.

    Returns:
        bool: True if all values are within the specified percentage deviation from the first value, otherwise False.
    """
    if len(dictionary) < len(categories):
        return True
    if not dictionary:
        return False

    # get min and max values in dictionary
    values = list(dictionary.values())
    max_value = max(values)
    min_value = min(values)

    # return false if unbalanced (x% deviation)
    eps = np.finfo(float).eps  # to avoid divison by zero
    if (max_value / (min_value + eps)) > (1 + percentage):
        current_min_class = min(dictionary, key=lambda k: dictionary[k])
        if current_class != current_min_class:
            return False

    return True
