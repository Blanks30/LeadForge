import React, { useState, useEffect, useRef } from 'react';
import { X, Copy, Check, Lock, Sparkles, RefreshCw, ShieldCheck, ExternalLink, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import { EpistemicBadge } from './EpistemicBadge';

export function OutreachModal({ prospect, onClose }) {
  const [draft, setDraft] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const [templateType, setTemplateType] = useState('EVIDENCE_PROBLEM_SOLUTION');
  const [tone, setTone] = useState('CONSULTATIVE_DIRECT');
  const [error, setError] = useState(null);
  const [highlightedRefId, setHighlightedRefId] = useState(null);

  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  // Focus trap, Escape key handling, and focus restoration
  useEffect(() => {
    previousActiveElement.current = document.activeElement;

    // Focus the first interactive element inside the modal
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

  const fetchOrCreateDraft = async () => {
    if (!prospect) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.generateOutreachDraft(prospect.id, {
        template_type: templateType,
        tone: tone,
      });
      setDraft(result);
    } catch (err) {
      setError(err.message || 'Failed to generate outreach draft');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrCreateDraft();
  }, [prospect?.id]);

  const handleCopy = async () => {
    if (!draft) return;
    const fullText = `Subject: ${draft.subject_line}\n\n${draft.body_text}`;
    try {
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      setCopyError(false);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      setCopyError(true);
      setTimeout(() => setCopyError(false), 3000);
    }
  };

  if (!prospect) return null;

  const evidenceItems = prospect.evidence_items || [];
  const referencedIds = new Set(draft?.citations || []);

  const wordCount = draft?.body_text
    ? draft.body_text.trim().split(/\s+/).filter(Boolean).length
    : 0;

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-black/75 flex justify-center items-center p-3 sm:p-4 md:p-6"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="outreach-studio-title"
    >
      <div
        ref={modalRef}
        className="bg-[#0D0D11] border border-[#272736] rounded-2xl max-w-5xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[92vh] animate-slide-up text-zinc-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Studio Header */}
        <div className="px-6 py-4 border-b border-[#272736] bg-[#131317] flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand-500/10 border border-brand-500/30 flex items-center justify-center text-brand-400 shadow-sm">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 id="outreach-studio-title" className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                <span>Grounded Outreach Studio</span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/30">
                  Review Draft
                </span>
              </h2>
              <p className="text-xs text-zinc-400">
                Target: <span className="font-semibold text-zinc-200">{prospect.company_name}</span> ({prospect.domain})
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-block text-[10px] text-zinc-500 font-mono">
              <kbd className="px-1.5 py-0.5 rounded bg-[#09090C] border border-[#272736] text-zinc-400">ESC</kbd> to exit
            </span>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-[#1A1A22] transition-colors focus-ring"
              aria-label="Close Outreach Studio"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Zero-Send Guarantee Banner */}
        <div className="bg-[#241305] border-b border-[#3B1F0A] px-6 py-2.5 flex items-center gap-2.5 text-xs text-amber-200 font-medium">
          <Lock className="w-4 h-4 text-brand-400 flex-shrink-0" />
          <span>
            <strong className="text-white">Zero-Send Guarantee:</strong> Outbound transmission is strictly disabled. Review citations, refine copy, and copy to your email client.
          </span>
        </div>

        {/* Studio Body: Split View on Desktop */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column (7 cols): Draft Editor & Controls */}
            <div className="lg:col-span-7 space-y-4">
              {/* Controls Toolbar */}
              <div className="p-3 bg-[#141418] border border-[#272736] rounded-xl flex flex-wrap items-center justify-between gap-3 shadow-sm">
                <div className="flex items-center gap-3 flex-wrap">
                  <div>
                    <label htmlFor="outreach-template" className="text-[10px] uppercase font-mono font-bold text-zinc-400 block mb-1">
                      Template
                    </label>
                    <select
                      id="outreach-template"
                      value={templateType}
                      onChange={(e) => setTemplateType(e.target.value)}
                      className="bg-[#09090C] border border-[#272736] text-xs text-zinc-200 rounded-lg px-2.5 py-1.5 focus-ring focus:border-brand-500 transition-colors cursor-pointer"
                    >
                      <option value="EVIDENCE_PROBLEM_SOLUTION">Evidence + Solution</option>
                      <option value="EXECUTIVE_CONCISE">Executive Concise (&lt; 80 words)</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="outreach-tone" className="text-[10px] uppercase font-mono font-bold text-zinc-400 block mb-1">
                      Tone
                    </label>
                    <select
                      id="outreach-tone"
                      value={tone}
                      onChange={(e) => setTone(e.target.value)}
                      className="bg-[#09090C] border border-[#272736] text-xs text-zinc-200 rounded-lg px-2.5 py-1.5 focus-ring focus:border-brand-500 transition-colors cursor-pointer"
                    >
                      <option value="CONSULTATIVE_DIRECT">Consultative Direct</option>
                      <option value="FOUNDER_TO_FOUNDER">Founder to Founder</option>
                    </select>
                  </div>
                </div>

                <button
                  onClick={fetchOrCreateDraft}
                  disabled={loading}
                  className="px-3 py-1.5 bg-[#1A1A22] hover:bg-[#22222D] disabled:opacity-50 text-xs font-medium text-zinc-200 border border-[#272736] hover:border-brand-500/40 rounded-lg flex items-center gap-1.5 transition-all focus-ring self-end"
                >
                  <RefreshCw className={`w-3.5 h-3.5 text-brand-400 ${loading ? 'animate-spin' : ''}`} />
                  <span>Regenerate</span>
                </button>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-3 bg-red-950/40 border border-red-800/50 rounded-xl text-xs text-red-300 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Loading State */}
              {loading ? (
                <div className="py-20 flex flex-col items-center justify-center space-y-3 text-zinc-400 bg-[#070709]/40 rounded-xl border border-[#272736]">
                  <RefreshCw className="w-7 h-7 animate-spin text-brand-400" />
                  <p className="text-xs font-medium text-zinc-300">Synthesizing evidence-grounded copy...</p>
                  <p className="text-[11px] text-zinc-500">Cross-referencing verified company citations</p>
                </div>
              ) : draft ? (
                <div className="space-y-4">
                  {/* Subject Line */}
                  <div className="space-y-1">
                    <label htmlFor="outreach-subject" className="text-xs font-semibold text-zinc-300 block">
                      Subject Line
                    </label>
                    <input
                      id="outreach-subject"
                      type="text"
                      value={draft.subject_line}
                      onChange={(e) => setDraft({ ...draft, subject_line: e.target.value })}
                      className="w-full bg-[#09090C] border border-[#272736] rounded-lg px-3.5 py-2 text-sm text-white font-medium focus-ring focus:border-brand-500 transition-colors"
                      placeholder="Email subject..."
                    />
                  </div>

                  {/* Body Textarea */}
                  <div className="space-y-1">
                    <div className="flex justify-between items-center">
                      <label htmlFor="outreach-body" className="text-xs font-semibold text-zinc-300">
                        Email Body (Editable Draft)
                      </label>
                      <span className="text-[11px] text-zinc-400 font-mono">
                        {wordCount} words
                      </span>
                    </div>
                    <textarea
                      id="outreach-body"
                      rows={9}
                      value={draft.body_text}
                      onChange={(e) => setDraft({ ...draft, body_text: e.target.value })}
                      className="w-full bg-[#09090C] border border-[#272736] rounded-xl p-3.5 text-sm text-zinc-200 leading-relaxed font-sans focus-ring focus:border-brand-500 transition-colors resize-none"
                    />
                  </div>

                  {/* Grounded Citation Chips */}
                  {draft.citations && draft.citations.length > 0 && (
                    <div className="p-3 bg-[#141418] rounded-xl border border-[#272736] text-xs space-y-1.5">
                      <span className="text-zinc-400 font-medium block">
                        Referenced Evidence Citations (click to highlight):
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {draft.citations.map((id) => (
                          <button
                            key={id}
                            type="button"
                            onClick={() =>
                              setHighlightedRefId(highlightedRefId === id ? null : id)
                            }
                            className={`px-2 py-0.5 rounded text-[11px] font-mono font-medium border transition-all ${
                              highlightedRefId === id
                                ? 'bg-emerald-500 text-zinc-950 border-emerald-400 font-bold'
                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25 hover:border-emerald-500/50'
                            }`}
                          >
                            [Ref: #{id}]
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}
            </div>

            {/* Right Column (5 cols): Supporting Evidence Reference */}
            <div className="lg:col-span-5 space-y-3 flex flex-col">
              <div className="flex items-center justify-between pb-1">
                <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5 font-mono">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Grounding Evidence ({evidenceItems.length})</span>
                </h3>
                <span className="text-[10px] text-zinc-500 font-mono">
                  {referencedIds.size} referenced in draft
                </span>
              </div>

              <div className="flex-1 space-y-2.5 max-h-[460px] overflow-y-auto pr-1">
                {evidenceItems.length === 0 ? (
                  <div className="text-center py-12 text-zinc-500 bg-[#070709]/40 rounded-xl border border-dashed border-[#272736] text-xs">
                    <p>No evidence items extracted yet.</p>
                  </div>
                ) : (
                  evidenceItems.map((item) => {
                    const isReferenced = referencedIds.has(item.id);
                    const isHighlighted = highlightedRefId === item.id;

                    return (
                      <div
                        key={item.id}
                        className={`p-3 rounded-xl border text-xs space-y-1.5 transition-all duration-200 ${
                          isHighlighted
                            ? 'bg-emerald-950/30 border-emerald-400 shadow-[0_0_15px_-3px_rgba(16,185,129,0.3)]'
                            : isReferenced
                            ? 'bg-[#141418] border-emerald-500/40'
                            : 'bg-[#141418]/60 border-[#272736] opacity-80'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-[10px] text-zinc-400 px-1.5 py-0.2 rounded bg-[#070709] border border-[#272736]">
                              #{item.id}
                            </span>
                            <EpistemicBadge status={item.epistemic_status} />
                          </div>
                          {isReferenced && (
                            <span className="text-[10px] font-mono text-emerald-400 font-semibold px-1.5 py-0.2 rounded bg-emerald-500/10 border border-emerald-500/20">
                              Cited
                            </span>
                          )}
                        </div>

                        <p className="text-zinc-200 font-medium leading-relaxed">
                          {item.claim_text}
                        </p>

                        {item.exact_quote && (
                          <div className="text-[11px] font-mono text-emerald-300/90 bg-[#070709] p-2 rounded border-l border-emerald-500/60 leading-relaxed overflow-x-auto">
                            "{item.exact_quote}"
                          </div>
                        )}

                        {item.gemini_reasoning && (
                          <div className="text-[11px] text-amber-300/80 bg-amber-950/20 p-1.5 rounded border-l border-amber-500/60 italic">
                            {item.gemini_reasoning}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Studio Footer */}
        <div className="px-6 py-3.5 border-t border-[#272736] bg-[#0E0E12] flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <span>Tip: Edit text directly above before copying.</span>
            {copyError && (
              <span className="text-red-400 text-xs font-semibold">
                Clipboard access denied. Please copy manually.
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              disabled={!draft || loading}
              className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all focus-ring disabled:opacity-50 ${
                copied
                  ? 'bg-emerald-600 text-white shadow-glow-fact'
                  : 'bg-brand-500 hover:bg-brand-600 text-white shadow-sm'
              }`}
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Copied to Clipboard!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy Cold Email</span>
                </>
              )}
            </button>

            <button
              onClick={onClose}
              className="px-4 py-2 bg-[#1A1A22] hover:bg-[#22222D] text-zinc-300 border border-[#272736] rounded-lg text-xs font-medium transition-colors focus-ring"
            >
              Close Studio
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

