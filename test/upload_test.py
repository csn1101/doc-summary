import boto3
import time
import os

s3 = boto3.client("s3")

INPUT_BUCKET = "599626541533-ap-south-1-doc-summary-input"
OUTPUT_BUCKET = "599626541533-ap-south-1-doc-summary-output"

# Include 'test' in filename ✅
FILE_NAME = "test_doc_summary.txt"

def upload_file():
    print("Uploading test file...")
    s3.upload_file("test_input.txt", INPUT_BUCKET, FILE_NAME)
    print("Upload complete.")

def wait_for_processing():
    print("Waiting for Lambda processing...")
    time.sleep(5)

def download_output():
    print("Downloading output...")
    os.makedirs("output", exist_ok=True)

    s3.download_file(
        OUTPUT_BUCKET,
        FILE_NAME,
        f"output/{FILE_NAME}"
    )
    print("Output downloaded.")

def main():
    upload_file()
    wait_for_processing()
    download_output()

    with open(f"output/{FILE_NAME}", "r") as f:
        print("\n=== SUMMARY OUTPUT ===")
        print(f.read())

if __name__ == "__main__":
    main()
