export default function Features() {
  const features = [
    {
      icon: '🔍',
      title: 'Vector Search',
      description: 'Semantic similarity search powered by ChromaDB embeddings for finding contextually relevant information'
    },
    {
      icon: '🔗',
      title: 'Knowledge Graphs',
      description: 'Relationship-based retrieval using Neo4j to understand connections between entities and concepts'
    },
    {
      icon: '⚡',
      title: 'Hybrid Retrieval',
      description: 'Combine vector and graph search for comprehensive results that leverage both semantic and structural knowledge'
    },
    {
      icon: '🧠',
      title: 'Local LLM',
      description: 'Run powerful language models locally with Ollama - no API keys, no data leaving your machine'
    },
    {
      icon: '🔒',
      title: 'Privacy First',
      description: 'All processing happens locally on your machine. Your documents and queries stay completely private'
    },
    {
      icon: '📊',
      title: 'Interactive Dashboard',
      description: 'Visualize your knowledge graphs, embeddings, and search results in real-time with an intuitive UI'
    }
  ];

  return (
    <section id="features" className="relative py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Powerful Features Built In
          </h2>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Everything you need for intelligent document retrieval and AI-powered search
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="group bg-slate-800/30 border border-slate-700/50 rounded-xl p-6 hover:border-teal-500/50 transition-all duration-300 hover:bg-slate-700/30"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
