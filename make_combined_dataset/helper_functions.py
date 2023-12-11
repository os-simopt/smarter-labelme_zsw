import os
from glob import glob
import re
import json


def get_filelists(folder):
    filelists = {}
    # append just annotated folders
    for o in folder:
        if 'birdrecorder-old' in o or 'birdrecorder-new' in o:
            annotated_folders_list = glob(o + "/*_done")  # just using hand annotated files
            # annotated_folders_list = glob(o + "/*") # using all files
            for annotated_folder in annotated_folders_list:
                folder.append(annotated_folder)
            folder.remove(o)
            break

    for o in folder:
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
            open(os.path.abspath(os.path.dirname(__file__)) + '/template_birds_3-class_no-coco.json'))
    elif not single_class and cocofolder == "":
        template = json.load(
            open(os.path.abspath(os.path.dirname(__file__)) + '/template_birds_3-class_coco.json'))
    return template


def get_frameid_and_date(o, f):
    if 'birdrecorder-old' in o or 'birdrecorder-new' in o:  # for selecting old birdrecorder data or other datasets
        # frame_id = int(re.search("([0-9]*)\.json", f)[1])
        frame_id = re.search("([0-9]{8})_([0-9]{6})_([0-9]{5})", f)  # our id consists of date + time + id
        frame_id = frame_id.group(1) + frame_id.group(2) + frame_id.group(3)
        date = frame_id[:8]
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



def within_X_percent(dictionary, anno, categories, percentage=0.05):
    """
    Check if all values in the dictionary are within a specified percentage deviation from the first value.

    Args:
        dictionary (dict): The input dictionary with string keys and numeric values.
        anno (object): The current annotation object.
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
    if (max_value - min_value) / max_value > percentage:
        current_class = anno['class']['name']
        current_min_class = min(dictionary, key=lambda k: dictionary[k])
        if current_class != current_min_class:
            return False

    return True