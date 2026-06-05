#!/usr/bin/env python3
"""
Generate canto_load.pl commands and TSV files from a phi-weaver export JSON.

Usage:
  python3 ui/canto_load_genes.py <export_json> [--tsv-dir <dir>]

This reads the gene metadata from a phi-weaver *_phi_canto.json file and:
  1. Writes one TSV file per organism (format: systematic_id, name, synonyms, product)
  2. Prints the canto_load.pl command to run for each organism

Run these commands inside your Canto container before importing the JSON:
  docker exec <container> ./script/canto_load.pl --genes fg_genes.tsv --for-taxon=229533
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def _infer_gene_taxons(pub_data: dict) -> dict:
    """Build gene_name → taxon_id map from genotype→allele→gene chain."""
    alleles   = pub_data.get("alleles", {})
    genotypes = pub_data.get("genotypes", {})
    gene_taxon: dict[str, int] = {}
    for geno in genotypes.values():
        taxon = geno.get("taxon_id")
        if not taxon:
            continue
        for aref in geno.get("alleles", []):
            auid = aref.get("allele_uniquename", "")
            allele_data = alleles.get(auid, {})
            gene_name = allele_data.get("gene") or auid.split(":")[0]
            if gene_name:
                gene_taxon.setdefault(gene_name, taxon)
    return gene_taxon


def _org_name_by_taxon(data: dict) -> dict:
    """Build taxon_id → organism name from the organisms section."""
    mapping: dict[int, str] = {}
    organisms = data.get("organisms", {})
    for org_list in [organisms.get("pathogens", []), organisms.get("hosts", [])]:
        for org in org_list:
            if org.get("taxon_id"):
                mapping[org["taxon_id"]] = org["name"]
    return mapping


def load_genes_from_json(json_path: str) -> tuple[dict, dict]:
    data = json.loads(Path(json_path).read_text())
    return data.get("canto_load", {}), data


def generate_tsv_files(canto_load: dict, full_data: dict, tsv_dir: Path) -> list[dict]:
    tsv_dir.mkdir(parents=True, exist_ok=True)

    org_by_taxon = _org_name_by_taxon(full_data)

    # Group genes by taxon_id across all publications
    by_taxon: dict[int, list[dict]] = defaultdict(list)

    for pub_key, pub_data in canto_load.items():
        # Build fallback taxon map from genotype structure
        inferred_taxon = _infer_gene_taxons(pub_data)

        for gene_id, gene_meta in (pub_data.get("genes") or {}).items():
            taxon = gene_meta.get("taxon_id") or inferred_taxon.get(gene_id)
            if not taxon:
                print(f"  [skip] {gene_id}: cannot determine taxon_id", file=sys.stderr)
                continue
            organism = (gene_meta.get("organism_name")
                        or org_by_taxon.get(taxon)
                        or f"taxon:{taxon}")
            by_taxon[taxon].append({
                "gene_id":      gene_id,
                "gene_name":    gene_meta.get("gene_name") or gene_id,
                "systematic_id": gene_meta.get("systematic_id") or gene_id,
                "product":      gene_meta.get("product") or "",
                "organism":     organism,
            })

    results = []
    for taxon, gene_list in sorted(by_taxon.items()):
        # Deduplicate by systematic_id
        seen: set[str] = set()
        unique = []
        for g in gene_list:
            if g["systematic_id"] not in seen:
                seen.add(g["systematic_id"])
                unique.append(g)

        organism_slug = unique[0]["organism"].replace(" ", "_").replace("/", "-")[:30]
        tsv_name = f"genes_{organism_slug}_{taxon}.tsv"
        tsv_path = tsv_dir / tsv_name

        with open(tsv_path, "w") as f:
            for g in unique:
                # Format: systematic_id \t name \t synonyms \t product
                f.write(f"{g['systematic_id']}\t{g['gene_name']}\t\t{g['product']}\n")

        results.append({
            "taxon_id":    taxon,
            "organism":    unique[0]["organism"],
            "gene_count":  len(unique),
            "tsv_path":    str(tsv_path),
            "tsv_name":    tsv_name,
        })

    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    json_path = sys.argv[1]
    tsv_dir_arg = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--tsv-dir" else "."
    tsv_dir = Path(tsv_dir_arg)

    canto_load, full_data = load_genes_from_json(json_path)
    if not canto_load:
        print("No canto_load section found in JSON.")
        sys.exit(1)

    results = generate_tsv_files(canto_load, full_data, tsv_dir)

    if not results:
        print("No genes with taxon_ids found.")
        sys.exit(1)

    print("\n=== Gene TSV files generated ===\n")
    for r in results:
        print(f"  {r['organism']} (taxon:{r['taxon_id']}) — {r['gene_count']} gene(s)")
        print(f"  File: {r['tsv_path']}")

    print("\n=== Run these commands inside your Canto container ===\n")
    for r in results:
        print(f"# {r['organism']}")
        print(f"docker exec <canto-container> ./script/canto_load.pl \\")
        print(f"  --genes /import_export/{r['tsv_name']} \\")
        print(f"  --for-taxon={r['taxon_id']}")
        print()

    print("=== Then import the JSON at http://localhost:5001/phi_weaver/import ===\n")

    # Copy TSVs to import_export dir hint
    import_export = Path("../CantoData/import_export")
    if import_export.exists():
        import textwrap
        print(f"Tip: copy TSVs to {import_export} so they're accessible in the container:")
        for r in results:
            print(f"  cp {r['tsv_path']} {import_export}/{r['tsv_name']}")
        print()


if __name__ == "__main__":
    main()
