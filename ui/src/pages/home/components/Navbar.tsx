interface NavbarProps {
  scrolled: boolean;
}

export default function Navbar({ scrolled }: NavbarProps) {
  return (
    <nav className={`relative z-20 transition-all duration-300 ${
      scrolled ? 'fixed top-0 left-0 right-0 bg-slate-900/95 backdrop-blur-xl border-b border-slate-800/50' : ''
    }`}>
      <div className="max-w-7xl mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center">
              <span className="text-xl text-white font-bold">⚡</span>
            </div>
            <span className="text-xl font-bold text-white">Hybrid RAG</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-slate-300 hover:text-white transition-colors cursor-pointer">Features</a>
            <a href="#how-it-works" className="text-slate-300 hover:text-white transition-colors cursor-pointer">How It Works</a>
            <a href="#tech-stack" className="text-slate-300 hover:text-white transition-colors cursor-pointer">Tech Stack</a>
            <a href="#use-cases" className="text-slate-300 hover:text-white transition-colors cursor-pointer">Use Cases</a>
          </div>
          <div className="flex items-center gap-4">
            <button className="px-6 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition-all cursor-pointer whitespace-nowrap">
              Documentation
            </button>
            <button className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-teal-500 to-cyan-600 text-white font-medium hover:shadow-lg hover:shadow-teal-500/20 transition-all cursor-pointer whitespace-nowrap">
              Try Now
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
