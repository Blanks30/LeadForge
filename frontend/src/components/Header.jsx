import React from 'react';
import { Target, Download, Database, Flame, Activity } from 'lucide-react';
import { api } from '../api/client';

export function Header({
  apiHealthy,
  onOpenIcp,
  onSeedDemo,
  seeding,
  prospectCount,
}) {
  const exportUrl = api.getExportUrl();

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Logo and Tagline */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 p-0.5 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Flame className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-white tracking-tight">LeadForge</h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                MVP
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Evidence-First Sales Intelligence • Zero Hallucination
            </p>
          </div>
        </div>

        {/* Global Action Toolbar */}
        <div className="flex items-center gap-2.5">
          {/* Health Indicator */}
          <div
            className={`hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
              apiHealthy
                ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40'
                : 'bg-red-950/40 text-red-400 border-red-800/40'
            }`}
            title={apiHealthy ? 'Backend API connected' : 'Backend API disconnected'}
          >
            <Activity className="w-3 h-3" />
            <span>{apiHealthy ? 'API Active' : 'API Offline'}</span>
          </div>

          {/* ICP Configuration Trigger */}
          <button
            onClick={onOpenIcp}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 text-xs font-semibold text-slate-200 border border-slate-700 flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Target className="w-3.5 h-3.5 text-indigo-400" />
            <span>Target ICP</span>
          </button>

          {/* Seed Demo Prospects */}
          <button
            onClick={onSeedDemo}
            disabled={seeding}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 text-xs font-semibold text-slate-200 border border-slate-700 flex items-center gap-1.5 transition-colors shadow-sm disabled:opacity-50"
            title="Seed 10 target Indian SMB SaaS companies"
          >
            <Database className={`w-3.5 h-3.5 text-indigo-400 ${seeding ? 'animate-spin' : ''}`} />
            <span>{seeding ? 'Seeding...' : 'Seed 10 Prospects'}</span>
          </button>

          {/* Export to CSV */}
          <a
            href={exportUrl}
            download="leadforge_prospects.csv"
            className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white shadow-md shadow-indigo-600/20 flex items-center gap-1.5 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>
    </header>
  );
}
