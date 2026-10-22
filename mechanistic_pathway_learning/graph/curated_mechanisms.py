"""Curated edges for perturbations whose established mechanism the imported sources leave without a route (decision
9.68 (a)).

Decision 9.68 measured 186 gene perturbations whose protein has no edge out, so the model can fit their labels only
through the gene's and the protein's own states. For a few of them the mechanism is established and sits inside layers
the graph already has: a co-chaperone that keeps the aromatic amino acid hydroxylases stable and active (DNAJC12), a
processing enzyme for a reaction Human-GEM leaves without a catalyst (MMACHC), and a cofactor the enzyme-regulation
source does not name (adenosylcobalamin for methylmalonyl-CoA mutase). Decision 9.71 found the same for a subunit:
GABRD belongs to no Reactome GABA-A receptor entity, so no delta-containing receptor conducted chloride, and its row
makes it a member of the GABA-bound heteropentamer entity that catalyses chloride entry. Each row of
docs/curated_dead_end_mechanisms.csv
names one edge with the papers behind it; the lysosomal release of cobalamin, a transport with no reaction to attach a
catalyst to, is a curated reaction in experiments/build_neuronal_graph_variant.py instead.

The rows are added to the neuronal variant, before the gene/protein split, so a gene end becomes the gene's protein node
as every imported edge's does (graph/gene_protein_split.py), and each edge's evidence_source starts with "curated" and
names its PubMed ids, which is how the edge evidence table reads a curated edge (graph/edge_evidence.py, decision 9.57).

A paralog that can stand in for a member of an entity is a row of docs/curated_alternative_members.csv instead
(add_alternative_members, below): VAMP1 beside VAMP2, which joins every entity VAMP2 belongs to with a share of VAMP2's
membership weight rather than a weight of its own.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DEFAULT_CURATED_MECHANISMS_PATH = Path("docs/curated_dead_end_mechanisms.csv")
REQUIRED_COLUMNS = ("source_id", "target_id", "relation_type", "sign", "decision", "pmids", "quotes", "reading")
# the sign each relation carries, and the node types its two ends must have before the split
SIGN_OF_RELATION = {"activates": 1.0, "inhibits": -1.0, "catalyzed_by": 1.0, "cofactor_of": 1.0, "member_of": 1.0}
NODE_TYPES_OF_RELATION = {"activates": ("gene", "gene"), "inhibits": ("gene", "gene"), "catalyzed_by": ("gene", "reaction"),
                          "cofactor_of": ("metabolite", "gene"), "member_of": ("gene", "protein_entity")}
EVIDENCE_PREFIX = "curated dead-end mechanism"


def read_curated_mechanisms(path: Path = DEFAULT_CURATED_MECHANISMS_PATH) -> pd.DataFrame:
    table = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    return table


def pubmed_ids_of(cell: str) -> list[str]:
    """The PubMed ids of a row, from a ';'-separated cell, each all digits."""
    identifiers = [part.strip() for part in str(cell).split(";") if part.strip()]
    for identifier in identifiers:
        if not identifier.isdigit():
            raise ValueError(f"not a PubMed id: {identifier!r}")
    return identifiers


def problems_of_row(row: pd.Series, node_type_of: dict[str, str], relation_types: list[str]) -> list[str]:
    """Why a row cannot be added as written (empty when it can)."""
    problems = []
    relation = row["relation_type"]
    if relation not in SIGN_OF_RELATION:
        return [f"relation {relation!r} is not one this table may add ({', '.join(sorted(SIGN_OF_RELATION))})"]
    if relation not in relation_types:
        problems.append(f"relation {relation!r} is not among the graph's relation types")
    try:
        sign = float(row["sign"])
    except ValueError:
        sign = float("nan")
    if sign != SIGN_OF_RELATION[relation]:
        problems.append(f"sign {row['sign']!r} does not match {relation} ({SIGN_OF_RELATION[relation]:+.0f})")
    for end, column, expected in (("source", "source_id", NODE_TYPES_OF_RELATION[relation][0]), ("target", "target_id", NODE_TYPES_OF_RELATION[relation][1])):
        node = row[column]
        if node not in node_type_of:
            problems.append(f"{end} {node} is not a node of the graph")
        elif node_type_of[node] != expected:
            problems.append(f"{end} {node} is a {node_type_of[node]} node, and {relation} needs a {expected} node there")
    try:
        if len(pubmed_ids_of(row["pmids"])) == 0:
            problems.append("no PubMed id")
    except ValueError as error:
        problems.append(str(error))
    if not str(row["quotes"]).strip():
        problems.append("no quote from the papers")
    return problems


def add_curated_mechanisms(nodes: pd.DataFrame, edges: pd.DataFrame, relation_types: list[str],
                           table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], dict]:
    """The graph with each row of the table added as one edge. A row that cannot be added as written raises, so the
    table cannot drift from the graph silently; a row whose edge the graph already holds (the same source, target and
    relation) is left out and reported, since the imported edge comes first."""
    node_type_of = dict(zip(nodes.node_id, nodes.node_type))
    problems = {index: problems_of_row(row, node_type_of, relation_types) for index, row in table.iterrows()}
    problems = {index: found for index, found in problems.items() if found}
    if problems:
        details = "; ".join(f"row {index + 2} ({table.loc[index, 'source_id']} -> {table.loc[index, 'target_id']}): {', '.join(found)}" for index, found in problems.items())
        raise ValueError(f"curated mechanisms that cannot be added: {details}")
    existing = set(zip(edges.source_id, edges.target_id, edges.relation_type))
    rows, already_present = [], []
    for row in table.itertuples():
        key = (row.source_id, row.target_id, row.relation_type)
        if key in existing:
            already_present.append(f"{row.source_id} -{row.relation_type}-> {row.target_id}")
            continue
        existing.add(key)
        pmids = "; ".join(f"PMID {identifier}" for identifier in pubmed_ids_of(row.pmids))
        rows.append({"source_id": row.source_id, "target_id": row.target_id, "relation_type": row.relation_type,
                     "sign": SIGN_OF_RELATION[row.relation_type], "evidence_source": f"{EVIDENCE_PREFIX}, decision {row.decision} ({pmids})"})
    new_edges = (pd.concat([edges, pd.DataFrame(rows, columns=edges.columns)], ignore_index=True).astype(edges.dtypes.to_dict())
                 if rows else edges.reset_index(drop=True).copy())
    counts = new_edges.source_id.value_counts().add(new_edges.target_id.value_counts(), fill_value=0)
    new_nodes = nodes.copy()
    if "degree" in new_nodes.columns:
        new_nodes["degree"] = counts.reindex(new_nodes.node_id).fillna(0).astype("int64").to_numpy()
    summary = {"edges_added": len(rows), "by_relation": pd.Series([row["relation_type"] for row in rows], dtype=str).value_counts().to_dict(),
               "already_present": already_present}
    return new_nodes, new_edges, list(relation_types), summary


# --- alternative members (decision 9.68 (a), the owner on 20 October 2026) ---------------------------------------------
#
# A paralog that can do a member's job in an entity, though with less of it, is an alternative member: VAMP1 beside
# VAMP2 as the vesicle SNARE. Reactome's entities are flattened to their genes (graph/reactome_import.py), so the
# alternative cannot be a set node of its own without a new relation; it joins every entity the primary member belongs
# to, as a member, and the two split the primary's edge weight between them by their brain expression:
#
#     weight(alternative -> entity) = s * w,   weight(primary -> entity) = (1 - s) * w,   s = a / (a + p)
#
# where w is the primary's weight before (1 for every Reactome membership) and a and p are the two genes' mean GTEx
# brain median TPM. Under item 28's total_in_degree divisor an edge weight acts as a share of the destination's input
# (decision 4.11), so the entity's divisor and every other member's share are unchanged: the alternative takes a part of
# the primary's share and nothing else moves. Losing the alternative removes its share, losing the primary leaves the
# alternative's, which is the backup to first order without a nonlinearity in the propagation.
#
# The pair is also a disjunction for the complex gate of decision 4.2: within an entity the two count as one member
# whose raw expression is the larger of theirs, the way evaluate_gene_rule reads "or", so a class with little of the
# alternative does not shut an entity the primary keeps open (graph/brain_expression_weights.py, alternative_groups).

DEFAULT_ALTERNATIVE_MEMBERS_PATH = Path("docs/curated_alternative_members.csv")
ALTERNATIVE_REQUIRED_COLUMNS = ("alternative_id", "primary_id", "decision", "share_basis", "pmids", "quotes", "reading")
ALTERNATIVE_EVIDENCE_PREFIX = "curated alternative member"
SHARE_BASES = ("gtex_brain_median_tpm_mean",)


def read_alternative_members(path: Path = DEFAULT_ALTERNATIVE_MEMBERS_PATH) -> pd.DataFrame:
    table = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = [column for column in ALTERNATIVE_REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    return table


def alternative_member_groups(table: pd.DataFrame) -> list[frozenset[str]]:
    """The gene nodes that count as one member of an entity, one set per primary (its alternatives joined to it)."""
    members_of_primary: dict[str, set[str]] = {}
    for row in table.itertuples():
        members_of_primary.setdefault(row.primary_id, {row.primary_id}).add(row.alternative_id)
    return [frozenset(members) for _, members in sorted(members_of_primary.items())]


def alternative_share(alternative_symbol: str, primary_symbol: str, brain_expression: pd.DataFrame,
                      basis: str = "gtex_brain_median_tpm_mean") -> dict:
    """s = a / (a + p) from the two genes' expression (build_physiology_graph.load_brain_expression's table, which can
    hold a symbol more than once; the largest value is taken, as that loader's own ordering does)."""
    if basis not in SHARE_BASES:
        raise ValueError(f"share basis {basis!r} is not one of {SHARE_BASES}")
    column = "brain_median_tpm_mean"
    values = {}
    for symbol in (alternative_symbol, primary_symbol):
        rows = brain_expression.loc[brain_expression.gene_symbol == symbol, column]
        if rows.empty:
            raise ValueError(f"{symbol} has no row in the brain expression table, so its share cannot be set")
        values[symbol] = float(rows.max())
    total = values[alternative_symbol] + values[primary_symbol]
    if total <= 0:
        raise ValueError(f"{alternative_symbol} and {primary_symbol} both have zero brain expression")
    return {"basis": basis, "alternative_value": values[alternative_symbol], "primary_value": values[primary_symbol],
            "share_of_alternative": values[alternative_symbol] / total}


def problems_of_alternative_row(row, node_type_of: dict[str, str]) -> list[str]:
    problems = []
    for column in ("alternative_id", "primary_id"):
        node = getattr(row, column)
        if node not in node_type_of:
            problems.append(f"{column} {node} is not a node of the graph")
        elif node_type_of[node] != "gene":
            problems.append(f"{column} {node} is a {node_type_of[node]} node, and an alternative member must be a gene")
    if row.alternative_id == row.primary_id:
        problems.append("a gene cannot be its own alternative")
    if row.share_basis not in SHARE_BASES:
        problems.append(f"share basis {row.share_basis!r} is not one of {SHARE_BASES}")
    try:
        if len(pubmed_ids_of(row.pmids)) == 0:
            problems.append("no PubMed id")
    except ValueError as error:
        problems.append(str(error))
    if not str(row.quotes).strip():
        problems.append("no quote from the papers")
    return problems


def add_alternative_members(nodes: pd.DataFrame, edges: pd.DataFrame, relation_types: list[str], table: pd.DataFrame,
                            brain_expression: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], dict]:
    """The graph with each row's alternative made a member of every protein entity its primary is a member of, the
    primary's membership weight split between the two by expression (see the section comment above). A row that cannot
    be added as written raises; an entity the alternative already belongs to keeps both edges as they are and is
    reported, since the imported membership comes first."""
    if "member_of" not in relation_types:
        raise ValueError("the graph has no member_of relation")
    node_type_of = dict(zip(nodes.node_id, nodes.node_type))
    symbol_of = dict(zip(nodes.node_id, nodes.gene_symbol))
    problems = {row.Index: problems_of_alternative_row(row, node_type_of) for row in table.itertuples()}
    problems = {index: found for index, found in problems.items() if found}
    if problems:
        details = "; ".join(f"row {index + 2} ({table.loc[index, 'alternative_id']} for {table.loc[index, 'primary_id']}): {', '.join(found)}"
                            for index, found in problems.items())
        raise ValueError(f"alternative members that cannot be added: {details}")
    new_edges = edges.reset_index(drop=True).copy()
    if "weight" not in new_edges.columns:
        new_edges["weight"] = 1.0
    is_membership = new_edges.relation_type.eq("member_of") & new_edges.target_id.map(node_type_of).eq("protein_entity")
    rows, per_row = [], []
    for row in table.itertuples():
        share = alternative_share(symbol_of[row.alternative_id], symbol_of[row.primary_id], brain_expression, row.share_basis)
        s = share["share_of_alternative"]
        primary_rows = new_edges.index[is_membership & new_edges.source_id.eq(row.primary_id)]
        entities_of_alternative = set(new_edges.target_id[is_membership & new_edges.source_id.eq(row.alternative_id)])
        pmids = "; ".join(f"PMID {identifier}" for identifier in pubmed_ids_of(row.pmids))
        joined, already_members = [], []
        for index in primary_rows:
            entity = new_edges.at[index, "target_id"]
            if entity in entities_of_alternative:
                already_members.append(entity)
                continue
            primary_weight = 1.0 if pd.isna(new_edges.at[index, "weight"]) else float(new_edges.at[index, "weight"])
            new_edges.at[index, "weight"] = (1.0 - s) * primary_weight
            rows.append({"source_id": row.alternative_id, "target_id": entity, "relation_type": "member_of", "sign": 1.0,
                         "evidence_source": f"{ALTERNATIVE_EVIDENCE_PREFIX} for {row.primary_id[5:]}, decision {row.decision} ({pmids})",
                         "weight": s * primary_weight})
            joined.append(entity)
        per_row.append({"alternative": row.alternative_id, "primary": row.primary_id, **share,
                        "entities_joined": sorted(joined), "entities_already_holding_the_alternative": sorted(already_members)})
    added = pd.DataFrame(rows, columns=new_edges.columns)
    new_edges = pd.concat([new_edges, added], ignore_index=True).astype(new_edges.dtypes.to_dict()) if rows else new_edges
    new_nodes = nodes.copy()
    if "degree" in new_nodes.columns:
        counts = new_edges.source_id.value_counts().add(new_edges.target_id.value_counts(), fill_value=0)
        new_nodes["degree"] = counts.reindex(new_nodes.node_id).fillna(0).astype("int64").to_numpy()
    return new_nodes, new_edges, list(relation_types), {"edges_added": len(rows), "rows": per_row}
