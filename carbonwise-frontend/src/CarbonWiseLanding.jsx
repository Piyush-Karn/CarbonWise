import React, { useState } from 'react';
import { Search, Leaf, ShoppingCart, BarChart3, Globe, ArrowRight, Sparkles, Heart, TrendingUp } from 'lucide-react';

export default function CarbonWiseLanding() {
  const [url, setUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8000';

  const handleAnalyze = async () => {
    if (!url.trim()) return;
    
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setError(null);
    setProgress(0);
    
    const progressInterval = setInterval(() => {
      setProgress(prev => prev >= 85 ? 85 : prev + Math.random() * 15);
    }, 300);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() })
      });

      const data = await response.json();
      clearInterval(progressInterval);
      setProgress(100);
      
      setTimeout(() => {
        setIsAnalyzing(false);
        if (data.success) {
          setAnalysisResult({
            product: data.product_name,
            carbon: data.carbon_footprint ? data.carbon_footprint.toFixed(2) : 'N/A',
            material: data.material,
            image: data.image_url,
            weight: data.weight_value,
            unit: data.weight_unit,
            recommendation: data.carbon_footprint > 20 ? 'High carbon footprint - consider eco-friendly alternatives' 
                          : data.carbon_footprint > 10 ? 'Moderate carbon footprint - look for greener options'
                          : 'Low carbon footprint - good environmental choice'
          });
        } else {
          setError(data.error || 'Failed to analyze product');
        }
      }, 500);
      
    } catch (err) {
      clearInterval(progressInterval);
      setIsAnalyzing(false);
      setError('Network error - please check if the backend server is running');
      console.error('Analysis error:', err);
    }
  };

  return (
    <div className="min-h-screen w-full bg-white relative">
      {/* Amber Glow Background */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `radial-gradient(125% 125% at 50% 90%, #ffffff 40%, #f59e0b 100%)`,
          backgroundSize: "100% 100%",
        }}
      />
      <div className="relative z-10">
        
        {/* Header */}
        <header className="relative z-10 px-6 py-4">
          <nav className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-2 group cursor-pointer hover:scale-105 transition-transform duration-300">
              <Leaf className="w-8 h-8 text-emerald-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                CarbonWise
              </span>
            </div>
          </nav>
        </header>

        {/* Main Content */}
        <main className="relative z-10">
          <div className="relative z-10 max-w-7xl mx-auto px-6 py-20">
            <div className="text-center mb-16">
              <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                <span className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 bg-clip-text text-transparent">
                  Shop Smarter,{' '}
                </span>
                <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
                  Planet Happier
                </span>
              </h1>
              
              <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
                Discover the hidden carbon footprint of your online purchases. Get AI-powered green recommendations.
              </p>

              {/* URL Input Section */}
              <div className="max-w-2xl mx-auto mb-16">
                <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">
                    Check Any Product's Carbon Impact
                  </h2>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex-1">
                      <input
                        type="url"
                        placeholder="Paste Amazon product URL here..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        disabled={isAnalyzing}
                        className="w-full px-6 py-4 rounded-xl border-2 border-gray-200 focus:border-emerald-500 focus:outline-none transition-all duration-300 text-gray-700 bg-white/90"
                      />
                    </div>
                    <button
                      onClick={handleAnalyze}
                      disabled={isAnalyzing || !url.trim()}
                      className="px-8 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                    >
                      {isAnalyzing ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Analyzing...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <Search className="w-5 h-5" />
                          <span>Analyze Impact</span>
                        </div>
                      )}
                    </button>
                  </div>
                  
                  {/* Loading Progress */}
                  {isAnalyzing && (
                    <div className="mt-6 space-y-4">
                      <div className="flex justify-between text-sm text-gray-600">
                        <span>Analyzing product...</span>
                        <span>{Math.round(progress)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="h-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-300"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Results */}
                  {analysisResult && !isAnalyzing && (
                    <div className="mt-8 p-6 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl border border-red-200">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex-1">
                          <p className="text-sm text-gray-600 mb-1">Analysis Complete:</p>
                          <div className="flex items-start space-x-3">
                            {analysisResult.image && (
                              <img 
                                src={analysisResult.image} 
                                alt={analysisResult.product}
                                className="w-16 h-16 object-cover rounded-lg border"
                              />
                            )}
                            <div>
                              <p className="font-semibold text-gray-800 mb-1">{analysisResult.product}</p>
                              <p className="text-xs text-blue-600 mb-1">Material: {analysisResult.material || 'Unknown'}</p>
                              {analysisResult.weight && (
                                <p className="text-xs text-purple-600">Weight: {analysisResult.weight} {analysisResult.unit || ''}</p>
                              )}
                            </div>
                          </div>
                          <p className="text-xs text-emerald-600 mt-2">
                            {analysisResult.recommendation}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-red-600">
                            {analysisResult.carbon} kg CO₂
                          </p>
                          <p className="text-sm text-gray-600">Carbon footprint</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Error Display */}
                  {error && !isAnalyzing && (
                    <div className="mt-8 p-6 bg-red-50 rounded-xl border border-red-200">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-sm font-bold">!</span>
                        </div>
                        <div>
                          <p className="font-semibold text-red-800">Analysis Failed</p>
                          <p className="text-sm text-red-600">{error}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}