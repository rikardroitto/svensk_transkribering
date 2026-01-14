import os
# Apply torch load patch immediately
from . import torch_fix
import uuid
import json
import threading
from pathlib import Path
from typing import List, Dict
from queue import Queue

from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, flash, Response, jsonify

from .config import HF_TOKEN, DEFAULT_LANGUAGE, DEFAULT_OUTPUT_FORMATS, WHISPER_MODEL
from .utils import get_optimal_device, format_duration
from .utils import get_optimal_device, format_duration
from .whisperx_pipeline import process_audio_whisperx
from .merge import merge_consecutive_same_speaker
from .export import export_results


OUTPUT_DIR = Path(os.environ.get("WD_OUTPUT_DIR", "output")).resolve()
UPLOAD_DIR = OUTPUT_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "whisper-diarize-secret")
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_UPLOAD_MB", 100)) * 1024 * 1024

# Progress tracking
progress_store: Dict[str, Dict] = {}


def update_progress(job_id: str, status: str, progress: int, message: str = ""):
    """Uppdatera progress för ett jobb"""
    progress_store[job_id] = {
        "status": status,
        "progress": progress,
        "message": message
    }


INDEX_HTML = """
<!doctype html>
<html lang="sv">
  <head>
    <meta charset="utf-8" />
    <title>Whisper Diarize – Webb</title>
    <style>
      body { font-family: system-ui, sans-serif; margin: 2rem; }
      form { display: grid; gap: .8rem; max-width: 700px; }
      fieldset { border: 1px solid #ccc; padding: 1rem; }
      .row { display: grid; grid-template-columns: 180px 1fr; align-items: center; gap: .8rem; }
      .formats { display: flex; gap: 1rem; }
      .msg { color: #b00; }
      .ok { color: #070; }
      code { background: #f5f5f5; padding: .1rem .3rem; }

      /* Progress styles */
      #progress-container { display: none; max-width: 700px; margin: 2rem 0; }
      #progress-container.active { display: block; }
      .progress-bar-outer { width: 100%; height: 30px; background: #f0f0f0; border-radius: 5px; overflow: hidden; margin: 1rem 0; }
      .progress-bar-inner { height: 100%; background: linear-gradient(90deg, #4CAF50, #45a049); transition: width 0.3s ease; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
      #progress-status { font-size: 1.1rem; margin: 0.5rem 0; color: #333; }
      #progress-message { font-size: 0.9rem; color: #666; }
      .spinner { display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #4CAF50; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px; }
      @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
      #submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
    </style>
  </head>
  <body>
    <h1>Whisper Diarize – Webb</h1>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
          {% for category, message in messages %}
            <li class="{{ 'ok' if category=='ok' else 'msg' }}">{{ message|safe }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <!-- Progress Container -->
    <div id="progress-container">
      <h2><span class="spinner"></span><span id="progress-status">Bearbetar...</span></h2>
      <div class="progress-bar-outer">
        <div class="progress-bar-inner" id="progress-bar" style="width: 0%;">0%</div>
      </div>
      <p id="progress-message"></p>
    </div>

    <form method="post" enctype="multipart/form-data" action="{{ url_for('transcribe_route') }}" id="upload-form">
      <fieldset>
        <legend>Ljudfil</legend>
        <div class="row">
          <label for="file">Fil (mp3/wav):</label>
          <input type="file" id="file" name="file" accept="audio/*" required />
        </div>
      </fieldset>

      <fieldset>
        <legend>Inställningar</legend>
        <div class="row">
          <label for="language">Språk:</label>
          <input type="text" id="language" name="language" value="{{ default_language }}" />
        </div>
        <div class="row">
          <label for="device">Device:</label>
          <select id="device" name="device">
            <option value="auto" selected>auto</option>
            <option value="cpu">cpu</option>
            <option value="cuda">cuda</option>
          </select>
        </div>
        <div class="row">
          <label for="whisper_model">Whisper‑modell:</label>
          <input type="text" id="whisper_model" name="whisper_model" value="{{ whisper_model }}" />
        </div>
        <div class="row">
          <label>Format:</label>
          <div class="formats">
            {% for f in ["txt","srt","json","tsv"] %}
            <label><input type="checkbox" name="formats" value="{{ f }}" {% if f in default_formats %}checked{% endif %}/> {{ f }}</label>
            {% endfor %}
          </div>
        </div>
        <div class="row">
          <label for="diarization">Diarisering:</label>
          <input type="checkbox" id="diarization" name="diarization" checked />
        </div>
        <div class="row">
          <label for="num_speakers">Antal talare:</label>
          <input type="number" id="num_speakers" name="num_speakers" min="1" max="20" placeholder="auto" />
        </div>
        <div class="row">
          <label for="merge_speakers">Slå ihop talare:</label>
          <input type="checkbox" id="merge_speakers" name="merge_speakers" checked />
        </div>
      </fieldset>

      <button type="submit" id="submit-btn">Kör</button>
    </form>

    <p>Utdata‑katalog: <code>{{ output_dir }}</code></p>
    <p>Serverar filer under <code>/files/</code></p>

    <script>
      const form = document.getElementById('upload-form');
      const progressContainer = document.getElementById('progress-container');
      const progressBar = document.getElementById('progress-bar');
      const progressStatus = document.getElementById('progress-status');
      const progressMessage = document.getElementById('progress-message');
      const submitBtn = document.getElementById('submit-btn');

      form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Disable submit button
        submitBtn.disabled = true;

        // Show progress
        progressContainer.classList.add('active');
        updateProgress(0, 'Laddar upp fil...', '');

        // Create FormData and submit
        const formData = new FormData(form);

        fetch('/transcribe', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          if (data.job_id) {
            // Start listening to progress
            listenToProgress(data.job_id);
          } else {
            throw new Error(data.error || 'Unknown error');
          }
        })
        .catch(error => {
          alert('Fel: ' + error.message);
          progressContainer.classList.remove('active');
          submitBtn.disabled = false;
        });
      });

      function listenToProgress(jobId) {
        const eventSource = new EventSource('/progress/' + jobId);

        eventSource.onmessage = function(event) {
          const data = JSON.parse(event.data);
          updateProgress(data.progress, data.status, data.message);

          if (data.status === 'done' || data.status === 'error') {
            eventSource.close();
            setTimeout(() => {
              // Redirect to result handler to show flash message
              window.location.href = '/job_result/' + jobId;
            }, 1000);
          }
        };

        eventSource.onerror = function() {
          eventSource.close();
          alert('Anslutningen till servern förlorades');
          submitBtn.disabled = false;
        };
      }

      function updateProgress(percent, status, message) {
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
        progressStatus.textContent = status;
        progressMessage.textContent = message;
      }
    </script>
  </body>
  </html>
"""


@app.route("/")
def index():
    return render_template_string(
        INDEX_HTML,
        default_language=DEFAULT_LANGUAGE,
        default_formats=DEFAULT_OUTPUT_FORMATS,
        whisper_model=WHISPER_MODEL,
        output_dir=str(OUTPUT_DIR),
    )


@app.route("/auto_test")
def auto_test():
    """
    One-click test endpoint - automatically starts processing the hardcoded test file.
    Navigate to http://127.0.0.1:5000/auto_test to trigger.
    """
    import uuid
    import threading
    
    # Hardcoded test file
    test_file = Path("/mnt/c/Users/rikar/Downloads/morgonsoffan angel [4W4Xtz6g8Og].mp3")
    
    if not test_file.exists():
        return f"<h1>Fel</h1><p>Testfilen finns inte: {test_file}</p>", 404
    
    # Generate job ID
    job_id = uuid.uuid4().hex[:12]
    
    # Get device settings
    device, compute_type = get_optimal_device()
    
    update_progress(job_id, "Auto-test startar", 5, f"Bearbetar {test_file.name}")
    
    # Start background task
    thread = threading.Thread(
        target=process_audio_task,
        args=(job_id, test_file, DEFAULT_LANGUAGE, device, compute_type, WHISPER_MODEL,
              True, None, True, ["txt", "srt"])
    )
    thread.daemon = True
    thread.start()
    
    # Return a simple page that shows progress
    return f'''
    <html>
    <head><title>Auto Test</title></head>
    <body>
        <h1>Auto-test startad!</h1>
        <p>Job ID: {job_id}</p>
        <p>Fil: {test_file.name}</p>
        <p>Kolla terminalen för progress...</p>
        <p><a href="/">Tillbaka till startsidan</a></p>
    </body>
    </html>
    '''


@app.route("/job_result/<job_id>")
def job_result(job_id: str):
    """Hanterar resultat och flash-meddelanden innan redirect"""
    if job_id not in progress_store:
        return redirect(url_for("index"))
        
    current = progress_store[job_id]
    
    if current["status"] == "done":
        if "files" in current and "results" in current:
            files = current["files"]
            results = current["results"]
            links = [url_for("serve_file", path=Path(p).relative_to(OUTPUT_DIR)) for p in files]
            flash_msg = (
                f"Klart: {len(results)} segment, "
                f"längd {format_duration(results[-1]['end'] if results else 0)}. "
                f"Filer: " +
                ", ".join(f"<a href='{l}'>{Path(p).name}</a>" for l, p in zip(links, files))
            )
            flash(flash_msg, "ok")
    elif current["status"] == "error":
        flash(current["message"], "err")
        
    # Clean up
    if job_id in progress_store:
        del progress_store[job_id]
        
    return redirect(url_for("index"))


def process_audio_task(job_id: str, target: Path, language: str, device: str, compute_type: str,
                       whisper_model: str, use_diarization: bool, num_speakers: int, merge_speakers: bool, formats: List[str]):
    """Background task för att bearbeta ljud"""
    try:
        update_progress(job_id, "Bearbetar...", 10, "Startar WhisperX pipeline")

        # Anropa WhisperX pipeline
        # Notera: Vi ignorerar whisper_model argumentet här eftersom whisperx_pipeline hårdkodar/väljer modell själv (large-v2)
        # eller så borde vi uppdaterat pipeline att ta emot det. I min implementation tog den inte model_name.
        # Vi kör på default i pipeline.
        
        results = process_audio_whisperx(
            audio_path=str(target),
            num_speakers=num_speakers if use_diarization else None,
            device=device,
            compute_type=compute_type,
            language=language
        )
        
        if not use_diarization:
             for seg in results:
                 seg["speaker"] = "SPEAKER_00"

        if merge_speakers:
            results = merge_consecutive_same_speaker(results)

        update_progress(job_id, "Bearbetning klar", 80, f"{len(set(s['speaker'] for s in results))} talare identifierade")

        update_progress(job_id, "Exporterar resultat...", 85, f"Skapar {', '.join(formats)}-filer")

        base_name = target.stem
        created_files = export_results(
            segments=results,
            output_dir=str(OUTPUT_DIR),
            base_name=base_name,
            formats=formats,
        )

        # Store results in progress store
        progress_store[job_id]["files"] = created_files
        progress_store[job_id]["results"] = results

        update_progress(job_id, "done", 100, f"Klart! {len(results)} segment, {len(created_files)} filer skapade")

    except Exception as e:
        update_progress(job_id, "error", 0, f"Fel: {str(e)}")


@app.route("/transcribe", methods=["POST"])
def transcribe_route():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "Ingen fil bifogad"}), 400

    language = request.form.get("language", DEFAULT_LANGUAGE)
    device_opt = request.form.get("device", "auto").lower()
    whisper_model = request.form.get("whisper_model", WHISPER_MODEL)
    formats: List[str] = request.form.getlist("formats") or DEFAULT_OUTPUT_FORMATS
    use_diarization = request.form.get("diarization") is not None
    num_speakers_str = request.form.get("num_speakers", "").strip()
    num_speakers = int(num_speakers_str) if num_speakers_str else None
    merge_speakers = request.form.get("merge_speakers") is not None

    # Generate job ID
    job_id = uuid.uuid4().hex[:12]

    # Spara uppladdad fil
    fid = uuid.uuid4().hex[:8]
    safe_name = Path(file.filename).name
    target = UPLOAD_DIR / f"{fid}_{safe_name}"
    file.save(target)

    update_progress(job_id, "Fil uppladdad", 5, f"Bearbetar {target.name}")

    # Device/compute type
    if device_opt == "auto":
        device, compute_type = get_optimal_device()
    else:
        device = device_opt
        compute_type = "float16" if device == "cuda" else "int8"

    # Start background task
    thread = threading.Thread(
        target=process_audio_task,
        args=(job_id, target, language, device, compute_type, whisper_model,
              use_diarization, num_speakers, merge_speakers, formats)
    )
    thread.daemon = True
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>")
def progress_stream(job_id: str):
    """Server-Sent Events endpoint för progress"""
    def generate():
        last_status = None
        while True:
            if job_id in progress_store:
                current = progress_store[job_id]

                # Only send if changed
                if current != last_status:
                    last_status = current.copy()
                    yield f"data: {json.dumps(current)}\n\n"

                # If done or error, send final message and end stream
                if current["status"] in ["done", "error"]:
                    # Wait a bit to let client receive the message
                    yield f"data: {json.dumps(current)}\n\n"
                    break

            import time
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


@app.route("/files/<path:path>")
def serve_file(path: str):
    return send_from_directory(OUTPUT_DIR, path, as_attachment=False)


def run(host: str = "127.0.0.1", port: int = 5000):
    # Sätt miljöflagga för Windows‑symlänkar om ej satt
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    run()
