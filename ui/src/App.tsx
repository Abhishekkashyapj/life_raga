import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/home/page'
import Sidebar from './components/Sidebar'
import MainContent from './components/MainContent'
import { motion } from 'framer-motion'

const API_BASE_URL = 'http://localhost:8001'

export interface Stats {
  total_nodes: number
  total_edges: number
  vector_storage_size: number
  graph_storage_size: number
}

export interface SearchResult {
  node_id: string
  text: string
  vector_score?: string | number
  graph_score?: string | number
  hybrid_score?: string | number
  similarity_score?: number
  source: string
  metadata?: Record<string, any>
  relevance?: number
}

export interface SearchResponse {
  mode: string
  query: string
  results: SearchResult[]
  total_candidates?: number
  total_found?: number
  confidence?: string | number
  latency_ms?: string
  relationships?: Array<{
    source: string
    target: string
    type: string
  }>
  entities_found?: number
  reachable_nodes?: number
  matching_entities?: Array<{
    node_id: string
    text: string
    relevance: number
  }>
}

function AppContent() {
  const [retrievalMode, setRetrievalMode] = useState<'vector' | 'graph' | 'hybrid'>('hybrid')
  const [stats, setStats] = useState<Stats | null>(null)
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Fetch stats on mount and after operations
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`)
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    try {
      const endpoint = 
        retrievalMode === 'vector' ? '/retrieve/local' :
        retrievalMode === 'graph' ? '/retrieve/global' :
        '/retrieve/hybrid'
      
      const body: any = {
        query_text: query,
        top_k: 5
      }

      if (retrievalMode === 'hybrid') {
        body.vector_weight = 0.6
        body.graph_weight = 0.4
      } else if (retrievalMode === 'graph') {
        body.depth = 2
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (response.ok) {
        const data = await response.json()
        
        // Normalize different response formats
        let normalizedData = { ...data }
        
        // Handle local/vector search format
        if (data.mode === 'local' && data.results) {
          normalizedData.results = data.results.map((r: any) => ({
            ...r,
            vector_score: r.similarity_score,
            source: r.source || 'vector_db'
          }))
        }
        
        // Handle global/graph search format
        if (data.mode === 'global') {
          normalizedData.results = data.matching_entities?.map((ent: any) => ({
            node_id: ent.node_id,
            text: ent.text,
            graph_score: ent.relevance,
            source: 'graph_db',
            metadata: {}
          })) || []
        }
        
        setSearchResults(normalizedData)
        await fetchStats() // Refresh stats after search
      } else {
        const errorText = await response.text()
        throw new Error(`Search failed: ${errorText}`)
      }
    } catch (error) {
      console.error('Search error:', error)
      alert('Search failed. Please check if the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        alert(`File uploaded successfully! ${data.nodes_created} nodes created.`)
        await fetchStats()
      } else {
        throw new Error('Upload failed')
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed. Please check if the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoData = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/demo/populate`, {
        method: 'POST'
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Demo data loaded! ${data.nodes_created} nodes and ${data.edges_created} edges created.`)
        await fetchStats()
      } else {
        throw new Error('Failed to load demo data')
      }
    } catch (error) {
      console.error('Demo data error:', error)
      alert('Failed to load demo data. Please check if the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div 
      className="h-screen w-screen flex bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Sidebar
        retrievalMode={retrievalMode}
        setRetrievalMode={setRetrievalMode}
        stats={stats}
        onDemoData={handleDemoData}
        onFileUpload={handleFileUpload}
        isLoading={isLoading}
      />
      <MainContent
        retrievalMode={retrievalMode}
        onSearch={handleSearch}
        searchResults={searchResults}
        isLoading={isLoading}
      />
    </motion.div>
  )
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/explore" element={<AppContent />} />
      </Routes>
    </Router>
  )
}
export default App
