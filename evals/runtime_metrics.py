#!/usr/bin/env python3
"""Build and exercise a disposable repository for the three runtime metrics cases.

Uses synthetic data only. Does not change a user repository or contact an aggregator.
The output directory must not exist, so prior evidence is never overwritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/aipos/skills/aipos-metrics-emit/scripts/emit_metrics.py'


def setup(out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=False)
    repo = out / 'testrepo'
    full = repo / 'features/checkout_assistant'
    partial = repo / 'features/incomplete_feature'
    full.mkdir(parents=True)
    partial.mkdir()
    (repo / '.govkit').mkdir()
    (repo / '.govkit/marker.json').write_text(json.dumps({'level': '5', 'organization': 'SYNTHETIC_ORG_SENTINEL'}))
    (full / 'acceptance.feature').write_text('''Feature: Checkout confirmation
  @rule:confirmation-required
  Rule: An order is placed only after confirmation
    @mvp @functional @scenario:confirmed-order
    Scenario: Confirm a prepared order
      Given a prepared order
      When the customer confirms it
      Then the order is placed once
''')
    (full / 'nfrs.md').write_text('# Reliability\nAn order is placed at most once. Owner: Engineering. Evidence: retry test.\n')
    (full / 'plan.md').write_text('''# Plan
```yaml
evaluation_prediction:
  thresholds_met: true
  first:
    average: 4.5
  virtues:
    average: 4.5
```
''')
    (full / 'architecture_preflight.md').write_text('# Preflight\nSynthetic deterministic checkout fixture.\n')
    for feature in (full, partial):
        (feature / 'eval_criteria.yaml').write_text('mode: deterministic\n')
    def git(*args):
        return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()
    git('init', '-q')
    git('config', 'user.name', 'Synthetic evaluator')
    git('config', 'user.email', 'fixture@example.invalid')
    git('add', '.')
    git('commit', '-qm', 'Initial synthetic feature packages')
    first = git('rev-parse', 'HEAD')
    (full / 'nfrs.md').write_text('# Reliability\nAn order is placed at most once, including retries. Owner: Engineering. Evidence: retry test.\n')
    git('add', '.')
    git('commit', '-qm', 'Clarify retry evidence')
    second = git('rev-parse', 'HEAD')
    # Deliberate org-identifying canaries are ignored input fields, never output facts.
    ci = [{'name': name, 'conclusion': 'success', 'createdAt': '2026-09-20T09:00:00Z',
           'updatedAt': '2026-09-20T09:01:00Z', 'headSha': second, 'attempt': 1,
           'displayTitle': 'features/checkout_assistant', 'organization': 'SYNTHETIC_ORG_SENTINEL',
           'url': 'https://internal.example.invalid/run'}
          for name in ('quality-gate', 'eval-gate', 'quality-gate', 'eval-gate')]
    prs = [{'number': n, 'title': 'features/checkout_assistant', 'headRefName': 'feature/checkout_assistant',
            'createdAt': '2026-09-20T08:00:00Z', 'mergedAt': '2026-09-20T09:00:00Z',
            'additions': 12, 'deletions': 2, 'changedFiles': 1,
            'commits': [{'messageBody': 'Co-Authored-By: Claude <noreply@anthropic.com>' if n == 42 else 'Human change'}],
            'reviews': [], 'organization': 'SYNTHETIC_ORG_SENTINEL', 'url': 'https://internal.example.invalid/pr'}
           for n in (42, 43)]
    (repo / 'ci_runs.json').write_text(json.dumps(ci, indent=2))
    (repo / 'prs.json').write_text(json.dumps(prs, indent=2))
    (out / 'fixture.json').write_text(json.dumps({'commits': [first, second], 'synthetic': True}, indent=2))
    return repo


def verify(out: Path, repo: Path) -> dict:
    output = out / 'events.ndjson'
    command = [sys.executable, str(SCRIPT), str(repo), '--ci-runs', str(repo / 'ci_runs.json'),
               '--prs', str(repo / 'prs.json'), '--validate', '--out', str(output)]
    completed = subprocess.run(command, capture_output=True, text=True)
    (out / 'emitter.log').write_text(completed.stdout + completed.stderr)
    if completed.returncode:
        raise RuntimeError(f'Emitter failed; see {out / "emitter.log"}')
    text = output.read_text()
    events = [json.loads(line) for line in text.splitlines() if line]
    counts = dict(Counter(e['event'] for e in events))
    snapshots = {e['feature_id']: e for e in events if e['event'] == 'feature.package.snapshot'}
    scores = {key: row['completeness']['score'] for key, row in snapshots.items()}
    ai = {e['pr_id']: e['ai_assisted'] for e in events if e['event'] == 'pr.merged'}
    checks = {
        'scores': scores == {'checkout_assistant': 100, 'incomplete_feature': 15},
        'counts': counts == {'feature.package.snapshot': 2, 'rework.observed': 2, 'gate.run.completed': 4, 'pr.merged': 2},
        'ai_trailer': ai == {42: True, 43: False},
        'no_input_canaries': not any(s in text for s in ('SYNTHETIC_ORG_SENTINEL', 'internal.example.invalid')),
        'no_readiness_token': not (repo / '.govkit/tokens').exists(),
    }
    record = {'checks': checks, 'scores': scores, 'counts': counts, 'ai_assisted': ai,
              'components': {key: row['completeness']['components'] for key, row in snapshots.items()},
              'command': command, 'note': 'Completeness is not an execution token or product approval.'}
    (out / 'verification.json').write_text(json.dumps(record, indent=2) + '\n')
    if not all(checks.values()):
        raise AssertionError(checks)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    record = verify(args.out, setup(args.out))
    print(json.dumps(record, indent=2))
