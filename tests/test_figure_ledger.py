#!/usr/bin/env python3
"""Tests for the figure-inspection ledger.

The point of the ledger is that "I looked at the figures" stops being an unverifiable
boolean, so these tests concentrate on the ways a draft can claim inspection it did not do.
"""

import struct
import unittest
from pathlib import Path

from phiweaver import figure_ledger as fl
from phiweaver.canto import entry_queue as eq


def _rec(figures=None, annotations=None):
    return {
        "figure_inspection": {"figures": figures or []},
        "canto": {"genes": [], "alleles": [], "genotypes": [], "metagenotypes": [],
                  "annotations": annotations or []},
        "meta": {"pmid": "39852455"},
    }


def _report(labels, not_openable=()):
    return {"figures": [{"label": l, "openable": l not in not_openable} for l in labels]}


class LabelParsingTests(unittest.TestCase):
    def test_normalises_common_spellings(self):
        for raw in ("Figure 5", "figure 5", "Fig 5", "Fig. 5", "Fig 5A,B", "5"):
            self.assertEqual(fl.normalise_label(raw), "Figure 5", raw)

    def test_citation_string_yields_every_figure(self):
        self.assertEqual(fl.figures_cited("Figure 5A,C; Figure 7A"),
                         ["Figure 5", "Figure 7"])
        self.assertEqual(fl.figures_cited("Figure 4B"), ["Figure 4"])

    def test_citation_string_deduplicates(self):
        self.assertEqual(fl.figures_cited("Figure 5A and Figure 5B"), ["Figure 5"])

    def test_non_figure_text_yields_nothing(self):
        self.assertEqual(fl.figures_cited("Section 1; Section 4"), [])
        self.assertEqual(fl.figures_cited(""), [])


class InspectionSemanticsTests(unittest.TestCase):
    def test_ticked_without_a_reading_does_not_count(self):
        # The core rule: ticking a box is not looking at a figure.
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": ""}])
        result = fl.audit(rec)
        self.assertEqual(result["inspected"], [])
        self.assertEqual(result["claimed_not_read"], ["Figure 1"])
        self.assertFalse(result["complete"])

    def test_whitespace_reading_does_not_count(self):
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": "   "}])
        self.assertEqual(fl.audit(rec)["claimed_not_read"], ["Figure 1"])

    def test_reading_recorded_counts_as_inspected(self):
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": "axis in nm, ~95 vs ~45"}])
        result = fl.audit(rec)
        self.assertEqual(result["inspected"], ["Figure 1"])
        self.assertTrue(result["complete"])

    def test_declined_with_a_reason_is_honest_not_an_error(self):
        rec = _rec([{"label": "Figure 2", "inspected": False, "read": "",
                     "note": "sequence alignment; nothing depends on it"}])
        result = fl.audit(rec)
        self.assertEqual(result["declined"], ["Figure 2"])
        self.assertEqual(result["claimed_not_read"], [])


class RosterCrossCheckTests(unittest.TestCase):
    def test_figure_with_no_ledger_entry_is_reported_but_not_a_failure(self):
        # Under decline-by-default a figure nobody needed and nobody opened is the
        # expected state, so it is reported without failing the draft.
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": "x"}])
        result = fl.audit(rec, _report(["Figure 1", "Figure 2"]))
        self.assertEqual(result["missing"], ["Figure 2"])
        self.assertTrue(result["complete"])

    def test_ledger_entry_for_a_nonexistent_figure_is_flagged(self):
        rec = _rec([{"label": "Figure 9", "inspected": True, "read": "x"}])
        self.assertEqual(fl.audit(rec, _report(["Figure 1"]))["unknown"], ["Figure 9"])

    def test_total_comes_from_the_roster_not_the_ledger(self):
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": "x"}])
        self.assertEqual(fl.audit(rec, _report(["Figure 1", "Figure 2", "Figure 3"]))
                         ["total_figures"], 3)

    def test_unavailable_image_is_reported_as_such(self):
        rec = _rec(annotations=[{"term_id": "PHIPO:1", "figure": "Figure 3",
                                 "needs_figure": True}])
        result = fl.audit(rec, _report(["Figure 3"], not_openable=["Figure 3"]))
        self.assertEqual(result["annotations_on_uninspected"][0]["reason"],
                         "image not available")


class AnnotationDependencyTests(unittest.TestCase):
    """The check that caught a real error: a figure declared irrelevant that two
    annotations actually cited."""

    def test_annotation_marked_needs_figure_is_flagged(self):
        rec = _rec(
            figures=[{"label": "Figure 7", "inspected": False, "read": "",
                      "note": "nothing depends on it"}],
            annotations=[{"term_id": "GO:0010508", "term_name": "positive regulation of autophagy",
                          "feature": "sec2", "figure": "Figure 5A,C; Figure 7A",
                          "needs_figure": True}])
        result = fl.audit(rec)
        self.assertEqual([f["figure"] for f in result["annotations_on_uninspected"]],
                         ["Figure 5", "Figure 7"])
        self.assertFalse(result["complete"])

    def test_unmarked_annotation_is_informational_not_a_failure(self):
        # Decline-by-default: curating this from text and captions is the normal path,
        # so it is reported for discovery but does not fail the draft.
        rec = _rec(
            figures=[{"label": "Figure 7", "inspected": False, "read": "", "note": "n/a"}],
            annotations=[{"term_id": "GO:0010508", "figure": "Figure 7A"}])
        result = fl.audit(rec)
        self.assertEqual(result["annotations_on_uninspected"], [])
        self.assertEqual([f["figure"] for f in result["optional_uninspected"]],
                         ["Figure 7"])
        self.assertTrue(result["complete"])

    def test_needs_figure_reason_is_carried_through(self):
        rec = _rec(annotations=[{"term_id": "PHIPO:0000985", "figure": "Figure 4C",
                                 "needs_figure": True,
                                 "needs_figure_reason": "qualitative histopathology claim"}])
        item = fl.audit(rec)["annotations_on_uninspected"][0]
        self.assertEqual(item["why_needed"], "qualitative histopathology claim")

    def test_annotation_on_inspected_figures_is_not_flagged(self):
        rec = _rec(
            figures=[{"label": "Figure 5", "inspected": True, "read": "nm axis"}],
            annotations=[{"term_id": "PHIPO:0000379", "figure": "Figure 5A,B"}])
        self.assertEqual(fl.audit(rec)["annotations_on_uninspected"], [])

    def test_annotation_citing_no_figure_is_ignored(self):
        rec = _rec(figures=[{"label": "Figure 1", "inspected": True, "read": "x"}],
                   annotations=[{"term_id": "GO:1", "figure": "Section 1"}])
        self.assertEqual(fl.audit(rec)["annotations_on_uninspected"], [])


class DerivedFlagTests(unittest.TestCase):
    def test_flag_is_derived_not_trusted(self):
        # meta says inspected; the ledger says one figure was ticked without a reading.
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": ""}])
        rec["meta"]["figures_inspected"] = True
        self.assertFalse(fl.figures_inspected_flag(rec))

    def test_no_ledger_yields_none_not_false(self):
        # Absent evidence is unknown, not a negative claim.
        self.assertIsNone(fl.figures_inspected_flag({"canto": {}}))


class SummaryLineTests(unittest.TestCase):
    def test_clean_ledger_reads_plainly(self):
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": "x"}])
        self.assertEqual(fl.summary_line(fl.audit(rec)), "**Figures inspected:** 1/1")

    def test_problems_are_warned(self):
        rec = _rec(figures=[{"label": "Figure 1", "inspected": True, "read": ""}])
        line = fl.summary_line(fl.audit(rec))
        self.assertIn("⚠️", line)
        self.assertIn("ticked without a reading", line)

    def test_no_ledger_yields_no_line(self):
        self.assertEqual(fl.summary_line(fl.audit({"canto": {}})), "")


class ImageMeasurementTests(unittest.TestCase):
    """Header-only sizing, so the token cost of a figure is knowable before reading it."""

    def _write(self, name, data):
        import tempfile
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        p = Path(d.name) / name
        p.write_bytes(data)
        return p

    def test_jpeg_dimensions(self):
        data = b"\xff\xd8" + b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", 455, 716) + b"\x03" * 8
        self.assertEqual(fl.image_dimensions(self._write("f.jpg", data)), (716, 455))

    def test_png_dimensions(self):
        data = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 800, 600)
        self.assertEqual(fl.image_dimensions(self._write("f.png", data)), (800, 600))

    def test_gif_dimensions(self):
        data = b"GIF89a" + struct.pack("<HH", 120, 90) + b"\x00" * 8
        self.assertEqual(fl.image_dimensions(self._write("f.gif", data)), (120, 90))

    def test_non_image_and_missing_file_degrade(self):
        self.assertIsNone(fl.image_dimensions(self._write("f.txt", b"not an image at all")))
        self.assertIsNone(fl.image_dimensions("/nonexistent/f.jpg"))
        self.assertEqual(fl.estimate_tokens("/nonexistent/f.jpg"), 0)

    def test_token_estimate_matches_the_pixel_rule(self):
        data = b"\xff\xd8" + b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", 1161, 724) + b"\x03" * 8
        # 724 x 1161 / 750 -> the real cost of this paper's Figure 7.
        self.assertEqual(fl.estimate_tokens(self._write("f.jpg", data)), 1121)


class NeededFiguresTests(unittest.TestCase):
    """The inspection set comes from the annotations, not from the figure list."""

    def _report_with_images(self, mapping):
        return {"figures": [{"label": label, "openable": True, "images_on_disk": [path]}
                            for label, path in mapping.items()]}

    def test_only_cited_figures_are_needed(self):
        rec = _rec(annotations=[{"term_id": "PHIPO:1", "figure": "Figure 1"},
                                {"term_id": "GO:1", "figure": "Figure 5A,B"}])
        plan = fl.needed_figures(rec, _report(["Figure 1", "Figure 2", "Figure 5"]))
        self.assertEqual([r["figure"] for r in plan["needed"]], ["Figure 1", "Figure 5"])
        self.assertEqual(plan["not_needed"], ["Figure 2"])

    def test_cited_by_lists_every_dependent_annotation(self):
        rec = _rec(annotations=[{"term_id": "GO:0010508", "figure": "Figure 7A"},
                                {"term_id": "GO:0032995", "figure": "Figure 7B"}])
        plan = fl.needed_figures(rec, _report(["Figure 7"]))
        self.assertEqual(plan["needed"][0]["cited_by"], ["GO:0010508", "GO:0032995"])

    def test_already_inspected_figures_are_not_pending(self):
        rec = _rec(figures=[{"label": "Figure 1", "inspected": True, "read": "axis in cm"}],
                   annotations=[{"term_id": "PHIPO:1", "figure": "Figure 1"}])
        plan = fl.needed_figures(rec, _report(["Figure 1"]))
        self.assertTrue(plan["needed"][0]["inspected"])
        self.assertEqual(plan["pending"], [])
        self.assertEqual(plan["pending_tokens"], 0)

    def test_pending_cost_sums_only_the_unread(self):
        import tempfile
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        paths = {}
        for label, (w, h) in {"Figure 1": (750, 300), "Figure 2": (750, 600)}.items():
            p = Path(d.name) / f"{label.replace(' ', '')}.jpg"
            p.write_bytes(b"\xff\xd8" + b"\xff\xc0\x00\x11\x08"
                          + struct.pack(">HH", h, w) + b"\x03" * 8)
            paths[label] = str(p)
        rec = _rec(figures=[{"label": "Figure 1", "inspected": True, "read": "done"}],
                   annotations=[{"term_id": "A", "figure": "Figure 1"},
                                {"term_id": "B", "figure": "Figure 2"}])
        plan = fl.needed_figures(rec, self._report_with_images(paths))
        self.assertEqual([r["figure"] for r in plan["pending"]], ["Figure 2"])
        self.assertEqual(plan["pending_tokens"], 600)   # 750*600/750, Figure 1 excluded

    def test_required_and_optional_are_separated(self):
        rec = _rec(annotations=[
            {"term_id": "A", "figure": "Figure 1", "needs_figure": True},
            {"term_id": "B", "figure": "Figure 2"}])
        plan = fl.needed_figures(rec, _report(["Figure 1", "Figure 2"]))
        self.assertEqual([r["figure"] for r in plan["required"]], ["Figure 1"])
        by_label = {r["figure"]: r["required"] for r in plan["needed"]}
        self.assertTrue(by_label["Figure 1"])
        self.assertFalse(by_label["Figure 2"])

    def test_no_annotations_means_nothing_needs_reading(self):
        plan = fl.needed_figures(_rec(), _report(["Figure 1", "Figure 2"]))
        self.assertEqual(plan["needed"], [])
        self.assertEqual(plan["not_needed"], ["Figure 1", "Figure 2"])

    def test_missing_image_yields_zero_cost_not_an_error(self):
        rec = _rec(annotations=[{"term_id": "A", "figure": "Figure 1"}])
        plan = fl.needed_figures(rec, _report(["Figure 1"]))
        self.assertEqual(plan["needed"][0]["est_tokens"], 0)


class EntryQueueIntegrationTests(unittest.TestCase):
    def _render(self, rec):
        text, _ = eq.render_entry_queue(rec)
        return text

    def test_coverage_line_appears(self):
        rec = _rec([{"label": "Figure 1", "inspected": True, "read": "x"}])
        self.assertIn("**Figures inspected:** 1/1", self._render(rec))

    def test_caption_only_annotations_get_their_own_advisory_section(self):
        rec = _rec(
            figures=[{"label": "Figure 7", "inspected": False, "read": "", "note": "n/a"}],
            annotations=[{"feature_type": "gene", "feature": "sec2",
                          "annotation_type": "biological_process",
                          "term_id": "GO:0010508", "term_name": "positive regulation of autophagy",
                          "evidence": "IMP", "figure": "Figure 7A",
                          "needs_figure": True,
                          "needs_figure_reason": "take-home claim"}])
        text = self._render(rec)
        # Match the heading text, not its number: section F is numbered over the sections
        # actually rendered, so the advisory's number depends on how many annotation types the
        # paper carries. This fixture renders none, so the advisory is F1.
        self.assertIn("Figure evidence — marked needs_figure, but not inspected", text)
        self.assertIn("positive regulation of autophagy", text)
        # Advisory, not parked — the claim may still be right, it is just weaker.
        self.assertLess(text.index("Figure evidence — marked"), text.index("G. Parked items"))

    def test_draft_without_a_ledger_renders_unchanged(self):
        rec = {"meta": {"pmid": "1"}, "canto": {"genes": [], "annotations": []}}
        text = self._render(rec)
        self.assertNotIn("Figures inspected", text)
        self.assertNotIn("F7. Figure evidence", text)


if __name__ == "__main__":
    unittest.main()
