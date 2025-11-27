import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import TechStack from './components/TechStack';
import UseCases from './components/UseCases';
import CTA from './components/CTA';
import Footer from './components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-black">
      <Hero />
      <Features />
      <HowItWorks />
      <TechStack />
      <UseCases />
      <CTA />
      <Footer />
    </div>
  );
}
