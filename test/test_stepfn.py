import boto3
import json
import time
from datetime import datetime

# ✅ Your Step Function ARN
STATE_MACHINE_ARN = "arn:aws:states:ap-south-1:599626541533:stateMachine:doc-summary-workflow"

stepfn = boto3.client("stepfunctions", region_name="ap-south-1")

LOG_FILE = "log/stepfn_test_log.txt"


def read_input_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def log_result(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write("\n" + "=" * 80 + "\n")
        log.write(f"Timestamp: {timestamp}\n")
        log.write(json.dumps(data, indent=2, default=str))
        log.write("\n")


def start_execution(input_payload):
    response = stepfn.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps(input_payload)
    )
    return response["executionArn"]


def check_execution_status(execution_arn):
    while True:
        response = stepfn.describe_execution(executionArn=execution_arn)
        status = response["status"]

        print(f"Current Status: {status}")

        if status in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
            return response

        time.sleep(2)


def main():
    # ✅ Read file
    file_content = read_input_file("input/test_input.txt")

    input_payload = {
        "input_text": file_content
    }

    print("🚀 Starting Step Function execution...")

    execution_arn = start_execution(input_payload)
    print(f"Execution ARN: {execution_arn}")

    print("⏳ Waiting for execution to complete...")

    result = check_execution_status(execution_arn)

    print("\n✅ Final Execution Result:")
    print(json.dumps(result, indent=2, default=str))

    # ✅ Log result to file
    log_result({
        "executionArn": execution_arn,
        "input": input_payload,
        "result": result
    })

    print(f"\n📝 Logged execution details to {LOG_FILE}")


if __name__ == "__main__":
    main()