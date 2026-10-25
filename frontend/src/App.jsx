import React from 'react';
import { useProspects } from './hooks/useProspects';
import { Header } from './components/Header';
import { ProspectList } from './components/ProspectList';
import { EvidenceModal } from './components/EvidenceModal';
import { OutreachModal } from './components/OutreachModal';
import { IcpConfigModal } from './components/IcpConfigModal';
import { Target, AlertTriangle } from 'lucide-react';

export default function App() {
  const {
    prospects,
    loading,
    error,
    apiHealthy,
    icp,
    setIcp,
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    minScore,
    setMinScore,
    researchingId,
    seeding,
    handleSeed,
    handleResearch,
    handleInspectEvidence,
    handleOpenDraft,
    showIcpModal,
    setShowIcpModal,
    evidenceProspect,
    setEvidenceProspect,
    outreachProspect,
    setOutreachProspect,
  } = useProspects();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <Header
        apiHealthy={apiHealthy}
        onOpenIcp={() => setShowIcpModal(true)}
        onSeedDemo={handleSeed}
        seeding={seeding}
        prospectCount={prospects.length}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-sm flex items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="text-xs bg-red-900/60 hover:bg-red-900 px-3 py-1 rounded text-white font-medium"
            >
              Retry
            </button>
          </div>
        )}

        {/* Active ICP Banner */}
        {icp && (
          <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800/80 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  Target Profile
                </span>
                <span className="text-xs text-slate-400">•</span>
                <span className="text-xs font-semibold text-slate-200">
                  {icp.vertical}
                </span>
                <span className="text-xs text-slate-400">({icp.target_geo})</span>
              </div>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {(icp.smb_criteria || []).slice(0, 3).map((criterion, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60"
                  >
                    {criterion}
                  </span>
                ))}
                {(icp.smb_criteria || []).length > 3 && (
                  <span className="text-[11px] text-slate-500 font-mono self-center">
                    +{icp.smb_criteria.length - 3} more
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={() => setShowIcpModal(true)}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 underline underline-offset-4"
            >
              Configure Criteria →
            </button>
          </div>
        )}

        {/* Prospects Dashboard Table */}
        <ProspectList
          prospects={prospects}
          loading={loading}
          search={search}
          setSearch={setSearch}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          minScore={minScore}
          setMinScore={setMinScore}
          onResearch={handleResearch}
          onInspectEvidence={handleInspectEvidence}
          onOpenDraft={handleOpenDraft}
          researchingId={researchingId}
          onSeedDemo={handleSeed}
          seeding={seeding}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-4 text-center text-xs text-slate-500">
        <p>LeadForge • Evidence-First Sales Intelligence for B2B SaaS • TriCode</p>
      </footer>

      {/* Modals */}
      {showIcpModal && (
        <IcpConfigModal
          icp={icp}
          onUpdate={(updated) => setIcp(updated)}
          onClose={() => setShowIcpModal(false)}
        />
      )}

      {evidenceProspect && (
        <EvidenceModal
          prospect={evidenceProspect}
          onClose={() => setEvidenceProspect(null)}
        />
      )}

      {outreachProspect && (
        <OutreachModal
          prospect={outreachProspect}
          onClose={() => setOutreachProspect(null)}
        />
      )}
    </div>
  );
}
