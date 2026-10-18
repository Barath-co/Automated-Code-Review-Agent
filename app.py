from flask import Flask, render_template, request, jsonify, send_file
from analyzer import review_code
import io, json, os
from datetime import datetime

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB upload limit

LANGUAGES = ["python", "javascript", "typescript", "java", "c", "cpp", "csharp", "go", "php", "ruby"]

@app.get("/")
def index():
    return render_template("index.html", languages=LANGUAGES)

@app.post("/api/review")
def api_review():
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    language = (data.get("language") or "python").lower()
    if not code:
        return jsonify({"error": "Paste or upload some source code first."}), 400
    if len(code) > 200_000:
        return jsonify({"error": "Code is too long. Please keep submissions under 200,000 characters."}), 413
    if language not in LANGUAGES:
        return jsonify({"error": "Unsupported language selection."}), 400
    try:
        result = review_code(code, language)
        result["meta"] = {
            "language": language,
            "lines": len(code.splitlines()),
            "reviewed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "engine": result.get("engine", "Local heuristic review")
        }
        return jsonify(result)
    except Exception as exc:
        app.logger.exception("Review failed")
        return jsonify({"error": "Review failed. Check the server log for details."}), 500

@app.post("/api/export")
def api_export():
    data = request.get_json(silent=True) or {}
    report = data.get("report")
    if not isinstance(report, dict):
        return jsonify({"error": "No report provided."}), 400
    content = json.dumps(report, indent=2, ensure_ascii=False)
    return send_file(io.BytesIO(content.encode("utf-8")), mimetype="application/json",
                     as_attachment=True, download_name="code-review-report.json")

@app.post("/api/upload")
def api_upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Choose a source file to upload."}), 400
    if file.content_length and file.content_length > 1_000_000:
        return jsonify({"error": "File must be smaller than 1 MB."}), 413
    try:
        code = file.read(1_000_001).decode("utf-8-sig")
    except UnicodeDecodeError:
        return jsonify({"error": "Please upload a UTF-8 text source file."}), 400
    if len(code) > 1_000_000:
        return jsonify({"error": "File must be smaller than 1 MB."}), 413
    return jsonify({"filename": file.filename, "code": code})

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
