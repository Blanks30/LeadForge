import React, { useState, useEffect, useRef } from 'react';
import { X, Target, Save, Check, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../api/client';

export function IcpConfigModal({ icp, onUpdate, onClose }) {
  const [vertical, setVertical] = useState(icp?.vertical || 'B2B SaaS serving SMBs / MSMEs');
  const [targetGeo, setTargetGeo] = useState(icp?.target_geo || 'India');
  const [criteriaText, setCriteriaText] = useState((icp?.smb_criteria || []).join('\n'));
  const [keywordsText, setKeywordsText] = useState((icp?.tech_keywords || []).join(', '));
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  // Focus trap, Escape key handling, and focus restoration
  useEffect(() => {
    previousActiveElement.current = document.activeElement;

    // Set initial focus to the first interactive field inside the modal
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
      // Restore focus to the trigger element when modal unmounts
      if (previousActiveElement.current && typeof previousActiveElement.current.focus === 'function') {
        previousActiveElement.current.focus();
      }
    };
  }, [onClose]);

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
      }, 900);
    } catch (err) {
      setError(err.message || 'Failed to update ICP settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto bg-black/75 flex justify-center items-center p-3 sm:p-4 md:p-6"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="icp-modal-title"
    >
      <div
        ref={modalRef}
        className="bg-[#0D0D11] border border-[#272736] rounded-2xl max-w-xl w-full shadow-2xl overflow-hidden flex flex-col animate-slide-up text-zinc-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#272736] bg-[#131317] flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand-500/10 border border-brand-500/30 flex items-center justify-center text-brand-400 shadow-sm flex-shrink-0">
              <Target className="w-4 h-4" />
            </div>
            <div>
              <h2 id="icp-modal-title" className="text-base font-bold text-white tracking-tight">
                Ideal Customer Profile (ICP)
              </h2>
              <p className="text-xs text-zinc-400">
                Configures TinyFish web crawl focus & the 100-point scoring rubric
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-[#1A1A22] transition-colors focus-ring"
            aria-label="Close ICP Configuration"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSave} className="p-6 space-y-4 text-sm">
          {error && (
            <div className="p-3 bg-red-950/40 border border-red-800/50 rounded-xl text-xs text-red-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="space-y-1">
            <label htmlFor="icp-vertical" className="text-xs font-semibold text-zinc-300 block">
              Target Vertical / Industry Focus
            </label>
            <input
              id="icp-vertical"
              type="text"
              value={vertical}
              onChange={(e) => setVertical(e.target.value)}
              className="w-full bg-[#09090C] border border-[#272736] rounded-lg px-3.5 py-2 text-sm text-white font-medium focus-ring focus:border-brand-500 transition-colors"
              required
            />
            <p className="text-[11px] text-zinc-500">
              e.g. B2B SaaS serving SMBs / Kiranas / MSMEs in India
            </p>
          </div>

          <div className="space-y-1">
            <label htmlFor="icp-target-geo" className="text-xs font-semibold text-zinc-300 block">
              Target Geography
            </label>
            <input
              id="icp-target-geo"
              type="text"
              value={targetGeo}
              onChange={(e) => setTargetGeo(e.target.value)}
              className="w-full bg-[#09090C] border border-[#272736] rounded-lg px-3.5 py-2 text-sm text-white font-medium focus-ring focus:border-brand-500 transition-colors"
              required
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <label htmlFor="icp-criteria" className="text-xs font-semibold text-zinc-300">
                SMB Alignment Criteria (One per line)
              </label>
              <span className="text-[10px] font-mono text-emerald-400">
                Rubric Weight: 35 pts
              </span>
            </div>
            <textarea
              id="icp-criteria"
              rows={4}
              value={criteriaText}
              onChange={(e) => setCriteriaText(e.target.value)}
              className="w-full bg-[#09090C] border border-[#272736] rounded-xl p-3 text-xs text-zinc-200 font-mono focus-ring focus:border-brand-500 transition-colors resize-none leading-relaxed"
              placeholder="e.g. INR pricing&#10;WhatsApp integration&#10;Self-serve onboarding"
            />
            <p className="text-[11px] text-zinc-500">
              Evaluated deterministically by the Python scoring engine for verified SMB focus.
            </p>
          </div>

          <div className="space-y-1">
            <label htmlFor="icp-keywords" className="text-xs font-semibold text-zinc-300 block">
              Technology & Industry Keywords (Comma-separated)
            </label>
            <input
              id="icp-keywords"
              type="text"
              value={keywordsText}
              onChange={(e) => setKeywordsText(e.target.value)}
              className="w-full bg-[#09090C] border border-[#272736] rounded-lg px-3.5 py-2 text-xs text-zinc-200 font-mono focus-ring focus:border-brand-500 transition-colors"
              placeholder="billing, invoicing, gst, merchant tech, kirana"
            />
          </div>

          {/* Form Actions */}
          <div className="pt-3 border-t border-[#272736] flex items-center justify-between">
            <span className="text-xs text-zinc-500 font-mono">
              Changes persist across sessions in SQLite.
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-[#1A1A22] hover:bg-[#22222D] text-zinc-300 border border-[#272736] rounded-lg text-xs font-medium transition-colors focus-ring"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all focus-ring disabled:opacity-50 ${
                  saved
                    ? 'bg-emerald-600 text-white shadow-glow-fact'
                    : 'bg-brand-500 hover:bg-brand-600 text-white shadow-sm'
                }`}
              >
                {saving ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : saved ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Saved!</span>
                  </>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5" />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

