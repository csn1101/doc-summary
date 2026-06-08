from flask import Flask, request, render_template
import boto3
import uuid
import datetime
import time

app = Flask(__name__)

ENV = "dev"
REGION = "ap-south-1"

INPUT_BUCKET = f"599626541533-{REGION}-{ENV}-doc-summary-input"
OUTPUT_BUCKET = f"599626541533-{REGION}-{ENV}-doc-summary-output"

s3 = boto3.client("s3", region_name=REGION)


def generate_key(filename):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    uid = str(uuid.uuid4())[:8]
    return f"{timestamp}-{uid}-{filename}"


def get_latest_output():
    response = s3.list_objects_v2(Bucket=OUTPUT_BUCKET)

    if "Contents" not in response:
        return "⚠️ No output found yet"

    # Sort by latest file
    latest = sorted(
        response["Contents"],
        key=lambda x: x["LastModified"]
    )[-1]["Key"]

    obj = s3.get_object(Bucket=OUTPUT_BUCKET, Key=latest)
    content = obj["Body"].read().decode("utf-8")

    return content


@app.route("/", methods=["GET", "POST"])
def upload():
    result = None

    if request.method == "POST":
        file = request.files["file"]

        if file:
            key = generate_key(file.filename)

            # ✅ Upload file
            s3.upload_fileobj(file, INPUT_BUCKET, key)

            # ✅ Give pipeline some time to process
            time.sleep(5)

            # ✅ Fetch output
            result = get_latest_output()

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)