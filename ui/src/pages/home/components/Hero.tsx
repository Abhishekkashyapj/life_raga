import { useEffect, useState } from 'react';
import Navbar from './Navbar';

export default function Hero() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="relative min-h-screen flex flex-col bg-gradient-to-b from-slate-900 via-slate-900/50 to-black">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-teal-500/20 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-cyan-500/20 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-purple-500/20 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
      </div>

      <Navbar scrolled={scrolled} />

      <div className="relative z-10 flex-1 flex items-center">
        <div className="w-full max-w-7xl mx-auto px-6 py-20 text-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-500/10 border border-teal-500/20 backdrop-blur-sm">
              <div className="w-2 h-2 rounded-full bg-teal-400 animate-pulse"></div>
              <span className="text-sm text-teal-300 font-medium">Powered by ChromaDB, Neo4j & Ollama</span>
            </div>

            <h1 className="text-6xl md:text-7xl font-bold text-white leading-tight">
              Hybrid RAG<br />
              <span className="bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">
                Explorer
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
              Combine the power of vector search and knowledge graphs for intelligent document retrieval with local AI models
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
              <button className="px-8 py-4 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-600 text-white font-semibold text-lg hover:shadow-2xl hover:shadow-teal-500/30 transition-all duration-300 hover:scale-105 cursor-pointer whitespace-nowrap">
                🚀 Get Started Free
              </button>
              <button className="px-8 py-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold text-lg hover:bg-white/20 transition-all cursor-pointer whitespace-nowrap">
                ▶️ Watch Demo
              </button>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-6 pt-8 text-sm text-slate-400">
              <div className="flex items-center gap-2">
                <span className="text-teal-400">✓</span>
                <span>No API Keys Required</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-teal-400">✓</span>
                <span>100% Local Processing</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-teal-400">✓</span>
                <span>Open Source</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Card */}
      <div className="relative z-10 pb-12">
        <div className="w-full max-w-6xl mx-auto px-6">
          <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-2 shadow-2xl overflow-hidden">
            <div className="bg-gradient-to-b from-slate-700/20 to-slate-900/20 rounded-xl p-8">
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="bg-slate-700/30 rounded-lg p-4">
                  <div className="text-teal-400 font-semibold mb-2">📊 83 Nodes</div>
                  <div className="text-slate-400 text-xs">Vector embeddings</div>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4">
                  <div className="text-cyan-400 font-semibold mb-2">🔗 0 Edges</div>
                  <div className="text-slate-400 text-xs">Graph relationships</div>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4">
                  <div className="text-purple-400 font-semibold mb-2">⚡ Hybrid</div>
                  <div className="text-slate-400 text-xs">Search Mode</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
