"""Fetch and pin the Reactome pathways the neuronal and oxidative graph variant imports
(mechanistic_pathway_learning/graph/reactome_import.py; design section 4.1).

Each pathway is exported as SBML by the Reactome content service (reactions with their reactants, products, catalysts
and positive or negative regulators, every species annotated with a ChEBI or UniProt identifier and a compartment)
and written to data/raw/reactome/v<release>/<stable id>.sbml with a pin beside it (URL, bytes, SHA-256, fetch time,
database release). Files already pinned are not fetched again unless --refresh is given.

The release is the one Reactome serves when this runs, and it is used until the lockbox is drawn (decision 9.111, the
owner, 4 November 2026: "Go with latest until the lockbox is drawn"). After writing a release, this points
data/raw/reactome/current at its directory, and every reader of the exports defaults to that pointer, so a build reads
the release the fetch wrote; before 4 November 2026 the readers named v97 while this wrote v98, the release Reactome
then served, and the neuronal build imported no pathway. Each graph's summary records the release it was built from
(`reactome_pathways` in experiments/build_neuronal_graph_variant.py). When the lockbox is drawn the release in use is
pinned (docs/confirmatory_runbook.md): Reactome's content service serves only its current release, so a release that is
not committed cannot be fetched again.

Usage:
  python experiments/fetch_reactome_pathways.py
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_node_descriptor_sources import download_and_pin  # noqa: E402

from mechanistic_pathway_learning.evidence.cached_http import USER_AGENT

PATHWAYS = {
    "R-HSA-112316": "Neuronal System (neurotransmitter release cycle, receptors, potassium channels, ionotropic and metabotropic transmission)",
    "R-HSA-983712": "Ion channel transport (stimuli-sensing channels, P-type ATPases, ligand-gated and other channels)",
    "R-HSA-426117": "Cation-coupled chloride cotransporters (NKCC1, KCC2 and relatives)",
    "R-HSA-8949215": "Mitochondrial calcium ion transport",
    "R-HSA-500792": "GPCR ligand binding",
    "R-HSA-418594": "G alpha (i) signalling events",
    "R-HSA-418555": "G alpha (s) signalling events",
    "R-HSA-416476": "G alpha (q) signalling events",
    "R-HSA-397795": "G-protein beta:gamma signalling",
    "R-HSA-3299685": "Detoxification of reactive oxygen species",
    "R-HSA-9755511": "KEAP1-NFE2L2 pathway",
    "R-HSA-9711123": "Cellular response to chemical stress",
    "R-HSA-202131": "Metabolism of nitric oxide: NOS3 activation and regulation",
    "R-HSA-1222556": "ROS and RNS production in phagocytes",
    "R-HSA-611105": "Respiratory electron transport",
}
# the link every reader of the exports defaults to: data/raw/reactome/current -> v<release> (decision 9.111)
CURRENT_RELEASE_LINK = "current"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--refresh", action="store_true")
    arguments = parser.parse_args()
    request = urllib.request.Request("https://reactome.org/ContentService/data/database/version", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        release = response.read().decode().strip()
    source = f"reactome/v{release}"
    pins = {}
    for stable_id, description in PATHWAYS.items():
        pin = download_and_pin(arguments.raw_root, source, f"{stable_id}.sbml", f"https://reactome.org/ContentService/exporter/sbml/{stable_id}.xml", arguments.refresh)
        pins[stable_id] = {"description": description, "bytes": pin["bytes"], "sha256": pin["sha256"], "fetched_at": pin["fetched_at"]}
        print(f"{stable_id} ({description}): {pin['bytes']:,} bytes, sha256 {pin['sha256'][:12]}")
    (arguments.raw_root / source / "pathways.json").write_text(json.dumps({"reactome_release": release, "pathways": pins}, indent=1) + "\n")
    point_current_at(arguments.raw_root / "reactome", f"v{release}")
    print(f"data/raw/reactome/current -> v{release}")


def point_current_at(reactome_root: Path, release_directory: str) -> None:
    """Make reactome_root/current a relative link to the release directory just written, replacing an older link. A
    real directory under that name is refused rather than replaced, since it would hold a release of its own."""
    current = reactome_root / CURRENT_RELEASE_LINK
    if current.exists() and not current.is_symlink():
        raise FileExistsError(f"{current} is a directory, not a link to a release; move it before fetching")
    staged = reactome_root / f".{CURRENT_RELEASE_LINK}.new"
    staged.unlink(missing_ok=True)
    staged.symlink_to(release_directory)
    staged.replace(current)


if __name__ == "__main__":
    main()
