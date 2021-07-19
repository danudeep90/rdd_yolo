# Printing current working directory
echo "Current working directory is $PWD"
echo

# Create a directory if it doesn't exist
echo "Creating directory named 'datasets' if it doesn't exist"
mkdir -p datasets/

# Change directory
cd datasets

# Remove train folder
rm -r train

# Changed directory to datasets
echo "Changed working directory to $PWD"
echo

# Download the training data
echo downloading training data.....

# Fetching the data from cloud
wget https://mycityreport.s3-ap-northeast-1.amazonaws.com/02_RoadDamageDataset/public_data/IEEE_bigdata_RDD2020/train.tar.gz 2>/dev/null || curl -L https://mycityreport.s3-ap-northeast-1.amazonaws.com/02_RoadDamageDataset/public_data/IEEE_bigdata_RDD2020/train.tar.gz -O train.tar.gz

# Message to inform user that tar.gz has been downloaded
echo training images downloaded

# Extracting the tar.gz
tar -xf train.tar.gz

# Removing the tar gz file
rm train.tar.gz

# Change working directory
cd ..
echo "Changed working directory back to $PWD"