import React, { useState } from 'react';
import './App.css';
import SearchForm from './components/SearchForm';
import ProductCard from './components/ProductCard';
import RecommendationReport from './components/RecommendationReport';
import SimilarSearch from './components/SimilarSearch';

function App() {
  const [products, setProducts] = useState([]);
  const [report, setReport] = useState(null);
  const [similarResults, setSimilarResults] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [recommLoading, setRecommLoading] = useState(false);
  const [similarLoading, setSimilarLoading] = useState(false);
  const [error, setError] = useState(null);

  // Pagination states
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [currentParams, setCurrentParams] = useState(null);

  const handleSearch = async (searchParams, pageNum = 1) => {
    setError(null);
    setPage(pageNum);
    
    // Only show full-screen scraping overlay and reset lists on page 1
    if (pageNum === 1) {
      setLoading(true);
      setProducts([]);
      setReport(null);
      setCurrentParams(searchParams);
    }
    
    const paramsWithPage = {
      ...(pageNum === 1 ? searchParams : currentParams),
      page: pageNum,
      limit: 6
    };

    try {
      // Step 1: Fetch candidate products list (Fast API retrieval)
      const searchRes = await fetch('http://127.0.0.1:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paramsWithPage)
      });

      if (!searchRes.ok) {
        throw new Error(`Search request failed with status: ${searchRes.status}`);
      }

      const productsData = await searchRes.json();
      setProducts(productsData.items);
      setTotalItems(productsData.total_items);
      setTotalPages(productsData.total_pages);
      setLoading(false); // Stop candidate search loader

      // Step 2: Fetch AI recommendation report on page 1 only
      if (pageNum === 1) {
        setRecommLoading(true);
        const recommRes = await fetch('http://127.0.0.1:8000/api/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(searchParams)
        });

        if (recommRes.ok) {
          const reportData = await recommRes.json();
          setReport(reportData);
        } else {
          console.warn("LLM recommendation request returned an error.");
        }
      }
    } catch (err) {
      console.error("Search pipeline error:", err);
      setError(err.message || "An unexpected error occurred during search retrieval.");
      setLoading(false);
    } finally {
      setRecommLoading(false);
    }
  };

  const handleSimilarSearch = async (queryTitle) => {
    setSimilarLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/similar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryTitle, limit: 5 })
      });
      if (res.ok) {
        const data = await res.json();
        setSimilarResults(data);
      }
    } catch (err) {
      console.error("Semantic search failed:", err);
    } finally {
      setSimilarLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Background loading overlay during active Playwright/API search runs */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <div className="loading-text">Scraping & Normalizing</div>
          <div className="loading-subtext">
            Executing Serper ➔ Tavily ➔ SerpAPI ➔ Playwright fallback crawler queries. Please stand by...
          </div>
        </div>
      )}

      {/* Header Panel */}
      <header className="app-header">
        <div className="app-title-container">
          <h1 className="app-title">VisionSpace AI</h1>
          <div className="app-subtitle">Product Intelligence Agent (VPIA)</div>
        </div>
      </header>

      {/* Inputs filters Card */}
      <SearchForm onSearch={handleSearch} loading={loading} />

      {error && (
        <div style={{ padding: '1.25rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--status-error)', borderRadius: '12px', marginBottom: '2rem', fontSize: '0.95rem' }}>
          ⚠️ <strong>Error:</strong> {error}
        </div>
      )}

      {/* Grid columns */}
      <div className="main-layout">
        
        {/* Results grid panel */}
        <div className="results-column">
          <h2 className="section-header">
            <span>Product Candidates</span>
            {products.length > 0 && (
              <span className="results-count">{totalItems} found</span>
            )}
          </h2>

          {products.length > 0 ? (
            <>
              <div className="products-grid">
                {products.map((p, idx) => (
                  <ProductCard
                    key={idx}
                    product={p}
                    onFindSimilar={handleSimilarSearch}
                  />
                ))}
              </div>

              {/* Pagination controls */}
              {totalPages > 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', marginTop: '2rem', paddingBottom: '1rem' }}>
                  <button
                    onClick={() => handleSearch(currentParams, page - 1)}
                    disabled={page === 1}
                    className="btn-similar"
                    style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem', cursor: page === 1 ? 'not-allowed' : 'pointer', opacity: page === 1 ? 0.5 : 1 }}
                  >
                    ◀ Previous
                  </button>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: '500' }}>
                    Page {page} of {totalPages} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>({totalItems} items)</span>
                  </span>
                  <button
                    onClick={() => handleSearch(currentParams, page + 1)}
                    disabled={page === totalPages}
                    className="btn-similar"
                    style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem', cursor: page === totalPages ? 'not-allowed' : 'pointer', opacity: page === totalPages ? 0.5 : 1 }}
                  >
                    Next ▶
                  </button>
                </div>
              )}
            </>
          ) : (
            !loading && (
              <div className="empty-view">
                <div className="empty-icon">🔍</div>
                <h3>No candidates retrieved</h3>
                <p>Submit a search query above to query search APIs, run merchant scraping fallbacks, and display results.</p>
              </div>
            )
          )}
        </div>

        {/* AI Recommendations panel */}
        <div className="recommendation-column">
          <h2 className="section-header">
            <span>Agent Intelligence</span>
          </h2>

          {/* ChromaDB Similarity box */}
          <SimilarSearch
            onSearch={handleSimilarSearch}
            results={similarResults}
            loading={similarLoading}
          />

          {/* Recommendation report card */}
          {recommLoading ? (
            <div className="recommendation-card" style={{ borderStyle: 'dashed', textAlign: 'center', padding: '3rem 2rem' }}>
              <div style={{ display: 'inline-block', width: '30px', height: '30px', border: '3px solid var(--border-light)', borderTop: '3px solid var(--accent-gold)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', marginBottom: '1rem' }}></div>
              <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>AI reasoning active...</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Analyzing products dimensions, availability, price ranges, and walking clearance limits.
              </p>
            </div>
          ) : (
            report && <RecommendationReport report={report} />
          )}
        </div>

      </div>
    </div>
  );
}

export default App;
