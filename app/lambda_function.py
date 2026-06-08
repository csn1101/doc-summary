import json
import boto3
import os

stepfn = boto3.client("stepfunctions")

STATE_MACHINE_ARN = os.environ["STEP_FN_ARN"]


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # ✅ Case 1: S3 trigger → start Step Function
    if "Records" in event:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"Triggering Step Function for {bucket}/{key}")

        input_payload = {
            "bucket": bucket,
            "key": key
        }

        response = stepfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(input_payload)
        )

        return {
            "statusCode": 200,
            "message": "Step Function started",
            "executionArn": response["executionArn"]
        }

    # ✅ Case 2: Step Function test mode (existing)
    elif "input_text" in event:
        input_text = event["input_text"]
        summary = input_text[:50]

        return {
            "statusCode": 200,
            "summary": summary
        }

    # ✅ ✅ Case 3: Step Function → processing S3 file (YOU ADD THIS HERE)
    elif "bucket" in event and "key" in event:
        bucket = event["bucket"]
        key = event["key"]

        print(f"Processing file from Step Function: {bucket}/{key}")

        # TODO: fetch file from S3 and process
        return {
            "statusCode": 200,
            "message": "Processed via Step Function"
        }

    # ✅ fallback
    else:
        return {
            "statusCode": 400,
            "error": "Invalid input format"
        }