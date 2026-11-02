"""Check scripts/rebuild_data_layer.sh before it runs: what it would skip, and what is stale.

Two traps this exists to catch, both of which have already cost a build.

**A step whose output exists is skipped.** `scripts/rebuild_data_layer.sh` says so in its own header ("Every step is
skipped when its output exists, so the script can be rerun after a stop"), which is what makes a rebuild resumable.
The cost is that a rebuild on a container that still holds earlier outputs keeps them and reports success. Decision
9.106 records the case: the build of 20 October 2026, which the owner had not asked for, wrote the same directory
names the real v5 will write, so a rebuild on that disk would have kept its graphs. This script lists what exists
before anything runs, so an operator sees what will be kept rather than discovering it afterwards.

**An output built before one of its input tables was regenerated is stale, and nothing says so.** The derived BRENDA
table feeds `experiments/build_neuronal_graph_variant.py`, so regenerating it after a neuronal graph is built leaves
that graph describing the old table while the skip rule keeps it. The BRENDA handoff of 26 October 2026 names the
ordering ("the derived table feeds build_neuronal_graph_variant.py, so regenerating it changes the graph. Either
regenerate it before the v5 rebuild's neuronal step [...] or rebuild the downstream variants afterwards"), and
decision 9.88's no-activation rule of 1 November 2026 means the table is regenerated at the next rebuild, so the
trap is live. This script compares each existing output's modification time against the inputs that build it and
fails when an input is newer.

**A committed derived table can be older than the script that generates it, and nothing says so.** The derived BRENDA
table is committed, not built by the rebuild, so the two checks above never look at it: the rebuild reads whatever is in
git. On 2 November 2026 it held no `no_activation` row, two days after decision 9.88's rule was built into
`experiments/extract_brenda_enzyme_regulation.py`, so a rebuild would have written a neuronal graph describing the rule
the owner replaced. This script compares the commit date of each such table against the commit dates of the scripts that
generate it and reports the ones that are behind. It reports rather than refuses, because the regeneration cannot run
first: it needs a gene-and-protein-split graph that only the rebuild builds, which is why the regeneration is the
rebuild's `brenda` stage (`scripts/rebuild_data_layer.sh`). Commit dates, not modification times, because on a fresh
clone every tracked file carries the checkout time and a modification-time comparison between two tracked files says
nothing.

What it does not do: it does not check that an input's *contents* are current, only its modification time, so a table
edited and restored looks unchanged. On a fresh clone every tracked file carries the checkout time, which is earlier
than anything built afterwards, so the comparison is only ever triggered by a regeneration during or after a build,
which is the case that matters. It changes nothing and runs no step.

Usage, from the repository root:
  PYTHONPATH=. python experiments/check_rebuild_inputs.py            # report, and fail on a stale output
  PYTHONPATH=. python experiments/check_rebuild_inputs.py --quiet    # the failures only
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REBUILD_SCRIPT = REPOSITORY_ROOT / "scripts" / "rebuild_data_layer.sh"
# The shell variables the rebuild script sets, so a step's output path can be read without running it. Read from the
# script's own assignments (lines 24, 25, 191, 200, 206, 263 and 264 on 2 November 2026); `descriptors` and `weights`
# are set inside a stage, so a parser that knew only the first two left nine of the 61 step outputs unexpanded and
# silently unchecked, which tests/test_check_rebuild_inputs.py now fails on.
SHELL_VARIABLES = {"processed": "data/processed", "log_directory": "data/processed/rebuild_logs",
                   "descriptors": "data/processed/node_descriptors", "weights": "data/processed/cell_class_weights",
                   "atlas": "data/raw/siletti_cellxgene"}
STEP_LINE = re.compile(r"^\s*step\s+(?P<output>\"[^\"]+\"|\S+)\s")

# Which committed tables each kind of output is built from. The key is a substring of the output path, so one entry
# covers every variant whose name holds it; the values are the inputs whose regeneration makes that output stale.
# Taken from the defaults of experiments/build_neuronal_graph_variant.py, which is what the rebuild calls.
INPUTS_OF_OUTPUT: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("neuronal", ("configs/brenda_metabolite_enzyme_regulation.csv",
                  "docs/curated_presynaptic_receptors.csv",
                  "docs/curated_oxidant_targets.csv",
                  "docs/curated_oxidant_sources.csv",
                  "configs/admitted_receptor_g_alpha_coupling.csv")),
    ("drugs", ("configs/drug_clearing_enzymes.csv",)),
)


# Committed derived tables, and the scripts whose output they hold. These are not built by the rebuild - they are in git
# and the rebuild reads them - so neither check above covers them; this pairing is what makes a table that predates its
# own rule visible. configs/brenda_metabolite_enzyme_regulation.csv is written by the mapping script from the records the
# extraction script writes, so a change to either leaves the committed table behind (decision 9.88).
GENERATORS_OF_TABLE: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("configs/brenda_metabolite_enzyme_regulation.csv",
     ("experiments/extract_brenda_enzyme_regulation.py", "experiments/map_brenda_regulation_to_graph.py")),
)


def last_commit_time(path: str, root: Path = REPOSITORY_ROOT) -> int | None:
    """When the last commit touching this path was made, as a Unix time, or None when git knows nothing of it (an
    untracked file, or a clone too shallow to hold the commit)."""
    result = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path],
                            cwd=root, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return int(result.stdout.strip())


def tables_behind_their_generator(root: Path = REPOSITORY_ROOT) -> list[tuple[str, str]]:
    """(table, generator) for every committed derived table whose last commit predates a generator's last commit, so
    the committed table cannot hold that generator's output."""
    behind = []
    for table, generators in GENERATORS_OF_TABLE:
        table_time = last_commit_time(table, root)
        if table_time is None:
            continue
        for generator in generators:
            generator_time = last_commit_time(generator, root)
            if generator_time is not None and generator_time > table_time:
                behind.append((table, generator))
    return behind


def expand(path_text: str) -> str:
    """A step's output path with the script's own variables filled in, and its quotes dropped."""
    expanded = path_text.strip().strip('"')
    for name, value in SHELL_VARIABLES.items():
        expanded = expanded.replace(f"${{{name}}}", value).replace(f"${name}", value)
    return expanded


def step_outputs(script_text: str) -> list[str]:
    """Every output path the rebuild script's steps name, in the order the script runs them, with the script's own
    variables filled in. A path still holding a `$` is one the script builds at run time; dynamic_outputs separates
    those, because this parser cannot resolve them and must not look as though it had."""
    outputs = []
    for line in script_text.splitlines():
        match = STEP_LINE.match(line)
        if match:
            outputs.append(expand(match.group("output")))
    return outputs


def resolved_and_dynamic(outputs: list[str]) -> tuple[list[str], list[str]]:
    """(the paths this script can check, the paths it cannot). A path is dynamic when the rebuild builds it from a
    function argument or a loop variable rather than a fixed name: `$suffix` is an argument of the function that
    writes the OnSIDES and evidence tables (line 82 on 2 November 2026) and `$graph` is the variable of the loop over
    four graph directories (line 147), so neither has one value to resolve. Those steps are reported and not checked,
    rather than dropped, so the report never understates how much of the rebuild it covers."""
    resolved = [output for output in outputs if "$" not in output]
    dynamic = [output for output in outputs if "$" in output]
    return resolved, dynamic


def newest_modification_time(path: Path) -> float:
    """The newest modification time in a file, or in a directory's tree. A built graph is a directory, and the step
    checks for one file inside it, so the directory's own time is not what changed when it was written."""
    if path.is_file():
        return path.stat().st_mtime
    return max((entry.stat().st_mtime for entry in path.rglob("*") if entry.is_file()), default=path.stat().st_mtime)


def stale_outputs(root: Path = REPOSITORY_ROOT) -> list[tuple[str, str]]:
    """(output, input) for every existing output an input was regenerated after, newest input first."""
    stale = []
    resolved, _ = resolved_and_dynamic(step_outputs((root / "scripts" / "rebuild_data_layer.sh").read_text()))
    for output in resolved:
        output_path = root / output
        if not output_path.exists():
            continue
        built_at = newest_modification_time(output_path)
        for marker, inputs in INPUTS_OF_OUTPUT:
            if marker not in output:
                continue
            for input_name in inputs:
                input_path = root / input_name
                if input_path.exists() and input_path.stat().st_mtime > built_at:
                    stale.append((output, input_name))
    return stale


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quiet", action="store_true", help="print the failures only, for a call from the rebuild script")
    arguments = parser.parse_args()

    outputs = step_outputs(REBUILD_SCRIPT.read_text())
    resolved, dynamic = resolved_and_dynamic(outputs)
    present = [output for output in resolved if (REPOSITORY_ROOT / output).exists()]
    if not arguments.quiet:
        print(f"{len(outputs)} steps, of which {len(resolved)} have a path this check can resolve: "
              f"{len(present)} of those already exist and would be SKIPPED, {len(resolved) - len(present)} would be built")
        for output in present:
            print(f"   skipped  {output}")
        if not present:
            print("   (none of the resolvable outputs exists: this is a clean rebuild)")
        if dynamic:
            print(f"{len(dynamic)} steps build their output path at run time and are NOT checked here:")
            for output in dynamic:
                print(f"   unchecked  {output}")

    stale = stale_outputs()
    if stale:
        print("\nSTALE: an output exists that one of its inputs was regenerated after, so the rebuild would keep it:")
        for output, input_name in stale:
            print(f"   {output}  is older than  {input_name}")
        print("Delete the output and run the rebuild again, or regenerate the input before the step that reads it.")
        raise SystemExit(1)
    behind = tables_behind_their_generator()
    if behind:
        print("\nBEHIND: a committed derived table is older than a script that generates it, so it cannot hold that "
              "script's output:")
        for table, generator in behind:
            print(f"   {table}  was last committed before  {generator}")
        print("The rebuild reads the committed table, so the graph it writes describes the older version. Regenerate it "
              "with the brenda stage (bash scripts/rebuild_data_layer.sh brenda), which runs after the graphs stage "
              "because the mapping needs the split graph that stage builds, then rerun the graphs stage on the new "
              "table. This is reported and not refused for that reason.")
    if not arguments.quiet:
        print("\nNo existing output is older than an input that builds it.")


if __name__ == "__main__":
    main()
