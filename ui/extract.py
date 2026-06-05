import json
import os
import re
from pathlib import Path

import fitz
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv(Path(__file__).parent.parent / ".env")

SYSTEM_PROMPT = """You are a PHI-base curation assistant. Extract structured data from scientific papers about pathogen-host interactions for entry into the PHI-base database.

Return ONLY valid JSON with this exact structure:
{
  "article": {
    "title": "string",
    "authors": "Author et al. style string",
    "journal": "string",
    "pub_year": integer or null,
    "pmid": "string or null",
    "doi": "string or null"
  },
  "pathogens": [
    {"name": "full binomial species name", "common_name": "string or null"}
  ],
  "hosts": [
    {"name": "full binomial species name", "common_name": "string or null"}
  ],
  "proteins": [
    {
      "gene_name": "short gene name e.g. FgTPP1",
      "gene_id": "locus tag e.g. FGSG_11164 or null",
      "species": "binomial species name this protein belongs to",
      "protein_type": "effector | resistance | virulence | other",
      "function_summary": "1-2 sentence mechanistic summary",
      "uniprot_id": "UniProt accession or null"
    }
  ],
  "curation_notes": "2-3 sentence summary of key pathogen-host interaction findings for PHI-Canto annotation"
}

Classification guide:
- effector: pathogen-secreted proteins that manipulate host immunity or physiology
- resistance: host resistance proteins (NLRs, PRRs, R genes)
- virulence: other pathogen virulence/pathogenicity factors
- other: any protein with a relevant experimental role not fitting above

Rules:
- Extract ALL proteins/genes studied experimentally, not just the main one
- Use null for unknown fields, never empty strings
- gene_id is the systematic locus tag if mentioned (e.g. FGSG_xxxxx, MGG_xxxxx)
- If PMID appears in the text include it"""


def get_client() -> OpenAI:
    return OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:8080/api/v1"),
        api_key=os.getenv("OPENAI_API_KEY", ""),
    )


def pdf_to_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n\n".join(page.get_text() for page in doc)


def list_models() -> list[str]:
    try:
        return sorted(m.id for m in get_client().models.list().data)
    except Exception:
        return []


def extract(text: str, model: str) -> dict:
    try:
        resp = get_client().chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract curation data from this paper:\n\n{text[:20000]}"},
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
