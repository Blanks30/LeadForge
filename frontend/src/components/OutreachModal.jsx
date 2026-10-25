import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Lock, Sparkles, RefreshCw } from 'lucide-react';
import { api } from '../api/client';

export function OutreachModal({ prospect, onClose }) {
  const [draft, setDraft] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [templateType, setTemplateType] = useState('EVIDENCE_PROBLEM_SOLUTION');
  const [tone, setTone] = useState('CONSULTATIVE_DIRECT');
  const [error, setError] = useState(null);

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
      setTimeout(() => setCopied(false), 2500);
    } catch {
      setError('Clipboard access denied');
    }
  };

  if (!prospect) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex justify-center items-start p-4 md:p-6">
      <div className="bg-slate-900 border border-slate-700/80 rounded-xl max-w-2xl w-full shadow-2xl my-8 overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/60">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              Grounded Outreach Draft
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Prospect: <span className="font-semibold text-slate-300">{prospect.company_name}</span> ({prospect.domain})
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Security / Zero-Send Warning Banner */}
        <div className="bg-indigo-950/40 border-b border-indigo-800/40 px-6 py-2.5 flex items-center gap-2 text-xs text-indigo-300 font-medium">
          <Lock className="w-4 h-4 text-indigo-400 flex-shrink-0" />
          <span>Architectural Zero-Send Guarantee: No automated dispatch. Review and copy to your email client.</span>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-5 text-sm">
          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-800/40 rounded-lg border border-slate-800">
            <div className="flex items-center gap-3">
              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                  Template
                </label>
                <select
                  value={templateType}
                  onChange={(e) => setTemplateType(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
                >
                  <option value="EVIDENCE_PROBLEM_SOLUTION">Evidence + Solution</option>
                  <option value="EXECUTIVE_CONCISE">Executive (Under 80 words)</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                  Tone
                </label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-indigo-500"
                >
                  <option value="CONSULTATIVE_DIRECT">Consultative Direct</option>
                  <option value="FOUNDER_TO_FOUNDER">Founder to Founder</option>
                </select>
              </div>
            </div>

            <button
              onClick={fetchOrCreateDraft}
              disabled={loading}
              className="mt-3 sm:mt-0 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-xs font-medium text-slate-200 rounded-lg flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Regenerate
            </button>
          </div>

          {error && (
            <div className="p-3 bg-red-950/40 border border-red-800/50 rounded-lg text-xs text-red-300">
              {error}
            </div>
          )}

          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-2 text-slate-400">
              <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
              <p className="text-xs">Synthesizing evidence-grounded copy...</p>
            </div>
          ) : draft ? (
            <div className="space-y-4">
              {/* Subject Line */}
              <div>
                <label className="text-xs font-semibold text-slate-400 block mb-1">
                  Subject Line
                </label>
                <input
                  type="text"
                  value={draft.subject_line}
                  onChange={(e) => setDraft({ ...draft, subject_line: e.target.value })}
                  className="w-full bg-slate-950/80 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Body Area */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-semibold text-slate-400">
                    Email Body (Grounded with Citations)
                  </label>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {draft.body_text.split(/\s+/).filter(Boolean).length} words
                  </span>
                </div>
                <textarea
                  rows={8}
                  value={draft.body_text}
                  onChange={(e) => setDraft({ ...draft, body_text: e.target.value })}
                  className="w-full bg-slate-950/80 border border-slate-700 rounded-lg p-3.5 text-sm text-slate-200 leading-relaxed font-sans focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              {/* Grounding Citations Chip */}
              {draft.citations && draft.citations.length > 0 && (
                <div className="p-2.5 bg-slate-950/40 rounded border border-slate-800/80 text-xs">
                  <span className="text-slate-400 font-semibold block mb-1">
                    Referenced Grounded Claims:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {draft.citations.map((id) => (
                      <span
                        key={id}
                        className="px-2 py-0.5 bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 rounded text-[11px] font-mono font-medium"
                      >
                        [Ref: #{id}]
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Tip: Edit locally before copying.
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              disabled={!draft || loading}
              className={`px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-1.5 transition-all shadow-lg ${
                copied
                  ? 'bg-emerald-600 text-white'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white'
              }`}
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  Copied to Clipboard!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy Email
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
