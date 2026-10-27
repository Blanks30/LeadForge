import React, { useState } from 'react';
import { ChevronDown, ArrowRight, FileText, Database, Shield, Sparkles, CheckCircle2, AlertTriangle, AlertCircle, Search, Send, Layers } from 'lucide-react';

export function HeroLanding({ onExploreClick, activeTab = 'sales-intelligence', onTabChange }) {
  const [activeDockTab, setActiveDockTab] = useState(activeTab);
  const [chatInput, setChatInput] = useState('');

  const handleDockClick = (tabId) => {
    setActiveDockTab(tabId);
    if (onTabChange) onTabChange(tabId);
    if (onExploreClick) onExploreClick();
  };

  return (
    <div className="w-full max-w-[1680px] mx-auto p-2 sm:p-4 lg:p-6 font-sans">
      {/* Flagship Hero Window Wrapper */}
      <section 
        className="w-full rounded-[28px] sm:rounded-[36px] overflow-hidden relative studio-backdrop border border-[#272736] shadow-[0_30px_90px_rgba(0,0,0,0.85)] flex flex-col justify-between select-none"
        aria-label="LeadForge Sales Intelligence Platform Overview"
      >
        {/* Subtle Ambient Studio Glows (Pure background layers, NO blur over content) */}
        <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
          <div className="absolute -top-32 -left-20 w-[580px] h-[580px] bg-amber-600/10 rounded-full blur-[140px]" />
          <div className="absolute bottom-10 left-1/4 w-[700px] h-[400px] bg-orange-700/10 rounded-full blur-[160px]" />
          <div className="absolute top-1/4 right-0 w-[500px] h-[500px] bg-stone-700/10 rounded-full blur-[130px]" />
        </div>

        {/* Top Navigation Header */}
        <header className="relative z-30 px-6 sm:px-10 lg:px-12 pt-6 pb-4 flex items-center justify-between border-b border-[#272736]/40">
          {/* Brand Logo with Fold Spiral Icon */}
          <div className="flex items-center gap-3">
            <a href="#hero" className="flex items-center gap-2.5 group">
              <div className="w-7 h-7 flex items-center justify-center text-brand-500 transition-transform group-hover:scale-105">
                <svg className="w-full h-full stroke-current" fill="none" strokeLinecap="round" strokeWidth="2.2" viewBox="0 0 28 28">
                  <path d="M5 14C5 9.02944 9.02944 5 14 5C18.9706 5 23 9.02944 23 14" />
                  <path d="M9 14C9 11.2386 11.2386 9 14 9C16.7614 9 19 11.2386 19 14" />
                  <path d="M13 14C13 13.4477 13.4477 13 14 13C14.5523 13 15 13.4477 15 14C15 17 12 19 12 22" />
                  <path d="M17 17C17 19.5 15.5 23 14 23" />
                </svg>
              </div>
              <span className="text-xl font-bold font-display tracking-tight text-white">LeadForge</span>
            </a>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-7 text-[13.5px] font-medium text-zinc-300">
            <div className="flex items-center gap-1.5 hover:text-white cursor-pointer transition-colors">
              <span>Products</span>
              <ChevronDown className="w-3.5 h-3.5 opacity-60" />
            </div>
            <a href="#live-console" onClick={onExploreClick} className="hover:text-white transition-colors">
              Live Console
            </a>
            <a href="#plans" className="hover:text-white transition-colors">
              Plans
            </a>
            <a href="#security" className="hover:text-white transition-colors">
              Security
            </a>
            <div className="flex items-center gap-1.5 hover:text-white cursor-pointer transition-colors">
              <span>Resources</span>
              <ChevronDown className="w-3.5 h-3.5 opacity-60" />
            </div>
            <a href="#company" className="hover:text-white transition-colors">
              Company
            </a>
          </nav>

          {/* CTA Group */}
          <div className="flex items-center gap-3">
            <button
              onClick={onExploreClick}
              className="text-[13.5px] font-medium text-zinc-300 hover:text-white transition-colors px-3 py-1.5 focus-ring rounded"
            >
              Sign in
            </button>
            <a
              href="#book-call"
              onClick={(e) => {
                e.preventDefault();
                if (onExploreClick) onExploreClick();
              }}
              className="text-[13px] font-semibold text-zinc-950 bg-white hover:bg-zinc-100 transition-all rounded-full px-5 py-2.5 shadow-sm active:scale-95 focus-ring"
            >
              Book a call
            </a>
          </div>
        </header>

        {/* Hero Body Layout */}
        <div className="relative z-20 flex-1 grid grid-cols-12 items-center px-3 sm:px-10 lg:px-14 py-6 sm:py-8 lg:py-12 gap-6 sm:gap-8 lg:gap-10">
          {/* Left Column: Cinematic Typography & Dual CTAs */}
          <div className="col-span-12 lg:col-span-5 flex flex-col justify-center max-w-xl z-20">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/25 text-brand-400 text-xs font-mono font-semibold mb-6 w-fit">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse" />
              <span>EVIDENCE-FIRST SALES INTELLIGENCE</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-[68px] font-extrabold font-display tracking-[-0.035em] text-white leading-[1.05]">
              Ask your prospects anything.
            </h1>

            <p className="mt-6 text-base sm:text-lg text-zinc-300 font-normal leading-relaxed max-w-md">
              B2B Sales Intelligence, built to discover verified revenue and eliminate deal hallucination.
            </p>

            {/* CTA Buttons */}
            <div className="mt-8 flex flex-wrap items-center gap-3.5">
              <button
                type="button"
                onClick={onExploreClick}
                className="inline-flex items-center justify-center gap-2 text-sm font-semibold bg-white text-zinc-950 hover:bg-zinc-100 rounded-full px-7 py-3.5 transition-transform active:scale-95 shadow-md focus-ring"
              >
                <span>Explore LeadForge</span>
                <ArrowRight className="w-4 h-4 text-zinc-950" />
              </button>
              <a
                href="#live-console"
                onClick={onExploreClick}
                className="inline-flex items-center justify-center text-sm font-medium text-white bg-[#1A1A22] hover:bg-[#22222D] border border-[#272736] rounded-full px-6 py-3.5 transition-all focus-ring"
              >
                Live Workstation
              </a>
            </div>

            {/* Quick ICP Proof Chips */}
            <div className="mt-10 pt-6 border-t border-[#272736]/60 flex flex-wrap items-center gap-4 text-xs font-mono text-zinc-400">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="text-zinc-200 font-semibold">FACT</span> Verbatim Grounding
              </div>
              <span className="text-zinc-600">•</span>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                <span className="text-zinc-200 font-semibold">100-pt</span> Rubric Engine
              </div>
              <span className="text-zinc-600">•</span>
              <div className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-brand-400" />
                <span className="text-zinc-200 font-semibold">Zero-Send</span> Protected
              </div>
            </div>
          </div>

          {/* Right Column: Studio Workstation with Angled High-Res Display */}
          <div className="col-span-12 lg:col-span-7 h-full flex items-center justify-center lg:justify-end relative perspective-container">
            {/* Physical Monitor Chassis */}
            <div className="relative w-full max-w-[760px] monitor-tilted rounded-[16px] sm:rounded-[20px] p-2 sm:p-[10px] bg-[#141418] border border-[#2B2B38] shadow-2xl flex flex-col">
              {/* Inner Screen Bezel */}
              <div className="w-full h-full bg-[#FAFAF9] text-zinc-900 rounded-[12px] overflow-hidden flex flex-col font-sans select-text shadow-inner">
                {/* App Topbar */}
                <div className="h-auto min-h-10 bg-[#F2F2F1] border-b border-zinc-200 px-3 sm:px-4 py-1.5 flex flex-wrap items-center justify-between gap-1.5 text-xs text-zinc-600">
                  <div className="flex items-center gap-1.5 sm:gap-2 overflow-hidden min-w-0">
                    <div className="w-4 h-4 text-zinc-800 flex-shrink-0">
                      <svg className="w-full h-full stroke-current" fill="none" strokeWidth="2.5" viewBox="0 0 28 28">
                        <path d="M5 14C5 9.02944 9.02944 5 14 5C18.9706 5 23 9.02944 23 14" />
                        <path d="M9 14C9 11.2386 11.2386 9 14 9C16.7614 9 19 11.2386 19 14" />
                      </svg>
                    </div>
                    <span className="font-semibold text-zinc-800 text-[11px] sm:text-[12px] truncate">LeadForge Workspace</span>
                    <span className="text-zinc-300">/</span>
                    <span className="text-zinc-600 font-medium hidden sm:inline text-[11px] sm:text-[12px]">Evaluation</span>
                    <span className="text-zinc-300 hidden sm:inline">/</span>
                    <span className="text-zinc-900 font-semibold truncate text-[11px] sm:text-[12px]">Khatabook</span>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <span className="inline-flex items-center px-1.5 sm:px-2 py-0.5 rounded text-[10px] sm:text-[10.5px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                      48 Verified
                    </span>
                    <span className="inline-flex items-center px-1.5 sm:px-2 py-0.5 rounded text-[10px] sm:text-[10.5px] font-semibold bg-rose-100 text-rose-800 border border-rose-300 hidden sm:inline-flex">
                      2 Discrepancies
                    </span>
                    <span className="inline-flex items-center px-1.5 sm:px-2 py-0.5 rounded text-[10px] sm:text-[10.5px] font-semibold bg-amber-100 text-amber-800 border border-amber-300">
                      1 Risk
                    </span>
                  </div>
                </div>

                {/* App Inner Content: Two Panes */}
                <div className="flex-1 flex overflow-hidden min-h-[340px] sm:min-h-[360px]">
                  {/* Left Sidebar */}
                  <aside className="w-44 bg-[#F7F7F6] border-r border-zinc-200 p-3 flex flex-col justify-between hidden sm:flex text-xs">
                    <div className="space-y-3">
                      <button 
                        onClick={onExploreClick}
                        className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-white border border-zinc-200 shadow-sm text-zinc-800 font-medium hover:bg-zinc-50 transition-colors"
                      >
                        <span className="text-brand-600 font-bold">+</span>
                        <span>New ICP Audit</span>
                      </button>

                      <div className="space-y-0.5 pt-1">
                        <div className="px-2 py-1 text-[10px] font-bold text-zinc-600 uppercase tracking-wider">
                          Intelligence
                        </div>
                        <div className="px-2.5 py-1.5 rounded bg-zinc-200/80 font-semibold text-zinc-900 flex items-center justify-between">
                          <span>Live Accounts</span>
                          <span className="text-[10px] bg-zinc-300 px-1.5 rounded text-zinc-700 font-mono">14</span>
                        </div>
                        <div className="px-2.5 py-1.5 text-zinc-600 hover:text-zinc-900 cursor-pointer">Evidence Vault</div>
                        <div className="px-2.5 py-1.5 text-zinc-600 hover:text-zinc-900 cursor-pointer">Rubric Scoring</div>
                        <div className="px-2.5 py-1.5 text-zinc-600 hover:text-zinc-900 cursor-pointer">CRM Sync Feed</div>
                      </div>
                    </div>

                    {/* Auditor Profile */}
                    <div className="pt-2 border-t border-zinc-200 flex items-center gap-2 text-zinc-700">
                      <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-stone-800 to-amber-700 text-white font-semibold flex items-center justify-center text-[10px]">
                        AD
                      </div>
                      <div className="truncate leading-tight">
                        <div className="font-medium text-[11px] text-zinc-900">Adam Driver</div>
                        <div className="text-[10px] text-zinc-600 font-medium">Enterprise SE</div>
                      </div>
                    </div>
                  </aside>

                  {/* Main Rubric & Investigation Pane */}
                  <main className="flex-1 p-2.5 sm:p-3.5 bg-white flex flex-col justify-between overflow-y-auto">
                    {/* Chat Prompt & Attachment Pills */}
                    <div className="space-y-2 sm:space-y-2.5">
                      <div className="flex items-start justify-end">
                        <div className="bg-zinc-100 border border-zinc-200 rounded-2xl rounded-tr-sm px-3 sm:px-3.5 py-2 text-[11.5px] sm:text-[12px] text-zinc-800 font-medium max-w-md shadow-sm">
                          Check this pipeline cohort against our 100-pt Enterprise ICP rubric.
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center justify-end gap-1 sm:gap-1.5 text-[10px] sm:text-[10.5px] text-zinc-600 font-mono">
                        <span className="inline-flex items-center gap-1 px-1.5 sm:px-2 py-0.5 rounded bg-zinc-100 border border-zinc-200 truncate max-w-full">
                          📄 khatabook_fy24_sec_filing.pdf
                        </span>
                        <span className="inline-flex items-center gap-1 px-1.5 sm:px-2 py-0.5 rounded bg-zinc-100 border border-zinc-200 truncate max-w-full">
                          📊 salesforce_opp_export.xlsx (14)
                        </span>
                      </div>

                      {/* LeadForge Status Lines */}
                      <div className="text-[11px] sm:text-[11.5px] text-zinc-600 space-y-1 font-sans">
                        <div className="flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse flex-shrink-0" />
                          <span className="truncate">Extracted 48 entities from SEC disclosures & hiring trends.</span>
                        </div>
                        <div className="flex items-center gap-2 text-zinc-600">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                          <span>Cross-referenced ICP: <strong className="text-zinc-900">92/100 Total Fit</strong></span>
                        </div>
                      </div>

                      {/* Rubric Verification Table */}
                      <div className="border border-zinc-200 rounded-lg overflow-hidden text-left mt-1 shadow-sm">
                        <div className="bg-zinc-50 px-2.5 sm:px-3 py-1.5 border-b border-zinc-200 text-[10px] sm:text-[10.5px] font-bold text-zinc-700 flex flex-wrap items-center justify-between gap-1">
                          <span className="truncate">ICP CRITERIA VERIFICATION</span>
                          <span className="font-mono text-zinc-600 font-semibold text-[10px] sm:text-[10.5px]">92/100 FIT SCORE</span>
                        </div>
                        <div className="overflow-x-auto">
                          <table className="w-full text-[11px] text-zinc-800 min-w-[360px]">
                            <thead className="bg-zinc-100 text-[10px] text-zinc-700 uppercase border-b border-zinc-200 font-bold">
                              <tr>
                                <th className="py-1 px-2">Rule ID</th>
                                <th className="py-1 px-2">Requirement</th>
                                <th className="py-1 px-2">Reported</th>
                                <th className="py-1 px-2">Verified</th>
                                <th className="py-1 px-2">Status</th>
                                <th className="py-1 px-2">Evidence</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-100 font-sans">
                              <tr>
                                <td className="py-1 px-2 font-mono text-zinc-700 font-medium text-[10px]">RRV-02</td>
                                <td className="py-1 px-2 font-medium">ARR Tier (&gt;$10M)</td>
                                <td className="py-1 px-2 text-zinc-700">$14.2M</td>
                                <td className="py-1 px-2 font-semibold text-zinc-950">$14.35M</td>
                                <td className="py-1 px-2 text-emerald-700 font-semibold font-mono text-[10px]">[FACT] +1.1%</td>
                                <td className="py-1 px-2 text-zinc-700 font-mono text-[9.5px]">10-K p. 64</td>
                              </tr>
                              <tr>
                                <td className="py-1 px-2 font-mono text-zinc-700 font-medium text-[10px]">V-DATE-01</td>
                                <td className="py-1 px-2 font-medium">Budget Cycle End</td>
                                <td className="py-1 px-2 text-zinc-700">Q3 2026</td>
                                <td className="py-1 px-2 font-semibold text-zinc-950">31.03.2026</td>
                                <td className="py-1 px-2 text-rose-700 font-semibold font-mono text-[10px]">Shifted</td>
                                <td className="py-1 px-2 text-zinc-700 font-mono text-[9.5px]">Amendment 1</td>
                              </tr>
                              <tr>
                                <td className="py-1 px-2 font-mono text-zinc-700 font-medium text-[10px]">RRV-04</td>
                                <td className="py-1 px-2 font-medium">Core Tech Stack</td>
                                <td className="py-1 px-2 text-zinc-700">Snowflake</td>
                                <td className="py-1 px-2 font-semibold text-zinc-950">Snowflake+dbt</td>
                                <td className="py-1 px-2 text-emerald-700 font-semibold font-mono text-[10px]">[FACT] Confirmed</td>
                                <td className="py-1 px-2 text-zinc-700 font-mono text-[9.5px]">Job Ad #82</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>

                      {/* Quick Action Buttons */}
                      <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 pt-1 text-[10px] sm:text-[10.5px]">
                        <button className="px-2 py-0.5 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-medium border border-zinc-200 transition-colors">
                          Keep contract value
                        </button>
                        <button className="px-2 py-0.5 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-medium border border-zinc-200 transition-colors">
                          Update CRM pipeline
                        </button>
                        <button 
                          onClick={onExploreClick}
                          className="px-2 py-0.5 rounded text-orange-700 hover:bg-orange-50 font-medium flex items-center gap-1 transition-colors"
                        >
                          <span>Open in Data Studio</span>
                          <span>→</span>
                        </button>
                      </div>
                    </div>

                    {/* Chat Prompt Input Bar */}
                    <div className="mt-2.5 sm:mt-3 pt-2 border-t border-zinc-100">
                      <div className="w-full rounded-lg bg-zinc-50 border border-zinc-200 px-2.5 sm:px-3 py-1.5 flex items-center justify-between text-xs">
                        <input
                          type="text"
                          id="hero-chat-input"
                          aria-label="Ask questions about this prospect or upload dossiers"
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          placeholder="Ask anything about this prospect or upload dossiers..."
                          className="w-full bg-transparent border-none text-xs text-zinc-800 placeholder:text-zinc-500 focus:outline-none pr-2"
                        />
                        <button 
                          onClick={onExploreClick}
                          className="w-6 h-6 rounded bg-zinc-800 hover:bg-zinc-700 text-white flex items-center justify-center flex-shrink-0 transition-colors"
                          title="Execute prompt"
                          aria-label="Execute prompt"
                        >
                          ↑
                        </button>
                      </div>
                    </div>
                  </main>
                </div>
              </div>
            </div>

            {/* Aluminum Stand & Base (Positioned Below Display) */}
            <div className="hidden lg:block absolute -bottom-7 right-[240px] w-24 h-16 aluminum-stand rounded-md -z-10 transform -skew-x-6" />
            <div className="hidden lg:block absolute -bottom-8 right-[180px] w-48 h-3.5 rounded-full bg-gradient-to-r from-zinc-700 via-zinc-400 to-zinc-800 shadow-2xl -z-10" />
          </div>
        </div>

        {/* Bottom Segmented Product Switcher / Dock */}
        <div className="relative z-30 px-6 sm:px-10 lg:px-12 pb-6 pt-3 desk-reflection" data-purpose="product-dock-switcher">
          <div className="flex items-end gap-3 overflow-x-auto pb-1 scrollbar-none">
            {/* Tab 1: Platform */}
            <button
              type="button"
              onClick={() => handleDockClick('platform')}
              className={`group flex items-center gap-3 px-5 py-3.5 rounded-xl border text-left min-w-[170px] transition-all focus-ring ${
                activeDockTab === 'platform'
                  ? 'bg-white text-zinc-950 border-white shadow-xl scale-[1.02] -translate-y-1'
                  : 'bg-[#141418] hover:bg-[#1B1B22] border-[#272736] text-zinc-300'
              }`}
            >
              <div className={`w-5 h-5 ${activeDockTab === 'platform' ? 'text-zinc-900' : 'text-zinc-400 group-hover:text-zinc-200'} transition-colors`}>
                <Layers className="w-full h-full stroke-current" />
              </div>
              <div>
                <div className={`text-[13px] font-semibold ${activeDockTab === 'platform' ? 'text-zinc-950 font-bold' : 'text-zinc-300 group-hover:text-white'}`}>
                  Platform
                </div>
              </div>
            </button>

            {/* Tab 2: Pipeline Intelligence */}
            <button
              type="button"
              onClick={() => handleDockClick('pipeline-intelligence')}
              className={`group flex items-center gap-3 px-5 py-3.5 rounded-xl border text-left min-w-[210px] transition-all focus-ring ${
                activeDockTab === 'pipeline-intelligence'
                  ? 'bg-white text-zinc-950 border-white shadow-xl scale-[1.02] -translate-y-1'
                  : 'bg-[#141418] hover:bg-[#1B1B22] border-[#272736] text-zinc-300'
              }`}
            >
              <div className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold border border-emerald-500/40">
                PI
              </div>
              <div>
                <div className={`text-[13px] font-semibold ${activeDockTab === 'pipeline-intelligence' ? 'text-zinc-950 font-bold' : 'text-zinc-300 group-hover:text-white'}`}>
                  Pipeline Intelligence
                </div>
              </div>
            </button>

            {/* Tab 3: Sales Intelligence (ACTIVE CARD HIGHLIGHT - Pure White Popout from Screenshot) */}
            <button
              type="button"
              onClick={() => handleDockClick('sales-intelligence')}
              className={`flex items-center gap-3 px-6 py-4 rounded-xl border text-left min-w-[220px] transition-all focus-ring ${
                activeDockTab === 'sales-intelligence'
                  ? 'bg-white text-zinc-950 shadow-2xl border-white scale-[1.03] -translate-y-1.5'
                  : 'bg-[#141418] hover:bg-[#1B1B22] border-[#272736] text-zinc-300'
              }`}
            >
              <div className="px-1.5 py-0.5 rounded bg-brand-500 text-white text-[10.5px] font-mono font-bold shadow-sm">
                SI
              </div>
              <div>
                <div className={`text-[13.5px] tracking-tight ${activeDockTab === 'sales-intelligence' ? 'font-bold text-zinc-950' : 'font-semibold text-zinc-300'}`}>
                  Sales Intelligence
                </div>
              </div>
            </button>

            {/* Tab 4: More coming in 2026 */}
            <button
              type="button"
              onClick={() => handleDockClick('more-2026')}
              className={`group flex items-center gap-3 px-5 py-3.5 rounded-xl border text-left min-w-[200px] transition-all focus-ring ${
                activeDockTab === 'more-2026'
                  ? 'bg-white text-zinc-950 border-white shadow-xl scale-[1.02] -translate-y-1'
                  : 'bg-[#141418] hover:bg-[#1B1B22] border-[#272736] text-zinc-400'
              }`}
            >
              <div className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 text-[10px] font-mono font-bold border border-indigo-500/40">
                AI
              </div>
              <div>
                <div className={`text-[13px] font-semibold ${activeDockTab === 'more-2026' ? 'text-zinc-950 font-bold' : 'text-zinc-400 group-hover:text-zinc-200'}`}>
                  More coming in 2026
                </div>
              </div>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
