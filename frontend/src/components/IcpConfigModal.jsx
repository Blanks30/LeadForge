import React, { useState } from 'react';
import { X, Target, Save, Check } from 'lucide-react';
import { api } from '../api/client';

export function IcpConfigModal({ icp, onUpdate, onClose }) {
  const [vertical, setVertical] = useState(icp?.vertical || 'B2B SaaS serving SMBs / MSMEs');
  const [targetGeo, setTargetGeo] = useState(icp?.target_geo || 'India');
  const [criteriaText, setCriteriaText] = useState((icp?.smb_criteria || []).join('\n'));
  const [keywordsText, setKeywordsText] = useState((icp?.tech_keywords || []).join(', '));
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const smbCriteria = criteriaText
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean);

    const techKeywords = keywordsText
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      const updated = await api.updateIcp({
        vertical,
        target_geo: targetGeo,
        smb_criteria: smbCriteria,
        tech_keywords: techKeywords,
      });
      onUpdate(updated);
      setSaved(true);
      setTimeout(() => {
        setSaved(false);
        onClose();
      }, 1000);
    } catch (err) {
      setError(err.message || 'Failed to update ICP settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex justify-center items-start p-4 md:p-6">
      <div className="bg-slate-900 border border-slate-700/80 rounded-xl max-w-xl w-full shadow-2xl my-8 overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/60">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Ideal Customer Profile (ICP)
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSave} className="p-6 space-y-4 text-sm">
          {error && (
            <div className="p-3 bg-red-950/40 border border-red-800/50 rounded-lg text-xs text-red-300">
              {error}
            </div>
          )}

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Target Vertical / Industry
            </label>
            <input
              type="text"
              value={vertical}
              onChange={(e) => setVertical(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Target Geography
            </label>
            <input
              type="text"
              value={targetGeo}
              onChange={(e) => setTargetGeo(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              SMB Alignment Criteria (One per line)
            </label>
            <textarea
              rows={4}
              value={criteriaText}
              onChange={(e) => setCriteriaText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-slate-200 font-mono text-xs focus:outline-none focus:border-indigo-500 resize-none"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Used by the 100-point rubric engine to evaluate prospect fit.
            </p>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">
              Technology & Industry Keywords (Comma-separated)
            </label>
            <input
              type="text"
              value={keywordsText}
              onChange={(e) => setKeywordsText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-xs font-mono focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className={`px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-1.5 transition-all ${
                saved
                  ? 'bg-emerald-600 text-white'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white'
              }`}
            >
              {saved ? (
                <>
                  <Check className="w-4 h-4" />
                  Saved!
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
