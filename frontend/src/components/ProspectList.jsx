import React from 'react';
import { Search, Filter, Database, CheckCircle, Clock } from 'lucide-react';
import { ProspectRow } from './ProspectRow';

export function ProspectList({
  prospects,
  loading,
  search,
  setSearch,
  statusFilter,
  setStatusFilter,
  minScore,
  setMinScore,
  onResearch,
  onInspectEvidence,
  onOpenDraft,
  researchingId,
  onSeedDemo,
  seeding,
}) {
  const analyzedCount = prospects.filter((p) => p.status === 'ANALYZED').length;
  const pendingCount = prospects.filter((p) => p.status === 'PENDING').length;

  return (
    <div className="space-y-4">
      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        <div className="p-4 rounded-xl bg-[#141418] border border-[#272736] shadow-sm flex items-center justify-between hover:border-brand-500/40 transition-all duration-200">
          <div className="space-y-0.5">
            <span className="text-xs text-zinc-400 font-medium block">Total Prospects</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold font-mono text-white tracking-tight">
                {prospects.length}
              </span>
              <span className="text-[11px] text-zinc-500 font-mono">B2B SaaS</span>
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-brand-500/10 text-brand-400 border border-brand-500/30 shadow-sm">
            <Database className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#141418] border border-[#272736] shadow-sm flex items-center justify-between hover:border-emerald-500/40 transition-all duration-200">
          <div className="space-y-0.5">
            <span className="text-xs text-zinc-400 font-medium block">Researched & Scored</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold font-mono text-emerald-400 tracking-tight">
                {analyzedCount}
              </span>
              <span className="text-[11px] text-zinc-500 font-mono">
                {prospects.length > 0
                  ? `${Math.round((analyzedCount / prospects.length) * 100)}% evaluated`
                  : '0%'}
              </span>
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shadow-sm">
            <CheckCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[#141418] border border-[#272736] shadow-sm flex items-center justify-between hover:border-amber-500/40 transition-all duration-200">
          <div className="space-y-0.5">
            <span className="text-xs text-zinc-400 font-medium block">Awaiting Research</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold font-mono text-amber-400 tracking-tight">
                {pendingCount}
              </span>
              <span className="text-[11px] text-zinc-500 font-mono">Pending crawl</span>
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30 shadow-sm">
            <Clock className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 bg-[#141418] border border-[#272736] rounded-xl flex flex-wrap items-center justify-between gap-3 shadow-sm">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[220px]">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            id="prospect-search"
            aria-label="Search prospects by company or domain"
            placeholder="Search by company or domain (e.g. Khatabook)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0C0C0F] border border-[#272736] text-xs text-zinc-200 placeholder:text-zinc-500 pl-9 pr-3 py-2 rounded-lg focus-ring focus:border-brand-500 transition-colors"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Status Dropdown */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="status-filter" className="sr-only">Filter by status</label>
            <Filter className="w-3.5 h-3.5 text-zinc-400 pointer-events-none" aria-hidden="true" />
            <select
              id="status-filter"
              aria-label="Filter prospects by research status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[#0C0C0F] border border-[#272736] text-xs text-zinc-200 px-3 py-2 rounded-lg focus-ring focus:border-brand-500 transition-colors cursor-pointer"
            >
              <option value="">All Statuses</option>
              <option value="ANALYZED">Analyzed</option>
              <option value="PENDING">Pending</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>

          {/* Min Score Filter */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="min-score-filter" className="text-xs text-zinc-400 font-medium cursor-pointer">
              Min Score:
            </label>
            <select
              id="min-score-filter"
              aria-label="Filter prospects by minimum lead score"
              value={minScore}
              onChange={(e) => setMinScore(e.target.value)}
              className="bg-[#0C0C0F] border border-[#272736] text-xs text-zinc-200 px-3 py-2 rounded-lg focus-ring focus:border-brand-500 transition-colors font-mono cursor-pointer"
            >
              <option value="">Any Score</option>
              <option value="80">High (80+ pts)</option>
              <option value="50">Moderate (50+ pts)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-[#0E0E12] rounded-xl overflow-hidden border border-[#272736] shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#272736] bg-[#141418] text-[11px] uppercase font-mono font-bold tracking-wider text-zinc-400 select-none">
                <th className="py-3 px-4 sm:px-6">Company & Domain</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Lead Score (0–100)</th>
                <th className="py-3 px-4 sm:px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && prospects.length === 0 ? (
                // Skeleton loading rows
                [1, 2, 3, 4, 5].map((idx) => (
                  <tr key={idx} className="border-b border-[#272736]/60 animate-pulse">
                    <td className="py-4 px-4 sm:px-6">
                      <div className="h-4 bg-[#1A1A22] rounded w-36 mb-2"></div>
                      <div className="h-3 bg-[#1A1A22]/70 rounded w-24"></div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-5 bg-[#1A1A22] rounded w-20"></div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-6 bg-[#1A1A22] rounded w-24"></div>
                    </td>
                    <td className="py-4 px-4 sm:px-6 text-right">
                      <div className="h-8 bg-[#1A1A22] rounded w-44 ml-auto"></div>
                    </td>
                  </tr>
                ))
              ) : prospects.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-16 text-center">
                    <div className="max-w-sm mx-auto space-y-3.5">
                      <div className="w-12 h-12 rounded-2xl bg-brand-500/10 border border-brand-500/30 flex items-center justify-center mx-auto text-brand-400 shadow-sm">
                        <Database className="w-6 h-6" />
                      </div>
                      <div className="space-y-1">
                        <h4 className="text-base font-bold text-white tracking-tight">No prospects found</h4>
                        <p className="text-xs text-zinc-400 leading-relaxed">
                          Seed the initial 10 curated Indian SMB SaaS prospects to evaluate TinyFish crawling, grounding, and rubric scoring.
                        </p>
                      </div>
                      <button
                        onClick={onSeedDemo}
                        disabled={seeding}
                        className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-xs font-semibold rounded-lg shadow-sm transition-all focus-ring disabled:opacity-50 active:scale-95"
                      >
                        {seeding ? 'Seeding Database...' : 'Seed 10 Sample Prospects'}
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                prospects.map((prospect) => (
                  <ProspectRow
                    key={prospect.id}
                    prospect={prospect}
                    onResearch={onResearch}
                    onInspectEvidence={onInspectEvidence}
                    onOpenDraft={onOpenDraft}
                    isResearching={researchingId === prospect.id}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
