import React from 'react';
import { X, ExternalLink, Globe, ShieldCheck } from 'lucide-react';
import { EpistemicBadge } from './EpistemicBadge';
import { formatDate } from '../utils/formatters';

export function EvidenceModal({ prospect, onClose }) {
  if (!prospect) return null;

  const evidenceItems = prospect.evidence_items || [];
  const webSources = prospect.web_sources || [];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex justify-center items-start p-4 md:p-6">
      <div className="bg-slate-900 border border-slate-700/80 rounded-xl max-w-3xl w-full shadow-2xl my-8 overflow-hidden flex flex-col max-h-[85vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/60">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white tracking-tight">
                {prospect.company_name}
              </h2>
              <a
                href={prospect.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 font-mono"
              >
                {prospect.domain}
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Researched: {formatDate(prospect.researched_at)} • {evidenceItems.length} Evidence Citations
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm">
          {/* Crawled Web Sources Header */}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-indigo-400" />
              Verified Crawl Sources ({webSources.length})
            </h3>
            {webSources.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No web sources crawled yet.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {webSources.map((source) => (
                  <a
                    key={source.id}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 hover:border-slate-600 text-xs flex justify-between items-center group transition-colors"
                  >
                    <div className="truncate mr-2">
                      <span className="font-mono text-indigo-300 font-medium block truncate">
                        {source.url}
                      </span>
                      <span className="text-[10px] text-slate-400 uppercase font-semibold">
                        {source.page_type} • HTTP {source.http_status}
                      </span>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300 flex-shrink-0" />
                  </a>
                ))}
              </div>
            )}
          </div>

          {/* Granular Evidence Items List */}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Epistemic Claims & Verbatim Citations
            </h3>

            {evidenceItems.length === 0 ? (
              <div className="text-center py-8 text-slate-500 bg-slate-800/20 rounded-lg border border-dashed border-slate-800">
                <p>No evidence extracted yet. Click "Research" to crawl and extract facts.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {evidenceItems.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/70 space-y-2 hover:border-slate-600 transition-colors"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <EpistemicBadge status={item.epistemic_status} />
                        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wide">
                          {item.category.replace('_', ' ')}
                        </span>
                      </div>
                      {item.rubric_criterion && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/70 text-indigo-300 border border-indigo-800/50">
                          {item.rubric_criterion}
                        </span>
                      )}
                    </div>

                    <p className="text-slate-200 font-medium leading-relaxed">
                      {item.claim_text}
                    </p>

                    {item.exact_quote && (
                      <div className="text-xs font-mono bg-slate-950/70 text-slate-300 p-2.5 rounded border-l-2 border-emerald-500 leading-relaxed overflow-x-auto">
                        <span className="text-slate-500 font-sans text-[10px] block mb-1">
                          VERBATIM QUOTE FROM SOURCE:
                        </span>
                        "{item.exact_quote}"
                      </div>
                    )}

                    {item.gemini_reasoning && (
                      <p className="text-xs text-amber-300/90 italic bg-amber-950/20 p-2 rounded border-l-2 border-amber-500">
                        <span className="font-semibold text-amber-400">Deductive Reasoning: </span>
                        {item.gemini_reasoning}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
