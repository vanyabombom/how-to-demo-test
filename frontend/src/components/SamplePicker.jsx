import React, { useRef } from 'react';
import { Video, Upload, Play, Sparkles, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function SamplePicker({
  samples,
  currentSampleId,
  onSelectSample,
  onReprocessSample,
  onUploadFile,
  isProcessing
}) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUploadFile(file);
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3.5 mb-5">
      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-3">
        <div className="flex items-center space-x-2">
          <Video className="w-4 h-4 text-slate-400" />
          <h2 className="text-xs font-semibold text-slate-200 tracking-tight uppercase tracking-wider">
            Input Demonstration Stream
          </h2>
          <span className="text-slate-600 text-xs">•</span>
          <span className="text-xs text-slate-400">
            Select sample scenario or upload any MP4
          </span>
        </div>

        {/* Upload Custom MP4 */}
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="video/mp4,video/webm,video/quicktime"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-50"
          >
            <Upload className="w-3.5 h-3.5 text-slate-400" />
            <span>Upload MP4</span>
          </button>
        </div>
      </div>

      {/* Grid of Clean Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
        {samples.map((sample) => {
          const isSelected = currentSampleId === sample.id;

          let scenarioBadge = 'Normal flow';
          let badgeStyle = 'text-slate-400 bg-slate-800/80 border-slate-700';

          if (sample.scenario_type === 'corrected_mistake') {
            scenarioBadge = 'Mistake recovery';
            badgeStyle = 'text-amber-400 bg-amber-950/40 border-amber-800/50';
          } else if (sample.scenario_type === 'incomplete_gap') {
            scenarioBadge = 'Validation edgecase';
            badgeStyle = 'text-rose-400 bg-rose-950/40 border-rose-800/50';
          } else if (sample.has_cached_result === false) {
            scenarioBadge = 'Vision AI needed';
            badgeStyle = 'text-indigo-400 bg-indigo-950/40 border-indigo-800/50';
          }

          return (
            <div
              key={sample.id}
              data-testid={`sample-card-${sample.id}`}
              onClick={() => !isProcessing && onSelectSample(sample.id)}
              className={`p-3 rounded-lg border transition-all cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? 'bg-blue-950/20 border-blue-500/80 shadow-sm'
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
              } ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}
            >
              <div>
                <div className="flex items-center justify-between gap-1.5 mb-1.5">
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${badgeStyle}`}>
                    {scenarioBadge}
                  </span>
                  {isSelected && (
                    <span className="text-[11px] font-mono text-blue-400 flex items-center space-x-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                      <span>Active</span>
                    </span>
                  )}
                </div>

                <div className="font-medium text-slate-200 text-xs mb-1 line-clamp-1">
                  {sample.title}
                </div>
                <div className="text-slate-400 text-[11px] leading-relaxed line-clamp-2">
                  {sample.description}
                </div>
              </div>

              {/* Bottom Actions */}
              <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-[11px] font-mono text-slate-400 flex items-center space-x-1 hover:text-slate-200">
                  <Play className="w-3 h-3" />
                  <span>{isSelected ? 'Loaded' : 'Select'}</span>
                </span>

                {onReprocessSample && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onReprocessSample(sample.id);
                    }}
                    title="Process recording with Multimodal Vision AI"
                    className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-blue-600 text-slate-300 hover:text-white border border-slate-700 hover:border-blue-500 text-[11px] font-medium transition"
                  >
                    <Sparkles className="w-3 h-3 text-blue-400 group-hover:text-white" />
                    <span>Run AI Analysis</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
