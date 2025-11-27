export default function HowItWorks() {
  const steps = [
    {
      number: '01',
      title: 'Upload Documents',
      description: 'Upload PDFs, TXT, JSON or CSV files. The system automatically processes and extracts text content.'
    },
    {
      number: '02',
      title: 'Create Embeddings',
      description: 'Documents are converted into vector embeddings using ChromaDB for semantic understanding.'
    },
    {
      number: '03',
      title: 'Build Knowledge Graph',
      description: 'Entities and relationships are extracted and stored in Neo4j for structural understanding.'
    },
    {
      number: '04',
      title: 'Search Intelligently',
      description: 'Query your documents using vector search, graph traversal, or hybrid search for best results.'
    }
  ];

  return (
    <section id="how-it-works" className="relative py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            How It Works
          </h2>
          <p className="text-xl text-slate-400">
            A simple 4-step process to intelligent document retrieval
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, idx) => (
            <div key={idx} className="relative">
              <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-xl p-6 h-full">
                <div className="text-4xl font-bold bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent mb-4">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">{step.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{step.description}</p>
              </div>
              {idx < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-0.5 bg-gradient-to-r from-teal-500 to-cyan-500 transform -translate-y-1/2"></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
