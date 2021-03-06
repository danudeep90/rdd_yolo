echo
echo ----------------- Running Training Pipeline ---------------------
echo "Creating log file for the run"

# Extract datetime in required format and india timezone
NOW=$(TZ=Asia/Kolkata date +"%d_%b_%Y-%H_%M_%S")

# Create Logs directory if it doesn't exist
mkdir -p logs/

# Log file name
LOGFILENAME="train-$NOW.log"
LOGFILEPATH="$PWD/logs/$LOGFILENAME"

echo
echo "Log will written to $LOGFILEPATH"
echo "Current Working directory is $PWD"
echo

echo ------------------------ Dataset Setup ----------------------------
echo Splitting the Dataset into train, validation and test sets
python src/prep_train_val_metadata.py | tee -a $LOGFILEPATH
train_val_meta_script_status=$?
echo

echo converting xml annotations to yolov5 format
python src/convert_xml_to_yolo.py | tee -a $LOGFILEPATH
xml_to_yolo_script_status=$?
echo


echo ----------------- Started Model Training ------------------
# Removing cache files
rm -f datasets/train.cache
rm -f datasets/valid.cache
rm -f datasets/test.cache

cd yolov5
echo "Changed working directory to yolov5 folder $PWD"

# Execute training code
python train.py --batch 16 --epochs 1 --data ../config/road.yaml --weights yolov5s.pt --device 0 | tee -a $LOGFILEPATH
train_script_status=$?
echo

echo ------------- Getting Latest Training Run Folder ------------
python ../src/get_latest_run_info.py | tee -a $LOGFILEPATH
latest_train_results_status=$?

# Reading variables from the text file
while read -r line; do declare  "$line"; done <../src/run_info_details.txt
echo 

echo ------------- Measuring performance on test dataset ------------
# Running on test dataset
python test.py --weights $latest_weights_path --data ../config/road.yaml --task test --device 0 | tee -a $LOGFILEPATH
test_perf_script_status=$?

# Get info of latest test folders
python ../src/get_latest_run_info.py --results_dir runs/test/ --tag test | tee -a $LOGFILEPATH
latest_test_results_status=$?

# Reading variables from the text file
while read -r line; do declare  "$line"; done <../src/run_info_details.txt
echo

echo ------------- Exporting model to torchscript.ptl lite format ------------
# Export model to torchscript.ptl in lite format 
python models/export.py --weights $latest_weights_path --device 0 | tee -a $LOGFILEPATH
model_export_script_status=$?
echo

# Print training and test results location
echo
echo "Latest training results are saved at $PWD/$latest_train_dir" | tee -a $LOGFILEPATH
echo "Latest weights are available at $PWD/$latest_weights_path " | tee -a $LOGFILEPATH
echo "Latest test results are saved at $PWD/$latest_test_dir" | tee -a $LOGFILEPATH
echo


# Check if all codes are successfully executed and then write to bucket

# Write to gcs bucket
echo ------------- Writing to gcs bucket ------------

# Getting the full paths of results directory
train_results_full_path="$PWD/$latest_train_dir"
test_results_full_path="$PWD/$latest_test_dir"

# Navigating to root folder
cd ..

# Executing script to push to GCS
python src/export_results_gcs.py --train_results_path "$train_results_full_path" --test_results_path "$test_results_full_path" --gcs_uri "rdd_yolov5/training" --logfile_path "$LOGFILEPATH" | tee -a $LOGFILEPATH
echo

# Final Log message
echo "Log is written to $LOGFILEPATH" | tee -a $LOGFILEPATH
echo