import React from 'react';
import { Target, Download, Database, RefreshCw, Plus, Globe } from 'lucide-react';
import { api } from '../api/client';

export function Header({
  apiHealthy,
  healthStatus,
  onRetryHealth,
  onOpenIcp,
  onOpenAddCompany,
  onOpenWebSearch,
  onSeedDemo,
  seeding,
  prospectCount,
}) {
  const exportUrl = api.getExportUrl();

  const mode = healthStatus?.mode || (apiHealthy ? 'MOCK' : 'OFFLINE');
  const isHealthy = healthStatus ? healthStatus.healthy : apiHealthy;
  const isLoading = healthStatus?.loading;

  // Three explicit operational states:
  // 1. LIVE_VERIFIED: Real external Gemini connection confirmed operational
  // 2. LIVE_CONFIGURED: Live keys in environment, awaiting/failing real ping check
  // 3. MOCK: Offline evaluation mode with deterministic fixtures
  const isLiveVerified = mode === 'LIVE_VERIFIED';
  const isLiveConfigured = mode === 'LIVE_CONFIGURED';
  const isMock = mode === 'MOCK';

  return (
    <header className="border-b border-[#272736] bg-[#0A0A0D] sticky top-0 z-40 transition-colors shadow-md">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-2.5 sm:py-3.5 flex flex-wrap items-center justify-between gap-3 sm:gap-4">
        {/* Logo and Tagline */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          <a href="#hero" className="flex items-center gap-2 sm:gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-[#14141A] border border-[#272736] flex items-center justify-center text-brand-500 shadow-sm group-hover:scale-105 transition-transform flex-shrink-0">
              <svg className="w-5 h-5 stroke-current" fill="none" strokeLinecap="round" strokeWidth="2.2" viewBox="0 0 28 28">
                <path d="M5 14C5 9.02944 9.02944 5 14 5C18.9706 5 23 9.02944 23 14" />
                <path d="M9 14C9 11.2386 11.2386 9 14 9C16.7614 9 19 11.2386 19 14" />
                <path d="M13 14C13 13.4477 13.4477 13 14 13C14.5523 13 15 13.4477 15 14C15 17 12 19 12 22" />
                <path d="M17 17C17 19.5 15.5 23 14 23" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-1.5 sm:gap-2">
                <h1 className="text-sm sm:text-base font-bold font-display text-white tracking-tight">LeadForge</h1>
                <span className="text-[10px] uppercase font-mono font-bold tracking-wider px-1.5 sm:px-2 py-0.2 sm:py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/30">
                  MVP
                </span>
              </div>
              <p className="text-[11px] sm:text-xs text-zinc-400 truncate max-w-[210px] sm:max-w-none">
                Evidence-First Sales Intelligence<span className="hidden sm:inline"> • Zero Hallucination</span>
              </p>
            </div>
          </a>
        </div>

        {/* Global Action Toolbar */}
        <div className="flex items-center flex-wrap gap-1.5 sm:gap-2.5">
          {/* Health & API Mode Indicator */}
          <div className="hidden sm:inline-flex items-center gap-2">
            {isLoading ? (
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border bg-[#14141A] text-zinc-400 border-[#272736]">
                <RefreshCw className="w-3 h-3 animate-spin text-zinc-400" />
                <span className="text-[11px]">Connecting...</span>
              </div>
            ) : isHealthy ? (
              <div className="inline-flex items-center gap-1.5">
                {/* Active Connection Dot */}
                <div
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-[#062E20] text-emerald-400 border-emerald-600/50 shadow-sm"
                  title="Backend API connected and SQLite database operational"
                >
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
                  </span>
                  <span className="font-medium text-[11px] font-mono">API Active</span>
                </div>

                {/* Clear MOCK vs LIVE Mode Indicator Badge with 3 distinct states */}
                <span
                  data-testid="api-mode-badge"
                  className={`text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded border inline-flex items-center gap-1 ${
                    isLiveVerified
                      ? 'bg-emerald-950/60 text-emerald-300 border-emerald-500/50'
                      : isLiveConfigured
                      ? 'bg-amber-950/60 text-amber-300 border-amber-500/50'
                      : 'bg-zinc-800/80 text-zinc-300 border-zinc-700/60'
                  }`}
                  title={
                    isLiveVerified
                      ? 'Live Mode Verified: Real Google Gemini API connectivity confirmed operational'
                      : isLiveConfigured
                      ? 'Live Mode Configured: API keys present, external connectivity check pending or degraded'
                      : 'Mock Mode: Offline evaluation using deterministic grounded fixtures'
                  }
                >
                  <span>
                    {isLiveVerified
                      ? 'LIVE • VERIFIED'
                      : isLiveConfigured
                      ? 'LIVE • CONFIGURED'
                      : 'MOCK'}
                  </span>
                </span>
              </div>
            ) : (
              /* Disconnected / Failure State with Retry Button */
              <div className="inline-flex items-center gap-1.5">
                <div
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-[#2A0E0E] text-rose-400 border-rose-800/50"
                  title={healthStatus?.error || 'Backend API offline'}
                >
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-400"></span>
                  <span className="font-medium text-[11px] font-mono">API Offline</span>
                </div>
                {onRetryHealth && (
                  <button
                    onClick={onRetryHealth}
                    className="p-1 rounded-md bg-[#14141A] hover:bg-[#1B1B22] text-zinc-400 hover:text-white border border-[#272736] text-[11px] font-mono transition-colors focus-ring"
                    title="Retry connection"
                    aria-label="Retry connection"
                  >
                    <RefreshCw className="w-3 h-3" />
                  </button>
                )}
              </div>
            )}
          </div>

          {/* ICP Configuration Trigger */}
          <button
            onClick={onOpenIcp}
            className="px-2.5 sm:px-3 py-1.5 rounded-lg bg-[#14141A] hover:bg-[#1B1B22] text-xs font-medium text-zinc-200 border border-[#272736] hover:border-brand-500/40 flex items-center gap-1.5 transition-all shadow-sm focus-ring"
            aria-label="Configure Ideal Customer Profile"
          >
            <Target className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
            <span>Target ICP</span>
          </button>

          {/* General-Purpose Web Search */}
          <button
            onClick={onOpenWebSearch}
            className="px-2.5 sm:px-3 py-1.5 rounded-lg bg-[#14141A] hover:bg-[#1B1B22] text-xs font-medium text-cyan-300 border border-cyan-800/40 hover:border-cyan-500/60 flex items-center gap-1.5 transition-all shadow-sm focus-ring"
            title="Search the web with Tavily"
            aria-label="Search the web"
          >
            <Globe className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
            <span>
              <span className="hidden sm:inline">Web Search</span>
              <span className="sm:hidden">Search</span>
            </span>
          </button>

          {/* Add Custom Company */}
          <button
            onClick={onOpenAddCompany}
            className="px-2.5 sm:px-3 py-1.5 rounded-lg bg-[#14141A] hover:bg-[#1B1B22] text-xs font-medium text-zinc-200 border border-[#272736] hover:border-brand-500/40 flex items-center gap-1.5 transition-all shadow-sm focus-ring"
            title="Add any custom company for AI research"
            aria-label="Add custom company"
          >
            <Plus className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
            <span>
              <span className="hidden sm:inline">Add Company</span>
              <span className="sm:hidden">Add</span>
            </span>
          </button>

          {/* Seed Demo Prospects */}
          <button
            onClick={onSeedDemo}
            disabled={seeding}
            className="px-2.5 sm:px-3 py-1.5 rounded-lg bg-[#14141A] hover:bg-[#1B1B22] text-xs font-medium text-zinc-200 border border-[#272736] hover:border-brand-500/40 flex items-center gap-1.5 transition-all shadow-sm disabled:opacity-50 focus-ring"
            title="Seed 10 target Indian SMB SaaS companies"
            aria-label="Seed 10 demo prospects"
          >
            <Database className={`w-3.5 h-3.5 text-brand-400 flex-shrink-0 ${seeding ? 'animate-spin' : ''}`} />
            <span>
              {seeding ? (
                'Seeding...'
              ) : (
                <>
                  <span className="hidden sm:inline">Seed 10 Prospects</span>
                  <span className="sm:hidden">Seed (10)</span>
                </>
              )}
            </span>
          </button>

          {/* Export to CSV */}
          <a
            href={exportUrl}
            download="leadforge_prospects.csv"
            className="px-2.5 sm:px-3 py-1.5 rounded-lg bg-brand-500 hover:bg-brand-600 text-xs font-semibold text-white shadow-sm hover:shadow-md flex items-center gap-1.5 transition-all focus-ring active:scale-95"
            aria-label="Export prospects to CSV"
          >
            <Download className="w-3.5 h-3.5 flex-shrink-0" />
            <span>
              <span className="hidden sm:inline">Export CSV</span>
              <span className="sm:hidden">Export</span>
            </span>
          </a>
        </div>
      </div>
    </header>
  );
}
