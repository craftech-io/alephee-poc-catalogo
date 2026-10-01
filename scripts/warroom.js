const slides = [...document.querySelectorAll('.slide')];
const selector = document.getElementById('section-select');
const notesPanel = document.getElementById('notes-panel');
let current = 0;
function show(n) {
  current = Math.max(0, Math.min(slides.length - 1, Number.isInteger(n) ? n : 0));
  slides.forEach((s, i) => {
    s.classList.toggle('active', i === current);
    s.hidden = i !== current;
    s.setAttribute('aria-hidden', String(i !== current));
  });
  document.getElementById('count').textContent = `${current + 1} / ${slides.length}`;
  document.getElementById('prev').disabled = current === 0;
  document.getElementById('next').disabled = current === slides.length - 1;
  const first = slides.findIndex(s => s.dataset.section === slides[current].dataset.section);
  selector.value = String(first);
  document.querySelector('.progress').style.width = `${100 * (current + 1) / slides.length}%`;
  document.getElementById('notes-body').innerHTML = slides[current].querySelector('.notes-content').innerHTML;
  // Algunos visores de HTML permiten scripts pero bloquean la History API.
  try {history.replaceState(null, '', `#${slides[current].id}`);} catch { /* La navegación sigue siendo local. */ }
  window.scrollTo(0, 0);
}
function toggleNotes(force) {
  notesPanel.hidden = force === undefined ? !notesPanel.hidden : !force;
  document.getElementById('notes').setAttribute('aria-expanded', String(!notesPanel.hidden));
  if (!notesPanel.hidden) document.getElementById('close-notes').focus();
  else document.getElementById('notes').focus();
}
selector.onchange = () => show(Number(selector.value));
document.getElementById('prev').onclick = () => show(current - 1);
document.getElementById('next').onclick = () => show(current + 1);
document.getElementById('notes').onclick = () => toggleNotes();
document.getElementById('close-notes').onclick = () => toggleNotes(false);
document.getElementById('print').onclick = () => window.print();
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && !notesPanel.hidden) {toggleNotes(false); return;}
  if (e.target.closest('select,input,textarea')) return;
  if (e.key.toLowerCase() === 'n') {toggleNotes();return;}
  if (!notesPanel.hidden) return;
  if (e.key === ' ' && e.target.closest('button,summary')) return;
  if (['ArrowRight','PageDown',' '].includes(e.key)) {e.preventDefault();show(current + 1);}
  if (['ArrowLeft','PageUp'].includes(e.key)) {e.preventDefault();show(current - 1);}
  if (e.key === 'Home') show(0);
  if (e.key === 'End') show(slides.length - 1);
});
document.querySelectorAll('.choice').forEach(b => b.onclick = () => {
  b.parentElement.querySelectorAll('.choice').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
});
const timers = [...document.querySelectorAll('.timer')].map(el => ({el,remaining:Number(el.dataset.seconds),deadline:null}));
function paintTimer(t) {
  const seconds = Math.max(0, Math.ceil(t.remaining));
  t.el.querySelector('output').textContent = `${String(Math.floor(seconds / 60)).padStart(2,'0')}:${String(seconds % 60).padStart(2,'0')}`;
  t.el.querySelector('[data-action=timer]').textContent = t.deadline === null ? (seconds ? 'Iniciar / seguir' : 'Tiempo cumplido') : 'Pausar';
  t.el.querySelector('[data-action=timer]').disabled = seconds === 0;
}
for (const t of timers) {
  t.el.querySelector('[data-action=timer]').onclick = () => {
    if (t.deadline === null) t.deadline = Date.now() + t.remaining * 1000;
    else {t.remaining = Math.max(0,(t.deadline-Date.now())/1000);t.deadline=null;}
    paintTimer(t);
  };
  t.el.querySelector('[data-action=reset-timer]').onclick = () => {t.remaining=Number(t.el.dataset.seconds);t.deadline=null;paintTimer(t);};
}
setInterval(() => {for (const t of timers) {if(t.deadline!==null){t.remaining=Math.max(0,(t.deadline-Date.now())/1000);if(t.remaining===0)t.deadline=null;paintTimer(t);}}},250);
let printDetails = [];
window.addEventListener('beforeprint', () => {printDetails=[...document.querySelectorAll('details')].filter(d=>!d.open);printDetails.forEach(d=>d.open=true);});
window.addEventListener('afterprint', () => {printDetails.forEach(d=>d.open=false);});
const hash=location.hash.slice(1);
const index=slides.findIndex(s=>s.id===hash);
show(index>=0?index:Math.max(0,(Number(hash)||1)-1));
