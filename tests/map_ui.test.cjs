const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../src/personal_warehouse/webui/static/app.js'), 'utf8');
const section = source.slice(source.indexOf('const MAP_ROT'), source.indexOf('function mapFlat'));

function setup(inventory) {
  const elements = [];
  const status = {};
  const context = vm.createContext({
    S: {page: 'locations'}, api: {inventory}, esc: value => String(value),
    t: (key, value) => `${key}:${value}`, $: () => status, $$: () => elements,
    ok: async () => false,
  });
  vm.runInContext(section + ';globalThis.state=MAP;globalThis.search=mapSearch;globalThis.matches=mapMatches;globalThis.badges=mapStockBadges;', context);
  context.state.data = {sections: [{cells: [{code: 'A1', n: 2, low: 1}, {code: 'A2', n: 0, low: 0}]}], legacy: []};
  return context;
}

test('filters intersect search and stock state without removing locations', () => {
  const context = setup();
  context.state.filter = 'empty';
  assert.equal(context.matches({code: 'A1', n: 1}), false);
  assert.equal(context.matches({code: 'A2', n: 0}), true);
  context.state.matches = new Set(['A1']);
  assert.equal(context.matches({code: 'A2', n: 0}), false);
  context.state.filter = 'low';
  assert.equal(context.matches({code: 'A1', n: 2, low: 1}), true);
});

test('direct location lookup can highlight an empty cell', async () => {
  const context = setup(async () => ({ok: true, rows: []}));
  context.state.query = 'a2';
  await context.search();
  assert.equal(context.state.matches.has('A2'), true);
  context.state.query = '';
  await context.search();
  assert.equal(context.state.matches, null);
});

test('warning and out states have separate symbols, labels and filters', () => {
  const context = setup();
  const mixed = {code: 'A1', n: 2, low: 2, warning: 1, out: 1};
  const markup = context.badges(mixed);
  assert.match(markup, /stock-warning.*▲/);
  assert.match(markup, /stock-out.*⊗/);
  assert.match(markup, /map_warning_count:1/);
  assert.match(markup, /map_out_count:1/);
  context.state.filter = 'warning';
  assert.equal(context.matches(mixed), true);
  assert.equal(context.matches({...mixed, warning: 0}), false);
  context.state.filter = 'out';
  assert.equal(context.matches(mixed), true);
  assert.equal(context.matches({...mixed, out: 0}), false);
  assert.equal(context.badges({warning: 0, out: 0}), '');
});

test('older search responses cannot overwrite newer matches', async () => {
  const pending = [];
  const context = setup(() => new Promise(resolve => pending.push(resolve)));
  context.state.query = 'first';
  const first = context.search();
  context.state.query = 'second';
  const second = context.search();
  pending[1]({ok: true, rows: [{location: 'A2'}]});
  await second;
  pending[0]({ok: true, rows: [{location: 'A1'}]});
  await first;
  assert.deepEqual(Array.from(context.state.matches), ['A2']);
});
