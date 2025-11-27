import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Send, Loader2, TrendingUp, Network, Sparkles } from 'lucide-react'
import { SearchResponse } from '../App'

interface MainContentProps {
  retrievalMode: 'vector' | 'graph' | 'hybrid'
  onSearch: (query: string) => void
  searchResults: SearchResponse | null
  isLoading: boolean
}

export default function MainContent({
  retrievalMode,
  onSearch,
  searchResults,
  isLoading
}: MainContentProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !isLoading) {
      onSearch(query.trim())
    }
  }

  const getModeInfo = () => {
    switch (retrievalMode) {
      case 'vector':
        return {
          name: 'Vector Search',
          description: 'Semantic similarity using embeddings',
          icon: TrendingUp,
          color: 'from-cyan-500 to-blue-600'
        }
      case 'graph':
        return {
          name: 'Graph Search',
          description: 'Relationship traversal and reasoning',
          icon: Network,
          color: 'from-purple-500 to-pink-600'
        }
      case 'hybrid':
        return {
          name: 'Hybrid Search',
          description: 'Combined vector + graph (BEST ACCURACY)',
          icon: Sparkles,
          color: 'from-orange-500 to-red-600'
        }
    }
  }

  const modeInfo = getModeInfo()
  const ModeIcon = modeInfo.icon

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950">
      {/* Header */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${modeInfo.color} flex items-center justify-center`}>
            <ModeIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{modeInfo.name}</h2>
            <p className="text-sm text-slate-400">{modeInfo.description}</p>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="p-6">
        <form onSubmit={handleSubmit} className="relative">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query..."
              className="w-full pl-12 pr-32 py-4 bg-slate-900 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg text-white font-medium hover:shadow-lg hover:shadow-cyan-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Search
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence mode="wait">
          {!searchResults && !isLoading && (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex items-center justify-center"
            >
              <div className="text-center">
                <Search className="w-16 h-16 mx-auto mb-4 text-slate-700" />
                <p className="text-slate-400">Enter a query to search the database</p>
                <p className="text-sm text-slate-500 mt-2">
                  Try queries like "technology companies" or "AI research"
                </p>
              </div>
            </motion.div>
          )}

          {isLoading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="h-full flex items-center justify-center"
            >
              <div className="text-center">
                <Loader2 className="w-12 h-12 mx-auto mb-4 text-cyan-400 animate-spin" />
                <p className="text-slate-400">Searching...</p>
              </div>
            </motion.div>
          )}

          {searchResults && !isLoading && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Search Metadata */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                  <div className="text-xs text-slate-400 mb-1">Results Found</div>
                  <div className="text-2xl font-bold text-white">{searchResults.results.length}</div>
                </div>
                {(searchResults.total_candidates || searchResults.total_found) && (
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-400 mb-1">Total Candidates</div>
                    <div className="text-2xl font-bold text-white">{searchResults.total_candidates || searchResults.total_found}</div>
                  </div>
                )}
                {searchResults.entities_found && (
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-400 mb-1">Entities Found</div>
                    <div className="text-2xl font-bold text-white">{searchResults.entities_found}</div>
                  </div>
                )}
                {searchResults.reachable_nodes && (
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-400 mb-1">Reachable Nodes</div>
                    <div className="text-2xl font-bold text-white">{searchResults.reachable_nodes}</div>
                  </div>
                )}
                {searchResults.confidence !== undefined && (
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-400 mb-1">Confidence</div>
                    <div className="text-2xl font-bold text-green-400">
                      {(typeof searchResults.confidence === 'string' ? parseFloat(searchResults.confidence) : searchResults.confidence) * 100}%
                    </div>
                  </div>
                )}
                {searchResults.latency_ms && (
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-400 mb-1">Latency</div>
                    <div className="text-2xl font-bold text-cyan-400">{searchResults.latency_ms}ms</div>
                  </div>
                )}
              </div>

              {/* Results List */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Search Results</h3>
                {searchResults.results.map((result, index) => (
                  <motion.div
                    key={result.node_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 hover:border-slate-700 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-mono text-slate-400">{result.node_id}</span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            result.source === 'hybrid'
                              ? 'bg-orange-500/20 text-orange-400'
                              : result.source === 'vector'
                              ? 'bg-cyan-500/20 text-cyan-400'
                              : 'bg-purple-500/20 text-purple-400'
                          }`}>
                            {result.source}
                          </span>
                        </div>
                        <p className="text-white leading-relaxed">{result.text}</p>
                      </div>
                    </div>
                    
                    {/* Scores */}
                    <div className="flex gap-4 mt-4 pt-4 border-t border-slate-800">
                      {result.hybrid_score !== undefined && (
                        <div>
                          <div className="text-xs text-slate-400">Hybrid Score</div>
                          <div className="text-sm font-bold text-orange-400">
                            {(typeof result.hybrid_score === 'string' ? parseFloat(result.hybrid_score) : result.hybrid_score) * 100}%
                          </div>
                        </div>
                      )}
                      {result.vector_score !== undefined && (
                        <div>
                          <div className="text-xs text-slate-400">Vector Score</div>
                          <div className="text-sm font-bold text-cyan-400">
                            {(typeof result.vector_score === 'string' ? parseFloat(result.vector_score) : result.vector_score) * 100}%
                          </div>
                        </div>
                      )}
                      {result.graph_score !== undefined && (
                        <div>
                          <div className="text-xs text-slate-400">Graph Score</div>
                          <div className="text-sm font-bold text-purple-400">
                            {(typeof result.graph_score === 'string' ? parseFloat(result.graph_score) : result.graph_score) * 100}%
                          </div>
                        </div>
                      )}
                      {result.similarity_score !== undefined && (
                        <div>
                          <div className="text-xs text-slate-400">Similarity Score</div>
                          <div className="text-sm font-bold text-cyan-400">
                            {(result.similarity_score * 100).toFixed(1)}%
                          </div>
                        </div>
                      )}
                      {result.relevance !== undefined && (
                        <div>
                          <div className="text-xs text-slate-400">Relevance</div>
                          <div className="text-sm font-bold text-purple-400">
                            {(result.relevance * 100).toFixed(1)}%
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Metadata */}
                    {result.metadata && Object.keys(result.metadata).length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-800">
                        <div className="text-xs text-slate-400">Metadata:</div>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {Object.entries(result.metadata).map(([key, value]) => (
                            <span key={key} className="text-xs px-2 py-1 bg-slate-800 rounded text-slate-300">
                              {key}: {String(value)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>

              {/* Relationships */}
              {searchResults.relationships && searchResults.relationships.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Related Relationships</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {searchResults.relationships.map((rel, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: (searchResults.results.length + index) * 0.1 }}
                        className="bg-slate-900/50 border border-slate-800 rounded-lg p-4"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-mono text-cyan-400">{rel.source}</span>
                          <span className="text-slate-500">→</span>
                          <span className="text-sm text-purple-400">{rel.type}</span>
                          <span className="text-slate-500">→</span>
                          <span className="text-sm font-mono text-cyan-400">{rel.target}</span>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
