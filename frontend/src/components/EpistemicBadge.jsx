import React from 'react';
import { CheckCircle2, Zap, HelpCircle } from 'lucide-react';

export function EpistemicBadge({ status }) {
  const normalized = (status || 'UNKNOWN').toUpperCase();

  const configs = {
    FACT: {
      bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      icon: CheckCircle2,
      label: 'FACT',
    },
    INFERENCE: {
      bg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      icon: Zap,
      label: 'INFERENCE',
    },
    UNKNOWN: {
      bg: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
      icon: HelpCircle,
      label: 'UNKNOWN',
    },
  };

  const config = configs[normalized] || configs.UNKNOWN;
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${config.bg}`}
      title={`Epistemic Classification: ${config.label}`}
    >
      <Icon className="w-3 h-3 stroke-[2.5]" />
      <span>{config.label}</span>
    </span>
  );
}
