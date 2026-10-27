import React from 'react';
import { CheckCircle2, Zap, HelpCircle, ShieldCheck } from 'lucide-react';

export function EpistemicBadge({ status, showDescription = false }) {
  const normalized = (status || 'UNKNOWN').toUpperCase();

  const configs = {
    FACT: {
      bg: 'bg-[#062E20] text-emerald-400 border-emerald-600/60 shadow-sm',
      icon: CheckCircle2,
      dotClass: 'bg-emerald-400',
      label: 'FACT',
      tooltip: 'Verified Fact: Direct verbatim quote backed by exact source URL and substring verification.',
      description: 'Grounding verified against source text',
    },
    INFERENCE: {
      bg: 'bg-[#2E1E05] text-amber-400 border-amber-600/60 shadow-sm',
      icon: Zap,
      dotClass: 'bg-amber-400',
      label: 'INFERENCE',
      tooltip: 'Logical Deduction: Conclusion derived from observed facts with explicitly logged reasoning.',
      description: 'Probabilistic deduction with logged reasoning',
    },
    UNKNOWN: {
      bg: 'bg-[#14171F] text-zinc-400 border-dashed border-zinc-600',
      icon: HelpCircle,
      dotClass: 'bg-zinc-500',
      label: 'UNKNOWN',
      tooltip: 'Acknowledged Gap: Data absent from public crawled sources. Never guessed or fabricated.',
      description: 'Public data absent; gap acknowledged',
    },
  };

  const config = configs[normalized] || configs.UNKNOWN;
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-xs font-medium border font-mono tracking-tight transition-all duration-150 select-none ${config.bg}`}
      title={config.tooltip}
      aria-label={`${config.label} - ${config.tooltip}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dotClass} flex-shrink-0`} />
      <Icon className="w-3 h-3 stroke-[2.2] flex-shrink-0" />
      <span className="font-semibold text-[11px]">{config.label}</span>
      {showDescription && (
        <span className="text-[10px] text-slate-400 font-sans ml-1 border-l border-slate-700 pl-1.5 hidden sm:inline">
          {config.description}
        </span>
      )}
    </span>
  );
}

