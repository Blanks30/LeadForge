import React, { useState } from 'react';
import { getScoreColor } from '../utils/formatters';
import { Info } from 'lucide-react';

export function ScoreBadge({ score, breakdown }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const color = getScoreColor(score);

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border transition-all ${color.bg}`}
      >
        <span className="text-sm font-bold">{score}</span>
        <span className="text-[10px] text-slate-400">/100</span>
        {breakdown && <Info className="w-3 h-3 text-slate-400 hover:text-slate-200" />}
      </button>

      {/* Score Breakdown Tooltip / Popover */}
      {showTooltip && breakdown && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-xl text-xs z-50 pointer-events-none">
          <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1.5 mb-2 flex justify-between items-center">
            <span>100-Point Rubric Breakdown</span>
            <span className="text-indigo-400 font-bold">{score} pts</span>
          </div>

          <div className="space-y-1.5 text-slate-300">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">SMB Focus (max 35):</span>
              <span className="font-mono font-medium text-emerald-400">
                +{breakdown.smb_focus ?? 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">SaaS Model (max 25):</span>
              <span className="font-mono font-medium text-emerald-400">
                +{breakdown.saas_model ?? 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Growth Signals (max 20):</span>
              <span className="font-mono font-medium text-emerald-400">
                +{breakdown.growth_signals ?? 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Evidence Quality (max 20):</span>
              <span className="font-mono font-medium text-emerald-400">
                +{breakdown.evidence_quality ?? 0}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
