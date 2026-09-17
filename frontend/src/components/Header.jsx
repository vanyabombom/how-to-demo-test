import React from 'react';
import { PlaySquare, Sliders, Download, CheckCircle, AlertCircle, Cpu } from 'lucide-react';

export default function Header({ config, onOpenSettings, onOpenExport, result }) {
  const isLive = result?.source_mode === 'live_ai_inference';
  const isDeclined = result?.declined_to_conclude;

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-30 px-3.5 sm:px-6 py-2.5 sm:py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left: Brand & Product Mark */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400 shrink-0">
            <PlaySquare className="w-4 h-4" />
          </div>
          <div className="flex items-center space-x-1.5 sm:space-x-2.5">
            <span className="font-semibold text-xs sm:text-sm text-slate-100 tracking-tight">Demo2HowTo</span>
            <span className="text-[9px] sm:text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/60">
              v1.0
            </span>
          </div>
          <span className="text-slate-600 hidden sm:inline">/</span>
          <span className="text-xs text-slate-400 hidden sm:inline">
            Screen Recording to Verified Guide
          </span>
        </div>

        {/* Right: State indicator & Actions */}
        <div className="flex items-center space-x-1.5 sm:space-x-2.5 shrink-0">
          {/* Status Dot */}
          {result && (
            <div className={`hidden md:flex items-center space-x-2 px-2.5 py-1 rounded-md text-xs font-mono border ${
              isDeclined
                ? 'bg-amber-950/30 border-amber-800/60 text-amber-300'
                : 'bg-emerald-950/30 border-emerald-800/60 text-emerald-300'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isDeclined ? 'bg-amber-400' : 'bg-emerald-400'}`} />
              <span className="text-[11px]">
                {isDeclined ? 'Prerequisite Missing' : 'Grounding Verified'}
              </span>
            </div>
          )}

          {/* Engine indicator */}
          {result && (
            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono bg-slate-900 border border-slate-800 text-slate-400">
              <Cpu className="w-3 h-3 text-slate-500" />
              <span>{isLive ? result.model_name : 'ground-truth'}</span>
            </div>
          )}

          {/* Export Action */}
          {result && (
            <button
              onClick={onOpenExport}
              className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-md text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 transition"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              <span>Export</span>
            </button>
          )}

          {/* Settings / Keys */}
          <button
            onClick={onOpenSettings}
            className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-md text-xs font-medium border transition ${
              config?.has_api_key
                ? 'bg-slate-900 hover:bg-slate-800 text-slate-200 border-slate-700/80'
                : 'bg-blue-600 hover:bg-blue-500 text-white border-blue-500'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>
              {config?.has_api_key ? (
                <>
                  <span className="hidden sm:inline">Engine </span>Settings
                </>
              ) : (
                <>
                  <span className="hidden sm:inline">Connect </span>Model
                </>
              )}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
