'use client';

import Link from 'next/link';
import { ArrowRight, Search, Bell, TrendingUp, Shield, Zap, Users } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Search className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">TenderLens</span>
            </div>
            <div className="flex gap-4">
              <Link href="/login" className="text-gray-600 hover:text-gray-900">Login</Link>
              <Link href="/register" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-20 pb-16 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6">Find the Perfect Tenders for Your Business</h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            AI-powered tender recommendations that match your expertise, location, and budget.
            Stop missing opportunities—let TenderLens find them for you.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/register" className="flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg font-semibold">
              Start Free Trial <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="#how-it-works" className="px-8 py-4 border-2 border-gray-300 rounded-lg hover:border-gray-400 text-lg font-semibold">
              See How It Works
            </Link>
          </div>
          <p className="mt-4 text-sm text-gray-500">No credit card • 14-day free trial • Cancel anytime</p>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 grid md:grid-cols-3 gap-8 text-center">
          <div><div className="text-4xl font-bold text-blue-600 mb-2">500+</div><div className="text-gray-600">Active Tenders</div></div>
          <div><div className="text-4xl font-bold text-blue-600 mb-2">95%</div><div className="text-gray-600">Match Accuracy</div></div>
          <div><div className="text-4xl font-bold text-blue-600 mb-2">24/7</div><div className="text-gray-600">Real-time Updates</div></div>
        </div>
      </section>

      {/* What is TenderLens */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">What is TenderLens?</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              TenderLens is an AI-powered tender discovery platform built for Ethiopian businesses.
              We use advanced machine learning to connect you with relevant procurement opportunities.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold mb-4">Stop Searching. Start Winning.</h3>
              <p className="text-gray-600 mb-6">
                Traditional tender hunting wastes hours searching portals for mismatched opportunities.
                TenderLens changes that.
              </p>
              <p className="text-gray-600">
                Our AI analyzes your profile—sectors, capabilities, regions, budget—to deliver
                personalized tender recommendations. Focus on winning bids, not finding them.
              </p>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-2xl space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Search className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold mb-1">Smart Discovery</h4>
                  <p className="text-sm text-gray-600">AI finds tenders you&apos;d never find manually</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Bell className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold mb-1">Real-time Alerts</h4>
                  <p className="text-sm text-gray-600">Notified when relevant tenders post</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold mb-1">Match Scoring</h4>
                  <p className="text-sm text-gray-600">See why each tender matches your profile</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-gray-50 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-600">Everything you need to discover, track, and win tenders</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: <Zap />, title: 'AI-Powered Matching', desc: 'BGE-M3 model analyzes semantic similarity for precise matches' },
              { icon: <Shield />, title: 'Multi-Sector Support', desc: 'IT, Construction, Healthcare, Manufacturing, and 15+ sectors' },
              { icon: <Bell />, title: 'Smart Alerts', desc: 'Customizable notifications—never miss a deadline' },
              { icon: <TrendingUp />, title: 'Match Insights', desc: 'Detailed reasons for each recommendation' },
              { icon: <Users />, title: 'Team Collaboration', desc: 'Invite members, assign tenders, track together' },
              { icon: <Search />, title: 'Advanced Filters', desc: 'Filter by budget, region, deadline, sector' }
            ].map((f, i) => (
              <div key={i} className="bg-white p-6 rounded-xl border hover:border-blue-300 hover:shadow-lg transition">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mb-4">{f.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-gray-600 text-sm">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How TenderLens Works</h2>
            <p className="text-xl text-gray-600">Get started in minutes, win in days</p>
          </div>
          <div className="grid md:grid-cols-4 gap-8 text-center">
            {[
              { n: '1', t: 'Create Profile', d: 'Tell us your sectors, regions, capabilities, budget' },
              { n: '2', t: 'AI Learns', d: 'ML model creates unique profile embedding' },
              { n: '3', t: 'Get Matches', d: 'Receive ranked recommendations with reasons' },
              { n: '4', t: 'Win Bids', d: 'Focus on right opportunities, grow business' }
            ].map(s => (
              <div key={s.n}>
                <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">{s.n}</div>
                <h3 className="text-lg font-semibold mb-2">{s.t}</h3>
                <p className="text-gray-600 text-sm">{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-blue-600 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Find Your Next Big Opportunity?</h2>
          <p className="text-xl text-blue-100 mb-8">Join hundreds of Ethiopian businesses winning more with TenderLens</p>
          <Link href="/register" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-gray-100 text-lg font-semibold">
            Start Your Free Trial <ArrowRight />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Search className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">TenderLens</span>
              </div>
              <p className="text-sm">AI-powered tender discovery for Ethiopian businesses</p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white">Features</Link></li>
                <li><Link href="#" className="hover:text-white">Pricing</Link></li>
                <li><Link href="#" className="hover:text-white">API</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white">About</Link></li>
                <li><Link href="#" className="hover:text-white">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white">Privacy</Link></li>
                <li><Link href="#" className="hover:text-white">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm">© 2026 TenderLens. All rights reserved.</p>
            <p className="text-sm">
              Built with care by <a href="https://techbloom.et" className="text-blue-400 hover:text-blue-300 font-semibold">TechBloom</a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
