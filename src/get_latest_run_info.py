import os
import argparse
import sys

# Function to get latest folder from a specified directory
def get_recent_directory(dirpath):
  dirs = [s for s in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, s))]
  dirs.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)

  return os.path.join(dirpath, dirs[0]) 


def main(results_dir, tag):
    # Getting path of latest training directory
    latest_dir = get_recent_directory(results_dir)
    print("Latest {} results are saved in {}".format(tag, latest_dir))

    # Create a tmp dictionary 
    tmp_dict = {}
    if tag == "train":
        latest_weights_path = os.path.join(latest_dir, "weights", "best.pt")
        print("Latest {} weights are available in {}".format(tag, latest_weights_path))

        tmp_dict["latest_train_dir"] = latest_dir
        tmp_dict["latest_weights_path"] = latest_weights_path

    elif tag == "test":
        tmp_dict["latest_test_dir"] = latest_dir        
    
    # Opening/Creating file to put the information
    file1 = open("../src/run_info_details.txt", "w")
    for key,value in tmp_dict.items():
        file1.write(str(key)+"="+str(value)+"\n")
    file1.close()

    return latest_dir

if __name__ == "__main__":

    try:
        parser = argparse.ArgumentParser(description="Code to extract latest run folder information")
        parser.add_argument('--results_dir', type=str,
                            help='Path where results are stored',
                            default="runs/train/")
        parser.add_argument('--tag', type=str,
                            help='Indicating whether information is fetched for train or test',
                            default="train")

        args = parser.parse_args()
        results_dir = args.results_dir
        tag = args.tag
        
        # Function call to get most recent directory
        main(results_dir, tag)
    
        sys.exit(0)

    except Exception as e:
        print(str(e))
        sys.exit(1)