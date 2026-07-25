#!/usr/bin/env python3
"""Network-free tests for phiweaver.canto.entry_queue (stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from phiweaver.canto import entry_queue as eq


def _section(md: str, display_name: str) -> str:
    """The body of the `### Fn. <display_name>` section, located by name not by number.

    Section numbers are assigned over the sections actually rendered, so they shift from paper
    to paper. Tests must therefore never hard-code `### F3.` — that coupling is what broke five
    of them when the headings moved to PHI-Canto's own display names.
    """
    for line in md.splitlines():
        if line.startswith("### F") and line.split(". ", 1)[-1].lower() == display_name.lower():
            return md.split(line, 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
    raise AssertionError(f"no section titled {display_name!r} in the queue")


def _entry_tables(md: str) -> str:
    """Everything in section F — i.e. every table a curator would actually type from.

    Use this to assert a parked item is *not* enterable. Asserting against one named section is
    too weak now that empty sections are omitted: if the only annotation of that type was parked,
    its section legitimately does not exist and a name lookup would error rather than pass.
    "Absent from every entry table" is the property these tests mean.
    """
    return md.split("## F. Annotation entry queue", 1)[1].split("## G.", 1)[0]


def _rec(**over):
    """A compact draft record; override the canto sub-block as needed."""
    canto = {
        "genes": [
            {"name": "GeneA", "uniprot": "P11111", "organism": "Fusarium x", "locus": "L1"},
            {"name": "GeneB", "uniprot": "", "organism": "Fusarium x", "locus": "L2",
             "note": "no UniProt entry"},
        ],
        "alleles": [
            {"name": "geneAΔ", "gene": "GeneA", "type": "deletion", "expression": "null"},
            {"name": "GeneA(reintroduced)", "gene": "GeneA", "type": "wild type",
             "expression": "wild-type level"},
            {"name": "geneBΔ", "gene": "GeneB", "type": "deletion", "expression": "null"},
        ],
        "genotypes": [
            {"name": "WT", "organism": "Fusarium x", "alleles": [], "role": "control"},
            {"name": "geneAΔ", "organism": "Fusarium x", "alleles": ["geneAΔ"], "role": "experimental"},
            {"name": "geneBΔ", "organism": "Fusarium x", "alleles": ["geneBΔ"], "role": "experimental"},
            {"name": "host wt", "organism": "Triticum aestivum", "alleles": [], "role": "host"},
        ],
        "metagenotypes": [
            {"name": "geneAΔ x host", "pathogen_genotype": "geneAΔ", "host_genotype": "host wt",
             "role": "experimental"},
            {"name": "WT x host", "pathogen_genotype": "WT", "host_genotype": "host wt", "role": "control"},
            {"name": "geneBΔ x host", "pathogen_genotype": "geneBΔ", "host_genotype": "host wt",
             "role": "experimental"},
        ],
        "annotations": [
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0001212", "term_name": "decreased hyphal growth",
             "evidence": "growth assay", "extensions": [], "conditions": "PDA", "figure": "Fig 1"},
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "", "term_name": "impaired autophagy", "evidence": "GFP flux",
             "extensions": [], "conditions": "MM-N", "figure": "Fig 3"},
            {"feature_type": "gene", "feature": "GeneA", "annotation_type": "molecular_function",
             "term_id": "GO:0005085", "term_name": "GEF activity",
             "evidence": "INTERPRETIVE — inferred from rescue, no direct assay",
             "extensions": [], "conditions": "", "figure": "Fig 8"},
            {"feature_type": "gene", "feature": "GeneA", "annotation_type": "physical_interaction",
             "term_id": "", "term_name": "physical interaction: GeneA – GeneB",
             "evidence": "Y2H + Co-IP", "extensions": [{"relation": "interactor", "value": "GeneB"}],
             "conditions": "", "figure": "Fig 1A"},
            {"feature_type": "metagenotype", "feature": "geneAΔ x host",
             "annotation_type": "pathogen_host_interaction_phenotype", "term_id": "PHIPO:0000015",
             "term_name": "reduced virulence", "evidence": "disease index",
             "extensions": [{"relation": "compared_to_control", "value": "WT x host"}],
             "conditions": "wheat", "figure": "Fig 2"},
            {"feature_type": "metagenotype", "feature": "WT x host", "annotation_type": "disease_name",
             "term_id": "PHIDO:0000162", "term_name": "Fusarium ear blight", "evidence": "",
             "extensions": [], "conditions": "", "figure": "Fig 2"},
            # annotation on a held gene -> must be parked
            {"feature_type": "genotype", "feature": "geneBΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0000052", "term_name": "decreased conidiation",
             "evidence": "growth assay", "extensions": [], "conditions": "", "figure": "Fig 4"},
        ],
    }
    canto.update(over.get("canto", {}))
    return {"meta": {"pmid": "999", "paper": "Test et al.", "system": "Fx -> wheat",
                     "model": "Fable 5", "date": "2026-07-08"}, "canto": canto}


class HeldGeneCascadeTests(unittest.TestCase):
    def setUp(self):
        self.md, self.counts = eq.render_entry_queue(_rec())

    def test_summary_counts(self):
        self.assertEqual(self.counts["genes_enter"], 1)   # GeneA
        self.assertEqual(self.counts["genes_held"], 1)    # GeneB (no accession)

    def test_held_gene_marked_hold_not_enter(self):
        # GeneB row is 'hold'; GeneA row is 'enter'
        self.assertRegex(self.md, r"GeneB.*unresolved.*hold")
        self.assertRegex(self.md, r"GeneA.*UniProtKB:P11111.*enter")

    def test_held_allele_and_genotype_not_in_entry_tables(self):
        # geneBΔ allele + genotype cascade to parked; not in the create tables
        c_section = self.md.split("## C. Create pathogen genotypes")[1].split("## D.")[0]
        self.assertNotIn("geneBΔ", c_section)

    def test_annotation_on_held_gene_is_parked(self):
        parked = self.md.split("## G. Parked items")[1]
        self.assertIn("decreased conidiation", parked)

    def test_blank_term_annotation_parked(self):
        parked = self.md.split("## G. Parked items")[1]
        self.assertIn("impaired autophagy", parked)
        self.assertIn("no ontology term resolved", parked)

    def test_interpretive_mf_parked(self):
        parked = self.md.split("## G. Parked items")[1]
        self.assertIn("interpretive molecular-function", parked)
        # and NOT enterable: absent from every table in section F
        self.assertNotIn("GEF activity", _entry_tables(self.md))


class HostPathogenSplitTests(unittest.TestCase):
    def setUp(self):
        self.md, _ = eq.render_entry_queue(_rec())

    def test_host_genotype_in_section_d(self):
        d = self.md.split("## D. Create host genotype")[1].split("## E.")[0]
        self.assertIn("host wt", d)

    def test_pathogen_genotype_not_in_host_table(self):
        d = self.md.split("## D. Create host genotype")[1].split("## E.")[0]
        self.assertNotIn("| ☐ | WT |", d)


class PhysicalInteractionAndTableSafetyTests(unittest.TestCase):
    def setUp(self):
        self.md, _ = eq.render_entry_queue(_rec())

    def test_physical_interaction_enterable_despite_blank_term(self):
        f = _section(self.md, "physical interaction")
        self.assertIn("GeneB", f)           # interactor listed
        self.assertIn("pick PSI-MI at entry", f)

    def test_pipe_in_data_is_escaped(self):
        rec = _rec(canto={"genes": [
            {"name": "wei|rd", "uniprot": "P1", "organism": "Fx", "locus": ""}]})
        md, _ = eq.render_entry_queue(rec)
        self.assertIn("wei\\|rd", md)       # escaped so the table can't corrupt

    def test_disease_name_uses_current_id(self):
        self.assertIn("PHIDO:0000162", _section(self.md, "disease name"))


class QualifierPhraseAnnotationTests(unittest.TestCase):
    """RNA/protein-level annotations carry a controlled phrase, not an ontology ID."""

    RNA = {"feature_type": "gene", "feature": "GeneA", "annotation_type": "wt_rna_expression",
           "term_id": "", "term_name": "RNA level increased", "evidence": "Northern assay",
           "extensions": [], "conditions": "PECO:0000257 + cycloheximide", "figure": "Figure 7A"}

    def _render(self, annotation):
        rec = _rec()
        rec["canto"]["annotations"] = rec["canto"]["annotations"] + [annotation]
        return eq.render_entry_queue(rec)

    def test_qualifier_phrase_is_enterable_and_visible(self):
        md, _ = self._render(self.RNA)
        f = _section(md, "Wild-type RNA level")
        self.assertIn("RNA level increased", f)
        self.assertIn("Northern assay", f)

    def test_blank_qualifier_is_still_parked(self):
        # An empty term_name means nothing was resolved — that must stay parked.
        md, _ = self._render({**self.RNA, "term_name": ""})
        self.assertNotIn("Wild-type RNA level", md)
        self.assertIn("no ontology term resolved", md)


class IntegrityAndStatusTests(unittest.TestCase):
    def test_dangling_allele_reference_parked(self):
        # an allele pointing at an undefined gene must be parked, not entered
        rec = _rec(canto={"alleles": [
            {"name": "orphanΔ", "gene": "GhostGene", "type": "deletion", "expression": "null"}]})
        md, _ = eq.render_entry_queue(rec)
        b = md.split("## B. Create alleles")[1].split("## C.")[0]
        self.assertNotIn("orphanΔ", b)
        parked = md.split("## G. Parked items")[1]
        self.assertIn("orphanΔ", parked)
        self.assertIn("undefined gene", parked)

    def test_annotation_with_undefined_subject_parked(self):
        rec = _rec(canto={"annotations": [
            {"feature_type": "genotype", "feature": "NoSuchGenotype",
             "annotation_type": "pathogen_phenotype", "term_id": "PHIPO:0000001",
             "term_name": "x", "evidence": "y", "extensions": [], "conditions": "", "figure": "F1"}]})
        md, _ = eq.render_entry_queue(rec)
        parked = md.split("## G. Parked items")[1]
        self.assertIn("is not defined", parked)

    def test_status_passthrough(self):
        md, _ = eq.render_entry_queue(_rec(), status="validated")
        self.assertIn("Status: validated", md)

    def test_status_defaults_to_draft(self):
        md, _ = eq.render_entry_queue(_rec())
        self.assertIn("Status: draft (not validated)", md)


class ExplicitHoldTests(unittest.TestCase):
    def test_explicit_hold_parks_with_reason(self):
        rec = _rec(canto={"annotations": [
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0000001", "term_name": "some phenotype", "evidence": "assay",
             "extensions": [], "conditions": "PDA", "figure": "F1",
             "hold": True, "hold_reason": "penetrance not quantified — curator confirm"}]})
        md, _ = eq.render_entry_queue(rec)
        parked = md.split("## G. Parked items")[1]
        self.assertIn("penetrance not quantified", parked)
        # and it is NOT enterable: absent from every table in section F
        self.assertNotIn("some phenotype", _entry_tables(md))

    def test_note_stays_out_of_entry_queue(self):
        rec = _rec(canto={"annotations": [
            {"feature_type": "genotype", "feature": "geneAΔ", "annotation_type": "pathogen_phenotype",
             "term_id": "PHIPO:0000001", "term_name": "enterable phenotype", "evidence": "assay",
             "extensions": [], "conditions": "PDA", "figure": "F1",
             "note": "SECRET-CURATOR-NOTE that must not appear in the lean queue"}]})
        md, _ = eq.render_entry_queue(rec)
        self.assertIn("enterable phenotype", md)          # the annotation is entered
        self.assertNotIn("SECRET-CURATOR-NOTE", md)       # but its note is not shown here


class GuardTests(unittest.TestCase):
    def _write(self, text):
        p = Path(tempfile.mkdtemp()) / "d.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_no_json_block_raises(self):
        p = self._write("# draft with no json block\n")
        with self.assertRaises(SystemExit):
            eq.queue_for_draft(p)

    def test_json_without_canto_raises(self):
        p = self._write("```json\n{\"meta\": {}}\n```\n")
        with self.assertRaises(SystemExit):
            eq.queue_for_draft(p)


class AnnotationSectionsMirrorCantoTests(unittest.TestCase):
    """Section F mirrors PHI-Canto: one section per annotation type, its own display names."""

    def _with(self, *annotations):
        rec = _rec()
        rec["canto"]["annotations"] = rec["canto"]["annotations"] + list(annotations)
        return eq.render_entry_queue(rec)[0]

    HOST_PHEN = {"feature_type": "genotype", "feature": "host wt",
                 "annotation_type": "host_phenotype", "term_id": "PHIPO:0000001",
                 "term_name": "host marker term", "evidence": "lesion assay",
                 "extensions": [], "conditions": "", "figure": "Fig 9"}
    PTM = {"feature_type": "gene", "feature": "GeneA",
           "annotation_type": "post_translational_modification", "term_id": "MOD:00046",
           "term_name": "O-phospho-L-serine", "evidence": "western", "extensions": [],
           "conditions": "", "figure": "Fig 8"}

    def test_every_configured_annotation_type_has_a_section(self):
        """The regression guard: a type with no section vanished from the queue entirely.

        `host_phenotype` and `post_translational_modification` did exactly that until
        2026-07-25 — enter-ready, unparked, and invisible.
        """
        covered = {atype for atype, _display, _shape in eq.ANNOTATION_SECTIONS}
        from phiweaver.lookup.canto_config import load_config
        configured = set(load_config().annotation_types)
        self.assertEqual(configured - covered, set(),
                         "PHI-Canto annotation types with no entry-queue section")

    def test_headings_use_canto_display_names(self):
        md = self._with(self.HOST_PHEN, self.PTM)
        # Capitalisation is the session page's, not the config's: canto_deploy.yaml stores
        # "pathogen phenotype" but the UI renders "Pathogen phenotype".
        for expected in ("### F1. Host phenotype", "### F2. Pathogen phenotype",
                         "### F3. Pathogen-host interaction phenotype",
                         "### F4. Protein modification", "### F5. Physical interaction",
                         "### F6. Disease name"):
            self.assertIn(expected, md)

    def test_host_phenotype_is_enterable(self):
        self.assertIn("host marker term", _section(self._with(self.HOST_PHEN), "host phenotype"))

    def test_protein_modification_is_enterable(self):
        self.assertIn("O-phospho-L-serine", _section(self._with(self.PTM), "protein modification"))

    def test_a_term_less_protein_modification_stays_parked(self):
        """Unlike physical interaction, PTM is not exempt from needing its term.

        PI is exempt because it genuinely has no ontology term (the evidence method carries it).
        A protein-modification annotation does take a PSI-MOD term, so a blank one is a real gap
        and must stay parked rather than being offered for entry.
        """
        md = self._with({**self.PTM, "term_id": ""})
        self.assertNotIn("O-phospho-L-serine", _entry_tables(md))
        self.assertIn("no ontology term resolved", md.split("## G. Parked items")[1])

    def test_empty_sections_are_omitted(self):
        md = self._with()
        self.assertNotIn("GO biological process", md)   # fixture has no BP annotation
        self.assertNotIn("Gene-for-gene phenotype", md)

    def test_sections_are_numbered_without_gaps(self):
        md = self._with(self.HOST_PHEN, self.PTM)
        numbers = [int(ln.split(".", 1)[0][5:]) for ln in md.splitlines()
                   if ln.startswith("### F")]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_gene_for_gene_is_its_own_section_not_merged(self):
        md = self._with({"feature_type": "metagenotype", "feature": "geneAΔ x host",
                         "annotation_type": "gene_for_gene_phenotype",
                         "term_id": "PHIPO:0000015", "term_name": "gfg marker term",
                         "evidence": "infection assay", "extensions": [], "conditions": "",
                         "figure": "Fig 5"})
        self.assertIn("gfg marker term", _section(md, "gene-for-gene phenotype"))
        # and it did not also land in the interaction table it used to share
        self.assertNotIn("gfg marker term",
                         _section(md, "pathogen-host interaction phenotype"))

    def test_an_unknown_type_is_parked_with_a_reason_not_dropped(self):
        """A future 13th PHI-Canto type must fail loudly, not disappear."""
        md = self._with({"feature_type": "gene", "feature": "GeneA",
                         "annotation_type": "some_future_type", "term_id": "XX:1",
                         "term_name": "future marker term", "evidence": "assay",
                         "extensions": [], "conditions": "", "figure": "Fig 1"})
        self.assertNotIn("future marker term", _entry_tables(md))
        parked = md.split("## G. Parked items")[1]
        self.assertIn("future marker term", parked)
        self.assertIn("no entry-queue section for annotation type 'some_future_type'", parked)


class StrainsSectionTests(unittest.TestCase):
    """A2 prompts Canto's required *Adding strains* step without inventing a strain."""

    def setUp(self):
        self.md, _ = eq.render_entry_queue(_rec())
        self.a2 = self.md.split("### A2.")[1].split("\n## ", 1)[0]

    def test_one_row_per_organism(self):
        self.assertIn("Fusarium x", self.a2)
        self.assertIn("Triticum aestivum", self.a2)

    def test_roles_come_from_metagenotype_use_not_the_species_name(self):
        for line in self.a2.splitlines():
            if "Fusarium x" in line:
                self.assertIn("pathogen", line)
            if "Triticum aestivum" in line:
                self.assertIn("host", line)

    def test_strain_is_never_guessed_from_the_genotype_name(self):
        # The fixture carries no `strain` field, so every cell must stay unset.
        for line in self.a2.splitlines():
            if line.startswith("| ☐ |"):
                self.assertIn("— set in Canto", line)

    def test_mutant_genotypes_are_excluded(self):
        """Curator ruling 2026-07-25: only a wild type carries a strain.

        `geneAΔ` is the allele-bearing mutant — it is named by its allele, so it must not be
        offered as a strain the way `AM25` wrongly was before the ruling.
        """
        self.assertNotIn("geneAΔ", self.a2)
        self.assertIn("WT", self.a2)          # the allele-free wild type is offered
        self.assertIn("host wt", self.a2)

    def test_an_explicit_strain_field_is_used_verbatim(self):
        rec = _rec()
        for g in rec["canto"]["genotypes"]:
            if g["name"] == "WT":
                g["strain"] = "Guy11"
        md, _ = eq.render_entry_queue(rec)
        a2 = md.split("### A2.")[1].split("\n## ", 1)[0]
        for line in a2.splitlines():
            if "Fusarium x" in line:
                self.assertIn("Guy11", line)
                self.assertNotIn("— set in Canto", line)

    def test_comes_before_the_genotype_sections(self):
        # Canto requires a strain before a genotype can be created.
        self.assertLess(self.md.index("### A2."),
                        self.md.index("## C. Create pathogen genotypes"))

    def test_omitted_when_no_organism_is_known(self):
        md, _ = eq.render_entry_queue(_rec(canto={"genes": [], "genotypes": [],
                                                  "metagenotypes": [], "annotations": []}))
        self.assertNotIn("### A2.", md)


class CantoDisplayNamesMatchTheLiveConfigTests(unittest.TestCase):
    """Our hardcoded display names must still match PHI-Canto's own.

    The labels are hardcoded so the queue renders identically on every machine (the deploy
    config is gitignored, so a config-driven heading would differ on a fresh clone). The cost
    of hardcoding is drift, so this check pays it back: where the private deploy file *is*
    present, an upstream rename or a new type fails here instead of silently diverging.
    Skipped rather than failed when the file is absent — a skip says "couldn't check", which
    is the truth, whereas a failure would claim weaver is broken when it is merely unconfigured.
    """

    def setUp(self):
        from phiweaver.lookup.canto_config import DEPLOY_CONFIG, load_config
        if not DEPLOY_CONFIG.exists():
            self.skipTest("private canto_deploy.yaml absent; cannot compare display names")
        self.raw = load_config().raw

    def test_display_names_and_order_match_canto(self):
        live = [(a["name"], a["display_name"])
                for a in self.raw.get("available_annotation_type_list", [])
                if isinstance(a, dict) and "display_name" in a]
        ours = [(atype, display) for atype, display, _shape in eq.ANNOTATION_SECTIONS]
        self.assertEqual(ours, live,
                         "entry_queue.ANNOTATION_SECTIONS has drifted from PHI-Canto's config")


if __name__ == "__main__":
    unittest.main()
