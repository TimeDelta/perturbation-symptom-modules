#!/bin/bash
# SessionStart hook for Claude Code cloud sessions: make sure the package, every extra and the pinned table libraries
# import, then relaunch the unfinished background jobs registered under runs/jobs/ (scripts/resume_jobs.sh). A usage
# limit can stop the session, after which the container is reclaimed and every running process dies; the session's
# disk survives, so the jobs resume from their checkpoints and caches. The job report printed here becomes part of the
# session's context.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

# Every extra, because tests/ imports the experiment scripts (matplotlib, scipy, h5py) and the graph build needs the
# graph extra; and the pandas and pyarrow versions that wrote data/releases/v0.4, without which the rebuilt tables do
# not match their recorded hashes (scripts/rebuild_data_layer.sh, docs/data_layer_rebuild.md).
if ! python -c "
import importlib.metadata as metadata
import mechanistic_pathway_learning, torch, pytest, matplotlib, scipy, h5py, cobra, decoupler, rdkit
assert metadata.version('pandas') == '2.3.3' and metadata.version('pyarrow') == '25.0.1'
" > /dev/null 2>&1; then
  echo "session-start: installing the package with every extra, pandas 2.3.3 and pyarrow 25.0.1"
  pip install --quiet -e ".[dev,descriptors,graph,experiments]" "pandas==2.3.3" "pyarrow==25.0.1" \
    || echo "session-start: dependency install failed; jobs are still resumed"
fi

# A cloud container clones the repository shallow. experiments/generate_decision_history.py reads every version of
# docs/open_decisions.md in the git log, so on a shallow clone it rewrites docs/decision_history.md from the versions
# the clone holds: on 24 October 2026 it read 31 of the 149, lost the dropped ids 1.5 and 9.10, and counted 53 decisions
# as recorded and closed in one commit instead of 13. Fetch the whole history before anything is generated.
if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
  echo "session-start: fetching the full git history (the clone is shallow)"
  git fetch --quiet --unshallow origin \
    || echo "session-start: unshallow failed; do not run the decision history generator"
fi

bash scripts/resume_jobs.sh
exit 0
