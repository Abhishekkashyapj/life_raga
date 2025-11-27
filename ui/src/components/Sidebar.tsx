import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Upload, Database, BarChart3, Sparkles, Network, Layers, Loader2 } from 'lucide-react'
import { Stats } from '../App'

interface SidebarProps {
  retrievalMode: 'vector' | 'graph' | 'hybrid'
  setRetrievalMode: (mode: 'vector' | 'graph' | 'hybrid') => void
  stats: Stats | null
  onDemoData: () => void
  onFileUpload: (file: File) => void
  isLoading: boolean
}

export default function Sidebar({
  retrievalMode,
  setRetrievalMode,
  stats,
  onDemoData,
  onFileUpload,
  isLoading
}: SidebarProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      onFileUpload(file)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileUpload(file)
    }
  }

  const modes = [
    {
      id: 'vector' as const,
      name: 'Vector Search',
      description: 'Semantic similarity',
      icon: Layers,
      color: 'from-cyan-500 to-blue-600'
    },
    {
      id: 'graph' as const,
      name: 'Graph Search',
      description: 'Relationship traversal',
      icon: Network,
      color: 'from-purple-500 to-pink-600'
    },
    {
      id: 'hybrid' as const,
      name: 'Hybrid Search',
      description: 'Best accuracy ⭐',
      icon: Sparkles,
      color: 'from-orange-500 to-red-600'
    }
  ]

  return (
    <div className="w-80 bg-slate-900/50 border-r border-slate-800 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 via-purple-500 to-pink-500 flex items-center justify-center">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Hybrid RAG
            </h1>
            <p className="text-xs text-slate-400">Vector + Graph Database</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Retrieval Mode Selection */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Retrieval Mode</h3>
          <div className="space-y-2">
            {modes.map((mode) => {
              const Icon = mode.icon
              const isActive = retrievalMode === mode.id
              return (
                <button
                  key={mode.id}
                  onClick={() => setRetrievalMode(mode.id)}
                  className={`w-full p-3 rounded-lg text-left transition-all duration-300 ${
                    isActive
                      ? `bg-gradient-to-r ${mode.color} shadow-lg`
                      : 'bg-slate-800/50 hover:bg-slate-800 border border-slate-700/30'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <div className="flex-1">
                      <div className={`text-sm font-semibold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                        {mode.name}
                      </div>
                      <div className={`text-xs ${isActive ? 'text-white/80' : 'text-slate-500'}`}>
                        {mode.description}
                      </div>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* File Upload */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3">Upload Document</h3>
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              isDragging
                ? 'border-cyan-400 bg-cyan-400/10'
                : 'border-slate-700 hover:border-slate-600'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="w-8 h-8 mx-auto mb-2 text-slate-400" />
            <p className="text-sm text-slate-400 mb-2">Drop file here or click</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-xs text-cyan-400 hover:text-cyan-300"
              disabled={isLoading}
            >
              Browse Files
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.json,.csv,.md"
              onChange={handleFileSelect}
              className="hidden"
            />
            <p className="text-xs text-slate-500 mt-2">Supported: TXT, JSON, CSV, MD</p>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div>
            <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Statistics
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center p-2 bg-slate-800/30 rounded">
                <span className="text-xs text-slate-400">Nodes</span>
                <span className="text-sm font-bold text-cyan-400">{stats.total_nodes}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-slate-800/30 rounded">
                <span className="text-xs text-slate-400">Edges</span>
                <span className="text-sm font-bold text-purple-400">{stats.total_edges}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-slate-800/30 rounded">
                <span className="text-xs text-slate-400">Vector Storage</span>
                <span className="text-xs font-mono text-slate-400">
                  {(stats.vector_storage_size / 1024).toFixed(1)} KB
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-slate-800/30 rounded">
                <span className="text-xs text-slate-400">Graph Storage</span>
                <span className="text-xs font-mono text-slate-400">
                  {(stats.graph_storage_size / 1024).toFixed(1)} KB
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Demo Data Button */}
        <button
          onClick={onDemoData}
          disabled={isLoading}
          className="w-full p-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg text-white font-medium text-sm hover:shadow-lg hover:shadow-purple-500/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Load Demo Data
            </>
          )}
        </button>
      </div>
    </div>
  )
}
