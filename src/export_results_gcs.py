import argparse
import os
from datetime import datetime
from pytz import timezone
from google.cloud import storage


def upload_to_bucket_uri(storage_client, gcs_uri, gcs_sub_folder_name, local_dir):

    # Extracting bucket name from the URI
    bucket_name = gcs_uri.split("/")[0]

    # Connect to bucket
    bucket = storage_client.get_bucket(bucket_name)

    # Creating full path in the bucket
    buck_dir_sub_folder = os.path.join(gcs_uri, gcs_sub_folder_name)
    buck_dir_sub_folder = buck_dir_sub_folder.replace(bucket_name + "/", "")

    print("Uploading all files from {}".format(local_dir))

    # Get full paths of all files in local dir
    lst_files_local_dir = os.listdir(local_dir)

    # Loop over all files
    for file in lst_files_local_dir:

        # Create destination blob path
        destination_blob_name = os.path.join(buck_dir_sub_folder, file)
        blob = bucket.blob(destination_blob_name)

        # Upload from local directory
        local_file_path = os.path.join(local_dir, file)

        print("Uploading file {} to {}".format(local_file_path, destination_blob_name))
        blob.upload_from_filename(local_file_path)


def main(train_results_path, test_results_path, gcs_uri, storage_client):

    # Creating datetime type folders
    ist_tz = timezone('Asia/Kolkata')
    india_datetime = datetime.now(ist_tz)
    fold_prefix_str = india_datetime.strftime("%d_%b_%Y-%H_%M_%S")
    out_folder_name = fold_prefix_str
    print(out_folder_name)

    # Write training results to gcs bucket
    upload_to_bucket_uri(storage_client, gcs_uri, out_folder_name, train_results_path)

    # Write test results to gcs bucket
    upload_to_bucket_uri(storage_client, gcs_uri, out_folder_name, test_results_path)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Code to push results to a bucket folder")
    parser.add_argument('--train_results_path', type=str,
                        help='Path where latest train results are stored')
    parser.add_argument('--test_results_path', type=str,
                        help='Path where latest test results are stored')
    parser.add_argument('--gcs_uri', type=str,
                        help='Google Cloud Storage uri')

    # Reading arguments
    args = parser.parse_args()
    train_results_path = args.train_results_path
    test_results_path = args.test_results_path
    gcs_uri = args.gcs_uri

    # Authentication using service account
    # storage_client = storage.Client.from_service_account_json('')

    # Execute function call
    # main(train_results_path, test_results_path, gcs_uri, storage_client)
