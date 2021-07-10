import os
import argparse
import xml.etree.ElementTree as ET
from PIL import Image
from collections import defaultdict
import shutil


# Convert  corner box co-ordinates into mid point, weight and height
def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return [x,y,w,h]


# convert minX,minY,maxX,maxY to normalized numbers required by Yolo
def getYoloBoxInfo(imgFilePath, minX, minY, maxX, maxY):

    image = Image.open(imgFilePath)
    w = int(image.size[0])
    h = int(image.size[1])
    b = (minX, maxX, minY, maxY)
    bb = convert((w, h), b)
    image.close()
    return bb


def main(input_train_file, input_valid_file, input_test_file, class_file):

    # Testing
    # input_train_file = "datasets/train/train.txt"
    # input_valid_file = "datasets/train/valid.txt"
    # class_file = "datasets/damage_classes.txt"

    # dictionary to store list of image paths in each class
    imageListDict = defaultdict(set)

    # Read the file
    with open(input_train_file, "r") as f:
        lst_img_details_train = f.readlines()
    f.close()

    with open(input_valid_file, "r") as f:
        lst_img_details_valid = f.readlines()
    f.close()

    with open(input_test_file, "r") as f:
        lst_img_details_test = f.readlines()
    f.close()


    # Combining both the lists
    lst_img_details = lst_img_details_train + lst_img_details_valid + lst_img_details_test

    # assign each class of dataset to a number
    outputCtoId = {}

    f = open(class_file, "r")
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):
        outputCtoId[lines[i].strip()] = i

    # Remove old label directories and create fresh directories
    # In case seed changes, training image will change,
    # so to remove labels for older seed images, it is better to remove label folders if exists
    all_img_master_folders = list(set([item.strip().rsplit("/", 1)[0] for item in lst_img_details]))
    all_expec_label_folders = [item.replace("images", "labels") for item in all_img_master_folders]

    # Loop over each folder path and clear it if exists
    for tmp_label_dir in all_expec_label_folders:
        if os.path.exists(tmp_label_dir):
            print("{} folder already exists. Removing it to create freshly in case of seed change"
                  .format(tmp_label_dir))
            shutil.rmtree(tmp_label_dir)

    # Loop over each file and create a labels related info as well
    for imgFilePath in lst_img_details:
        # print(imgFilePath)

        # Stripping the newline character
        imgFilePath = imgFilePath.strip()

        # Removing \n at the end of filename and extract info without .jpg extension
        tmp_str1 = imgFilePath.strip().rsplit(".", 1)[0]

        # Extracting the actual XML path of the image annotation
        actual_xml_path = tmp_str1.replace("images", "annotations/xmls") + ".xml"
        actual_xml_fullpath = os.path.abspath(actual_xml_path)

        # YOLOv5 expects the file to be a place as below
        # if image is present at train/India/images/image_0001.jpg
        # annotation is expected at train/India/labels/image_001.txt

        # Required annotation path
        req_annotation_path = actual_xml_path.replace("annotations/xmls", "labels")
        req_annotation_path = req_annotation_path.strip().rsplit(".", 1)[0] + ".txt"
        req_annotation_fullpath = os.path.abspath(req_annotation_path)

        # Parsing the XML file to convert to yolo annotation
        tree = ET.parse(actual_xml_fullpath)
        root = tree.getroot()

        # Create directory if it doesnt exists
        labels_dirpath = os.path.dirname(req_annotation_fullpath)
        if not os.path.exists(labels_dirpath):
            os.mkdir(labels_dirpath)

        # Opening file for writing information
        yoloOutput = open(req_annotation_fullpath, "w")

        # loop over each object tag in annotation tag
        for objects in root.findall('object'):
            defect_type = objects.find('name').text.replace(" ", "")

            if defect_type == "D00" or defect_type == "D10" or defect_type == "D20" or defect_type == "D40":
                bndbox = objects.find('bndbox')
                [minX, minY, maxX, maxY] = [int(child.text) for child in bndbox]

                # Convert to yolo format
                [x, y, w, h] = getYoloBoxInfo(imgFilePath, minX, minY, maxX, maxY)

                # Write to the yolo annotation text file
                yoloOutput.write(str(outputCtoId[defect_type]) + " " +
                                 str(x) + " " + str(y) + " " + str(w) + " " + str(h) + "\n")

                imageListDict[outputCtoId[defect_type]].add(imgFilePath)

        # Closing the file which is opened for editing
        yoloOutput.close()

    # Printing how many of each class are available
    for cl in imageListDict:
        print(lines[cl].strip(), ":", len(imageListDict[cl]))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Code to convert xml files to yolo format")
    parser.add_argument('--input_train_file', type=str,
                        help='Path of txt file which contains details of images for training',
                        default="datasets/train.txt")
    parser.add_argument('--input_valid_file', type=str,
                        help='Path of txt file which contains details of images for validation',
                        default="datasets/valid.txt")
    parser.add_argument('--input_test_file', type=str,
                    help='Path of txt file which contains details of images for test',
                    default="datasets/test.txt")
    parser.add_argument('--class_file', type=str,
                        help='Path of txt file which has classes information',
                        default="datasets/damage_classes.txt")

    args = parser.parse_args()

    input_train_file = args.input_train_file
    input_valid_file = args.input_valid_file
    input_test_file = args.input_test_file
    class_file = args.class_file

    # Function call
    main(input_train_file, input_valid_file, input_test_file, class_file)