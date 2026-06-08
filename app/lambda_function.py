import json
import boto3
import os

# ✅ Clients
stepfn = boto3.client("stepfunctions")
s3 = boto3.client("s3")

# ✅ Environment variables
STATE_MACHINE_ARN = os.environ["STEP_FN_ARN"]
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # ✅ Case 1: S3 trigger → start Step Function
    if "Records" in event:
        record = event["Records"][0]
        input_bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"Triggering Step Function for {input_bucket}/{key}")

        input_payload = {
            "bucket": input_bucket,
            "key": key
        }

        response = stepfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(input_payload)
        )

        print("Step Function started:", response["executionArn"])

        return {
            "statusCode": 200,
            "message": "Step Function started",
            "executionArn": response["executionArn"]
        }

    # ✅ Case 2: Direct test mode (optional)
    elif "input_text" in event:
        input_text = event["input_text"]
        summary = input_text[:50]

        return {
            "statusCode": 200,
            "summary": summary
        }

    # ✅ ✅ Case 3: Step Function → process file
    elif "bucket" in event and "key" in event:
        input_bucket = event["bucket"]
        key = event["key"]

        print(f"Processing file from Step Function: {input_bucket}/{key}")
        print(f"Output bucket: {OUTPUT_BUCKET}")

        try:
            # ✅ Step 1 — Read file from input bucket
            obj = s3.get_object(Bucket=input_bucket, Key=key)
            content = obj["Body"].read().decode("utf-8")

            print("File content read successfully")

            # ✅ Step 2 — Simple summarization
            summary = content[:100]

            # ✅ Step 3 — Create output file name
            if key.endswith(".txt"):
                output_key = key.replace(".txt", "_summary.txt")
            else:
                output_key = key + "_summary.txt"

            # ✅ Step 4 — Write to OUTPUT bucket
            s3.put_object(
                Bucket=OUTPUT_BUCKET,   # ✅ IMPORTANT (NOT input bucket)
                Key=output_key,
                Body=summary.encode("utf-8")
            )

            print(f"✅ Summary saved to {OUTPUT_BUCKET}/{output_key}")

            return {
                "statusCode": 200,
                "message": "File processed successfully",
                "output_bucket": OUTPUT_BUCKET,
                "output_key": output_key
            }

        except Exception as e:
            print("❌ Error processing file:", str(e))

            return {
                "statusCode": 500,
                "error": str(e)
            }

    # ✅ fallback
    else:
        return {
            "statusCode": 400,
            "error": "Invalid input format"
        }