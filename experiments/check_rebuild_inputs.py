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
the owner replaced. This script compares each such table with the scripts and input files it is generated from: each
one as it stood in the table's last commit against the same file at HEAD. A Python file counts as changed only when its
syntax tree without docstrings differs, so an edit to comments or docstrings alone, a change of layout, or a change
later reverted is not counted: none changes what the script writes, and CLAUDE.md asks that comments be kept current
(20 November 2026: a reorganization of docs/ that changed one comment line and one module-docstring line of
`experiments/extract_brenda_enzyme_regulation.py` made the commit-date comparison this replaced report the table as
behind it). Any other file, or a Python file that does not parse, is compared byte for byte. A file absent from the
table's commit counts as changed, so a script renamed since then is reported until the table is regenerated. It reports
rather than refuses, because the regeneration cannot run first: it needs a gene-and-protein-split graph that only the
rebuild builds, which is why the regeneration is the rebuild's `brenda` stage (`scripts/rebuild_data_layer.sh`).
Commits, not modification times, because on a fresh clone every tracked file carries the checkout time and a
modification-time comparison between two tracked files says nothing. In a shallow clone the table's last commit may lie
beyond the clone's boundary, so the comparison is not made there and the script says so.

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
import ast
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


# Committed derived tables, and the scripts and input files their content follows from. These are not built by the
# rebuild - they are in git and the rebuild reads them - so neither check above covers them; this pairing is what makes a
# table that predates its own rule visible. configs/brenda_metabolite_enzyme_regulation.csv is written by the mapping
# script from the records the extraction script writes (decision 9.88), and since 20 November 2026 (4c9ec119) the mapping
# reads Human-GEM's metabolites through the corrections applied where the model is read: the corrections table, the
# module that applies it, and the module whose human_gem_metabolites_by_chebi() indexes the result. A change to any of them
# can leave the committed table behind; a code change anywhere in those two modules counts, not only in the functions the
# mapping calls.
GENERATORS_OF_TABLE: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("configs/brenda_metabolite_enzyme_regulation.csv",
     ("experiments/extract_brenda_enzyme_regulation.py", "experiments/map_brenda_regulation_to_graph.py",
      "mechanistic_pathway_learning/graph/human_gem_corrections.py", "configs/human_gem_corrections.csv",
      "mechanistic_pathway_learning/evidence/laboratory_abnormality_labels.py")),
)


def git(arguments: list[str], root: Path) -> subprocess.CompletedProcess:
    """A git command's result as bytes, never raising."""
    return subprocess.run(["git", *arguments], cwd=root, capture_output=True, check=False)


def repository_is_shallow(root: Path = REPOSITORY_ROOT) -> bool:
    """True when the clone holds truncated history (as mechanistic_pathway_learning.documentation.repository_is_shallow,
    kept here so the preflight imports nothing from the package)."""
    return git(["rev-parse", "--is-shallow-repository"], root).stdout.decode().strip() == "true"


def last_commit_hash(path: str, root: Path = REPOSITORY_ROOT) -> str | None:
    """The last commit touching this path, or None when git knows nothing of it (an untracked file). In a shallow clone
    this is the clone's boundary commit when the real one lies beyond it, which is why main() does not run the
    comparison there."""
    result = git(["log", "-1", "--format=%H", "--", path], root)
    commit = result.stdout.decode().strip()
    return commit if result.returncode == 0 and commit else None


def blob_id(path: str, commit: str, root: Path = REPOSITORY_ROOT) -> str | None:
    """The id of the file at this path in that commit, or None when the commit does not hold it. Read from the tree, so a
    partial clone needs no download for it. A git failure raises with git's own message rather than reading as absent."""
    result = git(["ls-tree", "--full-tree", commit, "--", path], root)
    if result.returncode != 0:
        raise RuntimeError(f"git ls-tree {commit} -- {path} failed: {result.stderr.decode().strip()}")
    entry = result.stdout.decode().strip()
    return entry.split()[2] if entry else None


def blob_bytes(blob: str, root: Path = REPOSITORY_ROOT) -> bytes:
    """A file's bytes from its id; a git failure (for example a partial clone with its remote out of reach) raises with
    git's own message."""
    result = git(["cat-file", "blob", blob], root)
    if result.returncode != 0:
        raise RuntimeError(f"git cat-file blob {blob} failed: {result.stderr.decode().strip()}")
    return result.stdout


def code_without_docstrings(source: bytes) -> str | None:
    """A Python source's syntax tree with every docstring dropped, as text to compare; comments, layout and line numbers
    never reach it. Parsed from bytes, so a coding declaration is honoured. None when the source does not parse, so the
    caller compares the bytes instead."""
    try:
        module = ast.parse(source)
    except (SyntaxError, ValueError):
        return None
    for node in ast.walk(module):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            is_docstring = isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
            if is_docstring and isinstance(first.value.value, str):
                node.body = node.body[1:] or [ast.Pass()]
    return ast.dump(module, include_attributes=False)


def code_changed(before: bytes, after: bytes, path: str) -> bool:
    """Whether a file differs between two versions in a way that can change what it produces. A Python file is compared
    by its syntax tree without docstrings, so comments, docstrings and layout alone are not a change; anything else, or a
    version that does not parse, is compared byte for byte."""
    if path.endswith(".py"):
        before_code, after_code = code_without_docstrings(before), code_without_docstrings(after)
        if before_code is not None and after_code is not None:
            return before_code != after_code
    return before != after


def tables_behind_their_generator(root: Path = REPOSITORY_ROOT) -> list[tuple[str, str]]:
    """(table, generator) for every committed derived table one of whose scripts or input files differs at HEAD from its
    version in the table's last commit, so the committed table may not hold that version's output. Assumes full
    history; main() does not call it in a shallow clone. See the module docstring for what counts as a difference."""
    behind = []
    for table, generators in GENERATORS_OF_TABLE:
        table_commit = last_commit_hash(table, root)
        if table_commit is None:
            continue
        for generator in generators:
            current = blob_id(generator, "HEAD", root)
            if current is None:
                continue  # not in HEAD: the test of every named file's existence catches a rename not carried here
            then = blob_id(generator, table_commit, root)
            if then is None:
                behind.append((table, generator))
            elif then != current and code_changed(blob_bytes(then, root), blob_bytes(current, root), generator):
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
    if repository_is_shallow():
        print("\nNOT CHECKED: this clone is shallow, so a committed derived table's last commit may lie beyond its "
              "boundary and the comparison with its generators would be wrong. Deepen it (git fetch --depth=1000 origin "
              "main) and run this again.")
        behind = []
    else:
        behind = tables_behind_their_generator()
    if behind:
        print("\nBEHIND: a committed derived table was committed without the current version of a script or input it is "
              "generated from, so it may not hold that version's output:")
        for table, generator in behind:
            print(f"   {table}  was last committed without the current version of  {generator}")
        print("The rebuild reads the committed table, so the graph it writes describes the older version. Regenerate it "
              "with the brenda stage (bash scripts/rebuild_data_layer.sh brenda), which runs after the graphs stage "
              "because the mapping needs the split graph that stage builds, then rerun the graphs stage on the new "
              "table. This is reported and not refused for that reason.")
    if not arguments.quiet:
        print("\nNo existing output is older than an input that builds it.")


if __name__ == "__main__":
    main()
