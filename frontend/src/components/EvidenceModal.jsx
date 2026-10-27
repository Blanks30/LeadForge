import React, { useState, useEffect, useRef } from 'react';
import { X, ExternalLink, Globe, ShieldCheck, Zap, HelpCircle, FileText, CheckCircle2 } from 'lucide-react';
import { EpistemicBadge } from './EpistemicBadge';
import { formatDate } from '../utils/formatters';

export function EvidenceModal({ prospect, onClose }) {
  const [activeTab, setActiveTab] = useState('all');
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  // Focus trap, Escape key handling, and focus restoration
  useEffect(() => {
    previousActiveElement.current = document.activeElement;

    // Focus the first interactive element (close button or first tab)
    const focusableSelector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const modalNode = modalRef.current;
    if (modalNode) {
      const firstFocusable = modalNode.querySelector(focusableSelector);
      firstFocusable?.focus();
    }

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
      document.removeEventListener('keydown', handleKeyDown);
      if (previousActiveElement.current && typeof previousActiveElement.current.focus === 'function') {
        previousActiveElement.current.focus();
      }
    };
  }, [onClose]);

  if (!prospect) return null;

  const evidenceItems = prospect.evidence_items || [];
  const webSources = prospect.web_sources || [];

  const facts = evidenceItems.filter((i) => (i.epistemic_status || '').toUpperCase() === 'FACT');
  const inferences = evidenceItems.filter(
    (i) => (i.epistemic_status || '').toUpperCase() === 'INFERENCE'
  );
  const unknowns = evidenceItems.filter(
    (i) => (i.epistemic_status || '').toUpperCase() === 'UNKNOWN'
  );

  const displayedItems =
    activeTab === 'facts'
      ? facts
      : activeTab === 'inferences'
      ? inferences
      : activeTab === 'unknowns'
      ? unknowns
      : evidenceItems;

  return (
    <div
      className="fixed inset-0 z-50 overflow-hidden bg-black/75 flex justify-end transition-opacity"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="evidence-drawer-title"
    >
      <div
        ref={modalRef}
        className="relative w-full max-w-2xl md:max-w-3xl bg-[#0D0D11] border-l border-[#272736] h-full flex flex-col shadow-2xl animate-slide-in-right z-50 text-zinc-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="px-6 py-4 border-b border-[#272736] bg-[#131317] flex items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5 flex-wrap">
              <h2 id="evidence-drawer-title" className="text-lg font-bold text-white tracking-tight">
                {prospect.company_name}
              </h2>
              <a
                href={prospect.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-brand-400 hover:text-brand-300 inline-flex items-center gap-1 font-mono transition-colors focus-ring rounded"
                title={`Open ${prospect.website_url}`}
              >
                <span>{prospect.domain}</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              {prospect.status === 'ANALYZED' && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#062E20] text-emerald-400 border border-emerald-600/50">
                  Lead Score: {prospect.lead_score}/100
                </span>
              )}
            </div>
            <p className="text-xs text-zinc-400">
              Researched: {formatDate(prospect.researched_at)} • {evidenceItems.length} Citations Extracted
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-block text-[10px] text-zinc-500 font-mono">
              Press <kbd className="px-1.5 py-0.5 rounded bg-[#09090C] border border-[#272736] text-zinc-400">ESC</kbd> to exit
            </span>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-[#1A1A22] transition-colors focus-ring"
              aria-label="Close Evidence Drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="px-6 border-b border-[#272736] bg-[#0E0E12] flex items-center gap-1 overflow-x-auto text-xs font-medium">
          <button
            onClick={() => setActiveTab('all')}
            className={`py-3 px-3 border-b-2 flex items-center gap-1.5 whitespace-nowrap transition-colors ${
              activeTab === 'all'
                ? 'border-brand-500 text-white font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>All Evidence</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[#09090C] text-zinc-400 border border-[#272736]">
              {evidenceItems.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('facts')}
            className={`py-3 px-3 border-b-2 flex items-center gap-1.5 whitespace-nowrap transition-colors ${
              activeTab === 'facts'
                ? 'border-emerald-500 text-emerald-400 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Facts</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[#062E20] text-emerald-400 border border-emerald-600/50">
              {facts.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('inferences')}
            className={`py-3 px-3 border-b-2 flex items-center gap-1.5 whitespace-nowrap transition-colors ${
              activeTab === 'inferences'
                ? 'border-amber-500 text-amber-400 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Deductions</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[#2E1E05] text-amber-400 border border-amber-600/50">
              {inferences.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('unknowns')}
            className={`py-3 px-3 border-b-2 flex items-center gap-1.5 whitespace-nowrap transition-colors ${
              activeTab === 'unknowns'
                ? 'border-zinc-400 text-zinc-300 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5 text-zinc-400" />
            <span>Gaps</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[#14171F] text-zinc-400 border border-zinc-700">
              {unknowns.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('sources')}
            className={`py-3 px-3 border-b-2 flex items-center gap-1.5 whitespace-nowrap transition-colors ${
              activeTab === 'sources'
                ? 'border-brand-500 text-brand-300 font-semibold'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-brand-400" />
            <span>Sources</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-[#09090C] text-zinc-400 border border-[#272736]">
              {webSources.length}
            </span>
          </button>
        </div>

        {/* Drawer Body */}
        <div className="flex-1 p-6 overflow-y-auto space-y-5 text-sm">
          {activeTab === 'sources' ? (
            /* Crawled Web Sources View */
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-1">
                <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5 font-mono">
                  <Globe className="w-3.5 h-3.5 text-brand-400" />
                  Verified Crawled Pages ({webSources.length})
                </h3>
                <span className="text-[11px] text-zinc-500 font-mono">TinyFish Crawler Engine</span>
              </div>

              {webSources.length === 0 ? (
                <div className="text-center py-12 text-zinc-500 bg-[#070709]/60 rounded-xl border border-dashed border-[#272736]">
                  <Globe className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
                  <p className="text-xs">No web sources crawled yet.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-2.5">
                  {webSources.map((source) => (
                    <a
                      key={source.id}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-3 rounded-xl bg-[#141418] border border-[#272736] hover:border-brand-500/40 text-xs flex justify-between items-start group transition-all"
                    >
                      <div className="space-y-1 min-w-0 pr-3">
                        <span className="font-mono text-brand-400 font-medium block truncate break-all">
                          {source.url}
                        </span>
                        <div className="flex items-center gap-2 text-[10px] text-zinc-400 font-mono">
                          <span className="uppercase font-semibold px-1.5 py-0.5 rounded bg-[#070709] border border-[#272736]">
                            {source.page_type}
                          </span>
                          <span>HTTP {source.http_status}</span>
                          <span>•</span>
                          <span>Fetched: {formatDate(source.fetched_at)}</span>
                        </div>
                      </div>
                      <ExternalLink className="w-4 h-4 text-zinc-500 group-hover:text-brand-400 flex-shrink-0 mt-0.5 transition-colors" />
                    </a>
                  ))}
                </div>
              )}
            </div>
          ) : (
            /* Granular Evidence Items List */
            <div className="space-y-3">
              {displayedItems.length === 0 ? (
                <div className="text-center py-12 text-zinc-500 bg-[#070709]/60 rounded-xl border border-dashed border-[#272736] space-y-2">
                  <ShieldCheck className="w-8 h-8 text-zinc-600 mx-auto" />
                  <p className="text-sm font-medium text-zinc-300">No items in this category</p>
                  <p className="text-xs text-zinc-500 max-w-sm mx-auto">
                    {activeTab === 'unknowns'
                      ? 'No critical unknowns or data gaps were flagged for this prospect.'
                      : 'Trigger prospect research to crawl and extract grounded evidence.'}
                  </p>
                </div>
              ) : (
                displayedItems.map((item) => {
                  const isFact = (item.epistemic_status || '').toUpperCase() === 'FACT';
                  const isInference = (item.epistemic_status || '').toUpperCase() === 'INFERENCE';
                  const isUnknown = (item.epistemic_status || '').toUpperCase() === 'UNKNOWN';

                  return (
                    <div
                      key={item.id}
                      className={`p-4 rounded-xl border space-y-2.5 transition-all duration-150 ${
                        isFact
                          ? 'bg-[#141418] border-[#272736] hover:border-emerald-500/40'
                          : isInference
                          ? 'bg-[#141418] border-[#272736] hover:border-amber-500/40'
                          : 'bg-[#141418]/60 border-[#272736] border-dashed hover:border-zinc-500'
                      }`}
                    >
                      {/* Item Header */}
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <EpistemicBadge status={item.epistemic_status} />
                          <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider font-mono">
                            {item.category?.replace('_', ' ')}
                          </span>
                        </div>
                        {item.rubric_criterion && item.rubric_criterion !== 'NONE' && (
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/30">
                            {item.rubric_criterion}
                          </span>
                        )}
                      </div>

                      {/* Claim Text */}
                      <p className="text-zinc-100 font-medium leading-relaxed text-sm">
                        {item.claim_text}
                      </p>

                      {/* Verbatim Quote from Scraped Text */}
                      {item.exact_quote && (
                        <div className="text-xs font-mono bg-[#070709] text-emerald-300 p-3 rounded-lg border-l-2 border-emerald-500 leading-relaxed overflow-x-auto">
                          <span className="text-zinc-500 font-sans text-[10px] block mb-1 uppercase tracking-wider font-bold">
                            VERBATIM SOURCE EXCERPT:
                          </span>
                          "{item.exact_quote}"
                        </div>
                      )}

                      {/* Gemini Deductive Reasoning */}
                      {item.gemini_reasoning && (
                        <div className="text-xs text-amber-300/90 bg-amber-950/20 p-2.5 rounded-lg border-l-2 border-amber-500 leading-relaxed">
                          <span className="font-semibold text-amber-400 block mb-0.5">
                            Deductive Reasoning:
                          </span>
                          <span className="italic">{item.gemini_reasoning}</span>
                        </div>
                      )}

                      {/* Gap acknowledgment note for UNKNOWN items */}
                      {isUnknown && !item.exact_quote && (
                        <p className="text-xs text-zinc-500 italic bg-[#070709] p-2 rounded border border-[#272736]">
                          Acknowledged Gap: No direct evidence found on public pages. Not fabricated.
                        </p>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="px-6 py-3.5 border-t border-[#272736] bg-[#0E0E12] flex items-center justify-between">
          <span className="text-xs text-zinc-500 font-mono">
            {facts.length} Facts • {inferences.length} Deductions • {unknowns.length} Gaps
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-[#1A1A22] hover:bg-[#22222D] text-zinc-200 border border-[#272736] hover:border-brand-500/40 rounded-lg text-xs font-semibold transition-all focus-ring"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}

