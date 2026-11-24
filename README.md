# Does Rewriting Issues Help Coding Agents?

Artifacts of a study on rewriting issue reports before a coding agent resolves them.
Each issue goes to Claude Code (Sonnet 5.5) in three versions:

- **A (skill):** rewritten by Opus 5.5 with the [Spec-Driven Development skill](skill/SKILL.md) (Addy Osmani, MIT).
- **B (original):** the issue as written by the reporter.
- **C (literature):** rewritten by Opus 5.5 with a template from the bug report and feature request literature (bug or feature, by a type classifier).

Corpora: SWE-bench Lite (269 bug/feature issues) and SAPOS, a Ruby on Rails project
(20 issues with tests, 43 judged by a calibrated LLM judge).

## Layout

| Path | Content |
|---|---|
| `piloto.py` | SWE-bench Lite: classification, rewriting (A, C), resolution and evaluation |
| `sapos_candidatas.py`, `sapos_tarefas.py` | Build SWE-bench-style tasks from SAPOS issues |
| `sapos_experimento.py` | SAPOS: rewriting, resolution, evaluation, LLM judge and its calibration |
| `sapos_docker/Dockerfile` | SAPOS test environment (Ruby 3.2 or 3.4) |
| `prompts/` | Type classification prompt |
| `skill/` | Copy of the skill used in group A, with its license |
| `runs/` | Every run: rewritten issues (`specs/`, `specs_literatura/`), and per issue and group `patch.diff`, `report.json`, `saida.json` (agent usage), `meta.json`; SAPOS runs and tasks in `runs/sapos/` |
| `paper_tabelas.py`, `paper_graficos.py` | Tables and figure of the paper from `runs/` |
| `docs/adr/` | Design decisions, in Portuguese |
| `docs/paper/` | Paper sources |

## Running

Requirements: Python 3.12, Docker, the `claude` CLI and access to the Claude models.

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
mkdir -p ~/.agents/skills/spec-driven-development && cp skill/SKILL.md ~/.agents/skills/spec-driven-development/
# Claude Code token in ~/.config/ia-gen-es/oauth_token

# SWE-bench Lite
python piloto.py classificar       # bug / feature / neither / discard
python piloto.py rodar 300         # groups A and B
python piloto.py rodar_c 300       # group C (bug/feature only)
python piloto.py medir             # runs/tabela.csv

# SAPOS (needs a local clone of gems-uff/sapos and a GitHub token)
for v in 3.4.10 3.2.5 3.2.11; do docker build -t iagen-sapos:ruby-$v --build-arg RUBY_VERSION=$v sapos_docker; done
GITHUB_TOKEN=... python sapos_candidatas.py PATH_TO_CLONE
GITHUB_TOKEN=... python sapos_tarefas.py PATH_TO_CLONE                 # strict level
NIVEL=amplo GITHUB_TOKEN=... python sapos_tarefas.py PATH_TO_CLONE     # all level
python sapos_experimento.py classificar
python sapos_experimento.py rodar                  # strict level
NIVEL=amplo python sapos_experimento.py rodar      # all level
JUIZ=v2 python sapos_experimento.py julgar && python sapos_experimento.py calibrar

python paper_tabelas.py && python paper_graficos.py
```

Agent transcripts were not kept.
