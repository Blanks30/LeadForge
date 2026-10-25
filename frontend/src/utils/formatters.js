/**
 * Formatting helpers for LeadForge UI
 */

export function formatDate(dateString) {
  if (!dateString) return 'Not yet researched';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  } catch {
    return dateString;
  }
}

export function getScoreColor(score) {
  if (score >= 80) {
    return {
      bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      ring: 'text-emerald-400',
      label: 'High Alignment',
    };
  }
  if (score >= 50) {
    return {
      bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      ring: 'text-amber-400',
      label: 'Moderate Alignment',
    };
  }
  return {
    bg: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
    ring: 'text-slate-400',
    label: 'Low / Pending',
  };
}

export function sanitizeDisplayUrl(url) {
  if (!url) return '';
  return url.replace(/^https?:\/\//, '').replace(/\/$/, '');
}
