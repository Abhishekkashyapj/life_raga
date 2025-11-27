export default function UseCases() {
  const usecases = [
    {
      icon: '📚',
      title: 'Research & Academia',
      description: 'Index research papers, books, and academic articles for intelligent literature review and discovery'
    },
    {
      icon: '🏢',
      title: 'Enterprise Knowledge',
      description: 'Centralize company documentation, policies, and procedures for instant intelligent search'
    },
    {
      icon: '🤖',
      title: 'AI Assistants',
      description: 'Build custom AI assistants and chatbots grounded in your specific documents and knowledge'
    },
    {
      icon: '📰',
      title: 'Content Analysis',
      description: 'Extract insights from news, blog posts, and social media content automatically'
    },
    {
      icon: '⚖️',
      title: 'Legal & Compliance',
      description: 'Search through legal documents, contracts, and compliance materials effortlessly'
    },
    {
      icon: '🔬',
      title: 'Data Science',
      description: 'Organize and retrieve scientific data, experiment notes, and research findings efficiently'
    }
  ];

  return (
    <section id="use-cases" className="relative py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Use Cases
          </h2>
          <p className="text-xl text-slate-400">
            Versatile solution for any knowledge management need
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {usecases.map((usecase, idx) => (
            <div
              key={idx}
              className="bg-gradient-to-br from-slate-800/30 to-slate-900/30 border border-slate-700/50 rounded-xl p-6 hover:from-teal-900/20 hover:to-cyan-900/20 transition-all duration-300"
            >
              <div className="text-4xl mb-3">{usecase.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2">{usecase.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{usecase.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
