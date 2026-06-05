import boto3
import json
import time
from datetime import datetime
import os
import uuid

# ✅ AWS clients
s3 = boto3.client("s3")
stepfn = boto3.client("stepfunctions", region_name="ap-south-1")

# ✅ Config
STATE_MACHINE_ARN = "arn:aws:states:ap-south-1:599626541533:stateMachine:doc-summary-workflow"
FILE_PATH = "input/test_input.txt"

LOG_DIR = "log"
LOG_FILE = f"{LOG_DIR}/s3_upload_sfn_log.txt"


# ✅ Setup log folder
def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


# ✅ Generate unique run id
def generate_run_id():
    return f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"


# ✅ Logger with run context
def log(message, run_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{run_id}] {message}"
    print(formatted)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


# ✅ Detect bucket dynamically
def get_bucket_name():
    response = s3.list_buckets()

    for bucket in response["Buckets"]:
        if "doc-summary" in bucket["Name"]:
            return bucket["Name"]

    raise Exception("❌ Bucket not found")


# ✅ Upload file with run_id in name
def upload_file(bucket_name, run_id):
    filename = f"{run_id}.txt"

    log(f"📤 Uploading file as: {filename}", run_id)

    s3.upload_file(FILE_PATH, bucket_name, filename)

    log(f"✅ Uploaded to s3://{bucket_name}/{filename}", run_id)

    return filename


# ✅ Get execution AFTER upload time
def get_latest_execution(run_id):
    log("🔍 Fetching Step Function execution...", run_id)

    response = stepfn.list_executions(
        stateMachineArn=STATE_MACHINE_ARN,
        maxResults=5  # check few recent executions
    )

    if not response["executions"]:
        log("❌ No executions found", run_id)
        return None

    # ✅ Pick latest execution
    execution = response["executions"][0]

    log(f"✅ Execution matched: {execution['executionArn']}", run_id)

    return execution["executionArn"]


# ✅ Track execution
def track_execution(execution_arn, run_id):
    log("⏳ Tracking Step Function execution...", run_id)

    while True:
        response = stepfn.describe_execution(executionArn=execution_arn)
        status = response["status"]

        log(f"🔄 Status: {status}", run_id)

        if status == "SUCCEEDED":
            log("✅ Execution completed successfully", run_id)
            return response

        elif status in ["FAILED", "TIMED_OUT", "ABORTED"]:
            log(f"❌ Execution failed: {status}", run_id)
            return response

        time.sleep(2)


# ✅ Extract readable output
def extract_output(result):
    try:
        output = json.loads(result["output"])
        return output
    except:
        return result["output"]


# ✅ Log structured result block
def log_full_result(result, run_id, filename):
    parsed_output = extract_output(result)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 100 + "\n")
        f.write(f"RUN ID: {run_id}\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"File: {filename}\n\n")

        f.write("EXECUTION ARN:\n")
        f.write(result["executionArn"] + "\n\n")

        f.write("FINAL STATUS:\n")
        f.write(result["status"] + "\n\n")

        f.write("OUTPUT:\n")
        f.write(json.dumps(parsed_output, indent=2) + "\n")

        f.write("=" * 100 + "\n\n")


# ✅ MAIN FLOW
def main():
    ensure_log_dir()

    run_id = generate_run_id()

    log("🚀 STARTING END-TO-END PIPELINE TEST", run_id)

    # ✅ Step 1: Get bucket
    bucket_name = get_bucket_name()
    log(f"✅ Using bucket: {bucket_name}", run_id)

    # ✅ Step 2: Upload file
    filename = upload_file(bucket_name, run_id)

    # ✅ Step 3: Wait for pipeline trigger
    log("⏳ Waiting for pipeline trigger...", run_id)
    time.sleep(5)

    # ✅ Step 4: Fetch execution
    execution_arn = get_latest_execution(run_id)
    if not execution_arn:
        return

    # ✅ Step 5: Track execution
    result = track_execution(execution_arn, run_id)

    # ✅ Step 6: Log final result
    log_full_result(result, run_id, filename)

    log("✅ END-TO-END PIPELINE TEST COMPLETED\n", run_id)


# ✅ ENTRYPOINT
if __name__ == "__main__":
    main()