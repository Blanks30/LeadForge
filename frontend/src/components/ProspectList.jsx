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
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block">Total Prospects</span>
            <span className="text-xl font-bold text-white">{prospects.length}</span>
          </div>
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Database className="w-5 h-5" />
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block">Researched & Scored</span>
            <span className="text-xl font-bold text-emerald-400">{analyzedCount}</span>
          </div>
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <CheckCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 block">Awaiting Research</span>
            <span className="text-xl font-bold text-amber-400">{pendingCount}</span>
          </div>
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
            <Clock className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-3 shadow-sm">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by company or domain (e.g. Khatabook)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 pl-9 pr-3 py-2 rounded-lg focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        {/* Status Dropdown */}
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-200 px-2.5 py-2 rounded-lg focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="ANALYZED">Analyzed</option>
            <option value="PENDING">Pending</option>
          </select>
        </div>

        {/* Min Score Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Min Score:</span>
          <select
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-200 px-2.5 py-2 rounded-lg focus:outline-none focus:border-indigo-500"
          >
            <option value="">Any Score</option>
            <option value="80">High (80+)</option>
            <option value="50">Moderate (50+)</option>
          </select>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/80 text-[11px] uppercase font-bold tracking-wider text-slate-400">
                <th className="py-3 px-4 sm:px-6">Company & Domain</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Lead Score (0-100)</th>
                <th className="py-3 px-4 sm:px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && prospects.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-12 text-center text-slate-500">
                    Loading prospects...
                  </td>
                </tr>
              ) : prospects.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-16 text-center">
                    <div className="max-w-sm mx-auto space-y-3">
                      <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
                        <Database className="w-6 h-6" />
                      </div>
                      <h4 className="text-base font-bold text-white">No prospects found</h4>
                      <p className="text-xs text-slate-400">
                        Seed the initial 10 curated Indian SMB SaaS prospects to evaluate research and scoring.
                      </p>
                      <button
                        onClick={onSeedDemo}
                        disabled={seeding}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md transition-colors"
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
