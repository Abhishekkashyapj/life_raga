# Quick Reference - File Upload Feature

## ⚡ Quick Start

```bash
# 1. Start server
python hybrid_db_api.py

# 2. Upload file via web UI
# Open: upload_interface.html
# Drag & drop file → Done!

# 3. Search uploaded data
curl http://localhost:8001/search/hybrid \
  -d '{"query_text": "search term", "top_k": 5}'
```

---

## 📤 Upload Methods

### **Web Interface (Easiest)**
- Open `upload_interface.html`
- Drag & drop files
- Beautiful UI with feedback

### **Python API**
```python
import requests
with open('file.txt', 'rb') as f:
    r = requests.post('http://localhost:8001/upload', files={'file': f})
    print(r.json())
```

### **curl**
```bash
curl -F "file=@file.txt" http://localhost:8001/upload
```

---

## 📁 Supported Formats

| Type | Extension |
|------|-----------|
| Text | `.txt` |
| Markdown | `.md` |
| JSON | `.json` |
| CSV | `.csv` |

---

## 💾 Storage

- **Uploaded files:** `./rag_local/uploads/`
- **Vector nodes:** `./rag_local/hybrid_vectors.json`
- **Relationships:** `./rag_local/hybrid_graph.json`
- **All local:** No internet needed ✅

---

## 🔍 Search Example

```python
# After uploading, search with:
import requests

response = requests.post(
    'http://localhost:8001/search/hybrid',
    json={
        "query_text": "your search term",
        "vector_weight": 0.6,
        "graph_weight": 0.4,
        "top_k": 5
    }
)

results = response.json()
for result in results['results']:
    print(f"{result['text']} - Score: {result['hybrid_score']}")
```

---

## ⚙️ Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/upload` | Upload file |
| POST | `/nodes` | Create node |
| GET | `/nodes` | List nodes |
| POST | `/search/hybrid` | Hybrid search |
| GET | `/stats` | System stats |

---

## ✨ Features

✅ Drag-and-drop upload
✅ Auto vector embedding (768-dim)
✅ Local file storage
✅ Metadata tracking
✅ Hybrid search
✅ 100% offline capable
✅ Beautiful web UI

---

## 🚨 Troubleshooting

**Connection refused?**
- Start server: `python hybrid_db_api.py`
- Check port 8001

**No nodes created?**
- File must have text lines
- Lines must be > 10 characters
- Check file encoding (UTF-8)

**Want offline?**
- Turn off WiFi
- Upload files
- Everything works locally! ✅

---

## 📊 Response Example

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

## 🎯 Workflow

```
Upload File
    ↓
Auto-process
    ↓
Create Nodes
    ↓
Search Results
    ↓
All Offline! 🔒
```

---

**That's it! Simple, powerful, offline-capable file uploads.** 🚀
