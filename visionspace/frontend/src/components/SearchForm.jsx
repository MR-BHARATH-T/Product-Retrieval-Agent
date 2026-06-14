import React, { useState } from 'react';

function SearchForm({ onSearch, loading }) {
  const [query, setQuery] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [roomDimensions, setRoomDimensions] = useState('');
  const [minRating, setMinRating] = useState('');
  const [llmProvider, setLlmProvider] = useState('lm-studio');
  const [llmModel, setLlmModel] = useState('');
  const [showAiSettings, setShowAiSettings] = useState(false);
  const [currency, setCurrency] = useState('INR');
  const [openrouterKey, setOpenrouterKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [grokKey, setGrokKey] = useState('');
  const [groqKey, setGroqKey] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    onSearch({
      query: query.trim(),
      max_price: maxPrice ? parseFloat(maxPrice) : null,
      room_dimensions: roomDimensions.trim() || null,
      min_rating: minRating ? parseFloat(minRating) : 0.0,
      llm_provider: llmProvider,
      llm_model: llmModel.trim() || null,
      currency: currency,
      openrouter_key: openrouterKey.trim() || null,
      gemini_key: geminiKey.trim() || null,
      grok_key: grokKey.trim() || null,
      groq_key: groqKey.trim() || null
    });
  };

  return (
    <form className="search-form-card" onSubmit={handleSubmit}>
      <div className="form-grid">
        <div className="form-group">
          <label className="form-label" htmlFor="query-input">
            What product do you need?
          </label>
          <input
            id="query-input"
            className="form-input"
            type="text"
            placeholder="e.g. Study desk for 10x12 ft room"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="price-input">
            Max Price
          </label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              id="price-input"
              className="form-input"
              type="number"
              placeholder="e.g. 5000"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              disabled={loading}
              min="0"
              style={{ flex: 1 }}
            />
            <select
              className="form-input"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              disabled={loading}
              style={{ width: '105px', background: '#080c14', padding: '0.75rem 0.5rem' }}
            >
              <option value="INR">INR (₹)</option>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="CAD">CAD (C$)</option>
              <option value="AUD">AUD (A$)</option>
              <option value="JPY">JPY (¥)</option>
              <option value="SGD">SGD (S$)</option>
              <option value="AED">AED (AED)</option>
              <option value="CNY">CNY (元)</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="room-dims">
            Room Size (WxD)
          </label>
          <input
            id="room-dims"
            className="form-input"
            type="text"
            placeholder="e.g. 10x12 ft"
            value={roomDimensions}
            onChange={(e) => setRoomDimensions(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="rating-input">
            Min Rating
          </label>
          <input
            id="rating-input"
            className="form-input"
            type="number"
            placeholder="e.g. 4.0"
            value={minRating}
            onChange={(e) => setMinRating(e.target.value)}
            disabled={loading}
            min="0"
            max="5"
            step="0.1"
          />
        </div>
      </div>

      {/* Expandable AI Intelligence Settings */}
      <div style={{ marginTop: '1.25rem', borderTop: '1px solid var(--border-light)', paddingTop: '1.25rem' }}>
        <button
          type="button"
          onClick={() => setShowAiSettings(!showAiSettings)}
          style={{ background: 'none', border: 'none', color: 'var(--accent-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem', fontWeight: '600', padding: 0 }}
        >
          <span>{showAiSettings ? '▼' : '▶'} AI Intelligence Settings</span>
        </button>

        {showAiSettings && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem', animation: 'fadeIn 0.25s ease' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="provider-select">
                LLM Provider (Free Tier compatible)
              </label>
              <select
                id="provider-select"
                className="form-input"
                value={llmProvider}
                onChange={(e) => {
                  setLlmProvider(e.target.value);
                  setLlmModel('');
                }}
                disabled={loading}
                style={{ background: '#080c14' }}
              >
                <option value="lm-studio">Local (LM Studio / Qwen)</option>
                <option value="openrouter">OpenRouter (Free Tier Models)</option>
                <option value="gemini">Google Gemini (Direct API Key)</option>
                <option value="groq">Groq LPUs (Direct API Key)</option>
                <option value="grok">xAI Grok (Direct API Key)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="model-input">
                Model Name (Optional Override)
              </label>
              <input
                id="model-input"
                className="form-input"
                type="text"
                placeholder={
                  llmProvider === 'openrouter' ? 'e.g. google/gemma-4-31b-it:free' :
                  llmProvider === 'gemini' ? 'e.g. gemini-2.5-flash' :
                  llmProvider === 'groq' ? 'e.g. llama-3.3-70b-versatile (Open Source)' :
                  llmProvider === 'grok' ? 'e.g. grok-2-1212' :
                  'Auto-detect active local model'
                }
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label className="form-label" style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                Optional API Keys (Overrides environment settings):
              </label>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="openrouter-key-input">
                OpenRouter API Key
              </label>
              <input
                id="openrouter-key-input"
                className="form-input"
                type="password"
                placeholder="Enter OpenRouter API Key"
                value={openrouterKey}
                onChange={(e) => setOpenrouterKey(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="gemini-key-input">
                Gemini API Key
              </label>
              <input
                id="gemini-key-input"
                className="form-input"
                type="password"
                placeholder="Enter Gemini API Key"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="groq-key-input">
                Groq API Key
              </label>
              <input
                id="groq-key-input"
                className="form-input"
                type="password"
                placeholder="Enter Groq API Key"
                value={groqKey}
                onChange={(e) => setGroqKey(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="grok-key-input">
                Grok API Key
              </label>
              <input
                id="grok-key-input"
                className="form-input"
                type="password"
                placeholder="Enter Grok API Key"
                value={grokKey}
                onChange={(e) => setGrokKey(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>
        )}
      </div>

      <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn-search" type="submit" disabled={loading}>
          {loading ? (
            <>
              <span style={{ display: 'inline-block', width: '14px', height: '14px', border: '2px solid white', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 0.6s linear infinite' }}></span>
              Running Fallback Search...
            </>
          ) : (
            <>
              <svg style={{ width: '18px', height: '18px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              Retrieve & Recommend
            </>
          )}
        </button>
      </div>
    </form>
  );
}

export default SearchForm;
