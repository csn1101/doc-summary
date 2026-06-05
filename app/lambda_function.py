import json

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # ✅ Case 1: S3 event trigger
    if "Records" in event:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"S3 Trigger → Bucket: {bucket}, Key: {key}")

        # existing logic here
        return {
            "statusCode": 200,
            "body": "Processed via S3 trigger"
        }

    # ✅ Case 2: Step Function input
    elif "input_text" in event:
        input_text = event["input_text"]

        print(f"Step Function Trigger → Input: {input_text}")

        # simulate processing (replace with your logic)
        summary = input_text[:50]

        return {
            "statusCode": 200,
            "summary": summary
        }

    else:
        return {
            "statusCode": 400,
            "error": "Invalid input format"
        }