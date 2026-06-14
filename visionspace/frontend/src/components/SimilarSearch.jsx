import React, { useState } from 'react';

function SimilarSearch({ onSearch, results, loading }) {
  const [similarQuery, setSimilarQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!similarQuery.trim()) return;
    onSearch(similarQuery.trim());
  };

  // Format currency helper
  const formatPrice = (priceVal, currencyVal) => {
    if (priceVal === null || priceVal === undefined) return 'N/A';
    const curr = (currencyVal || 'INR').toUpperCase().trim();
    let locale = 'en-IN';
    if (curr === 'USD') locale = 'en-US';
    else if (curr === 'EUR') locale = 'en-IE';
    else if (curr === 'GBP') locale = 'en-GB';
    else if (curr === 'CAD') locale = 'en-CA';
    else if (curr === 'AUD') locale = 'en-AU';
    else if (curr === 'JPY') locale = 'ja-JP';
    else if (curr === 'SGD') locale = 'en-SG';
    else if (curr === 'AED') locale = 'ar-AE';
    else if (curr === 'CNY') locale = 'zh-CN';

    try {
      return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: curr,
        maximumFractionDigits: 0
      }).format(priceVal);
    } catch (e) {
      return `${curr} ${priceVal}`;
    }
  };

  return (
    <div className="similar-card">
      <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
        Semantic Vector Search
      </h3>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        Query ChromaDB to retrieve similar products.
      </p>

      <form onSubmit={handleSubmit} className="similar-input-row">
        <input
          type="text"
          className="form-input"
          placeholder="e.g. solid wood desk"
          value={similarQuery}
          onChange={(e) => setSimilarQuery(e.target.value)}
          disabled={loading}
          style={{ padding: '0.6rem 0.8rem', fontSize: '0.85rem' }}
        />
        <button
          type="submit"
          className="btn-similar"
          disabled={loading || !similarQuery.trim()}
          style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem' }}
        >
          {loading ? 'Searching...' : 'Find'}
        </button>
      </form>

      {results && results.length > 0 && (
        <div style={{ marginTop: '0.75rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            Vector Matches
          </div>
          <div className="similar-list">
            {results.map((item, idx) => (
              <div key={idx} className="similar-item" style={{ gap: '0.75rem' }}>
                <div style={{ flexShrink: 0, width: '40px', height: '40px', display: 'flex', justifyContent: 'center', alignItems: 'center', background: item.image ? '#0e1422' : 'linear-gradient(135deg, #0e1422 0%, #152035 100%)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '6px', overflow: 'hidden' }}>
                  {item.image ? (
                    <img src={item.image} alt={item.title} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                  ) : (
                    <svg style={{ width: '16px', height: '16px', color: 'var(--text-muted)', opacity: 0.4 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                    </svg>
                  )}
                </div>
                <div style={{ flexGrow: 1, minWidth: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
                  <div className="similar-item-title" title={item.title} style={{ margin: 0, maxWidth: 'none' }}>
                    {item.title}
                  </div>
                  <div className="similar-item-price" style={{ flexShrink: 0 }}>
                    {item.price ? formatPrice(item.price, item.currency) : 'Price N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {results && results.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          No vector matches found.
        </div>
      )}
    </div>
  );
}

export default SimilarSearch;
