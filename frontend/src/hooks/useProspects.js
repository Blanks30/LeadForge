import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

export function useProspects() {
  const [prospects, setProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiHealthy, setApiHealthy] = useState(true);

  const [icp, setIcp] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [minScore, setMinScore] = useState('');

  const [researchingId, setResearchingId] = useState(null);
  const [seeding, setSeeding] = useState(false);

  // Modals state
  const [showIcpModal, setShowIcpModal] = useState(false);
  const [evidenceProspect, setEvidenceProspect] = useState(null);
  const [outreachProspect, setOutreachProspect] = useState(null);

  // Check health & fetch initial ICP
  const loadInitialContext = useCallback(async () => {
    try {
      const health = await api.getHealth();
      setApiHealthy(health?.status === 'ok' && health?.db === true);
    } catch {
      setApiHealthy(false);
    }

    try {
      const icpData = await api.getIcp();
      setIcp(icpData);
    } catch (err) {
      console.warn('Could not load ICP profile:', err);
    }
  }, []);

  // Fetch prospect list based on active filters
  const loadProspects = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getProspects({
        minScore,
        status: statusFilter,
        search,
      });
      setProspects(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to LeadForge API');
    } finally {
      setLoading(false);
    }
  }, [minScore, statusFilter, search]);

  useEffect(() => {
    loadInitialContext();
  }, [loadInitialContext]);

  useEffect(() => {
    loadProspects();
  }, [loadProspects]);

  // Seed 10 sample prospects
  const handleSeed = async () => {
    setSeeding(true);
    try {
      await api.seedProspects();
      await loadProspects();
    } catch (err) {
      setError(err.message || 'Failed to seed initial prospects');
    } finally {
      setSeeding(false);
    }
  };

  // Trigger web crawl and research
  const handleResearch = async (id) => {
    setResearchingId(id);
    try {
      const updated = await api.researchProspect(id);
      setProspects((prev) =>
        prev.map((p) => (p.id === id ? { ...p, ...updated } : p))
      );
      // If modal is open for this prospect, update it too
      if (evidenceProspect?.id === id) {
        setEvidenceProspect(updated);
      }
    } catch (err) {
      setError(`Research failed for prospect #${id}: ${err.message}`);
      setProspects((prev) =>
        prev.map((p) => (p.id === id ? { ...p, status: 'FAILED' } : p))
      );
    } finally {
      setResearchingId(null);
    }
  };

  // Inspect granular evidence
  const handleInspectEvidence = async (id) => {
    try {
      const detail = await api.getProspectDetail(id);
      setEvidenceProspect(detail);
    } catch (err) {
      setError(err.message || 'Failed to fetch prospect evidence detail');
    }
  };

  // Open outreach draft modal
  const handleOpenDraft = async (id) => {
    try {
      const detail = await api.getProspectDetail(id);
      setOutreachProspect(detail);
    } catch (err) {
      setError(err.message || 'Failed to prepare outreach draft');
    }
  };

  return {
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
  };
}
