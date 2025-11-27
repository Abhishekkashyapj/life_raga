export default function CTA() {
  return (
    <section className="relative py-20 px-6 bg-gradient-to-r from-teal-900/20 to-cyan-900/20 border-t border-slate-700/50">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Ready to Get Started?
        </h2>
        <p className="text-xl text-slate-300 mb-10 leading-relaxed">
          Deploy Hybrid RAG Explorer locally in minutes. No cloud dependencies, no API keys, complete privacy and control over your data.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="px-8 py-4 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-600 text-white font-semibold text-lg hover:shadow-2xl hover:shadow-teal-500/30 transition-all duration-300 hover:scale-105 cursor-pointer">
            🚀 Launch Now
          </button>
          <button className="px-8 py-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold text-lg hover:bg-white/20 transition-all cursor-pointer">
            📖 Read Documentation
          </button>
        </div>
      </div>
    </section>
  );
}
