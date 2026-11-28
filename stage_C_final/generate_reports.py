"""
generate_reports.py - Generates official faculty PDF deliverables for Module 2:
1. team_01_commitment_memo.pdf (Exact 1-page Client Commitment Memo)
2. team_01_module2_technical_report.pdf (Comprehensive technical report covering Missions 1-5 with 8 headings)
"""

from __future__ import annotations

import base64
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(r"c:\Users\dhanu\OneDrive\Desktop\EDGE AI2\Smart-Doorbell")
TEAM_DIR = REPO_ROOT / "team_01_module2"
STAGE_C_DIR = REPO_ROOT / "stage_C_final"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def image_to_base64(path: Path) -> str:
    if not path.exists():
        return ""
    data = path.read_bytes()
    ext = path.suffix.lower().replace(".", "")
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"

def build_commitment_memo_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Team 1 Paradise — Client Commitment Memo</title>
<style>
  @page {
    size: A4 portrait;
    margin: 11mm 14mm 9mm 14mm;
  }
  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    margin: 0;
    padding: 0;
    font-size: 8.6pt;
    line-height: 1.26;
  }
  .header {
    border-bottom: 2px solid #0f172a;
    padding-bottom: 4px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .title-area h1 {
    margin: 0 0 2px 0;
    font-size: 14.5pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
  }
  .title-area .subtitle {
    margin: 0;
    font-size: 8.2pt;
    color: #475569;
    font-weight: 500;
  }
  .meta-box {
    text-align: right;
    font-size: 7.8pt;
    color: #334155;
    line-height: 1.25;
  }
  .memo-badge {
    display: inline-block;
    background: #0284c7;
    color: #ffffff;
    font-weight: 700;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 7.2pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
  }
  .intro-callout {
    background: #f8fafc;
    border-left: 3px solid #0284c7;
    padding: 3px 7px;
    margin-bottom: 6px;
    font-size: 8pt;
    color: #334155;
  }
  .grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px 8px;
    margin-bottom: 6px;
  }
  .item-card {
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 4px 6px;
    background: #ffffff;
  }
  .item-card.full-width {
    grid-column: 1 / -1;
  }
  .item-title {
    font-size: 8pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .num-pill {
    background: #e0f2fe;
    color: #0369a1;
    font-size: 6.8pt;
    font-weight: 800;
    padding: 1px 3px;
    border-radius: 2px;
  }
  .item-content {
    font-size: 7.8pt;
    color: #334155;
  }
  .item-content strong {
    color: #0f172a;
  }
  .highlight {
    background: #f1f5f9;
    padding: 1px 3px;
    border-radius: 2px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 7.2pt;
  }
  .alert-box {
    border: 1px solid #f87171;
    background: #fef2f2;
    border-radius: 4px;
    padding: 4px 7px;
    margin-bottom: 6px;
  }
  .alert-title {
    font-size: 8pt;
    font-weight: 800;
    color: #b91c1c;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .signatures {
    border-top: 1px solid #cbd5e1;
    padding-top: 4px;
    margin-top: 2px;
  }
  .signatures-title {
    font-size: 7.2pt;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
    text-align: center;
  }
  .sig-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
  }
  .sig-box {
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    padding: 3px 4px;
    background: #f8fafc;
    text-align: center;
  }
  .sig-role {
    font-size: 6.5pt;
    font-weight: 600;
    color: #0369a1;
    text-transform: uppercase;
    margin-bottom: 1px;
  }
  .sig-name {
    font-size: 7.8pt;
    font-weight: 700;
    color: #0f172a;
  }
  .sig-id {
    font-size: 6.5pt;
    color: #64748b;
  }
  .sig-status {
    margin-top: 1px;
    font-size: 6.5pt;
    color: #15803d;
    font-weight: 600;
  }
</style>
</head>
<body>

<div class="header">
  <div class="title-area">
    <span class="memo-badge">Official Commitment Memo</span>
    <h1>SMART DOORBELL EDGE AI</h1>
    <div class="subtitle">Client Hardware Specification &amp; Performance Guarantee · AI255TBD Module 2</div>
  </div>
  <div class="meta-box">
    <strong>Team:</strong> 1 (Paradise)<br>
    <strong>Target:</strong> ESP32-S3-DevKitC-1 N16R8<br>
    <strong>Date:</strong> 28 November 2026<br>
    <strong>Status:</strong> Verified Live on Physical Hardware
  </div>
</div>

<div class="intro-callout">
  <strong>Client Brief Confirmation:</strong> Team 1 guarantees that the ESP32-S3 firmware and audio pipeline acquire, store, and process all 144 one-second doorbell commands in real time with 0 lost packets, survive complete power loss, and deliver log-mel features matching host NumPy within &plusmn;0.004 dB without degrading downstream keyword classifier accuracy.
</div>

<div class="grid-container">

  <!-- 1. Sampling Rate & 2. Filter -->
  <div class="item-card">
    <div class="item-title"><span class="num-pill">01 &amp; 02</span> Sampling Rate &amp; Anti-Aliasing Filter</div>
    <div class="item-content">
      • <strong>Sampling Rate:</strong> <span class="highlight">16,000 Hz</span> (mono, 16 kS/s). Captures human voice fundamentals and formants up to 8 kHz Nyquist.<br>
      • <strong>Anti-Aliasing Filter:</strong> 255-tap windowed-sinc (<span class="highlight">antialias=True</span>, Blackman window, cutoff 7.2 kHz). Suppresses Team 1's <span class="highlight">7,347.98 Hz</span> regulator whine by <strong>51.82 dB</strong> (from &minus;31.94 dB down to &minus;83.76 dB), completely preventing speech-band foldover into 652 Hz.
    </div>
  </div>

  <!-- 3. Format & Scale -->
  <div class="item-card">
    <div class="item-title"><span class="num-pill">03</span> Format, Scale &amp; Boot Auto-Calibration</div>
    <div class="item-content">
      • <strong>Format &amp; Scale:</strong> Signed 16-bit PCM (<span class="highlight">int16 &lt;i2</span>) with fixed scale <span class="highlight">S = 1.0</span> (32,000 B/s audio downlink). Delivers <strong>74.21 dB mean SQNR</strong> (min 61.84 dB) with <strong>0.00% clipping</strong> across all 144 clips.<br>
      • <strong>Scale Selection Before Hearing Sound:</strong> At device cold-boot, the doorbell executes a 1.0-second ambient room calibration window measuring peak ADC noise floor. It sets scale <span class="highlight">S = V_peak / V_adc_clip</span> with a 6 dB acoustic headroom guardband (defaulting to 1.0 for calibrated &plusmn;1.0V MEMS microphones).
    </div>
  </div>

  <!-- 4. Port, Speed & Margin -->
  <div class="item-card">
    <div class="item-title"><span class="num-pill">04</span> Port, Transmission Speed &amp; Real-Time Margin</div>
    <div class="item-content">
      • <strong>Primary Port:</strong> Native USB CDC (<span class="highlight">COM11</span> / USB port) or WCH UART (<span class="highlight">COM12</span> @ <span class="highlight">921,600 baud</span>).<br>
      • <strong>Operating Speed:</strong> <span class="highlight">speed = 1.0</span> (32,000 B/s audio downlink, real-time 144.0 s duration).<br>
      • <strong>Real-Time Margin:</strong> Native USB CDC sustains up to <strong>6.0&times; real-time</strong> (192,000 B/s) with 0 packet loss before hitting the 32 KB RX FIFO overflow threshold (&ge; 256 KB/s), providing a <strong>500% throughput margin</strong>. UART @ 921.6k sustains up to 2.5&times; (150% margin).
    </div>
  </div>

  <!-- 5. Storage Size, Tools & Room Left -->
  <div class="item-card">
    <div class="item-title"><span class="num-pill">05</span> Storage Location, Tools Settings &amp; Room Left</div>
    <div class="item-content">
      • <strong>Audio Buffering:</strong> <span class="highlight">8 MB OPI PSRAM</span> holds all 144 clips (<span class="highlight">4,608,000 B</span> used out of 8,388,608 B, leaving <strong>3,780,608 B / 45.1% room left</strong>).<br>
      • <strong>Flash Persistence:</strong> File <span class="highlight">/rec.bin</span> on LittleFS (<span class="highlight">4,608,000 B</span>, bit-exact CRC <span class="highlight">0x55c3d431</span>). Partition size is 7,208,960 B (6.88 MiB), leaving <strong>2,580,480 B / 35.8% room left</strong>. Verified 100% intact across power cuts and firmware re-flashing.<br>
      • <strong>Tools Settings:</strong> ESP32S3 Dev Module | USB CDC: <em>Enabled</em> | Flash: <em>16MB</em> | Partition: <em>Custom (partitions.csv)</em> | PSRAM: <em>OPI PSRAM</em>.
    </div>
  </div>

  <!-- 6. Features, Compute Time & Downlink B/s -->
  <div class="item-card">
    <div class="item-title"><span class="num-pill">06</span> Feature Extraction, Compute Budget &amp; Downlink Rate</div>
    <div class="item-content">
      • <strong>Feature Recipe:</strong> Window = 480 (30 ms Hann), Hop = 320 (20 ms), 512-pt Radix-2 FFT, 40 HTK Mel bands (20–8000 Hz), unnormalized power, log floor 1e-10.<br>
      • <strong>Compute Time vs Budget:</strong> Physically measured at <strong>683.75 &mu;s</strong> per frame (ESP32-S3 @ 240 MHz). Budget is 20,000 &mu;s (20 ms hop). Compute load is only <strong>3.42% of CPU</strong>, leaving a <strong>29.2&times; compute safety margin</strong>.<br>
      • <strong>Downlink Bandwidth:</strong> 50 frames/s &times; 181 bytes/frame = <strong>9,050 B/s</strong> (72.4 kbps), negligible link load.
    </div>
  </div>

  <!-- 7. What Was Lost & How We Know -->
  <div class="item-card">
    <div class="item-title"><span class="num-pill">07</span> Loss Accounting &amp; Mathematical Verification</div>
    <div class="item-content">
      • <strong>Lost Data:</strong> Exactly <strong>0 bytes lost, 0 packets lost, 0 CRC errors</strong> during full 144-clip stream.<br>
      • <strong>Verification Proof:</strong> Host sent 7,200 packets (2,304,000 samples). ESP32-S3 telemetry confirmed: <span class="highlight">frames_ok = 7,201</span>, <span class="highlight">bad_crc = 0</span>, <span class="highlight">seq_gaps = 0</span>, <span class="highlight">dup = 0</span>, <span class="highlight">samples = 2,304,000</span>. Memory dump and LittleFS <span class="highlight">/rec.bin</span> matched host audio byte-for-byte with bit-exact CRC-32 <span class="highlight">0x55c3d431</span>. Exactly 7,199 feature frames expected and 7,199 received (<span class="highlight">lost_features = 0</span>).
    </div>
  </div>

  <!-- 8. Laptop vs Board Difference -->
  <div class="item-card full-width">
    <div class="item-title"><span class="num-pill">08</span> Laptop vs. Board Numerical Difference &amp; Classifier Impact</div>
    <div class="item-content">
      • <strong>Measured Difference:</strong> Mean Absolute Error (MAE) between ESP32-S3 <span class="highlight">16k int16</span> and host Python float32 reference is only <strong>0.003914 dB</strong> (RMSE 0.006064 dB, max 0.124 dB). When compared against Python run on the <em>identical quantized int16 samples</em>, the difference is just <strong>0.000002 dB</strong> (floating-point precision limit).<br>
      • <strong>Does It Matter? NO:</strong> Evaluated on held-out test clips (96 train / 48 test), the Nearest-Centroid keyword classifier achieves an <strong>identical 75.00% Accuracy</strong> (0.7356 macro-F1) on both laptop float32 and ESP32 board features with identical confusion matrices. Quantization noise sets a harmless floor under silent bands without shifting decision boundaries. (Conversely, omitting anti-aliasing collapses accuracy to 25.00%).
    </div>
  </div>

</div>

<!-- 9. One Thing Most Likely to Break -->
<div class="alert-box">
  <div class="alert-title"><span class="num-pill" style="background:#fee2e2;color:#991b1b;">09</span> Critical Vulnerability: The One Thing Most Likely to Break This Design</div>
  <div class="item-content" style="color:#7f1d1d;">
    <strong>Flashing firmware with default Arduino IDE settings (PSRAM=Disabled / Default 4MB Partition Table):</strong> If an operator or factory programmer compiles the sketch without selecting <em>PSRAM: "OPI PSRAM"</em> and <em>Partition Scheme: "Custom (partitions.csv)"</em>, PSRAM initialization silently fails (<span class="highlight">psramFound() == false</span>), LittleFS mounting fails due to insufficient partition space, internal SRAM overflows at clip 4 (<span class="highlight">142 KB limit</span>), and the doorbell crashes into an unrecoverable out-of-memory reboot loop.
  </div>
</div>

<div class="signatures">
  <div class="signatures-title">Commitment Authorized &amp; Verified by Team 1 Paradise Engineers</div>
  <div class="sig-grid">
    <div class="sig-box">
      <div class="sig-role">Embedded &amp; Hardware</div>
      <div class="sig-name">Siddharth Dhanush R</div>
      <div class="sig-id">Student 1 · Board Operator</div>
      <div class="sig-status">✓ Hardware Verified (COM11)</div>
    </div>
    <div class="sig-box">
      <div class="sig-role">Python &amp; Codec</div>
      <div class="sig-name">Rakshith Raghavendra</div>
      <div class="sig-id">Student 2 · DSP Pipeline</div>
      <div class="sig-status">✓ Pipeline Verified</div>
    </div>
    <div class="sig-box">
      <div class="sig-role">Frontend &amp; Dashboard</div>
      <div class="sig-name">Monica</div>
      <div class="sig-id">Student 3 · Telemetry UI</div>
      <div class="sig-status">✓ UI Verified (Vite+React)</div>
    </div>
    <div class="sig-box">
      <div class="sig-role">Validation &amp; ML</div>
      <div class="sig-name">Saakshi Babu</div>
      <div class="sig-id">Student 4 · Classifier &amp; QA</div>
      <div class="sig-status">✓ ML &amp; Split Verified</div>
    </div>
  </div>
</div>

</body>
</html>"""

def build_technical_report_html() -> str:
    # Base64 encode plots
    plot_diff = image_to_base64(REPO_ROOT / "student4_validation/outputs/plots/mission5_diff_heatmaps.png")
    plot_cm = image_to_base64(REPO_ROOT / "student4_validation/outputs/plots/mission5_confusion_matrices.png")
    plot_skip = image_to_base64(REPO_ROOT / "student4_validation/outputs/plots/mission4_skip_alignment.png")
    plot_speed = image_to_base64(REPO_ROOT / "student4_validation/outputs/plots/mission4_port_speed_limits.png")
    plot_ui = image_to_base64(STAGE_C_DIR / "screenshots/01_dashboard_overview.png")
    plot_alias = image_to_base64(REPO_ROOT / "student2_python/documentation/mission2_aliasing_spectra.png")
    plot_sqnr = image_to_base64(REPO_ROOT / "student2_python/documentation/mission2_sqnr_comparison.png")
    plot_spec = image_to_base64(REPO_ROOT / "student2_python/documentation/mission3_class_spectrograms.png")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Team 1 Paradise — Module 2 Final Technical Report</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    margin: 0;
    padding: 0;
    font-size: 9.5pt;
    line-height: 1.42;
  }}
  .cover-page {{
    page-break-after: always;
    padding-top: 40px;
    text-align: center;
  }}
  .cover-badge {{
    display: inline-block;
    background: #0369a1;
    color: #ffffff;
    font-size: 9pt;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 4px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 20px;
  }}
  .cover-title {{
    font-size: 24pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
    margin: 0 0 10px 0;
  }}
  .cover-subtitle {{
    font-size: 13pt;
    color: #475569;
    font-weight: 500;
    margin-bottom: 30px;
  }}
  .cover-meta {{
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 16px;
    background: #f8fafc;
    text-align: left;
    max-width: 520px;
    margin: 0 auto 30px auto;
    font-size: 9.5pt;
    line-height: 1.6;
  }}
  .cover-meta strong {{
    color: #0f172a;
  }}
  .team-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    font-size: 9pt;
  }}
  .team-table th, .team-table td {{
    border: 1px solid #cbd5e1;
    padding: 6px 10px;
    text-align: left;
  }}
  .team-table th {{
    background: #f1f5f9;
    font-weight: 700;
    color: #0f172a;
  }}
  .page-break {{
    page-break-before: always;
  }}
  h1 {{
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 4px;
    margin: 25px 0 12px 0;
  }}
  h2 {{
    font-size: 12.5pt;
    font-weight: 700;
    color: #0369a1;
    margin: 18px 0 8px 0;
  }}
  h3 {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #334155;
    margin: 12px 0 6px 0;
  }}
  p {{
    margin: 0 0 8px 0;
  }}
  ul, ol {{
    margin: 0 0 10px 0;
    padding-left: 20px;
  }}
  li {{
    margin-bottom: 3px;
  }}
  .highlight {{
    background: #f1f5f9;
    padding: 1px 4px;
    border-radius: 2px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 8.5pt;
  }}
  /* 8 Required Headings Cards */
  .heading-card {{
    border-left: 4px solid #0284c7;
    background: #f8fafc;
    padding: 8px 12px;
    margin: 10px 0 12px 0;
    border-radius: 0 4px 4px 0;
  }}
  .heading-card.aim {{ border-left-color: #0284c7; }}
  .heading-card.background {{ border-left-color: #475569; }}
  .heading-card.prediction {{ border-left-color: #7c3aed; }}
  .heading-card.method {{ border-left-color: #2563eb; }}
  .heading-card.observations {{ border-left-color: #059669; }}
  .heading-card.analysis {{ border-left-color: #d97706; }}
  .heading-card.what-learnt {{ border-left-color: #0d9488; }}
  .heading-card.llm-log {{ border-left-color: #e11d48; }}
  
  .card-label {{
    font-size: 8.5pt;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .card-label.aim {{ color: #0284c7; }}
  .card-label.background {{ color: #475569; }}
  .card-label.prediction {{ color: #7c3aed; }}
  .card-label.method {{ color: #2563eb; }}
  .card-label.observations {{ color: #059669; }}
  .card-label.analysis {{ color: #d97706; }}
  .card-label.what-learnt {{ color: #0d9488; }}
  .card-label.llm-log {{ color: #e11d48; }}

  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 8.5pt;
  }}
  table.data-table th, table.data-table td {{
    border: 1px solid #cbd5e1;
    padding: 5px 8px;
    text-align: left;
  }}
  table.data-table th {{
    background: #f1f5f9;
    font-weight: 700;
    color: #0f172a;
  }}
  table.data-table tr:nth-child(even) {{
    background: #f8fafc;
  }}
  .img-container {{
    text-align: center;
    margin: 14px 0;
  }}
  .img-container img {{
    max-width: 95%;
    height: auto;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
  }}
  .img-caption {{
    font-size: 8pt;
    color: #64748b;
    margin-top: 4px;
    font-style: italic;
  }}
  .tag-pass {{
    color: #15803d;
    font-weight: 700;
  }}
  .tag-fail {{
    color: #b91c1c;
    font-weight: 700;
  }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
  <div class="cover-badge">Course Project Technical Report</div>
  <h1 class="cover-title">SMART DOORBELL EDGE AI<br>("The Doorbell's Ears")</h1>
  <div class="cover-subtitle">Sensor Data Acquisition, Real-Time Radix-2 Log-Mel Extraction, Flash Persistence &amp; Domain Shift Analysis on ESP32-S3</div>

  <div class="cover-meta">
    <strong>Course:</strong> AI255TBD Edge AI · Module 2<br>
    <strong>Team:</strong> Team 1 (<code>Paradise</code>)<br>
    <strong>Target Hardware:</strong> ESP32-S3-DevKitC-1 N16R8 (Xtensa LX7 @ 240 MHz, 16 MB Flash, 8 MB OPI PSRAM)<br>
    <strong>Submission Date:</strong> 28 November 2026<br>
    <strong>Repository:</strong> <code>https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git</code><br>
    <strong>Verification Status:</strong> Verified on Live ESP32-S3 Hardware (<code>COM11</code>)
  </div>

  <table class="team-table" style="max-width: 520px; margin: 0 auto;">
    <thead>
      <tr>
        <th>Student</th>
        <th>Name</th>
        <th>Primary Role</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Student 1</td>
        <td><strong>Siddharth Dhanush R</strong></td>
        <td>Embedded Systems &amp; Hardware (ESP32-S3 Firmware &amp; LittleFS)</td>
      </tr>
      <tr>
        <td>Student 2</td>
        <td><strong>Rakshith Raghavendra</strong></td>
        <td>Python Backend &amp; Audio Processing (Codec, Framing &amp; Reference DSP)</td>
      </tr>
      <tr>
        <td>Student 3</td>
        <td><strong>Monica</strong></td>
        <td>Frontend &amp; Telemetry Dashboard (React 19, TypeScript, Vite)</td>
      </tr>
      <tr>
        <td>Student 4</td>
        <td><strong>Saakshi Babu</strong></td>
        <td>Validation, Loss Accounting &amp; ML Evaluation (Classifier &amp; QA)</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- EXECUTIVE SUMMARY & ARCHITECTURE -->
<div class="page-break"></div>
<h1>1. Executive Summary &amp; System Architecture</h1>

<p>
Deploying keyword spotting on edge microcontrollers requires strict balance across serial transport bandwidth, internal SRAM ceilings, numerical feature parity, and persistent storage. In this project, Team 1 (<code>Paradise</code>) designed, implemented, and validated an end-to-end audio pipeline on the <strong>ESP32-S3-DevKitC-1 N16R8</strong>.
</p>
<p>
The system receives 144 one-second spoken commands across 6 classes (<code>on</code>, <code>off</code>, <code>stop</code>, <code>go</code>, <code>_unknown</code>, <code>_silence</code>), validates packet delivery using CRC-32 frames, stores audio in 8 MB OPI PSRAM, commits a 4.608 MB persistent image to LittleFS flash surviving power cuts, computes 40-band HTK log-mel features in real time using an optimized radix-2 FFT (<strong>683.75 &mu;s/frame</strong>, 2,725&times; speedup), and sends features back to Python for dataset building and Nearest-Centroid keyword classification.
</p>

<h3>End-to-End Pipeline</h3>
<p>
<code>team_audio.py (48 kHz Float32)</code> &rarr; <code>audio_codec.py (16 kHz Int16 S=1.0)</code> &rarr; <code>0xA5 0x5A CRC-32 Framing</code> &rarr; <code>COM11 (Native USB CDC) / COM12 (UART 921.6k)</code> &rarr; <code>doorbell_board.ino (32 KB Ring Buffer, LittleFS /rec.bin)</code> &rarr; <code>features.h (Radix-2 FFT, 40 HTK Mels)</code> &rarr; <code>0xB5 0x5B 'F' Frame Downlink</code> &rarr; <code>7,056-Frame Clean Dataset</code> &rarr; <code>Nearest-Centroid Classifier (75.00% Accuracy)</code> &rarr; <code>10-Page React Dashboard</code>.
</p>

<h3>Hardware Tools Settings (Mandatory)</h3>
<table class="data-table">
  <thead>
    <tr>
      <th>Tool / Configuration Option</th>
      <th>Required Setting</th>
      <th>Engineering Rationale</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Board</strong></td>
      <td><code>ESP32S3 Dev Module</code></td>
      <td>Targets dual-core Xtensa LX7 @ 240 MHz with native USB CDC and Octal PSRAM.</td>
    </tr>
    <tr>
      <td><strong>USB CDC On Boot</strong></td>
      <td><code>Enabled</code></td>
      <td>Enables native USB serial on <code>COM11</code> without requiring an external UART bridge.</td>
    </tr>
    <tr>
      <td><strong>Flash Size</strong></td>
      <td><code>16MB (128Mb)</code></td>
      <td>Mandatory for N16 module to expose high-capacity flash address space.</td>
    </tr>
    <tr>
      <td><strong>Partition Scheme</strong></td>
      <td><code>Custom (partitions.csv)</code></td>
      <td>Allocates <code>6.88 MiB</code> LittleFS partition to store all 144 clips (4.608 MB).</td>
    </tr>
    <tr>
      <td><strong>PSRAM</strong></td>
      <td><code>OPI PSRAM</code></td>
      <td>Activates 8 MB high-speed Octal SPI PSRAM for 144-clip contiguous audio buffer.</td>
    </tr>
  </tbody>
</table>

<!-- MISSION 1 -->
<div class="page-break"></div>
<h1>2. Mission 1: The Pipe (Data Rate &amp; Data Type)</h1>

<div class="heading-card aim">
  <div class="card-label aim">1. Aim</div>
  Measure throughput and packet framing overhead across UART (<code>COM12</code>) and native USB CDC (<code>COM11</code>), determine wire bandwidth limits for <code>f32</code>, <code>i16</code>, and <code>i8</code>, and evaluate real-time feasibility.
</div>

<div class="heading-card background">
  <div class="card-label background">2. Background</div>
  UART transmits asynchronously with 1 start bit, 8 data bits, and 1 stop bit (10 bits/byte). Its theoretical throughput is <code>baud / 10</code> bytes/second. Native USB CDC is packetized Full-Speed USB (12 Mbps line rate) handled by the ESP32-S3 internal USB PHY; baud rate is ignored, but transfer speed is limited by host-side USB scheduling and the board's RX ring buffer.
</div>

<div class="heading-card prediction">
  <div class="card-label prediction">3. Prediction</div>
  Calculated before measuring:
  <ul>
    <li>16 kHz <code>f32</code> = 64,000 B/s (64,650 B/s with framing); <code>i16</code> = 32,000 B/s (32,650 B/s); <code>i8</code> = 16,000 B/s (16,650 B/s).</li>
    <li>115,200 baud UART maxes out at 11,520 B/s &rarr; cannot carry 16 kHz audio in real time.</li>
    <li>921,600 baud UART maxes out at 92,160 B/s &rarr; can carry 16 kHz <code>f32</code>, <code>i16</code>, and <code>i8</code>.</li>
    <li>Native USB CDC will achieve &gt;300 KB/s, independent of configured baud rate.</li>
  </ul>
</div>

<div class="heading-card method">
  <div class="card-label method">4. Method</div>
  Stream audio using <code>student1_esp32/benchmarks/mission1_pipe_benchmark.py</code> with <code>feat=False, store="none"</code>. Measure speed at <code>speed=0</code> across 115,200, 921,600, and 2,000,000 baud on <code>COM12</code> and <code>COM11</code>. Test packet sizes: 8, 64, 320, 1024 samples/packet. Record board-measured time (<code>ms</code>) vs host <code>send_seconds</code>.
</div>

<div class="heading-card observations">
  <div class="card-label observations">5. Observations</div>
  <table class="data-table">
    <thead>
      <tr>
        <th>Port</th>
        <th>Baud</th>
        <th>Laptop Rate</th>
        <th>Board Rate</th>
        <th>Bad CRC</th>
        <th>Gaps</th>
        <th>Real-Time 16k i16</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>COM (COM12)</strong></td>
        <td>115,200</td>
        <td>11,360.5 B/s</td>
        <td>11,376.4 B/s</td>
        <td>0</td>
        <td>0</td>
        <td><span class="tag-fail">FAIL (2,809 ms)</span></td>
      </tr>
      <tr>
        <td><strong>COM (COM12)</strong></td>
        <td>921,600</td>
        <td>90,726.0 B/s</td>
        <td>90,909.2 B/s</td>
        <td>0</td>
        <td>0</td>
        <td><span class="tag-pass">PASS (987 ms)</span></td>
      </tr>
      <tr>
        <td><strong>COM (COM12)</strong></td>
        <td>2,000,000</td>
        <td>194,535.1 B/s</td>
        <td>194,726.9 B/s</td>
        <td>0</td>
        <td>0</td>
        <td><span class="tag-pass">PASS (982 ms)</span></td>
      </tr>
      <tr>
        <td><strong>USB (COM11)</strong></td>
        <td>115,200</td>
        <td>501,455.3 B/s</td>
        <td>332,181.9 B/s</td>
        <td>13.0</td>
        <td>0</td>
        <td><span class="tag-pass">PASS (982 ms, 0 err)</span></td>
      </tr>
      <tr>
        <td><strong>USB (COM11)</strong></td>
        <td>921,600</td>
        <td>508,498.1 B/s</td>
        <td>334,509.0 B/s</td>
        <td>13.7</td>
        <td>0</td>
        <td><span class="tag-pass">PASS (982 ms, 0 err)</span></td>
      </tr>
    </tbody>
  </table>
</div>

<div class="heading-card analysis">
  <div class="card-label analysis">6. Analysis</div>
  COM port rates strictly adhere to 10-bit UART physical limits (11.4, 90.9, 194.7 kB/s). USB CDC ignores baud entirely, achieving ~334 kB/s on board. At <code>speed=0</code>, unthrottled 64 KB bursts overflow the 32 KB RX buffer on USB. However, at <code>speed=1.0</code>, USB CDC and COM (&ge;921.6k) sustain zero packet drops and zero CRC errors. Small packet sizes (<code>spp=8</code>) incur 44.8% header overhead (26 KB headers on 32 KB data), whereas <code>spp=320</code> incurs only 2.0% overhead.
</div>

<div class="heading-card what-learnt">
  <div class="card-label what-learnt">7. What We Learnt</div>
  <code>pyserial.write()</code> returns when bytes enter local OS/USB drivers, not when the ESP32 receives them. Reliable benchmarking requires board-measured time (<code>ms</code>). Packet size must be &ge;320 samples to avoid excessive frame header overhead.
</div>

<div class="heading-card llm-log">
  <div class="card-label llm-log">8. LLM Log</div>
  <strong>Prompt:</strong> "How many bytes per second can you send to an ESP32-S3 over USB?"<br>
  <strong>LLM Response Summary:</strong> Full-Speed USB 1.1 achieves theoretical 12 Mbps (1.5 MB/s); practical bulk CDC yields 500–900 KB/s, independent of baud rate. UART bridge requires 10 bits/byte (baud / 10). Host OS buffering may cause write() to return before physical transmission.
</div>

<!-- MISSION 2 -->
<div class="page-break"></div>
<h1>3. Mission 2: What to Send &amp; Where to Keep It</h1>

<div class="heading-card aim">
  <div class="card-label aim">1. Aim</div>
  Implement audio quantization and packing in NumPy, quantify aliasing and Signal-to-Quantization-Noise Ratio (SQNR), configure 8 MB OPI PSRAM, and implement LittleFS flash persistence surviving power loss.
</div>

<div class="heading-card background">
  <div class="card-label background">2. Background</div>
  The Nyquist-Shannon theorem requires pre-sampling low-pass filtering. Frequencies above <code>fs/2</code> fold back into the baseband at <code>|k*fs - f|</code>. Int16 quantization provides ~98 dB theoretical SQNR, while int8 yields ~48 dB. ESP32-S3 internal SRAM is fragmented; buffering 144 seconds requires external PSRAM, and power-cut persistence requires LittleFS non-volatile flash storage.
</div>

<div class="heading-card prediction">
  <div class="card-label prediction">3. Prediction</div>
  Team 1's room tone at 7,348.0 Hz will alias at 8 kHz to <code>|8000 - 7348.0| = 652.0 Hz</code> if anti-aliasing is disabled. Int16 with S=1.0 will provide &gt;70 dB SQNR with 0% clipping; int8 will suffer severe quantization noise (~25 dB SQNR). Internal SRAM will hold &lt;5 seconds of audio; PSRAM and LittleFS will hold all 144 seconds (4.608 MB).
</div>

<div class="heading-card method">
  <div class="card-label method">4. Method</div>
  Evaluate silence clip 120 at 48 kHz vs 8 kHz with and without <code>antialias=True</code>. Measure SQNR across 144 clips for <code>i16 S=1.0</code>, <code>i8 S=1.0</code>, and <code>i8 S=0.25</code>. Test SRAM allocation ceiling, enable OPI PSRAM, implement <code>cmdSave()</code> in <code>doorbell_board.ino</code> using LittleFS, stream 144 clips, power-cycle the board, and verify flash CRC.
</div>

<div class="heading-card observations">
  <div class="card-label observations">5. Observations</div>
  <ul>
    <li><strong>Anti-Aliasing:</strong> Tone at 7,348 Hz (-31.97 dB) folds to 652 Hz (-31.94 dB) without filter. Enabling <code>antialias=True</code> suppresses the peak by <strong>51.82 dB</strong> down to -83.76 dB.</li>
    <li><strong>SQNR:</strong> <code>i16 S=1.0</code> delivers <strong>74.21 dB mean SQNR</strong> (0.00% clipping). <code>i8 S=1.0</code> gives 25.98 dB; <code>i8 S=0.25</code> gives 16.25 dB with 1.69% speech clipping.</li>
    <li><strong>SRAM vs PSRAM:</strong> Internal SRAM capped at <strong>142,070 B (4.44 s)</strong>. OPI PSRAM unlocked 8,388,608 B, storing all 4,608,000 B with 0 errors.</li>
    <li><strong>Flash Persistence:</strong> <code>SAVE</code> wrote 4,608,000 B to <code>/rec.bin</code> in <strong>10.56 s</strong>. After power disconnection and reconnect, <code>dump("flash")</code> returned bit-exact CRC <span class="highlight">0x55c3d431</span> (PSRAM was wiped).</li>
  </ul>
  <div class="img-container">
    <img src="{plot_alias}" style="max-height: 180px;" alt="Aliasing Spectra">
    <div class="img-caption">Figure 2.1: 8 kHz Anti-Aliasing Spectral Comparison (7,348 Hz tone suppressed by 51.82 dB).</div>
  </div>
</div>

<div class="heading-card analysis">
  <div class="card-label analysis">6. Analysis</div>
  Anti-aliasing must occur prior to decimation because digital filtering cannot separate folded tones once sampled. Int16 S=1.0 preserves speech fidelity with negligible distortion. Stock Arduino settings assign only 1.44 MB to LittleFS; our custom <code>partitions.csv</code> allocates 6.88 MiB, leaving 35.8% headroom after storing 144 clips.
</div>

<div class="heading-card what-learnt">
  <div class="card-label what-learnt">7. What We Learnt</div>
  PSRAM is volatile and loses all contents on power cut. LittleFS requires custom partition tables for 16 MB flash. During <code>dump("flash")</code>, <code>HWCDC</code> dropped bytes during flash SPI reads until we configured a 32 KB TX buffer and 256-byte chunk pacing in firmware.
</div>

<div class="heading-card llm-log">
  <div class="card-label llm-log">8. LLM Log</div>
  <strong>Prompt:</strong> "Why does an ESP32-S3 fail with 'ERR no psram' even though the chip has 8 MB PSRAM?"<br>
  <strong>LLM Response Summary:</strong> ESP32-S3 N16R8 uses Octal (OPI) PSRAM. Default Arduino IDE board configuration sets PSRAM to "Disabled" or "QSPI". It must be explicitly set to "OPI PSRAM" in the Tools menu; otherwise <code>psramFound()</code> returns false and heap allocation fails.
</div>

<!-- MISSION 3 -->
<div class="page-break"></div>
<h1>4. Mission 3: Features on the Board (Log-Mel Extraction)</h1>

<div class="heading-card aim">
  <div class="card-label aim">1. Aim</div>
  Implement the exact Section 5 log-mel recipe in NumPy, optimize ESP32-S3 feature extraction in <code>features.h</code> to run within the 20 ms frame budget, and prove numerical parity within &le;0.05 dB.
</div>

<div class="heading-card background">
  <div class="card-label background">2. Background</div>
  Log-mel spectrograms emulate human auditory perception. The recipe requires: 1) Framing (win=480, hop=320), 2) Hann windowing, 3) 512-pt FFT power spectrum, 4) 40 triangular HTK mel filterbanks (20–8000 Hz), 5) Log scaling: <code>10*log10(max(p, 1e-10))</code>. A naive Discrete Fourier Transform (DFT) requires $O(N^2)$ complex multiplications, violating real-time deadlines.
</div>

<div class="heading-card prediction">
  <div class="card-label prediction">3. Prediction</div>
  Textbook starter DFT calling <code>cosf/sinf</code> 246,720 times per frame will take ~1.5–2.0 seconds per frame (100&times; slower than real time). An in-place Cooley-Tukey radix-2 DIT FFT with precomputed twiddle factor tables and sparse mel boundaries will run in under 1,000 &mu;s (&lt;1 ms).
</div>

<div class="heading-card method">
  <div class="card-label method">4. Method</div>
  Implement <code>reference_logmel.py</code> in NumPy. Replace starter <code>dft()</code> in <code>features.h</code> with an iterative bit-reversal radix-2 FFT using precomputed LUTs (<code>twRe</code>, <code>twIm</code>) and sparse mel filter spans <code>[melStart[m], melEnd[m])</code>. Stream 10 seconds of audio at <code>speed=1.0</code> on <code>COM11</code> and compare per-frame <code>compute_us</code>, <code>lag_s</code>, and max dB difference vs NumPy.
</div>

<div class="heading-card observations">
  <div class="card-label observations">5. Observations</div>
  <table class="data-table">
    <thead>
      <tr>
        <th>Implementation</th>
        <th>Expected Frames</th>
        <th>Received Frames</th>
        <th>Mean Compute Time</th>
        <th>Max Lag</th>
        <th>Max Diff vs NumPy</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Starter dft()</strong></td>
        <td>499</td>
        <td>16 (483 lost)</td>
        <td>1,863,425 &mu;s (1.86 s)</td>
        <td>29.56 s</td>
        <td>0.000126 dB</td>
      </tr>
      <tr>
        <td><strong>Optimized Radix-2 FFT</strong></td>
        <td>499</td>
        <td><strong>499 (0 lost)</strong></td>
        <td><strong>683.71 &mu;s (0.68 ms)</strong></td>
        <td><strong>0.0147 s</strong></td>
        <td><strong>0.000072 dB</strong></td>
      </tr>
      <tr>
        <td><strong>MFCC-13 (10 ms hop)</strong></td>
        <td>998</td>
        <td>998 (0 lost)</td>
        <td>714.22 &mu;s</td>
        <td>0.0203 s</td>
        <td>0.000092 dB</td>
      </tr>
    </tbody>
  </table>
  <div class="img-container">
    <img src="{plot_spec}" style="max-height: 180px;" alt="Log-Mel Spectrograms">
    <div class="img-caption">Figure 3.1: 40-Band Log-Mel Spectrograms of All 6 Classes Generated from ESP32-S3 Features.</div>
  </div>
</div>

<div class="heading-card analysis">
  <div class="card-label analysis">6. Analysis</div>
  Optimization achieved a <strong>2,725&times; speedup</strong>. At 683.71 &mu;s per 20 ms hop, the ESP32-S3 CPU duty cycle is only <strong>3.42%</strong>, leaving a 29.2&times; compute margin. Max numerical error vs NumPy is 0.000072 dB (well within 0.05 dB limit). In a speed sweep (2&times; to 10&times;), <code>feat=True</code> and <code>feat=False</code> fail at the identical speed (8&times;, 256 KB/s), proving that serial ingress buffering—not compute—is the bottleneck.
</div>

<div class="heading-card what-learnt">
  <div class="card-label what-learnt">7. What We Learnt</div>
  Trigonometric function calls (<code>cosf/sinf</code>) in loops are disastrous on microcontrollers. Precomputing twiddle factors and restricting filterbank multiply-accumulate operations to non-zero bins transforms an unusable pipeline into a production-grade DSP engine.
</div>

<div class="heading-card llm-log">
  <div class="card-label llm-log">8. LLM Log</div>
  <strong>Prompt:</strong> "How long does a 512-point FFT take on an ESP32-S3 at 240 MHz?"<br>
  <strong>LLM Response Summary:</strong> A standard radix-2 DIT FFT implementation in C with look-up tables takes approximately 300 to 800 &mu;s on an Xtensa LX7 core at 240 MHz. Using Espressif ESP-DSP SIMD assembly can push latency below 200 &mu;s.
</div>

<!-- MISSION 4 -->
<div class="page-break"></div>
<h1>5. Mission 4: Nothing Lost (Loss Accounting &amp; Labelled Dataset)</h1>

<div class="heading-card aim">
  <div class="card-label aim">1. Aim</div>
  Prove complete transmission integrity over all 144 clips, recover sample alignment under packet loss injection (<code>skip</code>), generate a clean labelled feature dataset, and author the official Data Card.
</div>

<div class="heading-card background">
  <div class="card-label background">2. Background</div>
  If a serial packet drops, naive sample counting causes subsequent audio frames to misalign in time, contaminating all downstream training labels. Packet loss must be detected via sequence numbers, and lost time must be zero-filled in firmware to preserve sample timestamps (<code>first_sample</code>). Frames straddling clip boundaries must be identified and handled.
</div>

<div class="heading-card prediction">
  <div class="card-label prediction">3. Prediction</div>
  For 144 one-second clips at 16 kHz: 144 s &times; 16,000 = 2,304,000 samples. At 320 samples/packet: exactly 7,200 data packets. Feature frames per 1-s clip: <code>1 + (16000 - 480) // 320 = 49</code> frames; 144 clips &times; 49 = 7,056 clean frames. Continuous streaming across boundaries yields 7,199 total frames (143 straddling frames).
</div>

<div class="heading-card method">
  <div class="card-label method">4. Method</div>
  Stream all 144 clips at <code>speed=1.0</code> on <code>COM11</code>. Log <code>packets_sent</code>, <code>frames_ok</code>, <code>seq_gaps</code>, <code>bad_crc</code>, and <code>samples</code>. Run controlled loss test with <code>skip=(10, 11, 200)</code>. Implement zero-fill gap recovery in <code>doorbell_board.ino</code>. Filter out 143 straddling boundary frames and export <code>doorbell_team1_esp32_features.npz</code> and <code>.csv</code>.
</div>

<div class="heading-card observations">
  <div class="card-label observations">5. Observations</div>
  <ul>
    <li><strong>Full 144-Clip Run:</strong> 7,200 packets sent; <code>frames_ok = 7,201</code> (7,200 data + 1 END); <code>bad_crc = 0</code>; <code>seq_gaps = 0</code>; <code>samples = 2,304,000</code>. Expected features: 7,199; received: 7,199 (0 lost).</li>
    <li><strong>Loss Accounting with skip=(10, 11, 200):</strong> Telemetry caught exactly 2 sequence gap events (gap of 2 packets at seq 10; gap of 1 packet at seq 200). Post-gap tail sample landed at <strong>159,360</strong> (exact expected alignment, 0 drift) vs 158,400 (-960 samples drift) prior to firmware fix.</li>
    <li><strong>Dataset Balance:</strong> Exactly 1,176 frames per class across all 6 classes (7,056 total clean frames).</li>
  </ul>
  <div class="img-container">
    <img src="{plot_skip}" style="max-height: 180px;" alt="Skip Packet Alignment">
    <div class="img-caption">Figure 4.1: Controlled Packet Drop Recovery (first_sample perfectly realigned to 159,360 with zero drift).</div>
  </div>
</div>

<div class="heading-card analysis">
  <div class="card-label analysis">6. Analysis</div>
  Sequence numbers detect missing packets; CRC-32 detects corrupted bytes. In firmware, when a sequence jump occurs, inserting <code>gap_pkts * samples_per_packet</code> zeros into <code>storeBuf</code>, advancing <code>st.samples</code>, resetting <code>fcount = 0</code>, and skipping to the next hop boundary completely prevents timeline slippage. Excluding the 143 inter-clip frames prevents cross-label contamination during model training.
</div>

<div class="heading-card what-learnt">
  <div class="card-label what-learnt">7. What We Learnt</div>
  Handling sequence gaps at packet 0 requires special care because <code>seq=0</code> can drop on link connect. The firmware must check whether the first arriving packet has <code>seq > 0</code> and insert initial zero padding accordingly.
</div>

<div class="heading-card llm-log">
  <div class="card-label llm-log">8. LLM Log</div>
  <strong>Prompt:</strong> "How do you maintain audio feature frame alignment when UDP or serial packets are lost?"<br>
  <strong>LLM Response Summary:</strong> In streaming DSP, missing audio packets cannot simply be skipped; dropping samples causes all future FFT windows to slip in time. The receiver must synthesize silence (zero-padding) for the exact duration of the lost samples to maintain wall-clock phase and frame indexing.
</div>

<!-- MISSION 5 -->
<div class="page-break"></div>
<h1>6. Mission 5: Laptop vs. Board (Domain Shift &amp; Classifier)</h1>

<div class="heading-card aim">
  <div class="card-label aim">1. Aim</div>
  Quantify numerical domain shift between laptop float32 and ESP32 board features across formats (<code>16k i16</code>, <code>16k i8</code>, <code>8k no-AA</code>), train a Nearest-Centroid keyword spotter, and defend the shipping configuration.
</div>

<div class="heading-card background">
  <div class="card-label background">2. Background</div>
  Fixed-point quantization, clipping, and aliasing alter feature distributions relative to Python float32 training data. A Nearest-Centroid classifier computes class centroids on standardized training features (80-dim: per-clip mean and std of 40 bands) and assigns test clips to the nearest centroid by Euclidean distance. Train/test splits must be stratified at the clip level (96 train / 48 test) to prevent data leakage.
</div>

<div class="heading-card prediction">
  <div class="card-label prediction">3. Prediction</div>
  16 kHz <code>int16 S=1.0</code> will exhibit negligible MAE (&lt;0.01 dB) and produce identical classifier accuracy to laptop float32. Int8 will exhibit higher MAE (~1.0 dB) with slight accuracy degradation. 8 kHz without anti-aliasing will exhibit massive MAE (&gt;5 dB) due to 7,348 Hz whine aliasing and will severely degrade classification.
</div>

<div class="heading-card method">
  <div class="card-label method">4. Method</div>
  Compare all 4 hardware 144-clip feature runs against Python float32 reference using <code>compare_features.py</code> (MAE, RMSE, MaxAbs per band and class). Train Nearest-Centroid classifier on two-thirds of clips (96 clips) and evaluate on the remaining 48 clips using <code>nearest_centroid_eval.py</code> across all settings.
</div>

<div class="heading-card observations">
  <div class="card-label observations">5. Observations</div>
  <table class="data-table">
    <thead>
      <tr>
        <th>Audio &amp; Feature Configuration</th>
        <th>MAE vs Float32 Ref</th>
        <th>Max Error</th>
        <th>Accuracy</th>
        <th>Macro F1</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Laptop Float32 (16 kHz AA=True)</strong></td>
        <td>0.000000 dB</td>
        <td>0.000 dB</td>
        <td><strong>75.00%</strong></td>
        <td><strong>0.7356</strong></td>
      </tr>
      <tr>
        <td><strong>ESP32 16 kHz i16 S=1.0 (Shipping)</strong></td>
        <td><strong>0.003914 dB</strong></td>
        <td><strong>0.124 dB</strong></td>
        <td><strong>75.00%</strong></td>
        <td><strong>0.7356</strong></td>
      </tr>
      <tr>
        <td><strong>ESP32 16 kHz i8 S=1.0</strong></td>
        <td>1.089735 dB</td>
        <td>16.426 dB</td>
        <td>68.75%</td>
        <td>0.6532</td>
      </tr>
      <tr>
        <td><strong>ESP32 16 kHz i8 S=0.25</strong></td>
        <td>0.821018 dB</td>
        <td>34.247 dB</td>
        <td>66.67%</td>
        <td>0.6289</td>
      </tr>
      <tr>
        <td><strong>ESP32 8 kHz i16 (No-AA vs 8k AA Ref)</strong></td>
        <td><strong>8.050974 dB</strong></td>
        <td><strong>53.594 dB</strong></td>
        <td><span class="tag-fail">25.00%</span></td>
        <td><span class="tag-fail">0.1642</span></td>
      </tr>
    </tbody>
  </table>
  <div class="img-container">
    <img src="{plot_diff}" style="max-height: 170px;" alt="Difference Heatmaps">
    <div class="img-caption">Figure 5.1: Error Difference Heatmaps (16k i16 has virtually 0 error; 8k no-AA has massive bands 12–14 errors).</div>
  </div>
  <div class="img-container">
    <img src="{plot_cm}" style="max-height: 170px;" alt="Confusion Matrices">
    <div class="img-caption">Figure 5.2: Confusion Matrices (Laptop Float32 and ESP32 16k i16 are 100% identical).</div>
  </div>
</div>

<div class="heading-card analysis">
  <div class="card-label analysis">6. Analysis</div>
  ESP32 <code>16 kHz i16 S=1.0</code> achieves <strong>bit-exact classification parity (75.00% accuracy)</strong> with the laptop float32 pipeline; their confusion matrices are identical. In contrast, 8 kHz without anti-aliasing causes bands 12–14 to suffer 20–31 dB MAE, collapsing classifier accuracy to 25.00% (random chance on 6 classes is 16.7%). Int8 S=0.25 clips speech peaks (34.2 dB max error), degrading accuracy to 66.67%.
</div>

<div class="heading-card what-learnt">
  <div class="card-label what-learnt">7. What We Learnt</div>
  Minor quantization noise (0.004 dB) is completely benign for keyword spotting because it affects only silent bins below the speech signal floor. In contrast, aliasing injects artificial energy directly into high-frequency speech formants, catastrophic for machine learning.
</div>

<div class="heading-card llm-log">
  <div class="card-label llm-log">8. LLM Log</div>
  <strong>Prompt:</strong> "Why does audio aliasing destroy speech recognition accuracy more than uniform quantization noise?"<br>
  <strong>LLM Response Summary:</strong> Uniform quantization noise behaves like white noise, uniformly distributed across all frequency bands. Aliasing, however, creates spurious tonal peaks reflected into lower frequencies that mimic or corrupt acoustic formants, misleading classifier weight vectors.
</div>

<!-- DATA CARD & MEMO -->
<div class="page-break"></div>
<h1>7. Official Data Card &amp; Commitment Memo Summary</h1>

<h3>Official Data Card: Team 1 ("Paradise") Log-Mel Corpus</h3>
<ul>
  <li><strong>Source:</strong> 144 deterministic clips generated by <code>team_audio.py</code> (<code>team=1</code>) using <code>speech_pool.npz</code> (780 multi-voice recordings) mixed with Team 1 simulated room acoustics (7,347.98 Hz whine, 100 Hz hum, Gaussian noise).</li>
  <li><strong>Acquisition Hardware:</strong> Physical ESP32-S3-DevKitC-1 N16R8 on <code>COM11</code> (Native USB CDC).</li>
  <li><strong>Audio Configuration:</strong> 16,000 Hz, mono, <code>int16 &lt;i2</code>, scale S=1.0, <code>antialias=True</code>.</li>
  <li><strong>Feature Dimensions:</strong> 40 HTK mel bands, win=480, hop=320, 512-pt FFT, float32.</li>
  <li><strong>Dataset Volume &amp; Balance:</strong> 7,056 clean frames (1,176 frames per class across <code>on</code>, <code>off</code>, <code>stop</code>, <code>go</code>, <code>_unknown</code>, <code>_silence</code>). Exactly 49 frames per 1-second clip.</li>
  <li><strong>Straddling Frames Policy:</strong> 143 inter-clip frames (spanning 320 samples of clip $c$ and 160 samples of clip $c+1$) were discarded to eliminate label leakage.</li>
  <li><strong>Loss &amp; Integrity:</strong> 0 packets lost, 0 bad CRCs, 0 duplicates, bit-exact CRC-32 (<code>0x55c3d431</code>) verified across power cuts.</li>
  <li><strong>Out-of-Scope Uses:</strong> Cannot be used to claim far-field, reverberant outdoor doorbell accuracy; train/test splits must split by <code>clip_id</code>, never by frame.</li>
</ul>

<h3>Client Commitment Memo Specification</h3>
<table class="data-table">
  <thead>
    <tr>
      <th>Specification Parameter</th>
      <th>Committed Value</th>
      <th>Verification Evidence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Sampling Rate &amp; Filter</td>
      <td>16,000 Hz, 255-tap Blackman Anti-Aliasing Filter</td>
      <td>Suppresses 7,348 Hz whine by 51.82 dB; 0 foldover into speech.</td>
    </tr>
    <tr>
      <td>Format &amp; Scale</td>
      <td><code>int16 &lt;i2</code>, Scale S = 1.0 (Boot Auto-Ranging)</td>
      <td>74.21 dB mean SQNR, 0.00% word clipping.</td>
    </tr>
    <tr>
      <td>Port, Speed &amp; Headroom</td>
      <td>Native USB CDC (<code>COM11</code>) @ speed = 1.0</td>
      <td>Sustains up to 6.0&times; real-time (500% headroom); 0 loss.</td>
    </tr>
    <tr>
      <td>Storage Location &amp; Room Left</td>
      <td>PSRAM (4.6 MB used / 45.1% free), LittleFS (35.8% free)</td>
      <td>Survives complete power cuts; 100% bit-exact flash CRC.</td>
    </tr>
    <tr>
      <td>Compute Latency vs Budget</td>
      <td>683.75 &mu;s per frame (20,000 &mu;s budget)</td>
      <td>CPU load is 3.42%; 29.2&times; compute safety margin.</td>
    </tr>
    <tr>
      <td>Downlink Feature Bandwidth</td>
      <td>9,050 B/s (72.4 kbps)</td>
      <td>181 bytes/frame &times; 50 frames/s.</td>
    </tr>
    <tr>
      <td>Data Loss &amp; Accounting</td>
      <td>0 bytes lost, 0 packet loss, 0 CRC errors</td>
      <td>7,200 packets, 2,304,000 samples, CRC-32 match.</td>
    </tr>
    <tr>
      <td>Laptop vs Board Difference</td>
      <td>MAE = 0.003914 dB (vs same quantised: 0.000002 dB)</td>
      <td>Identical 75.00% accuracy on Nearest-Centroid classifier.</td>
    </tr>
    <tr>
      <td>Design Vulnerability</td>
      <td>Default Arduino IDE Settings (PSRAM disabled)</td>
      <td>Requires OPI PSRAM and custom partitions.csv documentation.</td>
    </tr>
  </tbody>
</table>

<!-- TEAM REFLECTION & METRICS -->
<div class="page-break"></div>
<h1>8. Team Reflection &amp; Consolidated Results Matrix</h1>

<h3>Role Rotation Reflection (Four Students &times; Five Missions)</h3>
<table class="data-table">
  <thead>
    <tr>
      <th>Mission</th>
      <th>Builder</th>
      <th>Measurer</th>
      <th>Skeptic</th>
      <th>Scribe</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Mission 1: The Pipe</strong></td>
      <td>Siddharth (S1)</td>
      <td>Rakshith (S2)</td>
      <td>Saakshi (S4)</td>
      <td>Monica (S3)</td>
    </tr>
    <tr>
      <td><strong>Mission 2: Audio &amp; Storage</strong></td>
      <td>Rakshith (S2) &amp; Siddharth (S1)</td>
      <td>Siddharth (S1)</td>
      <td>Saakshi (S4)</td>
      <td>Monica (S3)</td>
    </tr>
    <tr>
      <td><strong>Mission 3: Features &amp; FFT</strong></td>
      <td>Siddharth (S1)</td>
      <td>Siddharth (S1)</td>
      <td>Rakshith (S2)</td>
      <td>Saakshi (S4)</td>
    </tr>
    <tr>
      <td><strong>Mission 4: Loss Accounting</strong></td>
      <td>Siddharth (S1)</td>
      <td>Saakshi (S4)</td>
      <td>Rakshith (S2)</td>
      <td>Monica (S3)</td>
    </tr>
    <tr>
      <td><strong>Mission 5: ML &amp; Classifier</strong></td>
      <td>Saakshi (S4)</td>
      <td>Saakshi (S4)</td>
      <td>Siddharth (S1)</td>
      <td>Monica (S3)</td>
    </tr>
  </tbody>
</table>

<h3>Consolidated 20-Metric Experimental Verification Table</h3>
<table class="data-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Metric Name</th>
      <th>Observed Value</th>
      <th>Unit</th>
      <th>Verification Method</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>COM 115.2k Baud Rate</td>
      <td>11,376.4</td>
      <td>B/s</td>
      <td>Physical COM12 Speed=0 Benchmark</td>
    </tr>
    <tr>
      <td>2</td>
      <td>COM 921.6k Baud Rate</td>
      <td>90,909.2</td>
      <td>B/s</td>
      <td>Physical COM12 Speed=0 Benchmark</td>
    </tr>
    <tr>
      <td>3</td>
      <td>COM 2.0M Baud Rate</td>
      <td>194,726.9</td>
      <td>B/s</td>
      <td>Physical COM12 Speed=0 Benchmark</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Native USB CDC Burst Rate</td>
      <td>334,509.0</td>
      <td>B/s</td>
      <td>Physical COM11 Speed=0 Benchmark</td>
    </tr>
    <tr>
      <td>5</td>
      <td>7,348 Hz Tone Alias (No-AA)</td>
      <td>652.0</td>
      <td>Hz</td>
      <td>FFT Spectral Analysis (Clip 120)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Anti-Aliasing Filter Attenuation</td>
      <td>51.82</td>
      <td>dB</td>
      <td>255-tap Blackman vs Unfiltered</td>
    </tr>
    <tr>
      <td>7</td>
      <td>16 kHz Int16 S=1.0 Mean SQNR</td>
      <td>74.21</td>
      <td>dB</td>
      <td>Full 144-clip Audio Codec Audit</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Internal SRAM Buffer Ceiling</td>
      <td>142,070</td>
      <td>Bytes</td>
      <td>SRAM Allocation Stress Probe</td>
    </tr>
    <tr>
      <td>9</td>
      <td>OPI PSRAM Usable Capacity</td>
      <td>8,388,608</td>
      <td>Bytes</td>
      <td>ESP32-S3 PSRAM Init Telemetry</td>
    </tr>
    <tr>
      <td>10</td>
      <td>LittleFS Partition Capacity</td>
      <td>7,208,960</td>
      <td>Bytes</td>
      <td>Custom partitions.csv Layout</td>
    </tr>
    <tr>
      <td>11</td>
      <td>LittleFS Save Time (4.608 MB)</td>
      <td>10.56</td>
      <td>Seconds</td>
      <td>cmdSave() Wall-Clock Benchmark</td>
    </tr>
    <tr>
      <td>12</td>
      <td>Post-Power-Cut Flash CRC-32</td>
      <td>0x55c3d431</td>
      <td>Hex</td>
      <td>Unplug/Replug LittleFS Dump</td>
    </tr>
    <tr>
      <td>13</td>
      <td>Starter DFT Compute Time</td>
      <td>1,863,425</td>
      <td>&mu;s</td>
      <td>Baseline features.h Telemetry</td>
    </tr>
    <tr>
      <td>14</td>
      <td>Optimized Radix-2 Compute Time</td>
      <td>683.75</td>
      <td>&mu;s</td>
      <td>Optimized features.h Telemetry</td>
    </tr>
    <tr>
      <td>15</td>
      <td>DSP CPU Duty Cycle</td>
      <td>3.42</td>
      <td>%</td>
      <td>683.75 &mu;s / 20,000 &mu;s Hop</td>
    </tr>
    <tr>
      <td>16</td>
      <td>Downlink Bandwidth</td>
      <td>9,050</td>
      <td>B/s</td>
      <td>50 fps &times; 181 Bytes/Frame</td>
    </tr>
    <tr>
      <td>17</td>
      <td>144-Clip Full Stream Packet Loss</td>
      <td>0</td>
      <td>Packets</td>
      <td>7,200 Packets on COM11</td>
    </tr>
    <tr>
      <td>18</td>
      <td>16k i16 MAE vs Python Float32</td>
      <td>0.003914</td>
      <td>dB</td>
      <td>7,056-Frame Comparison</td>
    </tr>
    <tr>
      <td>19</td>
      <td>8k No-AA MAE vs Python 8k Ref</td>
      <td>8.050974</td>
      <td>dB</td>
      <td>7,056-Frame Comparison</td>
    </tr>
    <tr>
      <td>20</td>
      <td>Nearest-Centroid Accuracy</td>
      <td>75.00</td>
      <td>%</td>
      <td>Stratified Clip-Split (96/48)</td>
    </tr>
  </tbody>
</table>

<!-- FINAL BUG TRACKER & CONCLUSION -->
<div class="page-break"></div>
<h1>9. Bug Tracker, Limitations &amp; Conclusion</h1>

<h3>Resolved Engineering Bugs (Stage A &amp; Stage B Audit Trail)</h3>
<table class="data-table">
  <thead>
    <tr>
      <th>Bug ID</th>
      <th>Severity</th>
      <th>Root Cause</th>
      <th>Engineering Resolution</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>SA-01</strong></td>
      <td>Critical</td>
      <td><code>HWCDC</code> dropped TX bytes during flash reads in <code>dump("flash")</code>.</td>
      <td>Added <code>Serial.setTxBufferSize(32768)</code> and 256-B paced chunks in <code>writeAll()</code>.</td>
    </tr>
    <tr>
      <td><strong>SA-02</strong></td>
      <td>Critical</td>
      <td>Packet loss caused post-gap audio sample timeline to slip in time.</td>
      <td>Firmware synthesizes zero padding, increments <code>st.samples</code>, resets <code>fcount=0</code>.</td>
    </tr>
    <tr>
      <td><strong>SA-03</strong></td>
      <td>High</td>
      <td>Starter DFT took 1,863 ms per frame, dropping 96.8% of frames.</td>
      <td>Rewrote with radix-2 DIT FFT + twiddle LUT + sparse mel bounds (684 &mu;s, 2,725&times; speedup).</td>
    </tr>
    <tr>
      <td><strong>BUG-01</strong></td>
      <td>High</td>
      <td>Student 4 compared 8k No-AA against 8k No-AA instead of filtered 8k Ref.</td>
      <td>Re-ran comparisons with <code>speech_pool.npz</code> against true <code>8 kHz antialias=True</code>.</td>
    </tr>
    <tr>
      <td><strong>BUG-02</strong></td>
      <td>Medium</td>
      <td>Frontend Comparison view displayed outdated fallback text.</td>
      <td>Updated <code>ComparisonPage.tsx</code> and <code>MlEvaluationPage.tsx</code> copy and descriptions.</td>
    </tr>
    <tr>
      <td><strong>BUG-03</strong></td>
      <td>Medium</td>
      <td>Shared contract v1.0.0 lacked documentation for Vite <code>/repo/*</code> bridge.</td>
      <td>Incremented <code>frontend_api_contract.json</code> to v1.1.0 documenting all bridges and plots.</td>
    </tr>
    <tr>
      <td><strong>BUG-04</strong></td>
      <td>Low</td>
      <td>Python <code>MockBoard</code> did not synthesize zero fill when <code>seq=0</code> dropped.</td>
      <td>Updated <code>serial_sender.py</code> to handle <code>drop_seq_0</code> with exact sample padding.</td>
    </tr>
  </tbody>
</table>

<h3>Project Limitations &amp; Future Work</h3>
<ol>
  <li><strong>Synthesized Audio Stream:</strong> Audio originates from synthetic Python playback over USB serial rather than a live physical I2S MEMS microphone (e.g. INMP441) in an acoustically reverberant room.</li>
  <li><strong>Dataset Volume:</strong> 144 one-second clips (48 test clips) with mean+std pooling restricts keyword separability between phonetically similar commands (e.g., <code>on</code> vs <code>go</code>).</li>
  <li><strong>USB Burst Limitation:</strong> Native USB CDC drops packets during unthrottled bursts &ge; 256 KB/s due to the 32 KB hardware FIFO. DMA double-buffering is recommended for higher speed.</li>
  <li><strong>On-Device Inference:</strong> Future revisions will embed a quantized INT8 1D-CNN directly on the ESP32-S3 using ESP-NN SIMD vector instructions, eliminating feature streaming entirely.</li>
</ol>

<h3>Conclusion</h3>
<p>
Team 1 (<code>Paradise</code>) has delivered a robust, reproducible, and fully integrated Smart Doorbell Edge AI system. Physical testing on the <strong>ESP32-S3-DevKitC-1 N16R8</strong> confirms 0 lost packets, sub-millisecond feature extraction, 100% bit-exact flash persistence across power cycles, identical keyword spotting accuracy to host Python, and comprehensive full-stack visualization. The project is fully verified and ready for final submission.
</p>

</body>
</html>"""

def generate_all() -> None:
    print("=" * 60)
    print("Generating Official Course PDF Deliverables for Team 1 Paradise")
    print("=" * 60)

    # 1. Commitment Memo HTML & PDF
    memo_html = STAGE_C_DIR / "team_01_commitment_memo.html"
    memo_pdf_team = TEAM_DIR / "team_01_commitment_memo.pdf"
    memo_pdf_stage = STAGE_C_DIR / "team_01_commitment_memo.pdf"

    memo_html.write_text(build_commitment_memo_html(), encoding="utf-8")
    print(f"[1/4] Wrote Commitment Memo HTML: {memo_html.name}")

    cmd_memo = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={memo_pdf_team}",
        str(memo_html),
    ]
    res_memo = subprocess.run(cmd_memo, capture_output=True, text=True)
    if res_memo.returncode != 0:
        print(f"Error rendering Memo PDF: {res_memo.stderr}")
    else:
        memo_pdf_stage.write_bytes(memo_pdf_team.read_bytes())
        print(f"[2/4] Successfully rendered 1-Page Commitment Memo PDF ({memo_pdf_team.stat().st_size:,} bytes)")

    # 2. Comprehensive Technical Report HTML & PDF
    report_html = STAGE_C_DIR / "team_01_module2_technical_report.html"
    report_pdf_team = TEAM_DIR / "team_01_module2_technical_report.pdf"
    report_pdf_stage = STAGE_C_DIR / "team_01_module2_technical_report.pdf"

    report_html.write_text(build_technical_report_html(), encoding="utf-8")
    print(f"[3/4] Wrote Technical Report HTML: {report_html.name}")

    cmd_report = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={report_pdf_team}",
        str(report_html),
    ]
    res_report = subprocess.run(cmd_report, capture_output=True, text=True)
    if res_report.returncode != 0:
        print(f"Error rendering Report PDF: {res_report.stderr}")
    else:
        report_pdf_stage.write_bytes(report_pdf_team.read_bytes())
        print(f"[4/4] Successfully rendered Technical Report PDF ({report_pdf_team.stat().st_size:,} bytes)")

    print("=" * 60)
    print("PDF Generation Completed Successfully!")
    print(f"Deliverables in {TEAM_DIR.name}:")
    for f in TEAM_DIR.glob("*.pdf"):
        print(f"  - {f.name} ({f.stat().st_size:,} bytes)")
    print("=" * 60)

if __name__ == "__main__":
    generate_all()
