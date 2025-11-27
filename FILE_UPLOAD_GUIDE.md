# File Upload Feature - Implementation Guide

## ✅ What's New

The Hybrid Database API now supports **file uploads**! Users can upload files directly to the backend, and the system automatically processes them and creates nodes.

---

## 📋 Features Added

### 1. **File Upload Endpoint** `POST /upload`
Users can upload files in multiple formats:
- **Text files** (.txt, .md)
- **JSON files** (.json)
- **CSV files** (.csv)

### 2. **Automatic Processing**
- Each line/entry in the uploaded file becomes a node
- 768-dimensional embeddings are automatically created
- Files are stored locally in `./rag_local/uploads/`
- Metadata tracks the source file and position

### 3. **Web Interface** (HTML)
- Beautiful drag-and-drop file upload interface
- Real-time feedback on upload status
- Supports file validation
- Shows number of nodes created

---

## 🚀 How to Use

### **Option 1: Web Interface (Easiest)**

1. **Start the server:**
```bash
python hybrid_db_api.py
```

2. **Open the upload interface:**
```
file:///path/to/upload_interface.html
```

3. **Upload a file:**
   - Drag and drop into the box
   - Or click to browse
   - Click "Upload & Process"

### **Option 2: API (Programmatic)**

```python
import requests

# Upload a file
with open('your_file.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8001/upload', files=files)
    
print(response.json())
# Output:
# {
#     "filename": "your_file.txt",
#     "file_type": ".txt",
#     "status": "success",
#     "nodes_created": 10,
#     "size_bytes": 512,
#     "location": "./rag_local/uploads/your_file.txt"
# }
```

### **Option 3: curl Command**

```bash
curl -X POST -F "file=@your_file.txt" http://localhost:8001/upload
```

---

## 📁 File Format Examples

### **Text File (.txt)**
```
This is line 1 - becomes a node
This is line 2 - becomes another node
Each paragraph becomes a separate node
```

### **JSON File (.json)**
```json
{
  "title": "Document Title",
  "content": "This becomes a node",
  "sections": [
    "Section 1 becomes a node",
    "Section 2 becomes a node"
  ]
}
```

### **CSV File (.csv)**
```
Name,Description
Item1,This becomes a node
Item2,This also becomes a node
Item3,And this one too
```

---

## 💾 Data Storage

### **Uploaded Files**
- Location: `./rag_local/uploads/`
- Persists locally on your machine
- Works offline completely

### **Vector Nodes**
- Location: `./rag_local/hybrid_vectors.json`
- Contains 768-dimensional embeddings
- Metadata includes file source

### **Search**
After uploading, use hybrid search to find content:

```python
# Search uploaded data
response = requests.post('http://localhost:8001/search/hybrid', json={
    "query_text": "search term",
    "top_k": 5
})
```

---

## 🔒 Offline Capability

**The file upload feature works completely offline!**

- Upload files without WiFi
- Process them locally
- Store them locally
- Search them locally
- Everything stays on your machine ✅

---

## 📊 API Response

```json
{
  "filename": "document.txt",
  "file_type": ".txt",
  "status": "success",
  "nodes_created": 25,
  "size_bytes": 2048,
  "location": "./rag_local/uploads/document.txt"
}
```

---

## 🛠️ Technical Details

### **Supported File Types**
| Type | Extension | Processing |
|------|-----------|-----------|
| Text | .txt | Line-by-line |
| Markdown | .md | Line-by-line |
| JSON | .json | Key-value extraction |
| CSV | .csv | Line-by-line |

### **Node Metadata**
Each uploaded node includes:
```json
{
  "text": "Content from file",
  "embedding": [768-dimensional vector],
  "metadata": {
    "source": "file_upload",
    "file_name": "example.txt",
    "line_index": 0
  }
}
```

---

## 📈 Workflow

```
User uploads file
        ↓
Backend receives file
        ↓
File is saved locally in ./rag_local/uploads/
        ↓
Content is extracted (line by line or structured)
        ↓
Each entry → creates vector embedding
        ↓
Node stored in ./rag_local/hybrid_vectors.json
        ↓
Available for search and analysis
```

---

## ✨ Example Use Cases

1. **Documentation Management**
   - Upload API docs
   - Upload README files
   - Search across all documentation

2. **Data Processing**
   - Upload CSV data
   - Auto-index all rows
   - Perform hybrid search

3. **Knowledge Base**
   - Upload articles
   - Upload research papers
   - Upload customer feedback

4. **Offline Data Analysis**
   - Load local files
   - Create vector embeddings
   - No internet required ✅

---

## 🚨 Troubleshooting

### **Error: Connection refused**
- Make sure server is running: `python hybrid_db_api.py`
- Check port 8001 is available
- Try on `http://localhost:8001`

### **Error: File too large**
- Current implementation handles files up to server limits
- Split large files into smaller chunks

### **No nodes created**
- Ensure file is in supported format
- Check file contains text content
- Verify lines are longer than 10 characters

---

## 🎯 Next Steps

1. ✅ Start the API server
2. ✅ Upload your first file
3. ✅ Search the uploaded data
4. ✅ Create relationships between nodes
5. ✅ Use hybrid search across all data

**Everything works offline! No WiFi needed after server starts.** 🔒

