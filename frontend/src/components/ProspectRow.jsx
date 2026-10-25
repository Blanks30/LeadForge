import React from 'react';
import { ExternalLink, Search, FileText, Sparkles, Loader2 } from 'lucide-react';
import { ScoreBadge } from './ScoreBadge';

export function ProspectRow({
  prospect,
  onResearch,
  onInspectEvidence,
  onOpenDraft,
  isResearching,
}) {
  const isAnalyzed = prospect.status === 'ANALYZED';

  return (
    <tr className="border-b border-slate-800/80 hover:bg-slate-800/40 transition-colors">
      {/* Company Name & Website */}
      <td className="py-4 px-4 sm:px-6">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-white text-sm">
            {prospect.company_name}
          </span>
          <a
            href={prospect.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-400 hover:text-indigo-400 transition-colors"
            title="Open company website"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
        <div className="text-xs font-mono text-slate-400 mt-0.5">
          {prospect.domain}
        </div>
        {(prospect.hq_location || prospect.employee_range) && (
          <div className="text-[11px] text-slate-500 mt-1">
            {[prospect.hq_location, prospect.employee_range && `${prospect.employee_range} emp`]
              .filter(Boolean)
              .join(' • ')}
          </div>
        )}
      </td>

      {/* Status */}
      <td className="py-4 px-4 text-xs">
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${
            isAnalyzed
              ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40'
              : 'bg-slate-800 text-slate-400 border-slate-700'
          }`}
        >
          {prospect.status}
        </span>
      </td>

      {/* Lead Score & Breakdown */}
      <td className="py-4 px-4">
        {isAnalyzed ? (
          <ScoreBadge
            score={prospect.lead_score}
            breakdown={prospect.score_breakdown}
          />
        ) : (
          <span className="text-xs text-slate-500 font-mono italic">
            Pending research
          </span>
        )}
      </td>

      {/* Actions */}
      <td className="py-4 px-4 sm:px-6 text-right">
        <div className="flex items-center justify-end gap-1.5">
          {/* Research Button */}
          <button
            onClick={() => onResearch(prospect.id)}
            disabled={isResearching}
            className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
              isAnalyzed
                ? 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30'
            } disabled:opacity-50`}
            title="Crawl website and extract grounded evidence"
          >
            {isResearching ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Crawling...</span>
              </>
            ) : (
              <>
                <Search className="w-3 h-3" />
                <span>{isAnalyzed ? 'Re-Research' : 'Research'}</span>
              </>
            )}
          </button>

          {/* Evidence Modal Button */}
          <button
            onClick={() => onInspectEvidence(prospect.id)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium flex items-center gap-1 transition-colors"
            title="Inspect granular evidence citations"
          >
            <FileText className="w-3 h-3 text-emerald-400" />
            <span className="hidden md:inline">Evidence</span>
          </button>

          {/* Outreach Draft Button */}
          <button
            onClick={() => onOpenDraft(prospect.id)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium flex items-center gap-1 transition-colors"
            title="Generate evidence-grounded cold email"
          >
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span className="hidden md:inline">Outreach</span>
          </button>
        </div>
      </td>
    </tr>
  );
}
