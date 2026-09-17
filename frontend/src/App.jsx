import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricsBar from './components/MetricsBar';
import SamplePicker from './components/SamplePicker';
import VideoPlayer from './components/VideoPlayer';
import StepList from './components/StepList';
import ApiKeyModal from './components/ApiKeyModal';
import ExportModal from './components/ExportModal';
import { Loader2, AlertCircle } from 'lucide-react';

export default function App() {
  const [config, setConfig] = useState(null);
  const [samples, setSamples] = useState([]);
  const [currentSampleId, setCurrentSampleId] = useState('demo_base');
  const [videoUrl, setVideoUrl] = useState('/sample_data/demo_base.mp4');
  const [result, setResult] = useState(null);
  const [seekTime, setSeekTime] = useState(null);
  const [activeTime, setActiveTime] = useState(0);

  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  // 1. Fetch initial configuration and sample list
  useEffect(() => {
    fetchConfig();
    fetchSamples();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      setConfig(data);
    } catch (err) {
      console.error("Failed to load config", err);
    }
  };

  const fetchSamples = async () => {
    try {
      const res = await fetch('/api/samples');
      const data = await res.json();
      setSamples(data);
      if (data.length > 0) {
        loadSample(data[0].id);
      }
    } catch (err) {
      console.error("Failed to load samples", err);
    }
  };

  // 2. Load pre-computed sample
  const loadSample = async (id) => {
    const sample = samples.find((s) => s.id === id);
    if (sample && sample.has_cached_result === false) {
      // If sample has no precomputed ground-truth, run the vision model on it
      return handleReprocessSample(id);
    }

    setIsProcessing(true);
    setProcessingStatus('Loading demo video & ground-truth evidence...');
    setErrorMessage(null);
    try {
      const res = await fetch(`/api/sample/${id}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Failed to load sample ${id}`);
      }
      const data = await res.json();
      setResult(data);
      setCurrentSampleId(id);
      setVideoUrl(sample?.video_url || `/sample_data/${id}.mp4`);
      setSeekTime(0);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // 2.1 Reprocess sample with Vision LLM directly
  const handleReprocessSample = async (id) => {
    setIsProcessing(true);
    setProcessingStatus('Running multi-modal AI vision model on selected recording...');
    setErrorMessage(null);
    try {
      const res = await fetch(`/api/sample/${id}/process`, {
        method: 'POST'
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Analysis failed');
      }
      const data = await res.json();
      setResult(data);
      setCurrentSampleId(id);
      setVideoUrl(`/sample_data/${id}.mp4`);
      setSeekTime(0);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // 3. Upload and process new custom MP4
  const handleUploadFile = async (file) => {
    setIsProcessing(true);
    setProcessingStatus('Analyzing video frames with multimodal vision model...');
    setErrorMessage(null);
    setCurrentSampleId(null);

    // Create local object URL for instant video playback preview
    const localVideoUrl = URL.createObjectURL(file);
    setVideoUrl(localVideoUrl);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/process', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Analysis failed');
      }
      const data = await res.json();
      setResult(data);
      setSeekTime(0);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // 4. Save API config
  const handleSaveConfig = async (newConfig) => {
    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      await fetchConfig();
    } catch (err) {
      console.error("Failed to save config", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Top Navigation */}
      <Header
        config={config}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenExport={() => setIsExportOpen(true)}
        result={result}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        {/* Sample Selection Bar */}
        <SamplePicker
          samples={samples}
          currentSampleId={currentSampleId}
          onSelectSample={loadSample}
          onReprocessSample={handleReprocessSample}
          onUploadFile={handleUploadFile}
          isProcessing={isProcessing}
        />

        {/* Error message alert */}
        {errorMessage && (
          <div className="mb-5 p-3 rounded-lg bg-rose-950/30 border border-rose-900/60 text-rose-200 text-xs flex items-center justify-between font-mono">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="px-2 py-0.5 rounded bg-rose-900/60 hover:bg-rose-800 text-rose-200 text-[11px] font-medium transition"
            >
              Open Settings
            </button>
          </div>
        )}

        {/* Processing Spinner Banner */}
        {isProcessing && (
          <div className="mb-5 p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-300 text-xs flex items-center space-x-3 shadow-sm">
            <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
            <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-2">
              <span className="font-medium text-slate-200">{processingStatus}</span>
              <span className="text-slate-500 text-[11px] font-mono hidden sm:inline">• Sampling frames and verifying screen actions</span>
            </div>
          </div>
        )}

        {/* Metrics Bar */}
        <MetricsBar result={result} />

        {/* Split View: Video Player (Left) + Step Guide (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Video Player */}
          <div className="lg:col-span-5">
            <VideoPlayer
              videoUrl={videoUrl}
              seekTime={seekTime}
              steps={result?.steps || []}
              onTimeUpdate={(time) => setActiveTime(time)}
            />
          </div>

          {/* Right Column: Interactive How-To Steps */}
          <div className="lg:col-span-7">
            <StepList
              result={result}
              activeTime={activeTime}
              onSeekTimestamp={(sec) => setSeekTime(sec)}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            Built with <strong>FastAPI</strong>, <strong>React/Vite</strong>, <strong>Gemini 2.0 / Llama 3.2 Vision</strong>, and <strong>FFmpeg</strong>.
          </div>
          <div>
            Free credits are not zero operating cost • All costs and latencies measured.
          </div>
        </div>
      </footer>

      {/* Modals */}
      <ApiKeyModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        config={config}
        onSaveConfig={handleSaveConfig}
      />

      <ExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        result={result}
      />
    </div>
  );
}
