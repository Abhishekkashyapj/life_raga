# 🔍 Retrieval System Guide

## Overview

Your Hybrid Database now supports **3 powerful retrieval modes**:

1. **Local (Vector-only)** - Pure semantic similarity
2. **Global (Graph-only)** - Entity relationships 
3. **Hybrid (Vector + Graph)** - Combined (BEST) ⭐

---

## 📊 Retrieval Modes Explained

### **1️⃣ LOCAL RETRIEVAL (Vector-only)**

Uses ChromaDB-style semantic embeddings.

**Use cases:**
- Pure semantic questions
- Similarity search
- Document matching
- Content-based search

**Request:**
```json
POST /retrieve/local
{
  "query_text": "Who is Sundar Pichai?",
  "top_k": 5
}
```

**Response:**
```json
{
  "mode": "local",
  "query": "Who is Sundar Pichai?",
  "results": [
    {
      "node_id": "node-0",
      "text": "Sundar Pichai is CEO of Google",
      "similarity_score": 0.8456,
      "source": "vector_db"
    }
  ],
  "confidence": 0.8456,
  "latency_ms": "12.34"
}
```

**When to use:**
- ✅ User asks: "What is machine learning?"
- ✅ User asks: "Explain neural networks"
- ✅ Similar document retrieval
- ❌ NOT good for: "Who works where?"

---

### **2️⃣ GLOBAL RETRIEVAL (Graph-only)**

Uses Neo4j-style relationship graphs.

**Use cases:**
- Entity questions
- Relationship queries
- Knowledge graph reasoning
- Network analysis

**Request:**
```json
POST /retrieve/global
{
  "query_text": "What companies does Google own?",
  "depth": 2
}
```

**Response:**
```json
{
  "mode": "global",
  "query": "What companies does Google own?",
  "entities_found": 3,
  "reachable_nodes": 8,
  "relationships": [
    {
      "source": "node-0",
      "target": "node-3",
      "type": "OWNS",
      "weight": 1.0
    }
  ],
  "matching_entities": [
    {
      "node_id": "node-0",
      "text": "Google owns YouTube",
      "relevance": 0.667
    }
  ],
  "latency_ms": "8.56"
}
```

**When to use:**
- ✅ User asks: "Who founded SpaceX?"
- ✅ User asks: "What's the relationship between X and Y?"
- ✅ User asks: "Show me connected entities"
- ❌ NOT good for: "Describe deep learning"

---

### **3️⃣ HYBRID RETRIEVAL (Vector + Graph) ⭐ BEST**

Combines both vector and graph signals.

**Use cases:**
- General questions (any type)
- Complex reasoning
- Maximum accuracy
- Production queries

**Request:**
```json
POST /retrieve/hybrid
{
  "query_text": "Where is Google headquartered?",
  "top_k": 5,
  "vector_weight": 0.6,
  "graph_weight": 0.4,
  "do_rerank": true
}
```

**Response:**
```json
{
  "mode": "hybrid",
  "query": "Where is Google headquartered?",
  "results": [
    {
      "node_id": "node-1",
      "text": "Google is headquartered in Mountain View, California",
      "vector_score": "0.7823",
      "graph_score": "0.6543",
      "hybrid_score": "0.7289",
      "source": "hybrid"
    }
  ],
  "confidence": "0.7289",
  "vector_weight": 0.6,
  "graph_weight": 0.4,
  "latency_ms": "28.45",
  "description": "Hybrid search combining vector + graph (BEST ACCURACY) ⭐"
}
```

**When to use:**
- ✅ **Use 90% of the time** - Best accuracy
- ✅ User asks anything
- ✅ Production queries
- ✅ Complex reasoning needed

---

## 🎯 Retrieval Comparison Table

| Aspect | Local (Vector) | Global (Graph) | Hybrid (Best) |
|--------|---|---|---|
| **Best for** | Semantic similarity | Entity relationships | Everything |
| **Accuracy** | Good | Good | **Excellent** ⭐ |
| **Speed** | Fast | Medium | Medium |
| **Complexity** | Simple | Medium | Complex |
| **Production ready** | ✓ | ✓ | ✓✓✓ |
| **Recommendation** | 10% | 10% | **80%** |

---

## 📈 Score Breakdown (Hybrid Mode)

In hybrid mode, final score is calculated as:

```
Hybrid Score = (Vector Score × 0.6) + (Graph Score × 0.4)
```

**Example:**
```
Vector Score: 0.75 (strong semantic match)
Graph Score:  0.60 (connected in graph)
---
Hybrid = (0.75 × 0.6) + (0.60 × 0.4)
Hybrid = 0.45 + 0.24 = 0.69
```

**Customize weights:**
```json
{
  "vector_weight": 0.7,   // Increase for more semantic focus
  "graph_weight": 0.3     // Increase for more entity focus
}
```

---

## 🔧 Advanced Features

### **Reranking**

Enable semantic reranking for better results:

```json
POST /retrieve/hybrid
{
  "query_text": "Your question",
  "do_rerank": true
}
```

Reranking uses semantic relevance to re-order results. Slightly slower but more accurate.

### **Custom Weights**

Adjust vector vs graph emphasis:

```json
// For entity-heavy queries
{
  "vector_weight": 0.4,
  "graph_weight": 0.6
}

// For semantic-heavy queries
{
  "vector_weight": 0.8,
  "graph_weight": 0.2
}
```

### **Depth Control** (Graph only)

Control how far to traverse the graph:

```json
// Shallow search (fast)
{ "depth": 1 }

// Medium search (balanced)
{ "depth": 2 }

// Deep search (comprehensive)
{ "depth": 3 }
```

---

## 💡 Usage Examples

### **Example 1: CEO Question**

**User:** "Who is the CEO of Google?"

**Best approach:** Hybrid with balanced weights

```python
import requests

response = requests.post(
    'http://localhost:8001/retrieve/hybrid',
    json={
        "query_text": "Who is the CEO of Google?",
        "top_k": 3,
        "vector_weight": 0.5,
        "graph_weight": 0.5
    }
)
```

---

### **Example 2: Document Search**

**User:** "Find documents about machine learning"

**Best approach:** Local (vector) search

```python
response = requests.post(
    'http://localhost:8001/retrieve/local',
    json={
        "query_text": "Find documents about machine learning",
        "top_k": 10
    }
)
```

---

### **Example 3: Network Analysis**

**User:** "Show connections between companies"

**Best approach:** Global (graph) search

```python
response = requests.post(
    'http://localhost:8001/retrieve/global',
    json={
        "query_text": "Show connections between companies",
        "depth": 3
    }
)
```

---

### **Example 4: General Question**

**User:** "Tell me everything about Elon Musk"

**Best approach:** Hybrid with deep settings

```python
response = requests.post(
    'http://localhost:8001/retrieve/hybrid',
    json={
        "query_text": "Tell me everything about Elon Musk",
        "top_k": 10,
        "vector_weight": 0.6,
        "graph_weight": 0.4,
        "do_rerank": True
    }
)
```

---

## 📊 Latency Expectations

| Mode | Typical Latency | Best Case | Worst Case |
|------|---|---|---|
| **Local** | 10-15ms | 5ms | 30ms |
| **Global** | 15-25ms | 8ms | 50ms |
| **Hybrid** | 20-40ms | 12ms | 75ms |

*Latencies depend on dataset size and graph depth*

---

## ✅ Best Practices

1. **Use Hybrid by default** - It's the safest choice
2. **Start with top_k=5** - Adjust based on results
3. **Monitor latency** - Optimize weights if too slow
4. **Enable reranking for production** - Better quality
5. **Test all 3 modes** - Understand your data
6. **Cache results** - For repeated queries
7. **Adjust weights per domain** - Different domains need different balances

---

## 🚀 Getting Started

### **1. Start the server:**
```bash
python hybrid_db_api.py
```

### **2. Populate with demo data:**
```bash
curl -X POST http://localhost:8001/demo/populate
```

### **3. Try each retrieval mode:**

**Local:**
```bash
curl -X POST http://localhost:8001/retrieve/local \
  -H "Content-Type: application/json" \
  -d '{"query_text":"Who founded SpaceX?","top_k":5}'
```

**Global:**
```bash
curl -X POST http://localhost:8001/retrieve/global \
  -H "Content-Type: application/json" \
  -d '{"query_text":"What companies are related?","depth":2}'
```

**Hybrid (BEST):**
```bash
curl -X POST http://localhost:8001/retrieve/hybrid \
  -H "Content-Type: application/json" \
  -d '{"query_text":"Tell me about Elon Musk","top_k":10,"do_rerank":true}'
```

---

## 🎓 Key Takeaways

- ✅ **Local mode** = Vector search (semantic)
- ✅ **Global mode** = Graph search (relationships)
- ✅ **Hybrid mode** = Both combined (BEST)
- ✅ Use hybrid for 90% of queries
- ✅ Adjust weights and parameters as needed
- ✅ Monitor latency and quality
- ✅ All modes work offline

---

**Next step:** Use these endpoints in your application to build powerful retrieval-augmented generation (RAG) systems! 🚀

