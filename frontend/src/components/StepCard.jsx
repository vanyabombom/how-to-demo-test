import React, { useState } from 'react';
import { Play, Eye, AlertTriangle, Check, VolumeX, ShieldAlert, Maximize2, X } from 'lucide-react';

export default function StepCard({ step, isActive, onSeek }) {
  const [showFullImage, setShowFullImage] = useState(false);

  // Close lightbox on Escape
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setShowFullImage(false);
      }
    };
    if (showFullImage) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showFullImage]);

  const isMistake = step.step_type === 'corrected_mistake';
  const isSilent = step.step_type === 'silent_action';
  const isGap = step.step_type === 'missing_step_gap';

  return (
    <div
      className={`rounded-lg border transition-all p-3.5 mb-2.5 relative ${
        isActive
          ? 'bg-slate-900 border-blue-500/80 shadow-xs ring-1 ring-blue-500/20'
          : isMistake
            ? 'bg-slate-950/40 border-amber-900/30 opacity-70'
            : isGap
              ? 'bg-rose-950/20 border-rose-900/50'
              : 'bg-slate-900/50 border-slate-800/80 hover:border-slate-700'
      }`}
    >
      {/* Active Left Marker Stripe */}
      {isActive && (
        <div className="absolute left-0 top-3 bottom-3 w-0.5 bg-blue-500 rounded-r" />
      )}

      {/* Header: Step Number, Title, Type Badges, Seek Button */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-start space-x-2.5 min-w-0">
          {/* Step Number Node */}
          <span
            className={`w-5 h-5 rounded flex items-center justify-center text-[11px] font-mono font-bold shrink-0 mt-0.5 ${
              isMistake
                ? 'bg-amber-950/80 text-amber-400 border border-amber-800/60 line-through'
                : isGap
                  ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
                  : isSilent
                    ? 'bg-purple-950/80 text-purple-300 border border-purple-800/60'
                    : 'bg-slate-800 text-slate-300 border border-slate-700'
            }`}
          >
            {step.step_number}
          </span>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5 mb-1">
              <h3
                className={`font-medium text-xs tracking-tight ${
                  isMistake
                    ? 'text-amber-400/80 line-through'
                    : isGap
                      ? 'text-rose-300 font-semibold'
                      : 'text-slate-100'
                }`}
              >
                {step.title}
              </h3>

              {/* Status Badges */}
              {isSilent && (
                <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-purple-950/50 text-purple-300 border border-purple-800/50">
                  <VolumeX className="w-2.5 h-2.5" />
                  <span>Silent visual action</span>
                </span>
              )}

              {isMistake && (
                <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-amber-950/50 text-amber-300 border border-amber-800/50">
                  <AlertTriangle className="w-2.5 h-2.5" />
                  <span>Pruned mistake</span>
                </span>
              )}

              {isGap && (
                <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-rose-950/50 text-rose-300 border border-rose-800/50">
                  <ShieldAlert className="w-2.5 h-2.5" />
                  <span>Missing step gap</span>
                </span>
              )}
            </div>

            {/* Instruction Prose */}
            <p className="text-xs text-slate-300 leading-relaxed font-normal">
              {step.instruction}
            </p>
          </div>
        </div>

        {/* Timestamp Seek Button */}
        <button
          onClick={() => onSeek(step.timestamp_keyframe_sec)}
          title={`Seek video to ${step.timestamp_start}`}
          className="shrink-0 flex items-center space-x-1 px-2 py-1 rounded text-[11px] font-mono bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700 transition"
        >
          <Play className="w-2.5 h-2.5 text-blue-400" />
          <span>{step.timestamp_start}</span>
        </button>
      </div>

      {/* Warning or Gap Note */}
      {step.warning_or_gap_note && (
        <div
          className={`mt-2 p-2 rounded text-[11px] flex items-start space-x-1.5 font-mono ${
            isGap
              ? 'bg-rose-950/40 text-rose-300 border border-rose-900/60'
              : isMistake
                ? 'bg-amber-950/40 text-amber-300 border border-amber-900/60'
                : 'bg-purple-950/40 text-purple-300 border border-purple-900/60'
          }`}
        >
          <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5 text-rose-400" />
          <span>{step.warning_or_gap_note}</span>
        </div>
      )}

      {/* Applied Setting & Evidence Row */}
      <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 text-[11px]">
        {step.chosen_setting && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-slate-500 font-mono text-[10px]">Applied:</span>
            {Object.entries(step.chosen_setting).map(([k, v]) => (
              <span
                key={k}
                className="px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-200 font-mono text-[10px] border border-slate-700/60"
              >
                <span className="text-slate-400">{k}:</span> {String(v)}
              </span>
            ))}
          </div>
        )}

        {step.evidence_description && (
          <div className="text-slate-400 text-[11px] flex items-center space-x-1 min-w-0">
            <Eye className="w-3 h-3 text-slate-500 shrink-0" />
            <span className="truncate max-w-[200px] sm:max-w-[340px] text-slate-400">{step.evidence_description}</span>
          </div>
        )}
      </div>

      {/* Keyframe Evidence Thumbnail */}
      {step.screenshot_url && (
        <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div
              onClick={() => setShowFullImage(true)}
              className="relative w-20 h-12 rounded overflow-hidden border border-slate-700/80 cursor-pointer group bg-black shrink-0"
            >
              <img
                src={step.screenshot_url}
                alt={`Keyframe at ${step.timestamp_start}`}
                className="w-full h-full object-cover transition group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition flex items-center justify-center">
                <Maximize2 className="w-3 h-3 text-white opacity-0 group-hover:opacity-100 transition" />
              </div>
            </div>

            <div>
              <div className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">Grounding Keyframe</div>
              <div className="text-[11px] font-mono text-slate-300">
                {step.timestamp_start} <span className="text-slate-600">({step.timestamp_keyframe_sec}s)</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => setShowFullImage(true)}
            className="text-[11px] font-mono text-slate-400 hover:text-blue-400 transition"
          >
            Inspect Frame
          </button>
        </div>
      )}

      {/* Lightbox Modal */}
      {showFullImage && step.screenshot_url && (
        <div
          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setShowFullImage(false)}
        >
          <div
            className="max-w-4xl max-h-[90vh] bg-slate-900 border border-slate-700 rounded-lg overflow-hidden shadow-2xl p-2 relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-2 py-1.5 border-b border-slate-800 text-xs font-mono text-slate-300 mb-2">
              <span>Step {step.step_number}: {step.title} ({step.timestamp_start})</span>
              <button
                onClick={() => setShowFullImage(false)}
                className="p-1 text-slate-400 hover:text-white rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <img
              src={step.screenshot_url}
              alt="Screenshot full view"
              className="w-full h-auto max-h-[78vh] object-contain rounded"
            />
          </div>
        </div>
      )}
    </div>
  );
}
