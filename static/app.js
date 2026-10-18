const codeEl = document.getElementById('code');
const gutter = document.getElementById('gutter');
const lineCount = document.getElementById('lineCount');
const reviewBtn = document.getElementById('reviewBtn');
const errorBox = document.getElementById('errorBox');
let latestReport = null;

function updateLines() {
  const count = Math.max(1, codeEl.value.split('\n').length);
  gutter.textContent = Array.from({length: count}, (_, i) => i + 1).join('\n');
  lineCount.textContent = `${codeEl.value ? codeEl.value.split('\n').length : 0} lines`;
}
codeEl.addEventListener('input', updateLines);
codeEl.addEventListener('scroll', () => { gutter.scrollTop = codeEl.scrollTop; });
codeEl.addEventListener('keydown', e => {
  if (e.key === 'Tab') {
    e.preventDefault();
    const start = codeEl.selectionStart, end = codeEl.selectionEnd;
    codeEl.setRangeText('    ', start, end, 'end');
    updateLines();
  }
});
updateLines();

document.getElementById('sampleBtn').addEventListener('click', () => {
  const lang = document.getElementById('language').value;
  const samples = {
    python: `import os\n\nAPI_KEY = "sk_test_123456789"\n\ndef run_command(user_input):\n    try:\n        os.system("echo " + user_input)\n    except:\n        print("Something went wrong")\n\nrun_command(input("Enter a value: "))`,
    javascript: `var userName = "guest";\nif (userName == "admin") {\n  console.log("Welcome");\n}\n// TODO: add input validation`,
    java: `public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello world");\n    }\n}`
  };
  codeEl.value = samples[lang] || samples.python;
  if (lang === 'java') document.getElementById('language').value = 'java';
  updateLines();
});
document.getElementById('language').addEventListener('change', () => {});

document.getElementById('fileInput').addEventListener('change', async e => {
  const file = e.target.files[0];
  if (!file) return;
  const form = new FormData(); form.append('file', file);
  try {
    const res = await fetch('/api/upload', {method:'POST', body:form});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Upload failed');
    codeEl.value = data.code; updateLines(); hideError();
    const ext = file.name.split('.').pop().toLowerCase();
    const map = {py:'python',js:'javascript',ts:'typescript',java:'java',c:'c',cpp:'cpp',h:'c',cs:'csharp',go:'go',php:'php',rb:'ruby'};
    if (map[ext]) document.getElementById('language').value = map[ext];
  } catch (err) { showError(err.message); }
  e.target.value = '';
});
function showError(msg) { errorBox.textContent = msg; errorBox.hidden = false; }
function hideError() { errorBox.hidden = true; errorBox.textContent = ''; }

reviewBtn.addEventListener('click', async () => {
  hideError();
  if (!codeEl.value.trim()) { showError('Paste code or load a sample before starting the review.'); return; }
  reviewBtn.disabled = true; reviewBtn.textContent = 'Reviewing…';
  document.getElementById('status').textContent = 'ANALYZING';
  try {
    const res = await fetch('/api/review', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({code:codeEl.value, language:document.getElementById('language').value})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Review failed');
    latestReport = {...data, source: {language:document.getElementById('language').value, lines:codeEl.value.split('\n').length}};
    renderReport(data);
    document.getElementById('status').textContent = 'COMPLETE';
  } catch (err) {
    showError(err.message); document.getElementById('status').textContent = 'ERROR';
  } finally {
    reviewBtn.disabled = false; reviewBtn.innerHTML = '<span>✦</span> Review code';
  }
});

function renderReport(data) {
  document.getElementById('emptyState').hidden = true;
  document.getElementById('report').hidden = false;
  document.getElementById('score').textContent = data.score;
  document.getElementById('scoreRingText').textContent = data.score;
  document.getElementById('summary').textContent = data.summary;
  const counts = document.getElementById('counts');
  counts.innerHTML = '';
  ['critical','high','medium','low','info'].forEach(s => {
    const item = document.createElement('div'); item.className = `count ${s}`;
    const b = document.createElement('b'); b.textContent = data.counts[s] || 0;
    const span = document.createElement('span'); span.textContent = s;
    item.append(b,span); counts.append(item);
  });
  document.getElementById('findingTotal').textContent = `${data.findings.length} total`;
  const findings = document.getElementById('findings'); findings.innerHTML = '';
  if (!data.findings.length) {
    const p = document.createElement('p'); p.className = 'summary'; p.textContent = 'No issues were flagged by the configured checks. This does not guarantee the code is defect-free.'; findings.append(p);
  }
  data.findings.forEach(f => {
    const card = document.createElement('article'); card.className = 'finding';
    const top = document.createElement('div'); top.className = 'finding-top';
    const sev = document.createElement('span'); sev.className = `sev sev-${f.severity}`; sev.textContent = f.severity.toUpperCase();
    const title = document.createElement('h4'); title.textContent = f.title;
    const line = document.createElement('span'); line.className = 'line-tag'; line.textContent = `L${f.line}`;
    top.append(sev,title,line); card.append(top);
    const msg = document.createElement('p'); msg.textContent = f.message; card.append(msg);
    const suggestion = document.createElement('p'); suggestion.className = 'suggestion'; suggestion.textContent = `Suggestion: ${f.suggestion}`; card.append(suggestion);
    if (f.snippet) { const snippet = document.createElement('div'); snippet.className = 'snippet'; snippet.textContent = f.snippet; card.append(snippet); }
    findings.append(card);
  });
  fillList('nextSteps', data.next_steps || []);
  const strengthsWrap = document.getElementById('strengthsWrap');
  strengthsWrap.hidden = !(data.strengths && data.strengths.length);
  fillList('strengths', data.strengths || []);
  document.getElementById('engineLabel').textContent = `Engine: ${data.engine} · ${data.meta?.language || ''} · ${data.meta?.lines || 0} lines`;
  document.getElementById('disclaimer').textContent = data.disclaimer || '';
}
function fillList(id, values) {
  const el = document.getElementById(id); el.innerHTML = '';
  values.forEach(value => { const li = document.createElement('li'); li.textContent = value; el.append(li); });
}
document.getElementById('exportBtn').addEventListener('click', async () => {
  if (!latestReport) return;
  const blob = new Blob([JSON.stringify(latestReport, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob); const a = document.createElement('a');
  a.href = url; a.download = 'code-review-report.json'; a.click(); URL.revokeObjectURL(url);
});
