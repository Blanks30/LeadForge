import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { getScoreColor } from '../utils/formatters';
import { Info, X } from 'lucide-react';

export function ScoreBadge({ score, breakdown }) {
  const [isOpen, setIsOpen] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0, placeBelow: false });
  const containerRef = useRef(null);
  const buttonRef = useRef(null);
  const popoverRef = useRef(null);

  const updatePosition = useCallback(() => {
    if (!buttonRef.current) return;
    const rect = buttonRef.current.getBoundingClientRect();
    const popoverWidth = 288; // w-72 = 288px
    const popoverHeight = 260;

    // Check space above button
    const spaceAbove = rect.top;
    const placeBelow = spaceAbove < popoverHeight + 16;

    // Center horizontally on button, clamped to screen edges with 12px margin
    let targetLeft = rect.left + rect.width / 2 - popoverWidth / 2;
    targetLeft = Math.max(12, Math.min(targetLeft, window.innerWidth - popoverWidth - 12));

    const targetTop = placeBelow ? rect.bottom + 8 : rect.top - 8;

    setCoords({
      top: targetTop,
      left: targetLeft,
      placeBelow,
    });
  }, []);

  // Update position on open, scroll, or resize
  useEffect(() => {
    if (isOpen) {
      updatePosition();
      window.addEventListener('resize', updatePosition);
      window.addEventListener('scroll', updatePosition, true);
    }
    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition, true);
    };
  }, [isOpen, updatePosition]);

  // Close on outside click and Escape key, restore focus on Escape
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    }
    function handleClickOutside(e) {
      const isOutsideButton = buttonRef.current && !buttonRef.current.contains(e.target);
      const isOutsidePopover = popoverRef.current && !popoverRef.current.contains(e.target);
      if (isOutsideButton && isOutsidePopover) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const numScore = Number(score) || 0;
  const color = getScoreColor(numScore);

  // Radial progress calculations (circle diameter 28px, radius 11px, circumference 2 * pi * 11 ≈ 69.1)
  const radius = 11;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset =
    circumference - (Math.min(100, Math.max(0, numScore)) / 100) * circumference;

  const ringColor =
    numScore >= 80
      ? 'text-emerald-400 stroke-emerald-400'
      : numScore >= 50
      ? 'text-amber-400 stroke-amber-400'
      : 'text-slate-400 stroke-slate-400';

  // 4 rubric dimensions accurately represented from backend scoring_engine.py
  const smbScore = breakdown?.smb_focus ?? 0;
  const saasScore = breakdown?.saas_model ?? 0;
  const growthScore = breakdown?.growth_signals ?? 0;
  const evidenceScore = breakdown?.evidence_quality ?? 0;

  const rubricItems = [
    {
      id: 'smb',
      label: 'SMB Focus in India',
      earned: smbScore,
      max: 35,
      color: 'bg-emerald-500',
    },
    {
      id: 'saas',
      label: 'SaaS Delivery Model',
      earned: saasScore,
      max: 25,
      color: 'bg-indigo-500',
    },
    {
      id: 'growth',
      label: 'Growth & Market Signals',
      earned: growthScore,
      max: 20,
      color: 'bg-amber-500',
    },
    {
      id: 'evidence',
      label: 'Evidence Quality',
      earned: evidenceScore,
      max: 20,
      color: 'bg-emerald-400',
    },
  ];

  return (
    <div className="relative inline-flex items-center" ref={containerRef}>
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsOpen(!isOpen);
          }
        }}
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        title="Click to view 100-point rubric breakdown"
        className={`group inline-flex items-center gap-2 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all duration-150 focus-ring cursor-pointer select-none ${
          numScore >= 80
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25 hover:border-emerald-500/40 hover:bg-emerald-500/15'
            : numScore >= 50
            ? 'bg-amber-500/10 text-amber-400 border-amber-500/25 hover:border-amber-500/40 hover:bg-amber-500/15'
            : 'bg-slate-500/10 text-slate-400 border-slate-500/25 hover:border-slate-500/40 hover:bg-slate-500/15'
        }`}
      >
        {/* Compact Radial Progress Meter */}
        <div className="relative w-6 h-6 flex-shrink-0 flex items-center justify-center">
          <svg className="w-6 h-6 -rotate-90 transform" viewBox="0 0 28 28">
            {/* Background track */}
            <circle
              cx="14"
              cy="14"
              r={radius}
              className="stroke-obsidian-border text-obsidian-border"
              strokeWidth="2.5"
              fill="transparent"
            />
            {/* Animated progress stroke */}
            <circle
              cx="14"
              cy="14"
              r={radius}
              className={`${ringColor} transition-all duration-500 ease-out`}
              strokeWidth="2.5"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
            />
          </svg>
        </div>

        {/* Numeric Score */}
        <div className="flex items-baseline gap-0.5 font-mono">
          <span className="text-sm font-bold tracking-tight text-white">{numScore}</span>
          <span className="text-[10px] text-slate-500">/100</span>
        </div>

        {/* Info indicator */}
        {breakdown && (
          <span className="p-0.5 rounded text-slate-500 group-hover:text-slate-300 transition-colors">
            <Info className="w-3 h-3" />
          </span>
        )}
      </button>

      {/* Accessible Score Breakdown Popover Rendered via Portal (never clipped by table overflow) */}
      {isOpen && breakdown && typeof document !== 'undefined' && createPortal(
        <div
          ref={popoverRef}
          role="dialog"
          aria-label="100-Point Rubric Breakdown"
          style={{
            position: 'fixed',
            top: `${coords.top}px`,
            left: `${coords.left}px`,
            transform: coords.placeBelow ? 'none' : 'translateY(-100%)',
          }}
          className="z-50 w-72 p-4 bg-[#15151C] border border-[#272736] rounded-xl shadow-2xl text-xs text-zinc-300 animate-slide-up"
        >
          {/* Popover Header */}
          <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-[#272736]">
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-white tracking-tight">Rubric Breakdown</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-brand-500/10 text-brand-400 border border-brand-500/30">
                0–100
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-sm text-white">{numScore} pts</span>
              <button
                type="button"
                onClick={() => {
                  setIsOpen(false);
                  buttonRef.current?.focus();
                }}
                className="text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors focus-ring"
                aria-label="Close popover"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* 4 Rubric Categories with Progress Bars */}
          <div className="space-y-3">
            {rubricItems.map((item) => {
              const pct = Math.min(100, Math.round((item.earned / item.max) * 100));
              return (
                <div key={item.id} className="space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-300 font-medium">{item.label}</span>
                    <span className="font-mono text-white font-semibold">
                      +{item.earned}
                      <span className="text-slate-500 text-[10px] font-normal"> / {item.max}</span>
                    </span>
                  </div>
                  {/* Progress Bar Track */}
                  <div className="w-full h-1.5 rounded-full bg-obsidian-950 overflow-hidden border border-obsidian-border/60">
                    <div
                      className={`h-full rounded-full ${item.color} transition-all duration-300`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Footnote */}
          <div className="mt-3 pt-2.5 border-t border-obsidian-border/80 flex items-center justify-between text-[10px] text-slate-500">
            <span>Deterministic Python Engine</span>
            <span className="text-slate-400 font-medium">{color.label}</span>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}

