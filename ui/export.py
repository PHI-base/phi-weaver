"""
Convert a phi-weaver extraction dict into the two formats Canto needs:

1. canto_load_json   — keyed by PMID, understood by LoadUtil::create_sessions_from_json
                       (genes, alleles, genotypes)

2. phi_weaver_json   — our extended format that the new PHIWeaverImport Perl module
                       will use for metagenotypes + annotations

Both are bundled into one file so the importer can use whichever it needs.
"""

import json
import uuid
from datetime import date


def _session_key() -> str:
    return "phiw-" + uuid.uuid4().hex[:8]


def _allele_uniquename(allele: dict, session_key: str, index: int) -> str:
    gene = allele.get("gene_systematic_id") or allele.get("gene_name") or "gene"
    return f"{gene}:{session_key}-{index + 1}"


def to_canto_json(data: dict) -> dict:
    """Return the full export bundle with both sections."""
    pmid = (data.get("article") or {}).get("pmid")
    pub_key = f"PMID:{pmid}" if pmid else "PMID:UNKNOWN"
    session_key = _session_key()
    today = str(date.today())

    alleles    = data.get("alleles", [])
    pg_list    = data.get("pathogen_genotypes", [])
    hg_list    = data.get("host_genotypes", [])
    mg_list    = data.get("metagenotypes", [])
    genes      = data.get("genes", [])

    # ── 1. allele uniquename map ─────────────────────────────────────────────
    allele_uid: dict[str, str] = {}          # allele["id"] → uniquename
    canto_alleles: dict[str, dict] = {}

    for i, a in enumerate(alleles):
        uid = _allele_uniquename(a, session_key, i)
        allele_uid[a["id"]] = uid
        entry: dict = {
            "gene":        a.get("gene_systematic_id") or a.get("gene_name"),
            "type":        a.get("type", "unknown"),
        }
        if a.get("name"):        entry["name"]        = a["name"]
        if a.get("description"): entry["description"] = a["description"]
        if a.get("expression"):  entry["expression"]  = a["expression"]
        canto_alleles[uid] = entry

    # ── 2. genes ─────────────────────────────────────────────────────────────
    canto_genes: dict[str, dict] = {}
    for g in genes:
        sid = g.get("systematic_id") or g.get("gene_name")
        if sid:
            canto_genes[sid] = {}   # LoadUtil looks them up from the gene DB

    # also ensure every allele's gene is listed
    for a in alleles:
        sid = a.get("gene_systematic_id") or a.get("gene_name")
        if sid and sid not in canto_genes:
            canto_genes[sid] = {}

    # ── 3. genotypes ─────────────────────────────────────────────────────────
    genotype_uid: dict[str, str] = {}        # our id → canto uniquename
    canto_genotypes: dict[str, dict] = {}

    for geno in pg_list + hg_list:
        canto_id = f"{session_key}-{geno['id']}"
        genotype_uid[geno["id"]] = canto_id
        allele_refs = [
            {"allele_uniquename": allele_uid[aid]}
            for aid in geno.get("allele_ids", [])
            if aid in allele_uid
        ]
        entry: dict = {
            "genotype_name": geno.get("label", ""),
            "background":    geno.get("background", ""),
            "taxon_id":      geno.get("taxon_id"),
            "alleles":       allele_refs,
        }
        if geno.get("strain"):
            entry["strain"] = geno["strain"]
        canto_genotypes[canto_id] = entry

    # ── 4. metagenotypes (extended section) ──────────────────────────────────
    ext_metagenotypes: dict[str, dict] = {}
    ext_annotations: list[dict] = []

    for mg in mg_list:
        canto_mg_id = f"{session_key}-{mg['id']}"
        pg_uid = genotype_uid.get(mg.get("pathogen_genotype_id", ""), "")
        hg_uid = genotype_uid.get(mg.get("host_genotype_id", ""), "")

        ext_metagenotypes[canto_mg_id] = {
            "pathogen_genotype": pg_uid,
            "host_genotype":     hg_uid,
            "type":              "pathogen-host",
            "is_control":        mg.get("is_control", False),
        }

        for ann in mg.get("interaction_annotations", []):
            ext_annotations.append({
                "type":            "metagenotype_phenotype",
                "status":          "new",
                "publication":     pub_key,
                "creation_date":   today,
                "metagenotype":    canto_mg_id,
                "phipo_term":      ann.get("phipo_term"),
                "evidence_code":   ann.get("evidence_code", "IMP"),
                "host_tissue":     ann.get("host_tissue"),
                "host_tissue_bto": ann.get("host_tissue_bto"),
                "infective_ability": ann.get("infective_ability"),
                "conditions":      ann.get("conditions", []),
                "figure":          ann.get("figure"),
                "comment":         ann.get("comment", ""),
                "curator":         {"name": "PHI-Weaver AI", "email": "phi-weaver@automated", "community_curated": False},
            })

        for ann in mg.get("disease_annotations", []):
            ext_annotations.append({
                "type":            "metagenotype_disease",
                "status":          "new",
                "publication":     pub_key,
                "creation_date":   today,
                "metagenotype":    canto_mg_id,
                "disease_name":    ann.get("disease_name"),
                "host_tissue":     ann.get("host_tissue"),
                "host_tissue_bto": ann.get("host_tissue_bto"),
                "figure":          ann.get("figure"),
                "curator":         {"name": "PHI-Weaver AI", "email": "phi-weaver@automated", "community_curated": False},
            })

    # GO + phenotype annotations on genes / pathogen genotypes
    for g in genes:
        sid = g.get("systematic_id") or g.get("gene_name")
        for ann in g.get("go_annotations", []):
            ext_annotations.append({
                "type":          "biological_process" if ann.get("go_aspect") == "biological_process"
                                  else "molecular_function" if ann.get("go_aspect") == "molecular_function"
                                  else "cellular_component",
                "status":        "new",
                "publication":   pub_key,
                "creation_date": today,
                "gene":          sid,
                "go_id":         ann.get("go_id"),
                "go_term":       ann.get("go_term"),
                "evidence_code": ann.get("evidence_code", "IMP"),
                "figure":        ann.get("figure"),
                "curator":       {"name": "PHI-Weaver AI", "email": "phi-weaver@automated", "community_curated": False},
            })

    for pg in pg_list:
        canto_pg_uid = genotype_uid.get(pg["id"], "")
        for ann in pg.get("phenotype_annotations", []):
            ext_annotations.append({
                "type":          "genotype_phenotype",
                "status":        "new",
                "publication":   pub_key,
                "creation_date": today,
                "genotype":      canto_pg_uid,
                "phipo_term":    ann.get("phipo_term"),
                "evidence_code": ann.get("evidence_code", "IMP"),
                "conditions":    ann.get("conditions", []),
                "figure":        ann.get("figure"),
                "comment":       ann.get("comment", ""),
                "curator":       {"name": "PHI-Weaver AI", "email": "phi-weaver@automated", "community_curated": False},
            })

    # ── assemble output ──────────────────────────────────────────────────────
    return {
        "phi_weaver_version": "1.0",
        "session_key":        session_key,
        "exported_date":      today,
        "curation_notes":     data.get("curation_notes", ""),
        "article":            data.get("article", {}),
        "organisms":          data.get("organisms", {}),

        # LoadUtil-compatible section (genes + alleles + genotypes)
        "canto_load": {
            pub_key: {
                "genes":     canto_genes,
                "alleles":   canto_alleles,
                "genotypes": canto_genotypes,
            }
        },

        # Extended section (metagenotypes + annotations — consumed by PHIWeaverImport.pm)
        "phi_weaver_extended": {
            "session_key":    session_key,
            "publication":    pub_key,
            "metagenotypes":  ext_metagenotypes,
            "annotations":    ext_annotations,
        },
    }


def to_json_str(data: dict) -> str:
    return json.dumps(to_canto_json(data), indent=2, ensure_ascii=False)
