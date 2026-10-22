// node --test viewers/cluster-review/model.test.mjs
// Pure board logic: comparison, prepared corrections, staleness. No DOM, no network.
import test from 'node:test';
import assert from 'node:assert/strict';
import {compare, prepareCorrection, isStale, signalsFor, handoff, sourceLabel} from './model.mjs';

const review = {
  contract: 'cluster-review.v1', draft: true,
  source: {mode: 'supplied', synthetic: true, server: 'opportunity-engine-mock', captured_at: '2026-10-21T18:00:00+00:00'},
  coverage: {problems_listed: 3, problems_total: 3, failed: []},
  problems: [
    {problem_id: 'A', title: 'Renewal quotes', personas: [{name: 'AE', confidence: 0.9}], workflow_tags: null,
     evidence: [{provenance_reference: 'gong:1'}, {provenance_reference: 'zendesk:2'}], originating_sources: ['gong:1']},
    {problem_id: 'B', title: 'Quote templates', personas: [{name: 'AE', confidence: 0.8}], workflow_tags: null,
     evidence: [{provenance_reference: 'gong:1'}], originating_sources: ['gong:1']},
    {problem_id: 'C', title: 'Triage', personas: [{name: 'Agent', confidence: 0.7}, {name: 'Admin', confidence: 0.6}], workflow_tags: null,
     evidence: [{provenance_reference: 'zendesk:9'}, {provenance_reference: 'gong:5'}], originating_sources: []},
  ],
  signals: [{kind: 'shared_evidence', problems: ['A', 'B'], refs: ['gong:1']}, {kind: 'shared_persona', problems: ['A', 'B'], refs: ['AE']}],
  suggestions: [
    {id: 's1', kind: 'merge', status: 'suggested', basis: 'I', problems: ['A', 'B'], rationale: 'same ask', evidence: {A: ['gong:1'], B: ['gong:1']}},
    {id: 's2', kind: 'split', status: 'suggested', basis: 'I', problems: ['C'], rationale: 'two personas',
     sides: [{label: 'Agents', persona: 'Agent', evidence: ['zendesk:9']}, {label: 'Admins', persona: 'Admin', evidence: ['gong:5']}]},
  ],
  excerpts: [],
};

test('compare separates what two problems share from what each holds alone', () => {
  const c = compare(review, 'A', 'B');
  assert.deepEqual(c.shared_evidence, ['gong:1']);
  assert.deepEqual(c.shared_origins, ['gong:1']);
  assert.deepEqual(c.shared_personas, ['AE']);
  assert.deepEqual(c.only, {A: ['zendesk:2'], B: []});
});

test('a prepared merge is pending, unapplied, has no destination yet and keeps its evidence', () => {
  const c = prepareCorrection(review, 's1', '2026-10-21T19:00:00+00:00');
  assert.equal(c.status, 'pending');
  assert.equal(c.applied, false);
  assert.match(c.destination, /^TBD/);
  assert.deepEqual(c.evidence, {A: ['gong:1'], B: ['gong:1']});
  assert.equal(c.based_on_capture, review.source.captured_at);
  assert.equal(c.stale, false);
  assert.ok(c.before_applying.length >= 2);
});

test('a prepared split carries both sides', () => {
  const c = prepareCorrection(review, 's2', '2026-10-21T19:00:00+00:00');
  assert.equal(c.kind, 'split');
  assert.deepEqual(c.sides.map(s => s.evidence), [['zendesk:9'], ['gong:5']]);
});

test('preparing from an old capture marks the correction stale', () => {
  const c = prepareCorrection(review, 's1', '2026-10-23T19:00:00+00:00');
  assert.equal(c.stale, true);
  assert.ok(c.before_applying.some(step => /re-read/i.test(step)));
});

test('staleness is measured from the capture, with a 24-hour default', () => {
  assert.equal(isStale('2026-10-21T18:00:00+00:00', '2026-10-22T17:59:00+00:00'), false);
  assert.equal(isStale('2026-10-21T18:00:00+00:00', '2026-10-22T18:01:00+00:00'), true);
  assert.equal(isStale('2026-10-21T18:00:00+00:00', '2026-10-21T20:00:00+00:00', 1), true);
});

test('unknown suggestions are refused rather than prepared', () => {
  assert.throws(() => prepareCorrection(review, 'nope', '2026-10-21T19:00:00+00:00'), /unknown suggestion/);
});

test('signalsFor lists a problem\'s overlaps', () => {
  assert.equal(signalsFor(review, 'A').length, 2);
  assert.equal(signalsFor(review, 'C').length, 0);
});

test('the hand-off says what it is and is not', () => {
  const text = handoff([prepareCorrection(review, 's1', '2026-10-21T19:00:00+00:00')]);
  const parsed = JSON.parse(text);
  assert.equal(parsed.kind, 'cluster-correction-request');
  assert.equal(parsed.draft, true);
  assert.match(parsed.note, /not applied/i);
  assert.equal(parsed.corrections.length, 1);
});

test('the source label never calls supplied data live', () => {
  assert.match(sourceLabel(review.source), /supplied/i);
  assert.match(sourceLabel(review.source), /synthetic/i);
  assert.doesNotMatch(sourceLabel(review.source), /live/i);
  assert.match(sourceLabel({...review.source, mode: 'connected', synthetic: false}), /connected/i);
});
