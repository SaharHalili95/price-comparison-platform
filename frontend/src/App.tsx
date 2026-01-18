import { useState } from 'react';
import Layout from './components/Layout';
import SearchBar from './components/SearchBar';
import ProductCard from './components/ProductCard';
import PriceComparisonTable from './components/PriceComparisonTable';
import { searchProducts } from './services/api';
import { ProductWithPrices, SearchResponse } from './types/product';

function App() {
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<ProductWithPrices | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setSelectedProduct(null);

    try {
      const results = await searchProducts(query);
      setSearchResults(results);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search products. Please make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (productId: number) => {
    const product = searchResults?.products.find(p => p.id === productId);
    if (product) {
      setSelectedProduct(product);
      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleBackToResults = () => {
    setSelectedProduct(null);
  };

  return (
    <Layout>
      {/* Hero Section */}
      <div className="text-center mb-12 relative">
        {/* Floating Decorative Elements */}
        <div className="absolute top-0 left-1/4 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
        <div className="absolute top-0 right-1/4 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-1/3 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>

        <div className="relative">
          <div className="inline-block mb-4 px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full">
            <span className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🎯 חסכו עד 40% בכל קנייה
            </span>
          </div>
          <h2 className="text-5xl md:text-6xl font-bold mb-4">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              השוו מחירים
            </span>
            <br />
            <span className="text-gray-900">וחסכו כסף חכם</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            חפשו כל מוצר וקבלו השוואת מחירים מיידית מ-Amazon, eBay ו-Walmart
            <br />
            כדי למצוא את העסקה הכי טובה בשוק 🚀
          </p>

          {/* Stats Section */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <div className="stat-card">
              <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                1M+
              </div>
              <div className="text-sm text-gray-600 mt-1">מוצרים במערכת</div>
            </div>
            <div className="stat-card">
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                35%
              </div>
              <div className="text-sm text-gray-600 mt-1">חיסכון ממוצע</div>
            </div>
            <div className="stat-card">
              <div className="text-3xl font-bold bg-gradient-to-r from-pink-600 to-red-600 bg-clip-text text-transparent">
                50K+
              </div>
              <div className="text-sm text-gray-600 mt-1">משתמשים מרוצים</div>
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} loading={loading} />

      {/* Error Message */}
      {error && (
        <div className="max-w-4xl mx-auto mb-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="font-semibold text-red-900 mb-1">Error</h3>
              <p className="text-sm text-red-700">{error}</p>
              <p className="text-sm text-red-600 mt-2">
                Make sure the backend is running: <code className="bg-red-100 px-2 py-0.5 rounded">uvicorn app.main:app --reload</code>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="text-center">
            <svg className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <p className="text-gray-600">Searching products and comparing prices...</p>
          </div>
        </div>
      )}

      {/* Selected Product Detail View */}
      {selectedProduct && !loading && (
        <div className="max-w-6xl mx-auto">
          <button
            onClick={handleBackToResults}
            className="mb-4 flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Results
          </button>
          <PriceComparisonTable product={selectedProduct} />
        </div>
      )}

      {/* Search Results Grid */}
      {searchResults && !selectedProduct && !loading && (
        <div className="max-w-6xl mx-auto">
          {/* Results Header */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900">
              Found {searchResults.total_results} {searchResults.total_results === 1 ? 'result' : 'results'} for "{searchResults.query}"
            </h3>
          </div>

          {/* Results Grid */}
          {searchResults.total_results > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {searchResults.products.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onViewDetails={handleViewDetails}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-600">No products found. Try a different search term.</p>
            </div>
          )}
        </div>
      )}

      {/* Welcome State */}
      {!searchResults && !loading && !error && (
        <div className="max-w-6xl mx-auto">
          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="feature-card group">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h4 className="font-bold text-lg text-gray-900 mb-2">השוואה מהירה</h4>
              <p className="text-gray-600">קבלו תוצאות מיידיות מכל החנויות המובילות במקום אחד</p>
            </div>

            <div className="feature-card group">
              <div className="bg-gradient-to-br from-green-500 to-green-600 w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="font-bold text-lg text-gray-900 mb-2">חיסכון אמיתי</h4>
              <p className="text-gray-600">מצאו את המחיר הזול ביותר וחסכו עד 40% מהמחיר הרגיל</p>
            </div>

            <div className="feature-card group">
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h4 className="font-bold text-lg text-gray-900 mb-2">מידע אמין</h4>
              <p className="text-gray-600">מחירים מעודכנים בזמן אמת ממקורות מהימנים ביותר</p>
            </div>
          </div>

          {/* Popular Categories */}
          <div className="card p-8">
            <h3 className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              קטגוריות פופולריות
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { name: 'אלקטרוניקה', icon: '💻', color: 'from-blue-500 to-cyan-500' },
                { name: 'מחשבים', icon: '🖥️', color: 'from-purple-500 to-indigo-500' },
                { name: 'אופנה', icon: '👕', color: 'from-pink-500 to-rose-500' },
                { name: 'בית וגן', icon: '🏠', color: 'from-green-500 to-emerald-500' },
                { name: 'ספורט ובריאות', icon: '⚽', color: 'from-orange-500 to-amber-500' },
                { name: 'ילדים ותינוקות', icon: '🍼', color: 'from-yellow-500 to-orange-500' },
                { name: 'מזון ושתייה', icon: '🍕', color: 'from-red-500 to-pink-500' },
                { name: 'טיפוח ויופי', icon: '💄', color: 'from-purple-500 to-pink-500' },
              ].map((category) => (
                <button
                  key={category.name}
                  onClick={() => handleSearch(category.name)}
                  className={`bg-gradient-to-br ${category.color} p-6 rounded-xl text-white font-semibold hover:scale-105 transition-transform duration-200 shadow-lg hover:shadow-xl`}
                >
                  <div className="text-3xl mb-2">{category.icon}</div>
                  <div>{category.name}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default App;
