# Demo2HowTo: Video Demonstration to Usable How-To Prototype

A working prototype that converts short screen demonstration recordings into actionable, verified, step-by-step how-to guides with grounded screenshot evidence, mistake pruning, and missing step detection.

---

## Quick Start (< 2 minutes)

### Prerequisites
- **Python 3.11+** (tested on 3.13 / 3.14)
- **Node.js 18+** & npm

> **Note on FFmpeg**: Zero manual installation is needed. The project uses `imageio-ffmpeg` which automatically provides a bundled, self-contained binary on Windows, Linux, and macOS.

### 1. One-Click Start (Windows)
Double-click `run.bat` (or run `./run.ps1` in PowerShell).

*Or run manually:*

#### Terminal 1: Backend
```powershell
cd backend
py -3.13 -m pip install -r requirements.txt
py -3.13 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2: Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open **`http://localhost:5173`** in your browser.

---

## Free API Key Options (Zero Payment / No Credit Card)

You can run the application **without any API key** immediately:
1. The **3 pre-loaded test samples** (Normal, Mistake Correction, Jump/Decline) work 100% offline out-of-the-box with ground truth and real-time frame extraction!
2. To test your **own custom MP4 videos**, get a **100% free API key** in 20 seconds from **[OpenRouter](https://openrouter.ai/keys)** (sign in with GitHub/Google, no credit card needed).
3. Paste the key directly in the web UI under **"Configure Free API"** or in `backend/.env`.

Supported free models:
- `google/gemini-2.0-flash-exp:free` *(Recommended on OpenRouter)*
- `meta-llama/llama-3.2-11b-vision-instruct:free`
- `qwen/qwen-2-vl-72b-instruct:free`
- `llama-3.2-11b-vision-preview` *(via Groq)*

---

## Core Capabilities Verified

1. **Visual Action Recovery (Silent Steps)**: Recovers necessary actions that occurred on screen without any spoken words.
2. **Mistake Pruning & Final Setting Retention**: Identifies abandoned mistakes, prunes them from the recommended guide, and preserves the final chosen settings.
3. **Anti-Hallucination & Gap Detection**: Refuses to fabricate clicks. Flags jump cuts (`missing_step_gap`) and declines to conclude when critical steps are omitted.
4. **Interactive Timeline & Grounding**: Every instruction links to an extracted screenshot frame and exact timestamp. Clicking any step in the guide automatically seeks the video player.
5. **Measured Speed & Cost**: End-to-end latency and itemized token / compute costs are reported per operation.

---

## Running Verification Tests

To verify backend tests:
```powershell
cd backend
py -3.13 -m pytest tests/test_backend.py -v
```

To run the full test suite evaluation against ground-truth:
```powershell
py -3.13 backend/sample_data/run_sample_eval.py
```

---

## Documentation
See [`DELIVERY_NOTES.md`](./DELIVERY_NOTES.md) for full delivery documentation including measured speed/cost metrics, failure analysis, model evaluation, and product trade-offs.
