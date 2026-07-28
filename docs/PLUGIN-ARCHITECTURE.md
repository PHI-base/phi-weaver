---
created: 2026-07-02
type: documentation
tags: [docs]
project: PHI-Weaver
---

# PHI-Weaver Plug-in Architecture

**Status:** design / strawman — not yet implemented · **Created:** 2026-07-02

**Not a description of the current system.** Nothing below is built. For how PHI-Weaver works
today see [`OVERVIEW.md`](OVERVIEW.md); to add a module now follow
[`ADDING-A-MODULE.md`](ADDING-A-MODULE.md). See [`README.md`](README.md).

A design for turning PHI-Weaver into a **plug-in host**: a small, dependency-light core that
independently-developed curation modules can be **plugged into, tested against a contract, and
incorporated** — without contaminating the core or each other. Captures the direction agreed in
the 2026-07-02 design discussion. No code yet; this fixes the target the modules build against.

---

## 0. Start simple (read this first)

This document describes the **destination, not the first step.** Most of it — containers,
Apptainer, GPU inference servers, plug-in discovery, a conformance harness — is specialist
infrastructure best tackled later, with research-computing / IT help, and only when a concrete
need forces it. You do **not** need any of it to try your two modules.

**The simple path that still moves toward the goal:**
1. Keep today's tools as they are — plain `python3 -m phiweaver.…` from the repo root, JSON
   in / out. Understandable, already working.
2. Add a new capability the way `docs/ADDING-A-MODULE.md` already describes: **one script + one
   skill + one test, in-tree.** No plug-in host needed.
3. For "figure phenotypes," start with the figure **caption / legend text** the PDF converter
   already extracts — feed that into phenotype→PHIPO. This skips the vision model, GPU, and
   containers entirely; add real image recognition later as an enhancement.
4. **Chain steps by hand at first** — run one, check the output, run the next. *You* are the pipe.
   Automate only once the manual version is proven and worth automating.
5. Keep the Obsidian vault as your human front-end — on the simple path it stays valuable.

**Keep only one habit from the big design:** the envelope (JSON in / out, a `status`, provenance,
never guess) plus a small test per tool. It is cheap, understandable, and it is the single thing
that keeps the door open to everything below — without committing to any of it now.

---

## 1. North star

PHI-Weaver is the **core + host**. Specialised capabilities arrive as **modules** developed
independently (other repos, other authors, other release cadences, other dependency stacks) and
plug in by honouring one contract. First two target modules:

1. **Figure-legend / image-recognition module** — reads a paper's figures + captions, emits
   candidate phenotype observations. Heavy vision/ML dependencies.
2. **Phenotype-extraction + PHIPO-mapping module** — reads phenotype descriptions (text and/or
   the output of module 1), emits PHIPO-mapped terms. (Overlaps today's reasoning-only
   `phipo-mapping` skill — see §8.)

These two **compose** into a chain (§7), and both plug in at the seam the `phiweaver/pdf/`
converter already produces (figures + captions).

## 2. Principles (inherited, non-negotiable)

- **Core stays stdlib-only, zero-setup, run-from-root.** Plugins bring their own dependencies;
  the core never inherits them.
- **The envelope is the ABI.** Every module speaks the shared result envelope: `status` +
  payload + **provenance** (source, cache hit/miss, UTC timestamp); `--json` machine output;
  exit `0`/`1`; **never guess** (ambiguity / not-found are explicit statuses, never invented data).
- **Behaviour-preserving for existing curation output.** Adding the host changes plumbing, not
  annotations.
- **Every module independently testable** — offline, deterministic, via a conformance harness (§6).

## 3. The dependency fork (the decision that sets everything)

Module 1 pulls in vision/ML libraries that **cannot** be imported into a stdlib-only core.
Therefore plugins run **out-of-process**: the host invokes a module as a subprocess (or
container) and exchanges the envelope over stdin/stdout (or a file handoff). The process
boundary is what isolates each module's dependency tree.

- **Rejected:** in-process imported plugins — simpler to call, but forces every plugin's deps
  into one environment, which module 1 breaks.
- **Chosen:** out-of-process, envelope-over-transport. This is where the earlier "Unix-pipe"
  idea earns its keep — as the *plugin boundary*, not as an interactive-curation optimisation.

GPU-bound modules (module 1's vision model, and the local AI of §11) run as **containers** on
the cluster. Note the HPC reality: many clusters disallow Docker and run **Apptainer/Singularity**
instead — so the manifest carries a container-engine field, and the same image should run under
both (Docker/OCI for the Linux-server/WSL2 case, Apptainer on ROGER).

## 4. What a plug-in is

A module = **a manifest + a backing command that speaks the envelope**, optionally + a skill
(the human/agent-facing workflow) + tests.

### 4a. Manifest (`plugin.toml` or `plugin.json`, one per module)
```toml
name        = "figure-phenotype-vision"
version     = "0.1.0"
command     = ["python", "-m", "figpheno.cli"]   # or a container image ref
inputs      = ["figures", "captions"]            # declared stage input types (§5)
outputs     = ["phenotype_observations"]         # declared stage output types
runtime     = "subprocess"                        # subprocess | container
dependencies = "self-contained (own venv/image)"  # informational; host does not install
conformance = "tests/conformance/figure-phenotype-vision/"
```

### 4b. Transport
Host writes an input envelope to the module's stdin (or a temp file path); module writes an
output envelope to stdout + returns exit `0`/`1`. Payload types are named, not ad-hoc, so the
host can validate that one module's `outputs` satisfy the next module's `inputs`.

Two invocation patterns, both behind the same envelope:
- **Job-per-item** — the host runs the module once per input (subprocess, or a scheduled
  cluster job, e.g. SLURM `srun`/`sbatch`). Fine for cheap or embarrassingly-parallel work
  (batch vision over many figures).
- **Persistent service** — the module is a long-running endpoint (local HTTP/socket) the host
  calls per item. Required for anything that loads a large model into GPU memory (the local AI,
  §11) — you load once, serve many. The manifest's `runtime`/`endpoint` fields pick which.

### 4c. Discovery
Host finds modules via (a) a **plugin directory** it scans for manifests, and/or (b) Python
**entry-points** (`importlib.metadata`) for pip-installed modules. Discovered modules extend the
existing generated registry (`phiweaver/registry.py` → `skills/REGISTRY.md`) with an
external-module section.

### 4d. Lifecycle
`discover → conformance test (§6) → register → incorporate`. A module that fails conformance is
listed as **candidate**, never wired into the live flow.

## 5. Typed stage contract (the socket)

Extend the P2 contract from "declares wiring" to "declares **input type → output type**". The
envelope in `phiweaver/common/` gains a small, versioned **payload schema** per named type
(`figures`, `captions`, `phenotype_observations`, `phipo_terms`, …). This is what makes modules
composable and lets the host reject an incompatible plug-in *before* running it. Cheap
(schema + a check), and it is the prerequisite for everything else.

## 6. Conformance harness (the "plug in for testing" gate)

A host-provided test runner + **golden fixtures** that any candidate module must pass to prove
it honours the contract:

- valid input → well-formed envelope, correct `status`, provenance present;
- ambiguous / not-found input → explicit status, **no invented data**;
- error input → exit `1`, no partial garbage on stdout;
- declared `inputs`/`outputs` types match what it actually consumes/produces.

Run with `python3 -m phiweaver.conformance <module>` (proposed). This is how a third party
validates their module offline before you incorporate it, and how you re-check on upgrade.

## 7. The two modules on this architecture

```
phiweaver/pdf  ──figures+captions──▶  [module 1: figure-legend vision]
                                              │ phenotype_observations
                                              ▼
                                      [module 2: phenotype→PHIPO]
                                              │ phipo_terms
                                              ▼
                                phiweaver/lookup/validate_ontology_ids  (exists)
```

Each arrow is one envelope. Module 1 **must** be out-of-process (ML deps). Module 2 overlaps the
existing `phipo-mapping` skill (§8).

## 8. Open decisions

- **Module 2 vs existing `phipo-mapping` skill:** extend the current reasoning-only skill into a
  backed, pluggable tool, or replace it? Affects the registry and QC wiring.
- **Container vs venv for isolation:** containers (reproducible, heavier) vs per-module venvs
  (lighter, host-OS-dependent). Manifest `runtime` field allows both; pick a default.
- **Schema format:** hand-rolled JSON-schema-lite in `common/` (keeps stdlib-only) vs a
  dependency. Prefer hand-rolled, consistent with the migration-runner choice (P5).
- **Registry surface:** one merged registry (in-tree + external) or a separate external manifest.
- **Container engine:** Docker/OCI (Linux server, WSL2) vs Apptainer/Singularity (ROGER). Target
  one image spec that runs under both; decide the build/publish flow.
- **Inference backend (§11):** which local-model server (vLLM / TGI / Ollama / llama.cpp), and
  whether cloud Claude stays available as a selectable backend for dev / comparison.

## 9. Priority order (supersedes the vault-first framing)

The plug-in goal pulls toward **engine-as-host portability**; the Obsidian vault drops to a
low-priority, optional human front-end.

1. **Decouple the engine from the vault** — finish the deferred `11-CLAUDE-AI/` split; remove
   hardcoded `11-CLAUDE-AI/...` paths, cwd assumptions, and any "a vault exists" assumption from
   `phiweaver/`. (A host with hardcoded vault paths can't cleanly call plugins.)
2. **Typed I/O schema** (§5) — the socket.
3. **Manifest + transport + discovery** (§4) — the host mechanism.
4. **Conformance harness** (§6) — the test-before-incorporate gate.
5. **Dependency-isolation policy** (§3, §8).
6. **Vault** — keep as optional front-end, decoupled; reorganise or remove only if it obstructs.
   *Do not delete working content up front.*

Because the reasoning stages will run on a **local AI** (§11), the fully-automated **batch** mode
is now a primary target, not a maybe — which is exactly what makes the typed contract (§5),
conformance harness (§6), and provenance discipline worth the effort.

## 10. Relationship to existing work

Builds directly on the completed modularity phases: the envelope + `phiweaver/common/` (P2), the
generated registry (P2), co-located tests (P3), the `phiweaver/` package boundary (P1), and the
namespaced DB migrations (P5) that already let a module add tables under its own namespace. This
document is the P8+ extension: from *in-tree modules you edit into the repo* to *external modules
you plug in*. See `docs/MODULARITY-PLAN.md` and `docs/ADDING-A-MODULE.md`.

---

## 11. Inference backend (local AI)

The reasoning stages (triage, phenotype extraction, PHIPO-mapping judgment, QC) are not
deterministic scripts — they need a model. Long-term that model is a **local AI running on
ROGER**, not a cloud API. So the host needs an **inference-backend abstraction**, structurally a
plug-in like any other:

- A single internal interface (`generate` / `chat`) that reasoning modules call, with **one or
  more selectable backends**: a local-model server on ROGER (vLLM / TGI / Ollama / llama.cpp) for
  production, optionally cloud Claude for development or quality comparison.
- The backend is a **persistent GPU service** (§4b) — load the model once, serve every item.
- **Provenance must record model identity**: model name + version + decoding params go into the
  envelope's provenance for every generated draft. Without this a batch run isn't scientifically
  reproducible ("which model produced this annotation?"). This extends the existing
  provenance field; it is not optional for a curation tool.
- "Never guess" still holds: a local model is more prone to fabrication than a frontier model, so
  the deterministic gates (ontology validation, QC exit codes) matter *more*, not less — they are
  the check on the local AI's output.

## 12. Deployment topology (ROGER / Linux / WSL2 / Docker)

Clean split between a **light, portable orchestrator** and **heavy GPU workers**:

```
  ┌─────────────────────────────┐         ┌───────────────── ROGER (GPU) ─────────────────┐
  │  phiweaver core (host)       │  env    │  container: local-AI inference server          │
  │  Linux server / WSL2 / Docker│◀──────▶ │  container: figure-legend vision module (mod 1)│
  │  CPU-light, stdlib-only      │ envelope│  (Apptainer/Singularity; job or service)       │
  │  orchestrates + validates    │         └────────────────────────────────────────────────┘
  └─────────────────────────────┘
        │ deterministic stages (convert, validate, metrics, tracking) run locally on the core
```

- **Core needs no GPU** — it dispatches heavy work to ROGER over the envelope transport and runs
  the deterministic stages itself. Runs identically on a Linux server, in WSL2, or as a container.
- **Dev/prod parity via containers**: the same image spec runs under Docker (server/WSL2) and
  Apptainer (ROGER). Develop in WSL2/Docker, deploy to ROGER unchanged.
- **The core is itself containerisable** — one image for the orchestrator, one per GPU module,
  one for the inference backend. Composed locally (Docker Compose) or scheduled on the cluster
  (SLURM).
- This topology is the concrete reason §9.1 (decouple engine from vault) comes first: the
  orchestrator has to run headless on a server/cluster with **no Obsidian and no vault present**.
