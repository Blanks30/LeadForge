import React from 'react';
import { ExternalLink, Search, FileText, Sparkles, Loader2, RefreshCw } from 'lucide-react';
import { ScoreBadge } from './ScoreBadge';

export function ProspectRow({
  prospect,
  onResearch,
  onInspectEvidence,
  onOpenDraft,
  isResearching,
}) {
  const isAnalyzed = prospect.status === 'ANALYZED';
  const isFailed = prospect.status === 'FAILED';

  return (
    <tr className="border-b border-[#272736]/70 hover:bg-[#15151C] transition-colors duration-150 group">
      {/* Company Name & Website */}
      <td className="py-3.5 px-4 sm:px-6">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-white text-sm tracking-tight group-hover:text-brand-400 transition-colors">
            {prospect.company_name}
          </span>
          <a
            href={prospect.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-zinc-500 hover:text-brand-400 transition-colors p-0.5 rounded focus-ring"
            title={`Visit ${prospect.company_name} (${prospect.website_url})`}
            aria-label={`Open ${prospect.company_name} website`}
          >
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
        <div className="text-xs font-mono text-zinc-400 mt-0.5">
          {prospect.domain}
        </div>
        {(prospect.hq_location || prospect.employee_range) && (
          <div className="text-[11px] text-zinc-500 mt-1 flex items-center gap-1.5 font-mono">
            {[prospect.hq_location, prospect.employee_range && `${prospect.employee_range} emp`]
              .filter(Boolean)
              .join(' • ')}
          </div>
        )}
      </td>

      {/* Status */}
      <td className="py-3.5 px-4 text-xs whitespace-nowrap">
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-semibold font-mono border transition-colors select-none ${
            isAnalyzed
              ? 'bg-[#062E20] text-emerald-400 border-emerald-600/50 shadow-sm'
              : isFailed
              ? 'bg-[#2A0E0E] text-rose-400 border-rose-800/50 shadow-sm'
              : 'bg-[#1C180C] text-amber-400 border-amber-600/40'
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isAnalyzed ? 'bg-emerald-400' : isFailed ? 'bg-rose-400' : 'bg-amber-400'
            }`}
          />
          {prospect.status}
        </span>
      </td>

      {/* Lead Score & Breakdown */}
      <td className="py-3.5 px-4">
        {isAnalyzed ? (
          <ScoreBadge
            score={prospect.lead_score}
            breakdown={prospect.score_breakdown}
          />
        ) : isFailed ? (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono text-rose-400 bg-rose-950/30 border border-rose-800/40">
            Crawl failed
          </span>
        ) : (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono text-zinc-500 bg-[#0C0C0F] border border-[#272736] italic">
            Pending research
          </span>
        )}
      </td>

      {/* Actions */}
      <td className="py-3.5 px-4 sm:px-6 text-right whitespace-nowrap">
        <div className="flex items-center justify-end gap-1.5">
          {/* Research / Retry Button */}
          <button
            onClick={() => onResearch(prospect.id)}
            disabled={isResearching}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all duration-150 focus-ring ${
              isResearching
                ? 'bg-[#3A1E0E] text-brand-300 border border-brand-500/40 cursor-wait'
                : isFailed
                ? 'bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-600/40 active:scale-95'
                : isAnalyzed
                ? 'bg-[#141418] hover:bg-[#1C1C24] text-zinc-300 border border-[#272736] hover:border-brand-500/40'
                : 'bg-brand-500 hover:bg-brand-600 text-white shadow-sm hover:shadow-md active:scale-95'
            } disabled:opacity-50`}
            title={isFailed ? "Retry web crawl and evidence extraction" : "Crawl website and extract grounded evidence"}
            aria-label={`${isFailed ? 'Retry research' : isAnalyzed ? 'Re-research' : 'Research'} ${prospect.company_name}`}
          >
            {isResearching ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin text-brand-400" />
                <span>Crawling...</span>
              </>
            ) : isFailed ? (
              <>
                <RefreshCw className="w-3 h-3 text-rose-400" />
                <span>Retry</span>
              </>
            ) : (
              <>
                <Search className="w-3 h-3 text-zinc-400 group-hover:text-white" />
                <span>{isAnalyzed ? 'Re-Research' : 'Research'}</span>
              </>
            )}
          </button>

          {/* Evidence Modal Button */}
          <button
            onClick={() => onInspectEvidence(prospect.id)}
            className="px-2.5 py-1.5 rounded-lg bg-[#141418] hover:bg-[#1C1C24] text-zinc-300 border border-[#272736] hover:border-emerald-500/50 text-xs font-medium flex items-center gap-1.5 transition-all duration-150 focus-ring"
            title="Inspect granular evidence citations"
            aria-label={`Inspect evidence for ${prospect.company_name}`}
          >
            <FileText className="w-3 h-3 text-emerald-400" />
            <span className="hidden sm:inline">Evidence</span>
          </button>

          {/* Outreach Draft Button */}
          <button
            onClick={() => onOpenDraft(prospect.id)}
            className="px-2.5 py-1.5 rounded-lg bg-[#141418] hover:bg-[#1C1C24] text-zinc-300 border border-[#272736] hover:border-amber-500/50 text-xs font-medium flex items-center gap-1.5 transition-all duration-150 focus-ring"
            title="Generate evidence-grounded cold email"
            aria-label={`Generate outreach draft for ${prospect.company_name}`}
          >
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span className="hidden sm:inline">Outreach</span>
          </button>
        </div>
      </td>
    </tr>
  );
}
