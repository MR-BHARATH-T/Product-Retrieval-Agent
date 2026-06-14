import React from 'react';

function RecommendationReport({ report }) {
  if (!report) return null;

  const { recommended_products, best_choice, summary } = report;

  return (
    <div className="recommendation-card">
      <div className="section-header" style={{ borderLeftColor: 'var(--accent-gold)', marginBottom: '1.5rem', fontSize: '1.25rem' }}>
        <span>VPIA AI Recommendation Report</span>
        <span style={{ fontSize: '1.2rem' }}>✨</span>
      </div>

      {best_choice && best_choice.title && (
        <div style={{ marginBottom: '2rem' }}>
          <div className="best-choice-badge">
            🏆 Best Choice
          </div>
          <h3 className="best-product-title">
            {best_choice.title}
          </h3>
          {best_choice.image ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#0e1422', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', overflow: 'hidden', height: '200px', margin: '1rem 0' }}>
              <img
                src={best_choice.image}
                alt={best_choice.title}
                style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }}
              />
            </div>
          ) : (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'linear-gradient(135deg, #0e1422 0%, #152035 100%)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', height: '200px', margin: '1rem 0' }}>
              <svg style={{ width: '48px', height: '48px', color: 'var(--text-muted)', opacity: 0.4 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
              </svg>
            </div>
          )}
          <p className="best-product-reason">
            {best_choice.reason}
          </p>
        </div>
      )}

      {recommended_products && recommended_products.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 className="recomm-section-title">Recommended Options</h4>
          <div className="recomm-grid">
            {recommended_products.map((item, idx) => (
              <div key={idx} className="recomm-item" style={{ display: 'flex', gap: '1rem', alignItems: 'stretch' }}>
                <div style={{ flexShrink: 0, width: '80px', height: '80px', display: 'flex', justifyContent: 'center', alignItems: 'center', background: item.image ? '#0e1422' : 'linear-gradient(135deg, #0e1422 0%, #152035 100%)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px', overflow: 'hidden' }}>
                  {item.image ? (
                    <img src={item.image} alt={item.title} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                  ) : (
                    <svg style={{ width: '24px', height: '24px', color: 'var(--text-muted)', opacity: 0.4 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                    </svg>
                  )}
                </div>
                <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <div className="recomm-item-title" style={{ margin: 0 }}>{item.title}</div>
                    <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--accent-primary)', whiteSpace: 'nowrap' }}>
                      {item.price} • {item.rating}
                    </div>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    Store: {item.store || 'Unknown'}
                  </div>
                  <p className="recomm-item-reason" style={{ margin: 0, flexGrow: 1 }}>{item.reason}</p>
                  {item.url && (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--accent-primary)', textDecoration: 'none', marginTop: '0.5rem', fontWeight: '500' }}
                    >
                      View Offer
                      <svg style={{ width: '10px', height: '10px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                      </svg>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {summary && (
        <div>
          <h4 className="recomm-section-title">Executive Summary</h4>
          <p className="recomm-summary">{summary}</p>
        </div>
      )}
    </div>
  );
}

export default RecommendationReport;
