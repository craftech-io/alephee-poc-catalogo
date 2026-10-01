import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync(new URL('../docs/presentacion-warroom.html', import.meta.url), 'utf8');
const data = JSON.parse(readFileSync(new URL('../docs/warroom/diapositivas.json', import.meta.url), 'utf8'));
const TOTAL = data.slides.length;
const id = n => `s${String(n).padStart(2, '0')}`;
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const css = html.match(/<style>([\s\S]*?)<\/style>/)[1];
const attrs = tag => Object.fromEntries([...tag.matchAll(/([\w-]+)="([^"]*)"/g)].map(m => [m[1], m[2]]));
const tags = [...html.matchAll(/<section\b[^>]*>/g)].map(m => m[0]);

// Contrato del HTML generado: reproduce la colisión que mostraba varias diapositivas.
test('los estilos de componentes no se aplican a las diapositivas', () => {
  assert.equal(tags.length, TOTAL);
  for (const tag of tags) {
    const classes = attrs(tag).class.split(' ');
    assert.ok(classes.every(c => c === 'slide' || c === 'active' || c.startsWith('slide--')), tag);
  }
  assert.match(css, /\.slide\[hidden\]\s*\{display:none!important\}/);
  assert.match(css, /@media print\{\.slide\[hidden\]\{display:flex!important\}\}/);
});

test('el HTML inicial solo deja visible la primera diapositiva', () => {
  assert.deepEqual(tags.filter(t => !/\shidden(?:\s|>)/.test(t)).map(t => attrs(t).id), ['s01']);
});

// Doble mínimo de DOM para probar la navegación real del script sin lanzar Chromium.
// No valida geometría, composición visual ni interacción nativa de details.
function page(hash = '', denyHistory = false) {
  const elements = new Map();
  function element(extra = {}) {
    return { hidden: false, value: '', textContent: '', innerHTML: '', style: {},
      setAttribute(name, value) { this[name] = value; }, focus() {}, ...extra };
  }
  const slides = tags.map(tag => {
    const a = attrs(tag), classes = new Set(a.class.split(' '));
    return element({ id: a.id, hidden: /\shidden(?:\s|>)/.test(tag), dataset: {section:a['data-section']},
      classList: {toggle(c,on) {if(on)classes.add(c);else classes.delete(c);}},
      querySelector() {return element({innerHTML:'Notas'});} });
  });
  for (const id of ['section-select','notes-panel','count','prev','next','notes-body','notes','close-notes','print']) elements.set(id, element());
  elements.get('notes-panel').hidden = true;
  const listeners = new Map();
  const ctx = vm.createContext({
    document: {querySelectorAll(s) {return s === '.slide' ? slides : [];},
      getElementById(id) {return elements.get(id);}, querySelector() {return element();},
      addEventListener(type,fn) {listeners.set(type,fn);} },
    history: {replaceState() {if(denyHistory)throw new Error('SecurityError');}},
    location:{hash}, window:{scrollTo(){},print(){},addEventListener(){}}, setInterval(){},
  });
  vm.runInContext(script, ctx);
  return {slides,elements,ctx,listeners};
}
const visible = p => p.slides.filter(s=>!s.hidden).map(s=>s.id);

test('recorre todas las diapositivas mostrando exactamente una cada vez', () => {
  const p = page();
  for (let n = 0; n < tags.length; n++) {
    assert.deepEqual(visible(p), [id(n+1)]);
    assert.equal(p.elements.get('count').textContent, `${n+1} / ${TOTAL}`);
    p.elements.get('next').onclick();
  }
  assert.equal(p.elements.get('next').disabled,true);
  p.elements.get('prev').onclick();
  assert.deepEqual(visible(p), [id(TOTAL-1)]);
});

test('selección de sección y enlaces directos conservan una sola diapositiva visible', () => {
  const second = tags.findIndex(t => attrs(t)['data-section'] !== attrs(tags[0])['data-section']);
  const p = page(`#${id(second+1)}`);
  assert.deepEqual(visible(p), [id(second+1)]);
  p.elements.get('section-select').value=String(second);
  p.elements.get('section-select').onchange();
  assert.deepEqual(visible(p), [id(second+1)]);
});

test('una restricción de History API no rompe avance ni notas', () => {
  const p = page('',true);
  p.elements.get('next').onclick();
  assert.deepEqual(visible(p), ['s02']);
  p.elements.get('notes').onclick();
  assert.equal(p.elements.get('notes-panel').hidden,false);
  p.elements.get('close-notes').onclick();
  assert.equal(p.elements.get('notes-panel').hidden,true);
});

test('un enlace con índice no entero vuelve al inicio sin dejar todo oculto', () => {
  assert.deepEqual(visible(page('#1.5')), ['s01']);
});

test('las láminas de código, decisión y demo existen y están escapadas', { todo: true }, () => {
  const kinds = new Set(data.slides.map(s => s.kind));
  for (const k of ['code', 'decision', 'demo']) assert.ok(kinds.has(k), k);
  assert.ok(html.includes('class="ln" data-n="'));
  assert.doesNotMatch(html, /<code>[^<]*<(?!\/code|span|\/span)/);
});
