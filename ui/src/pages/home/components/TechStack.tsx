export default function TechStack() {
  const techs = [
    { name: 'ChromaDB', category: 'Vector Database', icon: '💾' },
    { name: 'Neo4j', category: 'Graph Database', icon: '🔗' },
    { name: 'Ollama', category: 'Local LLM', icon: '🧠' },
    { name: 'FastAPI', category: 'Backend Framework', icon: '⚡' },
    { name: 'React', category: 'Frontend Library', icon: '⚛️' },
    { name: 'Tailwind CSS', category: 'Styling', icon: '🎨' }
  ];

  return (
    <section id="tech-stack" className="relative py-20 px-6 bg-slate-900/50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Modern Tech Stack
          </h2>
          <p className="text-xl text-slate-400">
            Built with best-in-class open-source technologies
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {techs.map((tech, idx) => (
            <div
              key={idx}
              className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 hover:border-teal-500/50 transition-all text-center"
            >
              <div className="text-4xl mb-3">{tech.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-1">{tech.name}</h3>
              <p className="text-sm text-slate-400">{tech.category}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
