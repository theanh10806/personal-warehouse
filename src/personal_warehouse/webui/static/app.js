/* Personal Warehouse - web interface.  Plain JavaScript, no build step, no external requests.
   All data and rules come from the Python side through `api.*` (see webui/api.py). */
(() => {
'use strict';

/* ------------------------------------------------------------------ helpers */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const icon = (id, cls = '') => `<svg class="${cls}" aria-hidden="true"><use href="#i-${id}"/></svg>`;
const debounce = (fn, ms) => { let h; return (...a) => { clearTimeout(h); h = setTimeout(() => fn(...a), ms); }; };

let B = null;                                   // bootstrap data: language, texts, option lists
const t = (key, ...args) => String((B && B.strings[key]) ?? key).replace(/\{(\d+)\}/g, (_, i) => args[+i] ?? '');

/* ------------------------------------------------------------------ api (pywebview or HTTP) */
const HTTP = document.documentElement.dataset.http === '1';
async function callApi(name, args) {
  try {
    if (!HTTP) return await window.pywebview.api[name](...args);
    const r = await fetch('/api/' + name, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(args)});
    return await r.json();
  } catch (e) {
    return {ok: false, error: String(e && e.message || e)};
  }
}
const api = new Proxy({}, {get: (_, name) => (...args) => callApi(name, args)});
const whenReady = () => new Promise(res => {
  if (HTTP || (window.pywebview && window.pywebview.api)) return res();
  window.addEventListener('pywebviewready', () => res(), {once: true});
});

/* ------------------------------------------------------------------ state */
const S = {
  page: 'dashboard', token: 0, compactManual: null,
  inv: {search: '', location: '', condition: '', low_only: false, archived: false, sort: 'location', desc: false},
  invRows: [], invLimit: 300, selected: null, checked: new Set(),
  item: {id: null, photoNew: null, photoRemove: false, photoCurrent: null, code: ''},
  mv: {item: null, onlyItem: false},
  scan: {itemId: null},
};
const PAGES = [
  ['dashboard', 'grid', 'nav_dashboard'], ['inventory', 'box', 'nav_inventory'], ['item', 'tag', 'nav_item'],
  ['movement', 'mv', 'nav_move'], ['scan', 'scan', 'nav_scan'], ['locations', 'map', 'nav_map'], ['settings', 'cog', 'nav_settings'],
];

/* ------------------------------------------------------------------ toasts and dialogs */
function toast(msg, kind = '', ms = 6000) {
  if (!msg) return;
  const el = document.createElement('div');
  el.className = 'toast ' + kind;
  el.textContent = msg;
  $('#toasts').appendChild(el);
  while ($('#toasts').children.length > 4) $('#toasts').firstChild.remove();
  setTimeout(() => el.remove(), ms);
}

function dialog({title, body = '', html = '', buttons, wide = false, onOpen}) {
  return new Promise(resolve => {
    const ov = $('#overlay');
    const prevFocus = document.activeElement;
    ov.hidden = false;
    ov.innerHTML = `<div class="dialog" role="dialog" aria-modal="true" ${wide ? 'style="width:min(620px,100%)"' : ''}>
      <h2>${esc(title)}</h2>${html || `<div class="body">${esc(body)}</div>`}
      <div class="foot">${buttons.map((b, i) => `<button type="button" class="btn ${b.kind || ''}" data-i="${i}">${esc(b.label)}</button>`).join('')}</div></div>`;
    const close = value => {
      ov.hidden = true; ov.innerHTML = '';
      document.removeEventListener('keydown', onKey, true);
      if (prevFocus && prevFocus.focus) prevFocus.focus();
      resolve(value);
    };
    const collect = () => $$('[name]', ov).reduce((o, el) => (o[el.name] = el.type === 'checkbox' ? el.checked : el.value, o), {});
    const onKey = e => {
      if (e.key === 'Escape') { e.stopPropagation(); close(buttons.find(b => b.cancel)?.value ?? null); }
    };
    document.addEventListener('keydown', onKey, true);
    ov.onclick = e => {
      const btn = e.target.closest('button[data-i]');
      if (btn) { const b = buttons[+btn.dataset.i]; close(b.collect ? {value: b.value, form: collect()} : b.value); }
      else if (e.target === ov) close(buttons.find(b => b.cancel)?.value ?? null);
    };
    if (onOpen) onOpen(ov);
    (ov.querySelector('[autofocus]') || ov.querySelector('.btn.primary,.btn.success,.btn.danger') || ov.querySelector('.btn')).focus();
  });
}
const alertBox = (title, body) => dialog({title, body, buttons: [{label: t('ui_ok'), value: true, kind: 'primary', cancel: true}]});
const confirmBox = (title, body, kind = 'primary', okLabel = t('ui_confirm')) => dialog({
  title, body, buttons: [{label: t('btn_cancel'), value: false, cancel: true}, {label: okLabel, value: true, kind}]});

/** Show an API failure in a dialog. Returns true when the call succeeded. */
async function ok(res) {
  if (res && res.ok !== false) return true;
  await alertBox((res && res.title) || t('ui_error'), (res && res.error) || t('ui_error'));
  return false;
}

/* ------------------------------------------------------------------ shell (sidebar, top bar) */
function applyShell() {
  const root = document.documentElement;
  root.lang = B.lang; root.dir = B.rtl ? 'rtl' : 'ltr'; root.dataset.theme = B.theme;
  document.title = t('app_name');
  $('#brandName').textContent = t('app_name');
  $('#brandSub').textContent = t('brand_sub');
  $('#sideFoot').textContent = t('nav_hint');
  $('#searchInput').placeholder = t('top_search');
  $('#burger').title = t('ui_menu');
  $('#themeBtn').title = t('ui_theme');
  $('#themeBtn').innerHTML = icon(B.theme === 'dark' ? 'sun' : 'moon');
  $('#langSeg').innerHTML = Object.keys(B.langs).map(c =>
    `<button type="button" data-lang="${c}" class="${c === B.lang ? 'on' : ''}" title="${esc(B.langs[c])}">${c === 'ar' ? 'ع' : c.toUpperCase()}</button>`).join('');
  $('#nav').innerHTML = PAGES.map(([id, ic, key]) =>
    `<button type="button" class="nav-item ${id === S.page ? 'active' : ''}" data-page="${id}" title="${esc(t(key))}">
       <span class="tile">${icon(ic)}</span><span class="nav-label">${esc(t(key))}</span></button>`).join('');
}

function setCompact() {
  const flag = S.compactManual ?? window.innerWidth < 1040;
  $('#app').classList.toggle('compact', flag);
}

/* ------------------------------------------------------------------ navigation */
const RENDER = {};
async function go(page, opts = {}) {
  S.page = page;
  const token = ++S.token;
  $$('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.page === page));
  $('#content').innerHTML = `<div class="loading">…</div>`;
  await RENDER[page](opts, () => token === S.token);
  if (token === S.token) { window.scrollTo(0, 0); $('#content').focus({preventScroll: true}); }
}
const head = (title, sub = '', actions = '') =>
  `<div class="page-head"><div><h1>${esc(title)}</h1>${sub ? `<p>${esc(sub)}</p>` : ''}</div><div class="head-actions">${actions}</div></div>`;
const btnHtml = (label, act, kind = '', ic = '', extra = '') =>
  `<button type="button" class="btn ${kind}" data-act="${act}" ${extra}>${ic ? icon(ic) : ''}${esc(label)}</button>`;

/* ------------------------------------------------------------------ dashboard */
function niceTop(maxv) {
  let top = Math.max(maxv, 1), step = 1;
  while (top / step > 5) step = '15'.includes(String(step)[0]) ? step * 2 : Math.floor(step * 5 / 2);
  return step * Math.ceil(top / step);
}
const fmtTick = v => String(Number(v.toFixed(2)));

RENDER.dashboard = async (_, live) => {
  const d = await api.dashboard();
  if (!live()) return;
  if (!(await ok(d))) return;
  const kdef = [['items', 'box', 'teal', 'm_items'], ['units', 'grid', 'yellow', 'm_units'],
                ['value', 'dollar', 'lilac', 'm_value'], ['alerts', 'alert', 'red', 'm_alerts']];
  const kpis = kdef.map(([k, ic, tone, label]) => {
    const o = d.kpis[k];
    const badge = o.badge ? `<span class="chip ${o.badge.kind === 'bad' && k === 'units' ? 'warn' : o.badge.kind}">${esc(o.badge.text)}</span>` : '';
    return `<div class="card kpi"><div class="top"><div class="glyph tone-${tone}">${icon(ic)}</div>${badge}</div>
      <div class="label">${esc(t(label))}</div><div class="value v-${tone}">${esc(o.value)}</div><div class="sub">${esc(o.sub)}</div></div>`;
  }).join('');

  // stock health donut
  const R = 54, C = 2 * Math.PI * R, h = d.health;
  const segs = [['var(--teal-fill)', h.ok], ['var(--yellow)', h.low], ['var(--red)', h.out]];
  let off = 0;
  const arcs = h.total ? segs.map(([col, p]) => {
    const len = C * p / 100, el = `<circle class="arc" cx="68" cy="68" r="${R}" fill="none" stroke="${col}" stroke-width="15"
      data-len="${len}" stroke-dasharray="0 ${C}" stroke-dashoffset="${-off}" style="transition:stroke-dasharray .8s cubic-bezier(.2,.8,.2,1)"/>`;
    off += len; return p ? el : '';
  }).join('') : '';
  const donut = `<div class="donut"><svg viewBox="0 0 136 136"><circle cx="68" cy="68" r="${R}" fill="none" stroke="var(--cream)" stroke-width="15"/>${arcs}</svg>
    <div class="center"><div><b>${h.total ? h.ok + '%' : '—'}</b><small>${esc(t('health_center'))}</small></div></div></div>`;
  const legend = [['health_ok', 'var(--teal-fill)', h.ok], ['health_low', 'var(--yellow)', h.low], ['health_out', 'var(--red)', h.out]]
    .map(([k, c, v]) => `<div class="row"><span class="sw" style="background:${c}"></span>${esc(t(k))}<b>${v}%</b></div>`).join('');

  // 14-day trend
  const top = niceTop(Math.max(...d.trend.flatMap(x => [x.in, x.out])));
  const any = d.trend.some(x => x.in || x.out);
  const ticks = [0, 1, 2, 3, 4].map(i => fmtTick(top * i / 4));
  const every = d.trend.length > 10 ? 2 : 1;
  const trend = any ? `<div class="trend"><div class="yaxis">${ticks.map(v => `<span>${v}</span>`).join('')}</div>
    <div class="plot"><div class="grid-lines">${ticks.map(() => '<i></i>').join('')}</div>
    <div class="cols">${d.trend.map(x => `<div class="col">
      <span class="tip">${esc(x.label)} · ${esc(t('legend_in'))} ${x.in} · ${esc(t('legend_out'))} ${x.out}</span>
      <div class="bar b-in" style="height:${x.in / top * 100}%"></div><div class="bar b-out" style="height:${x.out / top * 100}%"></div></div>`).join('')}</div>
    <div class="xlabels">${d.trend.map((x, i) => `<span>${i % every === 0 || i === d.trend.length - 1 ? esc(x.label) : ''}</span>`).join('')}</div></div></div>`
    : `<div class="trend"><div class="empty-note">${esc(t('trend_empty'))}</div></div>`;

  const insTone = {out: ['red', 'alert'], low: ['yellow', 'trend'], top: ['teal', 'trend'], idle: ['lilac', 'clock'], ok: ['teal', 'check']};
  const insights = d.insights.map(i => `<div class="ins"><div class="g tone-${insTone[i.kind][0]}">${icon(insTone[i.kind][1])}</div><div class="t">${esc(i.text)}</div></div>`).join('');

  const alerts = d.alerts.length ? `<div class="table-wrap" style="max-height:320px"><table><thead><tr><th>${esc(t('col_item'))}</th><th>${esc(t('col_loc'))}</th>
    <th class="num">${esc(t('col_qty'))}</th><th class="num">${esc(t('col_min'))}</th><th></th></tr></thead><tbody>${d.alerts.map(a =>
    `<tr data-act="edit" data-id="${a.id}" style="cursor:pointer"><td><b>${esc(a.name)}</b></td><td>${esc(a.loc)}</td>
     <td class="num ${a.state === 'out' ? 'qty-out' : 'qty-low'}">${esc(a.qty)}</td><td class="num">${esc(a.min)}</td>
     <td class="num"><button type="button" class="btn small" data-act="move" data-id="${a.id}" style="color:var(--red-ink);border-color:var(--red)">${esc(t('mv_in'))}</button></td></tr>`).join('')}
    </tbody></table></div>` : `<div class="muted">${esc(t('ins_ok'))}</div>`;

  const maxu = Math.max(1, ...d.sections.map(s => s.u));
  const sections = d.sections.map(s => `<div class="sect"><b>${esc(s.s)}</b><div class="track"><div class="fill" style="width:${s.u ? Math.max(3, s.u / maxu * 100) : 0}%"></div></div>
    <span class="meta">${s.n} • ${esc(s.u_text)}</span></div>`).join('');

  const recent = d.recent.length ? `<div class="table-wrap" style="max-height:320px"><table><thead><tr><th>${esc(t('col_time'))}</th><th>${esc(t('col_item'))}</th>
    <th>${esc(t('col_type'))}</th><th class="num">${esc(t('col_qty'))}</th></tr></thead><tbody>${d.recent.map(m =>
    `<tr><td class="muted" style="white-space:nowrap">${esc(m.time)}</td><td>${esc(m.name)}</td><td class="${m.kind ? 'kind-' + m.kind : ''}">${esc(m.type)}</td><td class="num">${esc(m.qty)}</td></tr>`).join('')}
    </tbody></table></div>` : `<div class="muted">${esc(t('ui_nodata'))}</div>`;

  const remind = d.remind
    ? `<section class="status"><div class="glyph tone-red">${icon('alert')}</div><div class="msg"><b>${esc(t('dash_remind', d.remind.count))}</b>
        <small>${esc(t('dash_remind_sub', d.remind.names))}</small></div>${btnHtml(t('dash_view_low'), 'low-stock', 'primary')}</section>`
    : `<section class="status"><div class="glyph tone-teal">${icon('check')}</div><div class="msg"><b>${esc(t('dash_all_ok'))}</b><small>${esc(t('dash_all_ok_sub'))}</small></div></section>`;

  const menu = `<div class="menu"><button type="button" class="btn" data-act="menu" aria-haspopup="true">${icon('more')}</button>
    <div class="pop" hidden><button type="button" data-act="labels-all">${icon('print')}${esc(t('qa_labels'))}</button>
    <button type="button" data-act="export">${icon('down')}${esc(t('qa_export'))}</button><button type="button" data-act="backup">${icon('archive')}${esc(t('qa_backup'))}</button></div></div>`;

  $('#content').innerHTML = head(t('dash_title'), t('dash_sub'),
    btnHtml(t('qa_scan'), 'go-scan', '', 'scan') + btnHtml(t('qa_move'), 'go-movement', '', 'mv') +
    btnHtml(t('btn_add_item').replace(/^＋\s*/, ''), 'new-item', 'primary', 'plus') + menu) +
    `<section class="grid kpis">${kpis}</section>
    <section class="grid g-mid">
      <div class="card"><div class="card-head"><div><h3>${esc(t('dash_health'))}</h3><p class="sub">${esc(t('dash_health_sub'))}</p></div></div>
        <div class="donut-wrap">${donut}<div class="legend">${legend}</div></div></div>
      <div class="card"><div class="card-head"><div><h3>${esc(t('card_trend'))}</h3></div>
        <div class="legend-inline"><span><i class="sw" style="background:var(--teal-fill)"></i>${esc(t('legend_in'))}</span><span><i class="sw" style="background:var(--red)"></i>${esc(t('legend_out'))}</span></div></div>${trend}</div>
    </section>
    <section class="grid g-two">
      <div class="card"><div class="card-head"><div><h3>${esc(t('card_insights'))}</h3><p class="sub">${esc(t('ins_sub'))}</p></div></div>${insights}</div>
      <div class="card"><div class="card-head"><h3>${esc(t('card_alerts'))}</h3><button type="button" class="link" data-act="low-stock">${esc(t('dash_view_all'))} ${B.rtl ? '‹' : '›'}</button></div>${alerts}</div>
    </section>
    <section class="grid g-eq">
      <div class="card"><div class="card-head"><h3>${esc(t('card_sections'))}</h3></div>${sections}</div>
      <div class="card"><div class="card-head"><h3>${esc(t('card_recent'))}</h3><button type="button" class="link" data-act="go-movement">${esc(t('dash_view_all'))} ${B.rtl ? '‹' : '›'}</button></div>${recent}</div>
    </section>${remind}`;
  requestAnimationFrame(() => requestAnimationFrame(() => $$('.arc').forEach(a => a.setAttribute('stroke-dasharray', `${a.dataset.len} ${C}`))));
};

/* ------------------------------------------------------------------ inventory */
const INV_COLS = [['code', 'h_code'], ['name', 'h_name'], ['category', 'h_category'], ['engine', 'h_engine'], ['location', 'h_location'],
                  ['condition', 'h_condition'], ['qty', 'h_qty'], ['buy', 'h_buy'], ['sell', 'h_sell']];

RENDER.inventory = async (opts, live) => {
  if (opts.location !== undefined) Object.assign(S.inv, {search: '', location: opts.location, condition: '', low_only: false});
  if (opts.low) Object.assign(S.inv, {search: '', location: '', condition: '', low_only: true});
  if (opts.search !== undefined) Object.assign(S.inv, {search: opts.search, location: '', condition: '', low_only: false});
  const f = S.inv;
  const opt = (list, cur) => list.map(o => `<option value="${esc(o.value)}" ${o.value === cur ? 'selected' : ''}>${esc(o.label)}</option>`).join('');
  $('#content').innerHTML = head(t('inv_title'), '',
    btnHtml(t('btn_add_item').replace(/^＋\s*/, ''), 'new-item', 'primary', 'plus') + btnHtml(t('btn_labels'), 'labels', '', 'print') + btnHtml(t('btn_export'), 'export', '', 'down')) + `
    <div class="card"><div class="filters">
      <label class="fld">${esc(t('lbl_search').replace(/:$/, ''))}<div class="row-inline"><input class="in" id="fSearch" type="search" autocomplete="off" value="${esc(f.search)}">
        <button type="button" class="btn" data-act="clear-search" title="${esc(t('ui_clear'))}">${icon('x')}</button></div></label>
      <label class="fld">${esc(t('h_location'))}<select class="in" id="fLoc">${opt(B.locations, f.location)}</select></label>
      <label class="fld">${esc(t('h_condition'))}<select class="in" id="fCond">${opt([{value: '', label: t('all_conditions')}, ...B.conditions], f.condition)}</select></label>
    </div><div class="checks"><label class="check"><input class="cb" type="checkbox" id="fLow" ${f.low_only ? 'checked' : ''}>${esc(t('low_only'))}</label>
      <label class="check"><input class="cb" type="checkbox" id="fArch" ${f.archived ? 'checked' : ''}>${esc(t('show_archived'))}</label></div></div>
    <div class="card" style="padding:8px"><div class="table-wrap" id="invWrap" style="max-height:calc(100vh - 360px);min-height:260px"></div></div>
    <div><p class="sub" id="invSummary" style="margin:0 0 10px"></p><div class="actions">
      ${btnHtml(t('btn_edit'), 'edit-sel', 'primary', 'edit')}${btnHtml(t('btn_move'), 'move-sel', '', 'mv')}${btnHtml(t('btn_archive'), 'archive-sel', '', 'archive')}${btnHtml(t('btn_delete'), 'delete-sel', 'danger', 'trash')}</div></div>`;
  await loadInventory(live);
};

async function loadInventory(live = () => true) {
  const r = await api.inventory(S.inv);
  if (!live() || S.page !== 'inventory') return;
  if (!(await ok(r))) return;
  S.invRows = r.rows;
  const ids = new Set(r.rows.map(x => String(x.id)));
  S.checked = new Set([...S.checked].filter(i => ids.has(String(i))));
  if (!ids.has(String(S.selected))) S.selected = null;
  $('#invSummary').textContent = r.summary;
  drawInventory();
}

function drawInventory() {
  const wrap = $('#invWrap');
  if (!wrap) return;
  const f = S.inv, rows = S.invRows, shown = rows.slice(0, S.invLimit);
  const arrow = c => f.sort === c ? `<span class="arrow ${f.desc ? 'desc' : ''}">${icon('sort')}</span>` : '';
  const numCols = ['qty', 'buy', 'sell'];
  const allChecked = shown.length && shown.every(r => S.checked.has(r.id));
  wrap.innerHTML = rows.length ? `<table><thead><tr><th style="width:36px"><input type="checkbox" class="cb" data-act="check-all" ${allChecked ? 'checked' : ''}></th>
    ${INV_COLS.map(([c, k]) => `<th class="sortable ${numCols.includes(c) ? 'num' : ''}" data-sort="${c}">${esc(t(k))} ${arrow(c)}</th>`).join('')}</tr></thead><tbody>
    ${shown.map(r => `<tr data-id="${r.id}" class="${r.state} ${S.selected === r.id ? 'sel' : ''}"><td><input type="checkbox" class="cb" data-check="${r.id}" ${S.checked.has(r.id) ? 'checked' : ''}></td>
      <td>${esc(r.code)}</td><td class="clip"><b>${esc(r.name)}</b></td><td class="clip">${esc(r.category)}</td><td class="clip">${esc(r.engine)}</td><td>${esc(r.location)}</td>
      <td>${esc(r.condition)}</td><td class="num ${r.state === 'out' ? 'qty-out' : r.state === 'low' ? 'qty-low' : ''}">${esc(r.qty)}</td><td class="num">${esc(r.buy)}</td><td class="num">${esc(r.sell)}</td></tr>`).join('')}
    </tbody></table>${rows.length > shown.length ? `<div style="text-align:center;padding:12px">${btnHtml(t('ui_show_more', rows.length - shown.length), 'more-rows')}</div>` : ''}`
    : `<div class="empty-note" style="padding:50px">${esc(t('ui_no_match'))}</div>`;
}

const selectedId = async () => {
  if (S.selected) return S.selected;
  await alertBox(t('sel_title'), t('sel_msg'));
  return null;
};

async function archiveItem(id) {
  let r = await api.toggle_archive(id, false);
  if (r.needs_confirm) {
    if (!(await confirmBox(r.title, r.message))) return;
    r = await api.toggle_archive(id, true);
  }
  if (!(await ok(r))) return;
  toast(r.message, 'ok');
  loadInventory();
}

/** Permanently delete items (ticked rows, else the clicked row). `after` runs once they are gone. */
async function deleteItems(ids, after) {
  if (!ids.length) { await alertBox(t('del_title'), t('del_pick')); return; }
  let r = await api.delete_items(ids, false);
  if (r.needs_confirm) {
    if (!(await confirmBox(r.title, r.message, 'danger', t('btn_delete')))) return;
    r = await api.delete_items(ids, true);
  }
  if (!(await ok(r))) return;
  toast(r.message, 'ok', 9000);
  S.checked.clear(); S.selected = null;
  after();
}

async function printLabels(ids) {
  if (!ids.length) { await alertBox(t('lbl_nothing_t'), t('lbl_nothing')); return; }
  const sel = (name, list) => `<select class="in" name="${name}">${list.map(o => `<option value="${esc(o.value ?? o)}">${esc(o.label ?? o)}</option>`).join('')}</select>`;
  const res = await dialog({
    title: t('lbl_title_msg') + ' — ' + t('lbl_dialog', ids.length), wide: true,
    html: `<div class="stack" style="margin-top:6px"><label class="fld">${esc(t('lbl_layout'))}${sel('layout', B.layouts)}</label>
      <label class="fld">${esc(t('lbl_size'))}<select class="in" name="size">${B.label_sizes.map(s => `<option ${s.startsWith('Medium') ? 'selected' : ''}>${esc(s)}</option>`).join('')}</select></label>
      <label class="fld">${esc(t('lbl_kind'))}${sel('kind', B.label_kinds)}</label>
      <label class="fld">${esc(t('lbl_copies'))}<input class="in" name="copies" type="number" min="1" max="50" value="1"></label>
      <label class="check"><input class="cb" type="checkbox" name="full">${esc(t('lbl_full'))}</label>
      <label class="check"><input class="cb" type="checkbox" name="prices">${esc(t('lbl_prices'))}</label>
      <p class="sub">${esc(t('lbl_hint'))}</p></div>`,
    buttons: [{label: t('btn_cancel'), value: null, cancel: true}, {label: t('lbl_open'), value: 'go', kind: 'primary', collect: true}]});
  if (!res || res.value !== 'go') return;
  let r = await api.print_labels(ids, res.form);
  if (r.needs_confirm) {
    if (!(await confirmBox(r.title, r.message))) return;
    r = await api.print_labels(ids, {...res.form, confirmed: true});
  }
  if (await ok(r)) toast(r.message, 'ok');
}

async function printFromInventory() {
  let ids = [...S.checked];
  if (!ids.length) {
    ids = S.invRows.map(r => r.id);
    if (!ids.length) { await alertBox(t('lbl_nothing_t'), t('lbl_nothing')); return; }
    if (!(await confirmBox(t('lbl_title_msg'), t('lbl_sel_none', ids.length)))) return;
  }
  printLabels(ids);
}

/* ------------------------------------------------------------------ item form */
const FIELDS = [['name', 'f_name', 'text'], ['name_ar', 'f_name_ar', 'tr'], ['category', 'f_category', 'text'], ['description', 'f_description', 'text'],
  ['engine_application', 'f_engine', 'text'], ['barcode', 'f_barcode', 'text'], ['section', 'f_section', 'section'], ['part', 'f_part', 'part'],
  ['condition', 'f_condition', 'condition'], ['unit', 'f_unit', 'unit'], ['quantity', 'f_qty', 'num'], ['min_stock', 'f_min', 'num'],
  ['purchase_price', 'f_buy', 'num'], ['selling_price', 'f_sell', 'num'], ['supplier', 'f_supplier', 'text'], ['notes', 'f_notes', 'text']];
const DEFAULTS = {section: 'A', part: '1', condition: 'New', unit: 'pcs', quantity: '0', min_stock: '0'};

RENDER.item = async (opts, live) => {
  let item = null, photo = '', svg = '';
  if (opts.id) {
    const r = await api.get_item(opts.id);
    if (!live()) return;
    if (!(await ok(r))) return go('inventory');
    item = r.item; photo = r.photo; svg = r.barcode_svg;
  }
  S.item = {id: item ? item.id : null, photoNew: null, photoRemove: false, photoCurrent: item ? item.photo_path : null, code: item ? item.item_code : ''};
  const sel = (key, list) => `<select class="in" id="f_${key}" data-loc>${list.map(o => {
    const v = o.value ?? o, l = o.label ?? o; return `<option value="${esc(v)}">${esc(l)}</option>`; }).join('')}</select>`;
  const cell = ([key, label, kind]) => {
    let ctl;
    if (kind === 'section') ctl = sel(key, B.sections);
    else if (kind === 'part') ctl = sel(key, B.parts);
    else if (kind === 'condition') ctl = sel(key, B.conditions);
    else if (kind === 'unit') ctl = sel(key, B.units);
    else if (kind === 'tr') ctl = `<div class="row-inline"><input class="in" id="f_${key}" ${B.lang === 'ar' ? 'dir="rtl"' : ''}><button type="button" class="btn small" data-act="translate">${icon('globe')}${esc(t('btn_translate'))}</button></div>`;
    else if (kind === 'num') ctl = `<input class="in" id="f_${key}" inputmode="decimal" autocomplete="off">`;
    else ctl = `<input class="in" id="f_${key}" autocomplete="off">`;
    return `<label class="fld">${esc(t(label))}${ctl}</label>`;
  };
  $('#content').innerHTML = head(item ? t('form_edit', item.item_code) : t('form_new'), '') +
    `<p class="sub" id="locPrev" style="margin-top:-8px"></p>
    <div class="form-layout"><div class="card"><div class="fields">${FIELDS.map(cell).join('')}</div></div>
      <div class="card"><p class="side-title">${esc(t('photo_title'))}</p><div class="photo" id="photoBox"></div>
        <div class="stack">${btnHtml(t('choose_photo'), 'choose-photo', 'block', 'img')}${btnHtml(t('remove_photo'), 'remove-photo', 'block')}</div>
        <p class="side-title" style="margin:16px 0 8px">${esc(t('bc_preview'))}</p><div class="bcprev" id="bcBox"></div></div></div>
    <div class="actions">${btnHtml(t('btn_save'), 'save-item', 'success', 'check')}${btnHtml(t('btn_clear'), 'clear-item')}
      ${btnHtml(t('btn_print_one'), 'print-one', '', 'print')}${item ? btnHtml(t('btn_delete'), 'delete-one', 'danger', 'trash') : ''}${btnHtml(t('btn_back'), 'go-inventory', 'ghost')}</div>`;
  for (const [key, , kind] of FIELDS) {
    const el = $('#f_' + key);
    let v = item ? item[key] : (DEFAULTS[key] ?? '');
    el.value = v ?? '';
    if (el.tagName === 'SELECT' && v && el.value !== String(v)) {       // value no longer in the list (old location)
      el.insertAdjacentHTML('afterbegin', `<option value="${esc(v)}">${esc(v)}</option>`);
      el.value = v;
    }
  }
  if (item) $('#f_quantity').disabled = true;
  $$('[data-loc]').forEach(el => el.addEventListener('change', updateLoc));
  setPhoto(photo);
  setBarcode(svg);
  updateLoc();
  if (!item) $('#f_name').focus();
};

function updateLoc() {
  const loc = ($('#f_section')?.value || '') + ($('#f_part')?.value || '');
  const el = $('#locPrev');
  if (el) el.textContent = t('loc_preview', loc) + (S.item.id ? t('loc_preview_edit') : '');
}
const setPhoto = uri => { const b = $('#photoBox'); if (b) b.innerHTML = uri ? `<img alt="" src="${uri}">` : esc(t('no_photo')); };
const setBarcode = svg => { const b = $('#bcBox'); if (b) b.innerHTML = svg ? `${svg}<small>${esc(S.item.code)}</small>` : esc(t('bc_none')); };

async function saveItem() {
  const v = {id: S.item.id, photo_path: S.item.photoNew, photo_remove: S.item.photoRemove, current_photo: S.item.photoCurrent, confirmed: []};
  FIELDS.forEach(([k]) => { v[k] = $('#f_' + k).value; });
  if (S.item.id) v.quantity = '0';
  $$('.in.bad').forEach(e => e.classList.remove('bad'));
  for (;;) {
    const r = await api.save_item(v);
    if (r.needs_confirm) {
      if (!(await confirmBox(r.title, r.message))) return;
      v.confirmed.push(r.needs_confirm);
      continue;
    }
    if (r.ok === false) {
      if (r.field && $('#f_' + r.field)) $('#f_' + r.field).classList.add('bad');
      await alertBox(r.title || t('ui_error'), r.error);
      if (r.field && $('#f_' + r.field)) $('#f_' + r.field).focus();
      return;
    }
    toast(r.message, 'ok');
    return go('inventory');
  }
}

/* ------------------------------------------------------------------ stock in / out */
const MOVES = () => B.move_types;
RENDER.movement = async (opts, live) => {
  S.mv.item = null;
  if (opts.id) {
    const r = await api.item_info(opts.id, 'Stock In');
    if (!live()) return;
    if (r.ok !== false) S.mv.item = {id: opts.id, label: r.label};
  }
  $('#content').innerHTML = head(t('mv_title'), t('mv_sub')) + `
    <div class="card"><div class="mv-form">
      <label class="fld">${esc(t('mv_item'))}<div class="combo"><input class="in" id="mvItem" autocomplete="off" role="combobox" aria-expanded="false"><div class="list" id="mvList" hidden></div></div></label>
      <label class="fld">${esc(t('mv_type'))}<select class="in" id="mvType">${MOVES().map(m => `<option value="${m.value}">${esc(m.label)}</option>`).join('')}</select></label>
      <label class="fld"><span id="mvQtyLbl">${esc(t('mv_qty'))}</span><input class="in" id="mvQty" inputmode="decimal" autocomplete="off"></label>
      <label class="fld">${esc(t('mv_price'))}<input class="in" id="mvPrice" inputmode="decimal" autocomplete="off"></label>
      <label class="fld">${esc(t('mv_reason'))}<input class="in" id="mvReason" autocomplete="off"></label>
    </div><div class="info-line" id="mvInfo">${esc(t('mv_pick'))}</div>
    <div class="actions" style="margin-top:14px">${btnHtml(t('mv_save'), 'save-move', 'primary', 'check')}</div></div>
    <div class="card"><div class="card-head"><h3>${esc(t('mv_history'))}</h3>
      <label class="check"><input class="cb" type="checkbox" id="mvOnly" ${S.mv.onlyItem ? 'checked' : ''}>${esc(t('mv_only'))}</label></div>
      <div class="table-wrap" id="mvHist" style="max-height:480px"></div></div>`;
  if (S.mv.item) $('#mvItem').value = S.mv.item.label;
  await refreshMoveInfo();
  await loadHistory(live);
  if (S.mv.item) $('#mvQty').focus(); else $('#mvItem').focus();
};

async function refreshMoveInfo() {
  const type = $('#mvType').value;
  $('#mvQtyLbl').textContent = type === 'Adjustment' ? t('mv_counted') : t('mv_qty');
  const box = $('#mvInfo');
  if (!S.mv.item) { box.textContent = t('mv_pick'); box.className = 'info-line'; return; }
  const r = await api.item_info(S.mv.item.id, type);
  if (!(await ok(r))) return;
  box.textContent = r.info;
  box.className = 'info-line ' + (r.state === 'out' ? 'out' : r.state === 'low' ? 'low' : '');
  $('#mvPrice').value = r.price;
}

async function loadHistory(live = () => true) {
  const r = await api.movements(S.mv.onlyItem && S.mv.item ? S.mv.item.id : null);
  if (!live() || !$('#mvHist')) return;
  if (!(await ok(r))) return;
  $('#mvHist').innerHTML = r.rows.length ? `<table><thead><tr><th>${esc(t('h_date'))}</th><th>${esc(t('h_code'))}</th><th>${esc(t('col_item'))}</th><th>${esc(t('h_move'))}</th>
    <th class="num">${esc(t('h_qty'))}</th><th>${esc(t('h_change'))}</th><th class="num">${esc(t('h_price'))}</th><th>${esc(t('h_reason'))}</th></tr></thead><tbody>
    ${r.rows.map(m => `<tr><td class="muted" style="white-space:nowrap">${esc(m.date)}</td><td>${esc(m.code)}</td><td class="clip">${esc(m.name)}</td>
    <td class="${m.kind ? 'kind-' + m.kind : ''}">${esc(m.type)}</td><td class="num">${esc(m.qty)}</td><td style="white-space:nowrap">${esc(m.change)}</td>
    <td class="num">${esc(m.price)}</td><td class="clip">${esc(m.reason)}</td></tr>`).join('')}</tbody></table>`
    : `<div class="empty-note" style="padding:40px">${esc(t('ui_nodata'))}</div>`;
}

let searchSeq = 0;
const searchItems = debounce(async () => {
  const input = $('#mvItem'), list = $('#mvList');
  if (!input) return;
  const mine = ++searchSeq;
  const r = await api.movement_items(S.mv.item && input.value === S.mv.item.label ? '' : input.value);
  if (r.ok === false || mine !== searchSeq || document.activeElement !== input) return;
  list.innerHTML = r.items.length ? r.items.map(i => `<div class="opt" role="option" data-id="${i.id}" data-label="${esc(i.label)}">${esc(i.label)}</div>`).join('')
    : `<div class="none">${esc(t('ui_no_match'))}</div>`;
  list.hidden = false; input.setAttribute('aria-expanded', 'true');
}, 120);

function closeCombo() { const l = $('#mvList'); if (l) l.hidden = true; $('#mvItem')?.setAttribute('aria-expanded', 'false'); }

async function pickMoveItem(id, label) {
  S.mv.item = {id: +id, label};
  $('#mvItem').value = label;
  searchSeq++; closeCombo();
  await refreshMoveInfo();
  if (S.mv.onlyItem) loadHistory();
  $('#mvQty').focus();
}

async function saveMove() {
  const r = await api.save_movement({item_id: S.mv.item?.id, type: $('#mvType').value, qty: $('#mvQty').value, price: $('#mvPrice').value, reason: $('#mvReason').value});
  if (!(await ok(r))) return;
  $('#mvQty').value = ''; $('#mvReason').value = '';
  toast(r.message, r.warn ? 'bad' : 'ok', 8000);
  await refreshMoveInfo();
  loadHistory();
  $('#mvQty').focus();
}

/* ------------------------------------------------------------------ scan */
RENDER.scan = async () => {
  S.scan.itemId = null;
  $('#content').innerHTML = head(t('scan_title'), t('scan_sub')) + `
    <div class="card"><form id="scanForm" class="stack"><div class="row-inline" style="flex-wrap:wrap">
      <input class="in scan-input" id="scanText" autocomplete="off" style="flex:1;min-width:220px">
      <button class="btn primary" type="submit">${icon('search')}${esc(t('scan_lookup_btn'))}</button>
      ${btnHtml(t('scan_camera').replace(/^\S*\s/, ''), 'scan-camera', '', 'cam')}${btnHtml(t('scan_image').replace('…', ''), 'scan-image', '', 'img')}</div>
      <div class="row-inline" style="align-items:center;flex-wrap:wrap;gap:12px"><span class="muted">${esc(t('scan_mode'))}</span>
        <select class="in" id="scanMode" style="max-width:220px"><option value="lookup">${esc(t('scan_lookup'))}</option>
        ${MOVES().filter(m => m.value !== 'Adjustment').map(m => `<option value="${m.value}">${esc(m.label)}</option>`).join('')}</select>
        <span class="muted">${esc(t('scan_qtyper'))}</span><input class="in" id="scanQty" type="number" min="1" value="1" style="max-width:110px"></div>
      <p class="sub" style="margin:0">${esc(t('scan_mode_hint'))}</p></form></div>
    <div class="form-layout"><div class="card" id="scanMain"></div>
      <div class="card"><div class="photo" id="scanPhoto">${esc(t('no_photo'))}</div><div class="stack">
        ${btnHtml(t('btn_move'), 'scan-move', 'primary block', 'mv', 'disabled')}${btnHtml(t('btn_edit'), 'scan-edit', 'block', 'edit', 'disabled')}${btnHtml(t('btn_print_one'), 'scan-print', 'block', 'print', 'disabled')}</div></div></div>`;
  showScan(null);
  $('#scanText').focus();
};

function showScan(res) {
  const main = $('#scanMain');
  if (!main) return;
  const set = (sel, dis) => $$('[data-act^="scan-"]').forEach(b => { if (['scan-move', 'scan-edit', 'scan-print'].includes(b.dataset.act)) b.disabled = dis(b.dataset.act); });
  if (!res) {
    main.innerHTML = `<h2 class="scan-head muted">${esc(t('scan_wait'))}</h2>`;
    set(null, () => true);
    return;
  }
  S.scan.itemId = res.item_id;
  main.innerHTML = `<h2 class="scan-head">${esc(res.head)}</h2>${res.flash ? `<div class="flash ${res.flash_ok ? 'ok' : 'bad'}">${esc(res.flash)}</div>` : ''}
    <dl class="scan-grid">${res.rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl>`;
  const ph = $('#scanPhoto');
  ph.innerHTML = res.photo ? `<img alt="" src="${res.photo}">` : esc(t('no_photo'));
  set(null, act => !res.found || (act === 'scan-move' && !res.can_move));
  if (res.found) toast(res.message, res.flash && !res.flash_ok ? 'bad' : 'ok', 3500);
}
window.onCameraScan = res => { if (S.page === 'scan') showScan(res); };

async function doScan(text) {
  text = (text || '').trim();
  const input = $('#scanText');
  if (input) input.value = '';
  if (text) {
    const r = await api.scan(text, $('#scanMode').value, $('#scanQty').value);
    if (await ok(r)) showScan(r);
  }
  input?.focus();
}

/* ------------------------------------------------------------------ storage map */
const cellHtml = c => `<button type="button" class="cell ${c.n ? 'occ' : ''}" data-act="open-loc" data-code="${esc(c.code)}"><b>${esc(c.code)}</b><span>${c.n} ${esc(t('ui_items_unit'))}</span><span>${esc(c.units)} ${esc(t('ui_units_unit'))}</span></button>`;
RENDER.locations = async (_, live) => {
  const r = await api.locations();
  if (!live()) return;
  if (!(await ok(r))) return;
  $('#content').innerHTML = head(t('map_title'), t('map_sub')) + `<section class="grid map">${r.sections.map(s => `<div class="card">
    <p class="sec-title">${esc(t('section_big', s.section))}</p><div class="cells">${s.cells.map(cellHtml).join('')}
    </div></div>`).join('')}</section>` + (r.legacy.length ? `<div class="card"><p class="sec-title">${esc(t('loc_legacy'))}</p>
    <p class="sub" style="margin:-4px 0 10px">${esc(t('loc_legacy_hint'))}</p><div class="cells">${r.legacy.map(cellHtml).join('')}</div></div>` : '');
};

/* ------------------------------------------------------------------ settings */
RENDER.settings = async () => {
  const pills = (list, cur, act) => `<div class="switch-row">${list.map(([v, l]) => `<button type="button" class="pill ${v === cur ? 'on' : ''}" data-act="${act}" data-v="${v}">${esc(l)}</button>`).join('')}</div>`;
  $('#content').innerHTML = head(t('set_title'), t('set_sub')) + `
    <div class="card"><div class="set-row"><b>${esc(t('set_lang'))}</b>${pills(Object.entries(B.langs), B.lang, 'set-lang')}</div>
      <div class="set-row"><b>${esc(t('set_theme'))}</b>${pills([['light', t('theme_light')], ['dark', t('theme_dark')]], B.theme, 'set-theme')}</div>
      <p class="sub">${esc(t('set_rtl'))}</p></div>
    <div class="card"><h3>${esc(t('set_translate'))}</h3><p class="sub" style="margin-bottom:12px">${esc(t('set_translate_hint'))}</p>${btnHtml(t('btn_translate'), 'bulk-translate', 'primary', 'globe')}</div>
    <div class="card"><p class="pre" style="margin:0 0 12px;color:var(--muted)">${esc(t('data_info', B.data_dir, B.backup_name, B.keep_backups))}</p>
      <div class="actions">${btnHtml(t('qa_export'), 'export', '', 'down')}${btnHtml(t('qa_backup'), 'backup', '', 'archive')}</div></div>
    <div class="card"><h3>${esc(t('upd_title'))}</h3><p class="sub" style="margin-bottom:10px">${esc(t('upd_version', B.version))}</p>
      <label class="check" style="margin-bottom:12px"><input class="cb" type="checkbox" id="autoUpd" ${B.auto_update ? 'checked' : ''}>${esc(t('upd_auto'))}</label>
      <div>${btnHtml(t('upd_check'), 'check-updates')}</div></div>`;
};

async function checkUpdates(manual) {
  const r = await api.check_updates(manual);
  if (r.ok === false) { if (manual) await ok(r); return; }
  if (r.status === 'new') {
    toast(r.toast, '', 8000);
    if (await confirmBox(r.title, r.message)) api.open_url(r.url);
  } else if (manual && r.message) await alertBox(r.title, r.message);
}

async function bulkTranslate() {
  const p = await api.bulk_translate_prepare();
  if (!(await ok(p))) return;
  if (!p.count) { await alertBox(t('tr_title'), p.message); return; }
  if (!(await confirmBox(p.title, p.message))) return;
  await api.bulk_translate_start();
  const timer = setInterval(async () => {
    const s = await api.bulk_translate_status();
    if (s.message && !s.finished) toast(s.message, '', 1500);
    if (s.finished) {
      clearInterval(timer);
      if (s.error) await alertBox(s.title, s.error); else await alertBox(s.title, s.message);
    }
  }, 600);
}

async function exportExcel() {
  const r = await api.export_excel();
  if (r.cancelled) return;
  if (await ok(r)) toast(r.message, 'ok');
}
async function backupAll() {
  const r = await api.backup_all();
  if (r.cancelled) return;
  if (await ok(r)) { toast(r.message, 'ok'); await alertBox(r.title, r.detail); }
}

/* ------------------------------------------------------------------ language / theme */
async function setLanguage(code) {
  if (code === B.lang) return;
  const b = await api.set_language(code);
  if (b.ok === false) return ok(b);
  B = b; applyShell(); go(S.page, S.page === 'item' && S.item.id ? {id: S.item.id} : {});
}
async function setTheme(name) {
  B.theme = name;
  document.documentElement.dataset.theme = name;
  $('#themeBtn').innerHTML = icon(name === 'dark' ? 'sun' : 'moon');
  api.set_theme(name);
  if (S.page === 'settings') go('settings');
}

/* ------------------------------------------------------------------ click actions */
const ACT = {
  'new-item': () => go('item'),
  'go-inventory': () => go('inventory'),
  'go-scan': () => go('scan'),
  'go-movement': () => go('movement'),
  'low-stock': () => go('inventory', {low: true}),
  'edit': el => go('item', {id: +el.dataset.id}),
  'move': el => go('movement', {id: +el.dataset.id}),
  'menu': el => { const p = el.parentElement.querySelector('.pop'); p.hidden = !p.hidden; },
  'labels-all': async () => { await go('inventory'); printFromInventory(); },
  'labels': printFromInventory,
  'export': exportExcel, 'backup': backupAll,
  'clear-search': () => { S.inv.search = ''; $('#fSearch').value = ''; loadInventory(); $('#fSearch').focus(); },
  'more-rows': () => { S.invLimit += 300; drawInventory(); },
  'edit-sel': async () => { const id = await selectedId(); if (id) go('item', {id}); },
  'move-sel': async () => { const id = await selectedId(); if (id) go('movement', {id}); },
  'archive-sel': async () => { const id = await selectedId(); if (id) archiveItem(id); },
  'delete-sel': () => deleteItems(S.checked.size ? [...S.checked] : S.selected ? [S.selected] : [], () => loadInventory()),
  'delete-one': () => deleteItems([S.item.id], () => go('inventory')),
  'check-all': el => { const shown = S.invRows.slice(0, S.invLimit); shown.forEach(r => el.checked ? S.checked.add(r.id) : S.checked.delete(r.id)); drawInventory(); },
  'translate': async () => {
    const r = await api.translate_name($('#f_name').value);
    if (await ok(r)) $('#f_name_ar').value = r.text;
  },
  'choose-photo': async () => {
    if (!B.desktop) return toast(t('ui_dev_only'));
    const r = await api.choose_photo();
    if (!(await ok(r)) || !r.path) return;
    S.item.photoNew = r.path; S.item.photoRemove = false; setPhoto(r.photo);
  },
  'remove-photo': () => { S.item.photoNew = null; S.item.photoRemove = true; setPhoto(''); },
  'save-item': saveItem,
  'clear-item': () => go('item'),
  'print-one': async () => { if (!S.item.id) return alertBox(t('lbl_title_msg'), t('lbl_save_first')); printLabels([S.item.id]); },
  'save-move': saveMove,
  'scan-camera': async () => { const r = await api.camera_scan($('#scanMode').value, $('#scanQty').value); if (r.ok === false) await ok(r); $('#scanText')?.focus(); },
  'scan-image': async () => {
    if (!B.desktop) return toast(t('ui_dev_only'));
    const r = await api.scan_image($('#scanMode').value, $('#scanQty').value);
    if (!r.cancelled && await ok(r)) showScan(r);
  },
  'scan-move': () => S.scan.itemId && go('movement', {id: S.scan.itemId}),
  'scan-edit': () => S.scan.itemId && go('item', {id: S.scan.itemId}),
  'scan-print': () => S.scan.itemId && printLabels([S.scan.itemId]),
  'open-loc': el => go('inventory', {location: 'loc:' + el.dataset.code}),
  'set-lang': el => setLanguage(el.dataset.v),
  'set-theme': el => setTheme(el.dataset.v),
  'bulk-translate': bulkTranslate,
  'check-updates': () => checkUpdates(true),
};

document.addEventListener('click', e => {
  if (!e.target.closest('.menu')) $$('.menu .pop').forEach(p => p.hidden = true);
  if (!e.target.closest('.combo')) closeCombo();
  const nav = e.target.closest('[data-page]');
  if (nav) return go(nav.dataset.page);
  const lang = e.target.closest('[data-lang]');
  if (lang) return setLanguage(lang.dataset.lang);
  const opt = e.target.closest('.combo .opt');
  if (opt) return pickMoveItem(opt.dataset.id, opt.dataset.label);
  const sortTh = e.target.closest('th[data-sort]');
  if (sortTh) { const c = sortTh.dataset.sort; S.inv.desc = S.inv.sort === c ? !S.inv.desc : false; S.inv.sort = c; return loadInventory(); }
  const chk = e.target.closest('[data-check]');
  if (chk) { const id = +chk.dataset.check; chk.checked ? S.checked.add(id) : S.checked.delete(id); return; }
  const act = e.target.closest('[data-act]');
  if (act && ACT[act.dataset.act]) {
    if (act.dataset.act === 'check-all') return ACT['check-all'](act);
    e.stopPropagation();
    return ACT[act.dataset.act](act);
  }
  const row = e.target.closest('#invWrap tbody tr');
  if (row) {
    S.selected = +row.dataset.id;
    $$('#invWrap tbody tr').forEach(r => r.classList.toggle('sel', +r.dataset.id === S.selected));
  }
});
document.addEventListener('dblclick', e => {
  const row = e.target.closest('#invWrap tbody tr');
  if (row && !e.target.closest('input')) go('item', {id: +row.dataset.id});
});

document.addEventListener('input', e => {
  const id = e.target.id;
  if (id === 'fSearch') { S.inv.search = e.target.value; reloadInv(); }
  else if (id === 'mvItem') { if (S.mv.item && e.target.value !== S.mv.item.label) { S.mv.item = null; } searchItems(); }
});
document.addEventListener('change', e => {
  const id = e.target.id;
  if (id === 'fLoc') { S.inv.location = e.target.value; loadInventory(); }
  else if (id === 'fCond') { S.inv.condition = e.target.value; loadInventory(); }
  else if (id === 'fLow') { S.inv.low_only = e.target.checked; loadInventory(); }
  else if (id === 'fArch') { S.inv.archived = e.target.checked; loadInventory(); }
  else if (id === 'mvType') refreshMoveInfo();
  else if (id === 'mvOnly') { S.mv.onlyItem = e.target.checked; loadHistory(); }
  else if (id === 'autoUpd') { B.auto_update = e.target.checked; api.set_auto_update(e.target.checked); }
});
const reloadInv = debounce(() => loadInventory(), 200);

document.addEventListener('focusin', e => { if (e.target.id === 'mvItem') searchItems(); });
document.addEventListener('keydown', e => {
  if (e.target.id === 'mvItem') {
    const list = $('#mvList');
    if (e.key === 'Enter') {
      e.preventDefault();
      const first = $('.opt.hl', list) || $('.opt', list);
      if (first && !list.hidden) pickMoveItem(first.dataset.id, first.dataset.label);
    } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      const opts = $$('.opt', list); if (!opts.length) return;
      let i = opts.findIndex(o => o.classList.contains('hl'));
      opts.forEach(o => o.classList.remove('hl'));
      i = e.key === 'ArrowDown' ? (i + 1) % opts.length : (i - 1 + opts.length) % opts.length;
      opts[i].classList.add('hl'); opts[i].scrollIntoView({block: 'nearest'});
    } else if (e.key === 'Escape') closeCombo();
  }
  if (e.ctrlKey || e.metaKey) {
    const k = e.key.toLowerCase();
    if (k === 'n') { e.preventDefault(); go('item'); }
    else if (k === 'k') { e.preventDefault(); $('#searchInput').focus(); $('#searchInput').select(); }
    else if (k === 'f') { e.preventDefault(); go('inventory').then(() => $('#fSearch')?.focus()); }
    else if (k === 's' && S.page === 'item') { e.preventDefault(); saveItem(); }
  }
});
document.addEventListener('submit', e => {
  if (e.target.id === 'scanForm') { e.preventDefault(); doScan($('#scanText').value); }
});

$('#searchForm').addEventListener('submit', e => {
  e.preventDefault();
  go('inventory', {search: $('#searchInput').value.trim()});
});
$('#burger').addEventListener('click', () => { S.compactManual = !$('#app').classList.contains('compact'); setCompact(); });
$('#themeBtn').addEventListener('click', () => setTheme(B.theme === 'dark' ? 'light' : 'dark'));
window.addEventListener('resize', debounce(setCompact, 90));

/* ------------------------------------------------------------------ start */
(async function start() {
  await whenReady();
  const b = await api.bootstrap();
  if (b.ok === false) { document.body.innerHTML = `<pre style="padding:20px">${esc(b.error)}</pre>`; return; }
  B = b;
  applyShell(); setCompact();
  await go('dashboard');
  setTimeout(() => checkUpdates(false), 3000);
})();
})();
