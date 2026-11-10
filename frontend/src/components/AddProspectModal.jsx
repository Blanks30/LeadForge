import React, { useState, useEffect, useRef } from 'react';
import { X, Building2, Plus, AlertCircle, CheckCircle2, Loader2, Globe } from 'lucide-react';
import { api } from '../api/client';

export function AddProspectModal({ isOpen, onClose, onProspectAdded, initialData = null }) {
  const [companyName, setCompanyName] = useState(initialData?.company_name || '');
  const [websiteUrl, setWebsiteUrl] = useState(initialData?.website_url || '');
  const [description, setDescription] = useState(initialData?.description || '');

  const [validationError, setValidationError] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const modalRef = useRef(null);
  const firstInputRef = useRef(null);
  const previousActiveElement = useRef(null);

  // Sync initialData when modal opens
  useEffect(() => {
    if (isOpen) {
      setCompanyName(initialData?.company_name || '');
      setWebsiteUrl(initialData?.website_url || '');
      setDescription(initialData?.description || '');
      setValidationError(null);
      setApiError(null);
      setSuccess(false);
    }
  }, [isOpen, initialData]);

  // Focus trap and Escape key listener
  useEffect(() => {
    if (!isOpen) return;

    previousActiveElement.current = document.activeElement;

    // Focus first input on mount
    const timer = setTimeout(() => {
      firstInputRef.current?.focus();
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidationError(null);
    setApiError(null);

    const trimmedName = companyName.trim();
    let trimmedUrl = websiteUrl.trim();

    if (!trimmedName) {
      setValidationError('Company name is required.');
      return;
    }

    if (!trimmedUrl) {
      setValidationError('Website URL is required.');
      return;
    }

    // Auto-prepend https:// if protocol was omitted
    if (!/^https?:\/\//i.test(trimmedUrl)) {
      if (/^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/.test(trimmedUrl)) {
        trimmedUrl = `https://${trimmedUrl}`;
        setWebsiteUrl(trimmedUrl);
      } else {
        setValidationError('Website URL must start with http:// or https:// (e.g. https://example.com)');
        return;
      }
    }

    setLoading(true);

    try {
      const payload = {
        company_name: trimmedName,
        website_url: trimmedUrl,
        description: description.trim() || null,
      };

      const newProspect = await api.createProspect(payload);
      setSuccess(true);

      setTimeout(() => {
        onProspectAdded(newProspect);
        onClose();
      }, 700);
    } catch (err) {
      const errorMsg = err.message || 'Failed to add company.';
      if (errorMsg.includes('already exists') || errorMsg.includes('409')) {
        setApiError(errorMsg);
      } else {
        setApiError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-prospect-modal-title"
      onClick={(e) => {
        if (e.target === e.currentTarget && !loading) {
          onClose();
        }
      }}
    >
      <div
        ref={modalRef}
        className="w-full max-w-lg bg-[#101014] border border-[#272736] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
      >
        {/* Modal Header */}
        <div className="p-4 sm:p-5 border-b border-[#272736] flex items-center justify-between bg-[#141418]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-brand-500/10 text-brand-400 border border-brand-500/30">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 id="add-prospect-modal-title" className="text-base font-bold text-white tracking-tight">
                Add Custom Company
              </h3>
              <p className="text-xs text-zinc-400">
                Enter any Indian SaaS prospect to evaluate with TinyFish & Gemini
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={loading}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-[#1A1A22] transition-colors focus-ring"
            aria-label="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body / Form */}
        <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 overflow-y-auto flex-1">
          {/* Validation or API Error Alert */}
          {(validationError || apiError) && (
            <div
              className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-start gap-2.5 animate-shake"
              role="alert"
            >
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1 leading-relaxed">
                {validationError || apiError}
              </div>
            </div>
          )}

          {/* Success Banner */}
          {success && (
            <div
              className="p-3 rounded-xl bg-emerald-950/50 border border-emerald-700/60 text-emerald-300 text-xs flex items-center gap-2.5"
              role="status"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>Company added successfully! Ready for research.</span>
            </div>
          )}

          {/* Company Name */}
          <div className="space-y-1.5">
            <label htmlFor="company-name-input" className="block text-xs font-semibold text-zinc-200">
              Company Name <span className="text-brand-400">*</span>
            </label>
            <input
              ref={firstInputRef}
              id="company-name-input"
              type="text"
              required
              disabled={loading || success}
              placeholder="e.g. Cleartax, Postman, BrowserStack"
              value={companyName}
              onChange={(e) => {
                setCompanyName(e.target.value);
                if (validationError) setValidationError(null);
                if (apiError) setApiError(null);
              }}
              className="w-full bg-[#0C0C0F] border border-[#272736] text-xs sm:text-sm text-zinc-100 placeholder:text-zinc-500 px-3.5 py-2.5 rounded-xl focus-ring focus:border-brand-500 transition-colors disabled:opacity-50"
            />
            <p className="text-[11px] text-zinc-500">
              Display name of the target SaaS organization.
            </p>
          </div>

          {/* Website URL */}
          <div className="space-y-1.5">
            <label htmlFor="website-url-input" className="block text-xs font-semibold text-zinc-200">
              Website URL <span className="text-brand-400">*</span>
            </label>
            <div className="relative">
              <Globe className="w-4 h-4 text-zinc-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                id="website-url-input"
                type="text"
                required
                disabled={loading || success}
                placeholder="https://cleartax.in"
                value={websiteUrl}
                onChange={(e) => {
                  setWebsiteUrl(e.target.value);
                  if (validationError) setValidationError(null);
                  if (apiError) setApiError(null);
                }}
                className="w-full bg-[#0C0C0F] border border-[#272736] text-xs sm:text-sm font-mono text-zinc-100 placeholder:text-zinc-500 pl-10 pr-3.5 py-2.5 rounded-xl focus-ring focus:border-brand-500 transition-colors disabled:opacity-50"
              />
            </div>
            <p className="text-[11px] text-zinc-500">
              Must be an HTTP/HTTPS address. Root domain is automatically derived.
            </p>
          </div>

          {/* Description (Optional) */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label htmlFor="description-input" className="block text-xs font-semibold text-zinc-200">
                Company Notes / Description
              </label>
              <span className="text-[11px] text-zinc-500 font-mono">Optional</span>
            </div>
            <textarea
              id="description-input"
              rows={3}
              disabled={loading || success}
              placeholder="e.g. Tax compliance and invoicing SaaS for Indian MSMEs and enterprises..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#0C0C0F] border border-[#272736] text-xs text-zinc-100 placeholder:text-zinc-500 p-3 rounded-xl focus-ring focus:border-brand-500 transition-colors resize-none disabled:opacity-50"
            />
          </div>

          {/* Pipeline Note */}
          <div className="p-3 rounded-xl bg-[#141418] border border-[#272736] text-[11px] text-zinc-400 flex items-start gap-2">
            <Plus className="w-3.5 h-3.5 text-brand-400 mt-0.5 flex-shrink-0" />
            <span>
              The company will be created with status <strong className="text-amber-400 font-mono">PENDING</strong>. You can trigger live TinyFish crawl and Gemini analysis whenever you are ready.
            </span>
          </div>

          {/* Footer Controls */}
          <div className="pt-2 flex items-center justify-end gap-2.5 border-t border-[#272736]">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-[#141418] hover:bg-[#1A1A22] text-xs font-medium text-zinc-300 border border-[#272736] transition-colors focus-ring disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || success}
              className="px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-xs font-semibold text-white shadow-sm hover:shadow-md transition-all flex items-center gap-1.5 focus-ring disabled:opacity-50 active:scale-95"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Adding Company...</span>
                </>
              ) : success ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Added!</span>
                </>
              ) : (
                <>
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Company</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

