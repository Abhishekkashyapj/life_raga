# Hybrid RAG Frontend

Professional frontend interface for the Vector + Graph Hybrid Database system.

## Features

- **File Upload**: Drag & drop or click to upload documents (TXT, JSON, CSV, MD)
- **Three Retrieval Modes**:
  - Vector Search - Semantic similarity
  - Graph Search - Relationship traversal
  - Hybrid Search - Combined approach (Best accuracy)
- **Real-time Statistics**: View nodes, edges, and storage metrics
- **Search Results Display**: Shows scores, metadata, and relationships
- **Demo Data Loader**: Quick way to populate with sample data

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8001

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

## Usage

1. **Start Backend**: Make sure `python hybrid_db_api.py` is running
2. **Load Demo Data**: Click "Load Demo Data" button to populate the database
3. **Upload Documents**: Drag and drop files or click to browse
4. **Select Retrieval Mode**: Choose Vector, Graph, or Hybrid search
5. **Search**: Enter your query and click Search
6. **View Results**: See scores, metadata, and relationships

## Tech Stack

- React 19
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Lucide React Icons

## API Integration

All API calls are made to `http://localhost:8001`:

- `GET /health` - Health check
- `GET /stats` - Statistics
- `POST /upload` - File upload
- `POST /demo/populate` - Load demo data
- `POST /retrieve/local` - Vector search
- `POST /retrieve/global` - Graph search
- `POST /retrieve/hybrid` - Hybrid search

