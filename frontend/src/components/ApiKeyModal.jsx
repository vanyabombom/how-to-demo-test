import React, { useState } from 'react';
import { X, Key, Check, Globe, AlertTriangle, ExternalLink, Sliders } from 'lucide-react';

const PROVIDER_DEFAULTS = {
  openrouter: {
    baseUrl: 'https://openrouter.ai/api/v1',
    models: [
      { id: 'openrouter/free', label: 'Auto Free Vision (Recommended)', tag: 'Free' },
      { id: 'google/gemma-4-26b-a4b-it:free', label: 'Gemma 4 26B Vision (Free)', tag: 'Vision' }
    ],
    info: {
      title: 'OpenRouter Free Multimodal Hub',
      url: 'https://openrouter.ai/keys',
      urlText: 'openrouter.ai/keys',
      note: 'Auto-routes to available free vision models. Supports sequential screen frames and structured JSON guide generation.'
    }
  },
  gemini: {
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/',
    models: [
      { id: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash', tag: 'Recommended' },
      { id: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash', tag: 'Stable' }
    ],
    info: {
      title: 'Google AI Studio (Gemini Direct)',
      url: 'https://aistudio.google.com/apikey',
      urlText: 'aistudio.google.com/apikey',
      note: 'Native vision keyframe support with high throughput and generous free quotas directly from Google.'
    }
  },
  groq: {
    baseUrl: 'https://api.groq.com/openai/v1',
    models: [
      { id: 'llama-3.2-11b-vision-preview', label: 'Llama 3.2 Vision (Deprecated by Groq)', tag: 'Decommissioned' }
    ],
    info: {
      title: 'Groq Multimodal Notice',
      url: 'https://console.groq.com/keys',
      urlText: 'console.groq.com/keys',
      note: 'Groq decommissioned its preview vision models. Text-only models will reject image payloads. Use OpenRouter or Google Direct for vision pipelines.'
    }
  }
};

export default function ApiKeyModal({ isOpen, onClose, config, onSaveConfig }) {
  const [provider, setProvider] = useState(config?.api_provider || 'openrouter');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState(config?.base_url || PROVIDER_DEFAULTS.openrouter.baseUrl);
  const [modelName, setModelName] = useState(config?.model_name || PROVIDER_DEFAULTS.openrouter.models[0].id);
  const [isSaving, setIsSaving] = useState(false);

  // Close on Escape key
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleProviderChange = (p) => {
    setProvider(p);
    const defaults = PROVIDER_DEFAULTS[p];
    if (defaults) {
      setBaseUrl(defaults.baseUrl);
      setModelName(defaults.models[0].id);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    await onSaveConfig({
      api_provider: provider,
      api_key: apiKey ? apiKey.trim() : undefined,
      base_url: baseUrl.trim(),
      model_name: modelName.trim()
    });
    setIsSaving(false);
    onClose();
  };

  const currentDefaults = PROVIDER_DEFAULTS[provider] || PROVIDER_DEFAULTS.openrouter;
  const isKeySavedForProvider = config?.has_api_key && config?.api_provider === provider;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-700/80 rounded-lg max-w-lg w-full p-5 shadow-xl relative max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded"
          title="Close (Esc)"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-2.5 mb-4">
          <div className="w-8 h-8 rounded bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-white">Multimodal Engine Settings</h3>
            <p className="text-xs text-slate-400 font-mono">Vision-Language Model and Provider Routing</p>
          </div>
        </div>

        {/* Informational Box */}
        <div
          className={`mb-4 p-3 rounded border text-xs font-mono leading-relaxed ${
            provider === 'groq'
              ? 'bg-amber-950/30 border-amber-900/50 text-amber-300'
              : 'bg-slate-950 border-slate-800 text-slate-300'
          }`}
        >
          <div className="font-semibold flex items-center space-x-1.5 mb-1 text-slate-200">
            {provider === 'groq' ? (
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            ) : (
              <Globe className="w-3.5 h-3.5 text-blue-400" />
            )}
            <span>{currentDefaults.info.title}</span>
          </div>
          <p className="text-slate-400 mb-1.5 text-[11px] leading-relaxed">{currentDefaults.info.note}</p>
          <div className="text-[11px]">
            Portal:{' '}
            <a
              href={currentDefaults.info.url}
              target="_blank"
              rel="noreferrer"
              className="text-blue-400 underline inline-flex items-center hover:text-blue-300"
            >
              <span>{currentDefaults.info.urlText}</span>
              <ExternalLink className="w-2.5 h-2.5 ml-0.5" />
            </a>
          </div>
        </div>

        <form onSubmit={handleSave} className="space-y-3.5 text-xs">
          {/* Provider Select Segment */}
          <div>
            <label className="block text-slate-300 font-medium mb-1 font-mono text-[11px]">API Provider</label>
            <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-950 rounded border border-slate-800">
              {[
                { id: 'openrouter', label: 'OpenRouter' },
                { id: 'gemini', label: 'Google Gemini' },
                { id: 'groq', label: 'Groq' }
              ].map((item) => (
                <button
                  type="button"
                  key={item.id}
                  onClick={() => handleProviderChange(item.id)}
                  className={`py-1.5 px-2 rounded text-center font-mono text-xs transition ${
                    provider === item.id
                      ? 'bg-slate-800 text-white font-medium border border-slate-700 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* API Key */}
          <div>
            <label className="block text-slate-300 font-medium mb-1 font-mono text-[11px]">
              API Key{' '}
              {isKeySavedForProvider ? (
                <span className="text-emerald-400 font-mono text-[10px]">
                  (Saved: {config.masked_key})
                </span>
              ) : config?.has_api_key ? (
                <span className="text-amber-400 font-mono text-[10px]">
                  (Key active for {config.api_provider} — enter new key for {provider})
                </span>
              ) : (
                <span className="text-slate-500 font-mono text-[10px]">(Not configured)</span>
              )}
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={isKeySavedForProvider ? 'Leave blank to keep existing key' : `Enter ${provider} API key`}
              className="w-full px-3 py-1.5 rounded bg-slate-950 border border-slate-800 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 font-mono text-xs"
            />
          </div>

          {/* Model Presets & Input */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-slate-300 font-medium font-mono text-[11px]">Vision Model ID</label>
              <span className="text-[10px] font-mono text-slate-500">Requires multimodal support</span>
            </div>

            {/* Quick Presets */}
            <div className="flex flex-wrap gap-1 mb-2">
              {currentDefaults.models.map((m) => (
                <button
                  type="button"
                  key={m.id}
                  onClick={() => setModelName(m.id)}
                  className={`px-2 py-0.5 rounded text-[11px] font-mono border transition ${
                    modelName === m.id
                      ? 'bg-blue-950/60 border-blue-500 text-blue-200'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>

            <input
              type="text"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              className="w-full px-3 py-1.5 rounded bg-slate-950 border border-slate-800 text-white font-mono text-xs focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Base URL */}
          <div>
            <label className="block text-slate-300 font-medium mb-1 font-mono text-[11px]">
              Base URL (OpenAI-compatible)
            </label>
            <input
              type="text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              className="w-full px-3 py-1.5 rounded bg-slate-950 border border-slate-800 text-white font-mono text-xs focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded text-xs font-mono bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-3.5 py-1.5 rounded text-xs font-mono font-medium bg-blue-600 hover:bg-blue-500 text-white flex items-center space-x-1.5 transition disabled:opacity-50"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{isSaving ? 'Saving...' : 'Save Configuration'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
