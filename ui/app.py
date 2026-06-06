from flask import Flask, request, render_template
import boto3
import uuid
import datetime

app = Flask(__name__)

# ✅ Change env if needed
ENV = "dev"

BUCKET_NAME = f"599626541533-ap-south-1-{ENV}-doc-summary-input"

s3 = boto3.client("s3")


def generate_key(filename):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    uid = str(uuid.uuid4())[:8]
    return f"{timestamp}-{uid}-{filename}"


@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]

        if file:
            key = generate_key(file.filename)
            s3.upload_fileobj(file, BUCKET_NAME, key)

            return f"✅ Uploaded to S3:<br>s3://{BUCKET_NAME}/{key}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)