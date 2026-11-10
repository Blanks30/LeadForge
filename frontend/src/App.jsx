import React, { useRef, useState } from 'react';
import { useProspects } from './hooks/useProspects';
import { HeroLanding } from './components/HeroLanding';
import { Header } from './components/Header';
import { ProspectList } from './components/ProspectList';
import { EvidenceModal } from './components/EvidenceModal';
import { OutreachModal } from './components/OutreachModal';
import { IcpConfigModal } from './components/IcpConfigModal';
import { AddProspectModal } from './components/AddProspectModal';
import { WebSearchModal } from './components/WebSearchModal';
import { Target, AlertTriangle } from 'lucide-react';

export default function App() {
  const {
    prospects,
    loading,
    error,
    apiHealthy,
    healthStatus,
    checkHealth,
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
    showAddModal,
    setShowAddModal,
    handleProspectAdded,
    evidenceProspect,
    setEvidenceProspect,
    outreachProspect,
    setOutreachProspect,
  } = useProspects();

  const [showWebSearchModal, setShowWebSearchModal] = useState(false);
  const [addCompanyInitialData, setAddCompanyInitialData] = useState(null);

  const consoleRef = useRef(null);

  const scrollToConsole = () => {
    if (consoleRef.current) {
      consoleRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleAddCandidateFromSearch = (candidate) => {
    setShowWebSearchModal(false);
    setAddCompanyInitialData(candidate);
    setShowAddModal(true);
  };

  return (
    <div className="min-h-screen bg-[#070709] text-zinc-100 flex flex-col font-sans selection:bg-brand-500 selection:text-white overflow-x-hidden">
      {/* 1. Flagship Cinematic Hero Window Section */}
      <div id="hero">
        <HeroLanding
          onExploreClick={scrollToConsole}
          activeTab="sales-intelligence"
        />
      </div>

      {/* 2. Persistent Live Console Header */}
      <div id="live-console" ref={consoleRef} className="scroll-mt-4">
        <Header
          apiHealthy={apiHealthy}
          healthStatus={healthStatus}
          onRetryHealth={checkHealth}
          onOpenIcp={() => setShowIcpModal(true)}
          onOpenAddCompany={() => {
            setAddCompanyInitialData(null);
            setShowAddModal(true);
          }}
          onOpenWebSearch={() => setShowWebSearchModal(true)}
          onSeedDemo={handleSeed}
          seeding={seeding}
          prospectCount={prospects.length}
        />
      </div>

      {/* 3. Main Live Dashboard Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 space-y-4 sm:space-y-6">
        {/* Error Notification */}
        {error && (
          <div className="p-3.5 sm:p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-sm flex items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="text-xs bg-red-900/60 hover:bg-red-900 px-3 py-1 rounded text-white font-medium focus-ring"
            >
              Retry
            </button>
          </div>
        )}

        {/* Active ICP Banner (Solid Opaque Surface) */}
        {icp && (
          <div className="p-3.5 sm:p-4 rounded-xl bg-[#141418] border border-[#272736] shadow-sm flex flex-wrap items-center justify-between gap-3 sm:gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-brand-400" />
                <span className="text-xs font-bold font-mono uppercase tracking-wider text-brand-400">
                  Target Profile
                </span>
                <span className="text-xs text-zinc-500">•</span>
                <span className="text-xs font-semibold text-zinc-200">
                  {icp.vertical}
                </span>
                <span className="text-xs text-zinc-400 font-mono">({icp.target_geo})</span>
              </div>
              <div className="flex flex-wrap gap-1.5 pt-0.5">
                {(icp.smb_criteria || []).slice(0, 3).map((criterion, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#0C0C0F] text-zinc-300 border border-[#272736]"
                  >
                    {criterion}
                  </span>
                ))}
                {(icp.smb_criteria || []).length > 3 && (
                  <span className="text-[11px] text-zinc-500 font-mono self-center">
                    +{icp.smb_criteria.length - 3} more
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={() => setShowIcpModal(true)}
              className="text-xs font-semibold text-brand-400 hover:text-brand-300 underline underline-offset-4 focus-ring rounded"
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
          onOpenAddCompany={() => setShowAddModal(true)}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-[#272736] py-6 text-center text-xs text-zinc-500 bg-[#0A0A0D]">
        <p>LeadForge • Evidence-First Sales Intelligence for B2B SaaS • TriCode</p>
      </footer>

      {/* Modals */}
      {showWebSearchModal && (
        <WebSearchModal
          isOpen={showWebSearchModal}
          onClose={() => setShowWebSearchModal(false)}
          onAddAsCompany={handleAddCandidateFromSearch}
          existingProspects={prospects}
        />
      )}

      {showAddModal && (
        <AddProspectModal
          isOpen={showAddModal}
          onClose={() => {
            setShowAddModal(false);
            setAddCompanyInitialData(null);
          }}
          onProspectAdded={handleProspectAdded}
          initialData={addCompanyInitialData}
        />
      )}

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
