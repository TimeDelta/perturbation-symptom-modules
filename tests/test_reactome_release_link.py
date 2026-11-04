"""The Reactome release a build reads is the one the fetch wrote (decision 9.111).

The owner, 4 November 2026: "Go with latest until the lockbox is drawn". experiments/fetch_reactome_pathways.py writes
the release Reactome serves and links data/raw/reactome/current to it; every reader of the exports defaults to that
link. Before that day the readers named v97 while the fetch wrote v98, and the neuronal build imported no pathway.
"""
import io
import json
import re
from pathlib import Path

import pytest

import experiments.fetch_reactome_pathways as fetcher

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
READERS = ["experiments/build_neuronal_graph_variant.py", "experiments/build_gene_protein_split.py",
           "experiments/build_complex_descriptors.py", "experiments/measure_complex_conjunction_semantics.py"]


def fake_fetch(monkeypatch, tmp_path, release):
    class VersionResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exception):
            return False

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", lambda request, timeout=None: VersionResponse(release.encode()))

    def fake_download_and_pin(raw_root, source, file_name, url, refresh):
        target = raw_root / source / file_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("<sbml/>")
        return {"bytes": 7, "sha256": "0" * 64, "fetched_at": "2026-11-04T00:00:00Z"}

    monkeypatch.setattr(fetcher, "download_and_pin", fake_download_and_pin)
    monkeypatch.setattr("sys.argv", ["fetch_reactome_pathways.py", "--raw-root", str(tmp_path)])
    fetcher.main()


def test_the_fetch_links_current_to_the_release_it_wrote_and_moves_the_link_on_a_new_release(monkeypatch, tmp_path):
    fake_fetch(monkeypatch, tmp_path, "98")
    current = tmp_path / "reactome" / fetcher.CURRENT_RELEASE_LINK
    assert current.is_symlink() and current.resolve() == (tmp_path / "reactome" / "v98").resolve()
    assert json.loads((current / "pathways.json").read_text())["reactome_release"] == "98"
    fake_fetch(monkeypatch, tmp_path, "99")
    assert current.resolve() == (tmp_path / "reactome" / "v99").resolve()
    assert (tmp_path / "reactome" / "v98" / "pathways.json").exists()


def test_a_real_directory_under_the_links_name_is_refused(monkeypatch, tmp_path):
    (tmp_path / "reactome" / fetcher.CURRENT_RELEASE_LINK).mkdir(parents=True)
    with pytest.raises(FileExistsError):
        fake_fetch(monkeypatch, tmp_path, "98")


@pytest.mark.parametrize("reader", READERS)
def test_every_reader_defaults_to_the_link_and_names_no_fixed_release(reader):
    text = (REPOSITORY_ROOT / reader).read_text()
    assert 'default=Path("data/raw/reactome/current")' in text
    assert not re.search(r'default=Path\("data/raw/reactome/v\d+"\)', text)


def test_the_rebuild_step_waits_on_the_link():
    script = (REPOSITORY_ROOT / "scripts" / "rebuild_data_layer.sh").read_text()
    assert "step data/raw/reactome/current/pathways.json" in script
    assert not re.search(r"data/raw/reactome/v\d+", script)
