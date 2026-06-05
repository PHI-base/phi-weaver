import json
import os
import re
from pathlib import Path

import fitz
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# PHI-Canto requires this complete data model:
#   article → organisms (pathogens + hosts with strains) → genes (with GO
#   annotations + physical interactions) → alleles → pathogen/host genotypes
#   → metagenotypes → interaction/disease/phenotype annotations
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a PHI-base curation assistant. Extract ALL data needed to pre-populate a PHI-Canto curation session from this scientific paper about pathogen-host interactions.

Return ONLY valid JSON. Use null for unknown values, never empty strings or empty objects unless specified.

{
  "article": {
    "title": "string",
    "authors": "Smith et al. style",
    "journal": "string",
    "pub_year": integer or null,
    "pmid": "string or null",
    "doi": "string or null"
  },

  "organisms": {
    "pathogens": [
      {
        "name": "full binomial e.g. Fusarium graminearum",
        "taxon_id": integer or null,
        "strains": ["PH-1", "DAOM180378"]
      }
    ],
    "hosts": [
      {
        "name": "full binomial e.g. Triticum aestivum",
        "taxon_id": integer or null,
        "strains": ["Chinese Spring", "Bobwhite"]
      }
    ]
  },

  "genes": [
    {
      "gene_name": "short name e.g. FgTPP1",
      "systematic_id": "locus tag e.g. FGSG_11164 or null",
      "uniprot_accession": "A0A016PBU3 if explicitly mentioned, else null",
      "organism_name": "species name",
      "taxon_id": integer or null,
      "product": "protein product description",
      "is_effector": true or false,
      "go_annotations": [
        {
          "go_id": "GO:0140418 or null if uncertain",
          "go_term": "effector-mediated modulation of host process by symbiont",
          "go_aspect": "molecular_function | biological_process | cellular_component",
          "evidence_code": "IMP | IDA | IGI | IPI | ISS | IEP | IBA | IC | ND",
          "figure": "Figure 3A or null"
        }
      ],
      "physical_interactions": [
        {
          "interacting_gene": "gene name",
          "interacting_organism": "species name",
          "interaction_type": "binds | phosphorylates | cleaves | suppresses | activates",
          "evidence_code": "IPI | IDA | IGI",
          "figure": "Figure X or null"
        }
      ]
    }
  ],

  "alleles": [
    {
      "id": "allele-1",
      "gene_systematic_id": "locus tag matching a gene above",
      "gene_name": "gene name",
      "name": "allele name e.g. FgTPP1delta",
      "type": "deletion | substitution | insertion | wild type | unknown | other",
      "description": "e.g. complete deletion or T196A or amino acids 1-50 or null",
      "expression": "null | decreased | wild type product level | increased | not assayed"
    }
  ],

  "pathogen_genotypes": [
    {
      "id": "pg-1",
      "label": "human-readable label e.g. deltaFgTPP1",
      "organism_name": "species name",
      "taxon_id": integer or null,
      "strain": "strain name or null",
      "allele_ids": ["allele-1"],
      "background": "background mutations text or empty string",
      "is_wild_type": false,
      "phenotype_annotations": [
        {
          "phipo_term": "PHIPO term name e.g. reduced pathogenicity | loss of pathogenicity | increased virulence | normal pathogenicity | reduced sporulation | increased sporulation",
          "evidence_code": "IMP",
          "conditions": ["spray inoculation", "rich medium"],
          "figure": "Figure 4A or null",
          "comment": ""
        }
      ]
    }
  ],

  "host_genotypes": [
    {
      "id": "hg-1",
      "label": "e.g. Chinese Spring wild type",
      "organism_name": "species name",
      "taxon_id": integer or null,
      "strain": "cultivar or strain name",
      "allele_ids": [],
      "is_wild_type": true,
      "phenotype_annotations": []
    }
  ],

  "metagenotypes": [
    {
      "id": "mg-1",
      "pathogen_genotype_id": "pg-1",
      "host_genotype_id": "hg-1",
      "is_control": false,
      "interaction_annotations": [
        {
          "phipo_term": "PHIPO term e.g. reduced pathogenicity | loss of pathogenicity | increased virulence | absence of pathogen growth on host | presence of hypersensitive response",
          "evidence_code": "IMP",
          "host_tissue": "leaf | root | inflorescence | stem | seed or null",
          "host_tissue_bto": "BTO:0000713 (leaf) | BTO:0001199 (root) | BTO:0000628 (inflorescence) | BTO:0001225 (stem) or null",
          "infective_ability": "pathogenic | non-pathogenic | reduced pathogenicity | increased pathogenicity or null",
          "compared_to_control_id": "mg-control or null",
          "conditions": ["spray inoculation"],
          "figure": "Figure 4A or null",
          "comment": ""
        }
      ],
      "disease_annotations": [
        {
          "disease_name": "PHIDO disease term e.g. head blight | leaf spot | anthracnose | powdery mildew | blast | blight",
          "host_tissue": "inflorescence or null",
          "host_tissue_bto": "BTO:0000628 or null",
          "figure": "Figure 1 or null"
        }
      ]
    }
  ],

  "curation_notes": "2-3 sentence summary of the key pathogen-host interaction findings"
}

=== CLASSIFICATION RULES ===

ALLELE TYPES:
- deletion: ΔgeneX, geneXΔ, ΔgeneX::hph, gene knockout, disruption mutant
- substitution: point mutation, amino acid change (e.g. T196A, S120A), domain swap
- insertion: gene insertion, GFP fusion, tag fusion (unless that IS the study)
- wild type: reference/WT strain with no modifications

EXPRESSION:
- null: deletion/knockout produces no protein
- decreased: RNAi, partial promoter deletion, reduced expression
- wild type product level: complemented strain, WT control
- increased: OE::gene, overexpression, strong promoter fusion
- not assayed: expression level not tested

EVIDENCE CODES:
- IMP: inferred from mutant phenotype (deletion/knockout experiments)
- IDA: inferred from direct assay (biochemical, in vitro)
- IGI: inferred from genetic interaction
- IPI: inferred from physical interaction (co-IP, Y2H, etc.)
- IEP: inferred from expression pattern

GO ANNOTATIONS FOR EFFECTORS:
- ALWAYS include GO:0140418 "effector-mediated modulation of host process by symbiont" for effectors
- Add specific child terms if the mechanism is known

ALWAYS CREATE:
- A wild-type pathogen genotype (is_wild_type: true, no alleles)
- A control metagenotype (is_control: true) pairing wild-type pathogen × host
- disease_annotations ONLY for wild-type pathogen × natural host metagenotype

TAXON IDs for common organisms (use these if not stated):
- Fusarium graminearum: 229533
- Fusarium oxysporum: 5507
- Magnaporthe oryzae: 318829
- Botrytis cinerea: 332648
- Blumeria graminis: 34373
- Puccinia striiformis: 27350
- Zymoseptoria tritici: 336722
- Pseudomonas syringae: 317
- Xanthomonas oryzae: 64187
- Ralstonia solanacearum: 305
- Triticum aestivum: 4565
- Oryza sativa: 4530
- Arabidopsis thaliana: 3702
- Nicotiana benthamiana: 4100
- Solanum lycopersicum: 4081
- Hordeum vulgare: 4513
"""


def get_client() -> OpenAI:
    return OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:8080/api/v1"),
        api_key=os.getenv("OPENAI_API_KEY", ""),
    )


def list_models() -> list[str]:
    try:
        return sorted(m.id for m in get_client().models.list().data)
    except Exception:
        return []


def pdf_to_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n\n".join(page.get_text() for page in doc)


def extract(text: str, model: str) -> dict:
    try:
        resp = get_client().chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract all PHI-Canto curation data from this paper:\n\n{text[:22000]}"},
            ],
            temperature=0.1,
        )
        return _parse_json(resp.choices[0].message.content)
    except OpenAIError as e:
        raise RuntimeError(f"[{model}] {_clean_api_error(str(e))}") from e


def _parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise RuntimeError("Model did not return valid JSON")


def _clean_api_error(msg: str) -> str:
    if "<html" in msg.lower() or "<!doctype" in msg.lower():
        if "502" in msg:
            return "Model unavailable (502) — not loaded or server starting up."
        if "503" in msg:
            return "Model unavailable (503) — server overloaded."
        return "API returned an HTML error page — model may be down or base URL is wrong."
    return msg
