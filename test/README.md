## 🧪 System Testing & Validation

### 📌 Objective

To validate the end-to-end functionality of the document summarization pipeline using an automated test script.

---

### 🧭 Test Flow

```
Local Script → S3 Input → Lambda → S3 Output → Local Download
```

---

### 📂 Test Setup

```
test/
├── test_input.txt       # Sample input text
├── upload_test.py       # Automation script
├── requirements.txt     # Dependencies
├── output/              # Stores results
```

---

### ⚙️ Test Execution Steps

#### ✅ 1. Activate Virtual Environment

```bash
venv\Scripts\activate
```

---

#### ✅ 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

#### ✅ 3. Run Test Script

```bash
python upload_test.py
```

---

### 🧪 Test Input

Sample file (`test_input.txt`):

```
This is a document used for testing. It contains multiple sentences. The system should summarize this into a shorter version. This verifies the pipeline.
```

---

### ✅ Expected Behavior

1. File uploaded to input S3 bucket  
2. Lambda triggered automatically  
3. Text processed and summarized  
4. Output stored in output bucket  
5. Output downloaded locally  

---

### ✅ Sample Output

```
This is a document used for testing. It contains multiple sentences
```

---

### ✅ Naming Convention

Test files follow:

```
test_<description>.txt
```

Example:
```
test_doc_summary.txt
```

---

### ✅ Outcome

The test confirms:

- ✅ S3 event trigger working  
- ✅ Lambda execution successful  
- ✅ IAM permissions correctly configured  
- ✅ End-to-end pipeline functional  

---

### 🧠 Future Enhancements

- Add multiple test cases  
- Add automated validation checks  
- Integrate into CI/CD pipeline  
- Replace script with AWS Step Functions  

# ✅ Step Function Testing

## 📌 Objective

Validate and verify the execution of the AWS Step Function workflow that triggers Lambda processing.

This test ensures:

- Step Function execution starts correctly ✅  
- Lambda is invoked successfully ✅  
- Input and output handling works ✅  
- End-to-end workflow completes ✅  

---

## 📂 Test Files

| File | Purpose |
|------|--------|
| `test_input.txt` | Sample document for testing |
| `test_stepfn.py` | Script to trigger Step Function |
| `stepfn_test_log.txt` | Execution logs (ignored in Git) |

---

## 🚀 How to Run the Test

---

### ✅ Step 1 — Update Step Function ARN

In `test_stepfn.py`:

```python
STATE_MACHINE_ARN = "arn:aws:states:ap-south-1:599626541533:stateMachine:doc-summary-workflow"
```

---

### ✅ Step 2 — Run the script

```bash
python test/test_stepfn.py
```

---

## ✅ Expected Execution Flow

```
Test Script → Step Function → Lambda → Result ✅
```

---

## ✅ Sample Output

```
Starting Step Function execution...
Execution ARN: arn:...

Current Status: RUNNING
Current Status: SUCCEEDED

Final Execution Result:
{
  "status": "SUCCEEDED",
  ...
}
```

---

## ✅ Logging Mechanism

Each test execution is logged to:

```
test/stepfn_test_log.txt
```

---

### ✅ Log includes:

- Timestamp  
- Execution ARN  
- Input payload  
- Execution result  

---

### ✅ Example Log Entry

```
================================================================================
Timestamp: 2026-06-05 23:30:12

Execution ARN: arn:aws:states:...

Status: SUCCEEDED

Input:
"This is a document used for testing..."

Output:
{
  "summary": "This is a document..."
}
```

---

## ⚠️ Note

The log file is excluded from version control using `.gitignore`:

```
test/stepfn_test_log.txt
```

---

## ✅ Key Validation Points

| Check | Expected |
|------|----------|
| Execution status | SUCCEEDED ✅ |
| Lambda invoked | ✅ |
| Input passed correctly | ✅ |
| Output generated | ✅ |

---

## 🧠 Design Insight

This testing approach provides:

- ✅ Automated validation  
- ✅ Repeatable test runs  
- ✅ Local execution logs  
- ✅ Debugging traceability  

---

## ✅ Conclusion

The Step Function workflow is verified to:

- Execute successfully ✅  
- Integrate with Lambda correctly ✅  
- Handle input and produce output ✅  

---

## 🔮 Next Step

Workflow integration:

```
S3 → Step Function → Lambda ✅
```

This will replace the direct S3 → Lambda pipeline.