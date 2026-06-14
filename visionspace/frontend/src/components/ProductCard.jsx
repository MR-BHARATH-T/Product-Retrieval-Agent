import React from 'react';

function ProductCard({ product, onFindSimilar }) {
  const { title, price, rating, reviews, store, url, brand, dimensions, image, currency } = product;

  // Format store class name helper
  const getStoreClass = (storeName) => {
    if (!storeName) return 'unknown';
    const name = storeName.toLowerCase();
    if (name.includes('amazon')) return 'amazon';
    if (name.includes('ikea')) return 'ikea';
    if (name.includes('flipkart')) return 'flipkart';
    return 'unknown';
  };

  // Format currency symbol helper
  const formatPrice = (priceVal, currencyVal) => {
    if (priceVal === null || priceVal === undefined) return null;
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
    <div className="product-card">
      {!image ? (
        <div style={{ width: '100%', height: '180px', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'linear-gradient(135deg, #0e1422 0%, #152035 100%)', borderBottom: '1px solid var(--border-light)', position: 'relative' }}>
          <svg style={{ width: '48px', height: '48px', color: 'var(--text-muted)', opacity: 0.4 }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
          </svg>
        </div>
      ) : (
        <div style={{ width: '100%', height: '180px', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#0e1422', borderBottom: '1px solid var(--border-light)', overflow: 'hidden', position: 'relative' }}>
          <img
            src={image}
            alt={title}
            style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', transition: 'transform 0.5s ease' }}
            className="product-card-image"
          />
        </div>
      )}
      <div className="card-body">
        <div className="card-header-row">
          <span className={`store-badge ${getStoreClass(store)}`}>
            {store || 'Store'}
          </span>
          {rating && (
            <span className="product-rating">
              <span className="star-icon">★</span>
              {rating.toFixed(1)} {reviews > 0 && `(${reviews})`}
            </span>
          )}
        </div>

        <h3 className="product-title" title={title}>
          {title}
        </h3>

        {brand && (
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Brand: {brand}
          </div>
        )}

        <div className="product-specs">
          {dimensions && (
            <div className="spec-item">
              <span className="spec-icon">📐</span>
              <span>Size: {dimensions}</span>
            </div>
          )}
        </div>

        <div className="product-meta-row">
          <span className={`product-price ${price === null ? 'missing' : ''}`}>
            {price !== null ? formatPrice(price, currency) : 'Price N/A'}
          </span>

          <button
            onClick={() => onFindSimilar(title)}
            className="btn-similar"
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', borderRadius: '6px' }}
          >
            Find Similar
          </button>
        </div>
      </div>

      {url && (
        <a
          className="card-footer-btn"
          href={url}
          target="_blank"
          rel="noopener noreferrer"
        >
          View Store Offer
          <svg style={{ width: '12px', height: '12px', marginLeft: '4px', verticalAlign: 'middle' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
          </svg>
        </a>
      )}
    </div>
  );
}

export default ProductCard;
