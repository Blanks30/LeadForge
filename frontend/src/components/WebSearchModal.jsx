import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Search,
  Globe,
  ExternalLink,
  Plus,
  Loader2,
  AlertCircle,
  Sparkles,
  Building2,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';
import { api } from '../api/client';

const SUGGESTED_QUERIES = [
  'Best open-source AI agents',
  'Cybersecurity trends',
  'Linways official website',
  'Competitors of Zoho',
  'Latest developments in artificial intelligence',
  'Cloud computing technologies',
];

export function WebSearchModal({ isOpen, onClose, onAddAsCompany, existingProspects = [] }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const modalRef = useRef(null);
  const inputRef = useRef(null);
  const previousActiveElement = useRef(null);

  const existingDomains = new Set(
    existingProspects.map((p) => (p.domain || '').toLowerCase().trim())
  );

  // Focus trap, Escape key handling, and auto-focus
  useEffect(() => {
    if (!isOpen) return;

    previousActiveElement.current = document.activeElement;
    const timer = setTimeout(() => {
      inputRef.current?.focus();
    }, 50);

    const focusableSelector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }

      if (e.key === 'Tab' && modalRef.current) {
        const focusableElements = Array.from(
          modalRef.current.querySelectorAll(focusableSelector)
        ).filter((el) => !el.disabled && el.offsetParent !== null);

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      clearTimeout(timer);
      document.removeEventListener('keydown', handleKeyDown);
      if (previousActiveElement.current && typeof previousActiveElement.current.focus === 'function') {
        previousActiveElement.current.focus();
      }
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSearch = async (queryToSearch) => {
    const q = (queryToSearch || query).trim();
    if (!q) return;

    setLoading(true);
    setError(null);

    try {
      const data = await api.searchWeb(q);
      setResponse(data);
    } catch (err) {
      setError(err.message || 'Failed to complete internet search.');
    } finally {
      setLoading(false);
    }
  };

  const handleChipClick = (suggestion) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  const onSubmit = (e) => {
    e.preventDefault();
    handleSearch(query);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="web-search-modal-title"
      onClick={(e) => {
        if (e.target === e.currentTarget && !loading) {
          onClose();
        }
      }}
    >
      <div
        ref={modalRef}
        className="w-full max-w-3xl bg-[#0E0E12] border border-[#272736] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[88vh]"
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-[#272736] flex items-center justify-between bg-[#141418]">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 id="web-search-modal-title" className="text-base font-bold text-white tracking-tight">
                  Search the Web
                </h3>
                <span className="text-[10px] uppercase font-mono font-bold tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  Tavily Search
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                General-purpose internet search for any topic, market trend, or company
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-[#1A1A22] transition-colors focus-ring"
            aria-label="Close search"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Bar Input & Suggestion Chips */}
        <div className="p-4 sm:p-5 border-b border-[#272736] bg-[#101015] space-y-3">
          <form onSubmit={onSubmit} className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search anything on the internet..."
                disabled={loading}
                className="w-full bg-[#09090D] border border-[#272736] text-sm text-zinc-100 placeholder:text-zinc-500 pl-10 pr-4 py-2.5 rounded-xl focus-ring focus:border-cyan-500 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm focus-ring disabled:opacity-50 active:scale-95 flex-shrink-0"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Search</span>
                </>
              )}
            </button>
          </form>

          {/* Suggested Queries Chips */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] text-zinc-500 flex items-center gap-1 mr-1">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              Try:
            </span>
            {SUGGESTED_QUERIES.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => handleChipClick(suggestion)}
                className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-[#14141A] text-zinc-300 border border-[#272736] hover:border-cyan-500/40 hover:text-white transition-colors focus-ring"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Content Body: Results, Loading, or Error */}
        <div className="p-4 sm:p-5 overflow-y-auto flex-1 space-y-3.5">
          {error && (
            <div
              className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs space-y-1.5"
              role="alert"
            >
              <div className="flex items-center gap-2 font-semibold">
                <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                <span>Search Failed</span>
              </div>
              <p className="leading-relaxed pl-6">{error}</p>
            </div>
          )}

          {loading && (
            <div className="py-12 text-center space-y-3">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
              <p className="text-xs text-zinc-400 font-mono">
                Searching the live web with Tavily...
              </p>
            </div>
          )}

          {!loading && !error && !response && (
            <div className="py-16 text-center max-w-md mx-auto space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400 shadow-sm">
                <Globe className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-white tracking-tight">
                  Unrestricted Internet Search
                </h4>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Enter any topic, technology trend, or organization name above. Tavily retrieves real-time public web results without restricting to predefined verticals.
                </p>
              </div>
            </div>
          )}

          {!loading && response && response.results.length === 0 && (
            <div className="py-12 text-center text-xs text-zinc-400">
              No web results found for &ldquo;<span className="text-zinc-200">{response.query}</span>&rdquo;. Try adjusting your search query.
            </div>
          )}

          {!loading && response && response.results.length > 0 && (
            <div className="space-y-3">
              {/* Results Meta Banner */}
              <div className="flex items-center justify-between text-xs text-zinc-400 pb-1 border-b border-[#272736]/60">
                <div className="flex items-center gap-2">
                  <span>
                    Found <strong className="text-zinc-200">{response.total_results}</strong> results for &ldquo;
                    <span className="text-cyan-300 font-medium">{response.query}</span>&rdquo;
                  </span>
                </div>
                <div className="flex items-center gap-1.5 font-mono text-[10px]">
                  <span
                    className={`px-2 py-0.5 rounded border ${
                      response.is_live
                        ? 'bg-emerald-950/60 text-emerald-300 border-emerald-500/50'
                        : 'bg-zinc-800 text-zinc-300 border-zinc-700'
                    }`}
                  >
                    {response.is_live ? 'LIVE TAVILY' : 'MOCK SEARCH'}
                  </span>
                </div>
              </div>

              {/* Result Cards */}
              <div className="space-y-3">
                {response.results.map((item, idx) => {
                  const itemDomain = (item.domain || '').toLowerCase().trim();
                  const isAlreadyAdded = existingDomains.has(itemDomain);

                  return (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-[#14141A] border border-[#272736] hover:border-cyan-500/40 transition-all space-y-2 group shadow-sm"
                    >
                      {/* Title & Domain */}
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1 flex-1">
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm font-semibold text-white hover:text-cyan-400 transition-colors flex items-center gap-1.5 leading-snug group"
                          >
                            <span>{item.title}</span>
                            <ExternalLink className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 flex-shrink-0" />
                          </a>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-800/40">
                              {item.domain || 'web'}
                            </span>
                            {item.score !== null && item.score !== undefined && (
                              <span className="text-[10px] font-mono text-zinc-500">
                                Relevance: {Math.round(item.score * 100)}%
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Add as Company Action */}
                        <div className="flex-shrink-0">
                          {isAlreadyAdded ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono text-emerald-400 bg-emerald-950/30 border border-emerald-800/40">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Added</span>
                            </span>
                          ) : (
                            <button
                              type="button"
                              onClick={() => {
                                onAddAsCompany({
                                  company_name: item.candidate_company_name || item.domain,
                                  website_url: item.url,
                                  description: item.content ? item.content.slice(0, 300) : null,
                                });
                              }}
                              className="px-2.5 py-1 rounded-lg bg-[#1B1B24] hover:bg-cyan-600 hover:text-white text-zinc-300 border border-[#2F2F42] hover:border-cyan-500 text-xs font-medium flex items-center gap-1.5 transition-all shadow-sm focus-ring"
                              title={`Add ${item.candidate_company_name || item.domain} into LeadForge prospect database`}
                            >
                              <Plus className="w-3.5 h-3.5" />
                              <span>Add as Company</span>
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Snippet Content */}
                      <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">
                        {item.content}
                      </p>

                      {/* URL Footer */}
                      <div className="pt-1 flex items-center justify-between text-[11px] text-zinc-500 font-mono">
                        <span className="truncate max-w-[80%]">{item.url}</span>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-cyan-400 hover:underline flex items-center gap-1 flex-shrink-0"
                        >
                          <span>Visit</span>
                          <ArrowRight className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

