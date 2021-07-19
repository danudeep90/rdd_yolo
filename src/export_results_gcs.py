import argparse
import os
from datetime import datetime
from pytz import timezone
from google.cloud import storage

# Function to get all subfolders in a directory recursively
def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


def upload_to_bucket_uri(storage_client, gcs_uri, gcs_sub_folder_name, local_dir, tag):

    # Extracting bucket name from the URI
    bucket_name = gcs_uri.split("/")[0]

    # Connect to bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Creating full path in the bucket
    buck_dir_sub_folder = os.path.join(gcs_uri, gcs_sub_folder_name, tag)
    buck_dir_sub_folder = buck_dir_sub_folder.replace(bucket_name + "/", "")

    print("Uploading all files from {}".format(local_dir))

    # Get all folders inside the directory
    lst_folder_paths = []
    lst_folder_paths.append(local_dir)
    lst_sub_folders_paths = fast_scandir(local_dir)
    lst_folder_paths.extend(lst_sub_folders_paths)

    # Iterate over all folders
    for folder_path in lst_folder_paths:
        print("-"*20)
        print("Uploading files in the folder {}".format(folder_path))

        # Get full paths of all files in local dir
        lst_files_folder_dir = [f for f in os.listdir(folder_path)
                                 if os.path.isfile(os.path.join(folder_path, f))]

        # Loop over all files
        for filename in lst_files_folder_dir:

            # Getting a proper prefix for destination name
            tmp_prefix = folder_path.replace(local_dir,"").lstrip("/")

            # Create destination blob path
            destination_blob_name = os.path.join(buck_dir_sub_folder, tmp_prefix, filename)
            blob = bucket.blob(destination_blob_name)

            # Upload from local directory
            local_file_path = os.path.join(folder_path, filename)

            print("Uploading file {} to {}".format(local_file_path, destination_blob_name))
            blob.upload_from_filename(local_file_path)

        print("-"*20)


def upload_file_to_bucket(storage_client, gcs_uri, gcs_sub_folder_name, local_file_path):

    # Extracting bucket name from the URI
    bucket_name = gcs_uri.split("/")[0]

    # Connect to bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Creating full path in the bucket
    buck_dir_sub_folder = os.path.join(gcs_uri, gcs_sub_folder_name)
    buck_dir_sub_folder = buck_dir_sub_folder.replace(bucket_name + "/", "")

    # Extracting filename
    tmp_folder_path1, tmp_file_name1 = os.path.split(local_file_path)

    # Create destination blob path
    destination_blob_name = os.path.join(buck_dir_sub_folder, tmp_file_name1)
    blob = bucket.blob(destination_blob_name)

    # Uploading file
    print("Uploading file {} to {}".format(local_file_path, destination_blob_name))
    blob.upload_from_filename(local_file_path)



def main(train_results_path, test_results_path, logfile_path, gcs_uri, storage_client):

    # Creating datetime type folders
    # ist_tz = timezone('Asia/Kolkata')
    # india_datetime = datetime.now(ist_tz)
    # fold_prefix_str = india_datetime.strftime("%d_%b_%Y-%H_%M_%S")
    # out_folder_name = fold_prefix_str
    # print(out_folder_name)

    # Extracting folder name from logfile path
    tmp_folder_path, tmp_file_name = os.path.split(logfile_path)

    # Removing the train- and .log
    tmp_folder_name = tmp_file_name.replace("train-","")
    out_folder_name = tmp_folder_name.replace(".log","")

    # Write training results to gcs bucket
    upload_to_bucket_uri(storage_client, gcs_uri, out_folder_name, train_results_path, tag="train")

    # Write test results to gcs bucket
    upload_to_bucket_uri(storage_client, gcs_uri, out_folder_name, test_results_path, tag="test")

    # Upload log file to the bucket
    upload_file_to_bucket(storage_client, gcs_uri, out_folder_name, logfile_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Code to push results to a bucket folder")
    parser.add_argument('--train_results_path', type=str,
                        help='Path where latest train results are stored')
    parser.add_argument('--test_results_path', type=str,
                        help='Path where latest test results are stored')
    parser.add_argument('--gcs_uri', type=str,
                        help='Google Cloud Storage uri')
    parser.add_argument('--logfile_path', type=str,
                        help='Log file of the training pipeline run')
        

    # Reading arguments
    args = parser.parse_args()
    train_results_path = args.train_results_path
    test_results_path = args.test_results_path
    gcs_uri = args.gcs_uri
    logfile_path = args.logfile_path

    print(train_results_path)
    print(test_results_path)
    print(gcs_uri)
    print(logfile_path)

    # Authentication using service account
    storage_client = storage.Client.\
    from_service_account_json('secured_conf/road-damage-detection-320308-8c4c570bb890.json')

    # Execute function call
    main(train_results_path, test_results_path, logfile_path,
         gcs_uri, storage_client)
