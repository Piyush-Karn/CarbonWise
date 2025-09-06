import React, { useState, useEffect } from 'react';
import { Search, Leaf, Sparkles, ArrowRight, Globe, Zap, Shield, TrendingDown, Heart, Star, Award } from 'lucide-react';

export default function CarbonWiseLanding() {
  const [url, setUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [scrollY, setScrollY] = useState(0);
  const [particles, setParticles] = useState([]);

  // Scroll tracking for parallax effects
  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Generate floating particles
  useEffect(() => {
    const newParticles = Array.from({ length: 15 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 2,
      speed: Math.random() * 2 + 1,
      color: ['emerald', 'teal', 'green', 'lime'][Math.floor(Math.random() * 4)]
    }));
    setParticles(newParticles);
  }, []);

  const API_BASE_URL = 'http://127.0.0.1:8000';

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError("Please enter a valid product URL.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setError(null);
    setProgress(0);
    setRecommendations([]);

    const progressInterval = setInterval(() => {
      setProgress(prev => (prev >= 90 ? 90 : prev + Math.random() * 10));
    }, 400);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() })
      });
      
      clearInterval(progressInterval);
      setProgress(100);

      if (!response.ok) {
        throw new Error(`Network response was not ok (status: ${response.status})`);
      }

      const data = await response.json();

      if (data.success) {
        const analysis = {
          product: data.product_name,
          carbon: data.carbon_footprint ? data.carbon_footprint.toFixed(2) : 'N/A',
          material: data.material,
          image: data.image_url,
          weight: data.weight_value,
          unit: data.weight_unit,
          recommendation: data.carbon_footprint > 20
            ? 'High carbon footprint - consider eco-friendly alternatives'
            : data.carbon_footprint > 10
            ? 'Moderate carbon footprint - look for greener options'
            : 'Low carbon footprint - good environmental choice'
        };
        setAnalysisResult(analysis);
        setRecommendations(data.recommendations || []);
      } else {
        setError(data.error || 'Failed to analyze the product.');
      }
    } catch (err) {
      clearInterval(progressInterval);
      setError(err.message || 'An unexpected error occurred. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-lime-50 via-emerald-50 to-teal-50 relative overflow-hidden">
      {/* Floating Particles */}
      {particles.map(particle => (
        <div
          key={particle.id}
          className={`absolute rounded-full bg-${particle.color}-400/30 animate-float`}
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            animationDelay: `${particle.id * 0.5}s`,
            animationDuration: `${particle.speed + 3}s`
          }}
        />
      ))}

      {/* Organic Shapes Background */}
      <div className="absolute inset-0 overflow-hidden">
        <svg className="absolute -top-40 -right-40 w-96 h-96 text-emerald-200/40 animate-spin-slow" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="currentColor" />
        </svg>
        <svg className="absolute top-1/3 -left-32 w-80 h-80 text-teal-200/30 animate-pulse" viewBox="0 0 100 100">
          <path d="M20,50 Q50,20 80,50 Q50,80 20,50" fill="currentColor" />
        </svg>
        <svg className="absolute bottom-20 right-1/4 w-64 h-64 text-lime-200/40 animate-bounce-slow" viewBox="0 0 100 100">
          <ellipse cx="50" cy="50" rx="30" ry="45" fill="currentColor" />
        </svg>
      </div>

      {/* Header */}
      <header className="relative z-20 px-6 py-6">
        <nav className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 group cursor-pointer">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-all duration-300 shadow-lg shadow-emerald-500/30">
                  <Leaf className="w-7 h-7 text-white group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <div className="absolute -inset-1 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl opacity-0 group-hover:opacity-20 blur-md transition-all duration-300" />
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text text-transparent">
                  CarbonWise
                </h1>
                <p className="text-xs text-emerald-600 font-medium">Smart Shopping Assistant</p>
              </div>
            </div>

            <div className="hidden lg:flex items-center space-x-8">
              {[
                { icon: Globe, text: 'Global Impact', color: 'emerald' },
                { icon: Zap, text: 'AI Powered', color: 'blue' },
                { icon: Shield, text: 'Verified Data', color: 'purple' }
              ].map((item, index) => (
                <div key={index} className={`flex items-center space-x-2 px-4 py-2 bg-${item.color}-100 rounded-full border border-${item.color}-200 hover:shadow-lg hover:scale-105 transition-all duration-300`}>
                  <item.icon className={`w-4 h-4 text-${item.color}-600`} />
                  <span className={`text-sm font-medium text-${item.color}-700`}>{item.text}</span>
                </div>
              ))}
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Hero Section */}
          <div className="text-center mb-16">
            {/* Badge */}
            <div className="inline-flex items-center px-6 py-3 bg-white/80 backdrop-blur-sm border-2 border-emerald-200 rounded-full text-emerald-700 text-sm font-semibold mb-8 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <Award className="w-4 h-4 mr-2 text-emerald-500" />
              Trusted by 100,000+ eco-conscious shoppers
              <Sparkles className="w-4 h-4 ml-2 text-yellow-500" />
            </div>

            {/* Main Heading */}
            <div 
              className="mb-8"
              style={{ transform: `translateY(${scrollY * 0.1}px)` }}
            >
              <h1 className="text-6xl md:text-8xl font-black mb-6 leading-none">
                <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-green-600 bg-clip-text text-transparent">
                  Eco-Smart
                </span>
                <br />
                <span className="text-gray-800">
                  Shopping 🌱
                </span>
              </h1>
              
              <p className="text-xl md:text-2xl text-gray-700 mb-8 max-w-4xl mx-auto leading-relaxed font-medium">
                Transform your shopping habits with AI-powered carbon footprint analysis. 
                Make every purchase count for our planet! 🌍✨
              </p>
            </div>

            {/* Interactive Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-16">
              {[
                { icon: TrendingDown, value: '2.3M', label: 'kg CO₂ Saved', color: 'bg-gradient-to-br from-emerald-400 to-teal-500', emoji: '📉' },
                { icon: Search, value: '150K', label: 'Products Analyzed', color: 'bg-gradient-to-br from-blue-400 to-cyan-500', emoji: '🔍' },
                { icon: Heart, value: '98%', label: 'Satisfaction Rate', color: 'bg-gradient-to-br from-pink-400 to-rose-500', emoji: '💚' },
                { icon: Star, value: '4.9', label: 'User Rating', color: 'bg-gradient-to-br from-yellow-400 to-orange-500', emoji: '⭐' }
              ].map((stat, index) => (
                <div key={index} className="group cursor-pointer">
                  <div className="bg-white rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-110 border-2 border-gray-100 hover:border-emerald-200">
                    <div className="text-4xl mb-3">{stat.emoji}</div>
                    <div className={`inline-flex items-center justify-center w-12 h-12 ${stat.color} rounded-2xl mb-4 shadow-lg`}>
                      <stat.icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="text-3xl font-black text-gray-800 mb-2">{stat.value}+</div>
                    <div className="text-gray-600 text-sm font-medium">{stat.label}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Main Analysis Card */}
            <div className="max-w-4xl mx-auto">
              <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 md:p-12 shadow-2xl border-2 border-emerald-100 hover:border-emerald-200 transition-all duration-500">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                    <Search className="w-8 h-8 text-white" />
                  </div>
                  <h2 className="text-3xl md:text-4xl font-black text-gray-800 mb-4">
                    Discover Your Product's Impact 🔍
                  </h2>
                  <p className="text-gray-600 text-lg">
                    Paste any Amazon product URL and get instant environmental insights
                  </p>
                </div>

                {/* URL Input */}
                <div className="flex flex-col lg:flex-row gap-4 mb-8">
                  <div className="flex-1 relative group">
                    <input
                      type="url"
                      placeholder="🔗 Paste your Amazon product URL here..."
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      disabled={isAnalyzing}
                      className="w-full px-6 py-5 text-lg rounded-2xl border-3 border-gray-200 focus:border-emerald-400 focus:outline-none transition-all duration-300 bg-gray-50 focus:bg-white shadow-inner focus:shadow-lg group-hover:border-emerald-300"
                    />
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400">
                      <ArrowRight className="w-5 h-5" />
                    </div>
                  </div>
                  
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || !url.trim()}
                    className="px-8 py-5 bg-gradient-to-r from-emerald-500 via-teal-500 to-green-500 hover:from-emerald-600 hover:via-teal-600 hover:to-green-600 text-white rounded-2xl font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3 transition-all duration-300 transform hover:scale-105 shadow-xl hover:shadow-2xl shadow-emerald-500/30 relative overflow-hidden group"
                  >
                    <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 skew-x-12" />
                    <div className="relative flex items-center space-x-3">
                      {isAnalyzing ? (
                        <>
                          <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Analyzing Magic ✨</span>
                        </>
                      ) : (
                        <>
                          <Search className="w-6 h-6" />
                          <span>Analyze Now! 🚀</span>
                        </>
                      )}
                    </div>
                  </button>
                </div>

                {/* Progress Bar */}
                {isAnalyzing && (
                  <div className="mb-8">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-emerald-600 font-semibold flex items-center space-x-2">
                        <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse" />
                        <span>Working our magic...</span>
                        <span className="text-2xl">🔮</span>
                      </span>
                      <span className="text-emerald-700 font-bold text-lg">{Math.round(progress)}%</span>
                    </div>
                    <div className="w-full bg-emerald-100 rounded-full h-4 overflow-hidden shadow-inner">
                      <div 
                        className="h-full bg-gradient-to-r from-emerald-400 via-teal-400 to-green-400 rounded-full transition-all duration-500 shadow-lg relative overflow-hidden"
                        style={{ width: `${progress}%` }}
                      >
                        <div className="absolute inset-0 bg-white/30 animate-pulse" />
                      </div>
                    </div>
                  </div>
                )}

                {/* Error Message */}
                {error && !isAnalyzing && (
                  <div className="mb-8 bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-2xl shadow-lg animate-shake">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">⚠️</span>
                      <div>
                        <strong className="font-bold">Oops!</strong>
                        <p className="mt-1">{error}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Results */}
                {analysisResult && !isAnalyzing && (
                  <div className="space-y-8 animate-slide-up">
                    {/* Main Product Result */}
                    <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl p-6 border-2 border-orange-200 shadow-lg">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold text-gray-800 flex items-center space-x-2">
                          <span className="text-2xl">📦</span>
                          <span>Product Analysis</span>
                        </h3>
                        <div className="text-right">
                          <div className="text-4xl font-black text-red-600">{analysisResult.carbon}</div>
                          <div className="text-red-500 font-semibold">kg CO₂e</div>
                        </div>
                      </div>

                      <div className="flex flex-col md:flex-row items-start space-x-0 md:space-x-6 space-y-4 md:space-y-0">
                        {analysisResult.image && (
                          <img 
                            src={analysisResult.image} 
                            alt={analysisResult.product}
                            className="w-24 h-24 object-cover rounded-xl shadow-lg border-2 border-white"
                          />
                        )}
                        <div className="flex-1">
                          <h4 className="font-bold text-gray-800 text-lg mb-3">{analysisResult.product}</h4>
                          <div className="flex flex-wrap gap-2 mb-4">
                            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium border border-blue-200">
                              🧬 {analysisResult.material || 'Unknown Material'}
                            </span>
                            {analysisResult.weight && (
                              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium border border-purple-200">
                                ⚖️ {analysisResult.weight} {analysisResult.unit || ''}
                              </span>
                            )}
                          </div>
                          <div className="bg-emerald-100 border border-emerald-200 rounded-xl p-4">
                            <p className="text-emerald-800 font-semibold flex items-center space-x-2">
                              <span className="text-xl">💡</span>
                              <span>{analysisResult.recommendation}</span>
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Recommendations */}
                    {recommendations.length > 0 && (
                      <div className="space-y-4">
                        <h3 className="text-2xl font-bold text-gray-800 flex items-center space-x-3">
                          <span className="text-3xl">🌟</span>
                          <span>Better Alternatives</span>
                          <span className="text-xl">🌱</span>
                        </h3>
                        
                        <div className="space-y-4">
                          {recommendations.map((rec, index) => (
                            <div key={rec.product_id} className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl p-6 border-2 border-emerald-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-4 flex-1">
                                  {rec.image_url && (
                                    <img 
                                      src={rec.image_url} 
                                      alt={rec.product_name} 
                                      className="w-20 h-20 object-cover rounded-xl shadow-lg border-2 border-white"
                                    />
                                  )}
                                  <div>
                                    <a 
                                      href={rec.link} 
                                      target="_blank" 
                                      rel="noopener noreferrer" 
                                      className="font-bold text-gray-800 hover:text-emerald-600 transition-colors duration-300 text-lg flex items-center space-x-2 group"
                                    >
                                      <span>{rec.product_name}</span>
                                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                                    </a>
                                    <p className="text-sm text-blue-600 mt-2 flex items-center space-x-1">
                                      <span className="text-base">🧬</span>
                                      <span>Material: {rec.material || 'Unknown'}</span>
                                    </p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className="text-3xl font-black text-emerald-600">{rec.carbon_footprint.toFixed(2)}</div>
                                  <div className="text-emerald-500 font-semibold">kg CO₂e</div>
                                  <div className="mt-2">
                                    <span className="px-3 py-1 bg-emerald-500 text-white rounded-full text-xs font-bold">
                                      ECO CHOICE 🌿
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes bounce-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-25px); }
        }
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        .animate-float { animation: float 4s ease-in-out infinite; }
        .animate-spin-slow { animation: spin-slow 20s linear infinite; }
        .animate-bounce-slow { animation: bounce-slow 3s ease-in-out infinite; }
        .animate-slide-up { animation: slide-up 0.8s ease-out; }
        .animate-shake { animation: shake 0.5s ease-in-out; }
        .border-3 { border-width: 3px; }
      `}</style>
    </div>
  );
}