import json
import boto3

s3 = boto3.client("s3")

def summarize(text):
    sentences = text.split(".")
    return ".".join(sentences[:2])  # basic summary

def lambda_handler(event, context):
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")

        summary = summarize(content)

        output_bucket = bucket.replace("input", "output")

        s3.put_object(
            Bucket=output_bucket,
            Key=key,
            Body=summary
        )

    return {
        "statusCode": 200,
        "body": json.dumps("Processed successfully")
    }