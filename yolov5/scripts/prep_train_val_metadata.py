import argparse
import os
import random
import numpy as np


def main(train_ratio, valid_ratio, test_ratio, imgs_dir, countries):

    # Counters to compute num of examples
    train_examples_count = 0
    val_examples_count = 0
    test_examples_count = 0

    # Directory where the text files would be written
    other_dir = "/".join(imgs_dir.split("/")[0:-1])

    # Removing existing text files
    try:
        os.remove(os.path.join(other_dir, "train.txt"))
        os.remove(os.path.join(other_dir, "valid.txt"))
        os.remove(os.path.join(other_dir, "test.txt"))
    except:
        pass

    for country in countries:

        # Path of the india images
        tmp_path = os.path.join(imgs_dir, country, "images")

        # Get list of files
        img_files = [os.path.join(tmp_path, filename)
                     for filename in os.listdir(tmp_path) if filename.endswith('.jpg')]

        # Printing len of img_files
        print(len(img_files))

        # Creating indices for files
        img_file_idxs = list(range(len(img_files)))

        # Shuffling the indices
        random.seed(0)
        random.shuffle(img_file_idxs)

        # Computing number of examples for each set
        num_train_examples = int(train_ratio * len(img_file_idxs))
        num_val_examples = int(valid_ratio * len(img_file_idxs))
        num_test_examples = len(img_file_idxs) - num_train_examples - num_val_examples

        print("Number of training examples for {} are {}".format(country, num_train_examples))
        print("Number of validation examples for {} are {}".format(country, num_val_examples))
        print("Number of test examples for {} are {}".format(country, num_test_examples))
        print("--------------------------------------------------------------------")

        # Write all these to text files for book keeping
        train_indices = img_file_idxs[0:num_train_examples]
        val_indices = img_file_idxs[num_train_examples:num_train_examples + num_val_examples]
        test_indices = img_file_idxs[num_train_examples + num_val_examples:]

        # Get details of the examples
        req_train_files = list(np.array(img_files)[train_indices])
        req_val_files = list(np.array(img_files)[val_indices])
        req_test_files = list(np.array(img_files)[test_indices])

        # Writing to a file
        with open(os.path.join(other_dir, "train.txt"), "a") as outfile:
            outfile.write("\n".join(req_train_files))
            outfile.write("\n")

        with open(os.path.join(other_dir, "valid.txt"), "a") as outfile:
            outfile.write("\n".join(req_val_files))
            outfile.write("\n")

        with open(os.path.join(other_dir, "test.txt"), "a") as outfile:
            outfile.write("\n".join(req_test_files))
            outfile.write("\n")

        train_examples_count += len(req_train_files)
        val_examples_count += len(req_val_files)
        test_examples_count += len(req_test_files)

    print("Total Number of training examples are {}".format(train_examples_count))
    print("Total Number of validation examples are {}".format(val_examples_count))
    print("Total Number of test examples are {}".format(test_examples_count))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Preparing meta data for training and validation data")
    parser.add_argument('--train_ratio', type=float,
                        help='Percentage of data to be taken for training',
                        default=0.80)
    parser.add_argument('--valid_ratio', type=float,
                        help='Percentage of data to be taken for validation',
                        default=0.15)
    parser.add_argument('--test_ratio', type=float,
                        help='Percentage of data to be taken for validation',
                        default=0.05)
    parser.add_argument("--imgs_dir", type=str,
                        help='Folder containing the training images. The folder should contain '
                             'sub-folders for countries and relative to yolov5 folder',
                        default="datasets/train")

    args = parser.parse_args()

    # Reading inputs from command line
    train_ratio = args.train_ratio
    valid_ratio = args.valid_ratio
    test_ratio = args.test_ratio
    imgs_dir = args.imgs_dir

    # Other arguments
    countries = ["Czech", "Japan", "India"]

    # Function call
    main(train_ratio, valid_ratio, test_ratio, imgs_dir, countries)
