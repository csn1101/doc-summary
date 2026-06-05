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