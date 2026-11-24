"""Issue original (B) vs. reescrita com a skill Spec-Driven Development (A) vs. reescrita pelos critérios da literatura (C).

Uso:
    python piloto.py rodar N [parte total]     # grupos A e B, para as N primeiras issues
    python piloto.py classificar               # bug/feature/neither/discard das 300 issues (ADR 0008)
    python piloto.py rodar_c N [parte total]   # grupo C, só issues bug/feature (ADR 0009)
    python piloto.py medir                     # tabela runs/tabela.csv + resumo no terminal

Decisões em docs/adr/. Token da assinatura em ~/.config/ia-gen-es/oauth_token.
"""
import csv
import fcntl
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from datasets import load_dataset

RAIZ = Path(__file__).parent
RUNS = RAIZ / "runs"
SKILL = Path.home() / ".agents/skills/spec-driven-development/SKILL.md"
TOKEN = (Path.home() / ".config/ia-gen-es/oauth_token").read_text().strip()
CLAUDE_BIN = Path.home() / ".local/bin/claude"
GRUPOS = ("original", "skill")
GRUPOS_MEDIR = ("original", "skill", "literatura")
PASTA_TEXTO = {"skill": "specs", "literatura": "specs_literatura"}  # texto gerado que o Resolvedor recebe
PROMPT_TIPO = RAIZ / "prompts/classificacao_tipo_herzig.md"
MODELO_GERADOR = "claude-opus-5-5"
MODELO_RESOLVEDOR = "claude-sonnet-5-5"
LIMITE_S = 3600  # ADR 0002: 60 min de relógio, só contra processo travado
# ADR 0004: repositórios de imagem leve primeiro
ORDEM_REPOS = ["psf/requests", "pallets/flask", "pytest-dev/pytest", "pylint-dev/pylint",
               "mwaskom/seaborn", "pydata/xarray", "astropy/astropy", "sphinx-doc/sphinx",
               "scikit-learn/scikit-learn", "matplotlib/matplotlib", "sympy/sympy", "django/django"]

INSTRUCAO_GERADOR = """

---
EXPERIMENT CONTEXT (overrides the interactive parts above):
There is no human in the loop and you have no access to the repository.
Apply ONLY Phase 1 (Specify) to the issue the user sends, in a single pass.
Write the spec with the spec template above. Anything you would ask the human goes
under "Open Questions"; anything you assume goes in an "Assumptions" list.
Do not invent commands, paths or code you cannot see in the issue; mark them unknown.
Do not write the plan, tasks, or the fix.
Reply with the spec in Markdown only, in English.
"""

# ADR 0009: Bettenburg et al. (2008), §3.1
INSTRUCAO_BUG = """You rewrite a GitHub bug report so that it contains the information developers find most useful,
according to Bettenburg et al. (2008), "What makes a good bug report?" (FSE). Section 3.1 of that study:
"the most widely used items across projects are steps to reproduce, observed and expected behavior,
stack traces, and test cases"; code examples are also used.

Rewrite the report the user sends into Markdown with exactly these sections:
## Summary
## Steps to reproduce
## Observed behavior
## Expected behavior
## Stack trace / error output
## Test case
## Code example
## Version and environment

Rules:
- Use only information contained in the original report. You have no access to the repository.
- Restructure and clarify. You may turn a reproduction snippet from the report into numbered steps or a minimal test case.
- If the report does not contain the information for a section, write "Not provided in the original report."
  Never invent outputs, stack traces, versions, file paths or code.
- Do not propose or describe the fix.
Reply with the rewritten report only, in English.
"""

# ADR 0009: Heck & Zaidman (2017), Fig. 2, QC1 (completude)
INSTRUCAO_FEATURE = """You rewrite a GitHub feature request so that it is complete according to the quality framework of
Heck & Zaidman (2017), "A framework for quality assessment of just-in-time requirements: the case of open source
feature requests" (Requirements Engineering). Completeness (QC1): basic elements (summary and description, product
version), required element rationale (why the feature is needed), optional elements (use case or scenario, possible solution).

Rewrite the request the user sends into Markdown with exactly these sections:
## Summary
## Description
## Product version
## Rationale
## Use case or scenario
## Possible solution

Rules:
- Use only information contained in the original request. You have no access to the repository.
- Restructure and clarify.
- If the request does not contain the information for a section, write "Not provided in the original request."
  Never invent versions, file paths or code.
- "Possible solution" only restates a solution the original request suggests; do not design the solution yourself.
Reply with the rewritten request only, in English.
"""

INSTRUCAO_RESOLVEDOR = """You are working in a Python repository at /testbed (current directory).
Resolve the issue below by editing the repository's source code.
Do not modify existing tests. When you are done, stop.

<issue>
{issue}
</issue>
"""


def ambiente(**extra):
    return {**os.environ, "CLAUDE_CODE_OAUTH_TOKEN": TOKEN, **extra}


def instancias():
    d = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
    por_repo = {r: sorted((x for x in d if x["repo"] == r), key=lambda x: x["instance_id"]) for r in ORDEM_REPOS}
    ordem = []
    for r in ORDEM_REPOS:
        random.Random(42).shuffle(por_repo[r])
        ordem += por_repo[r]
    return ordem


def chamar_opus(sistema, entrada):
    # ADR 0005: config vazia e pasta vazia, sem hooks/plugins do host
    with tempfile.TemporaryDirectory() as config, tempfile.TemporaryDirectory() as cwd:
        r = subprocess.run(
            ["claude", "-p", "--model", MODELO_GERADOR, "--tools", "", "--system-prompt", sistema,
             "--output-format", "json", "--no-session-persistence"],
            input=entrada, capture_output=True, text=True, cwd=cwd,
            env=ambiente(CLAUDE_CONFIG_DIR=config), timeout=900)
    saida = json.loads(r.stdout)
    if saida.get("is_error"):
        raise RuntimeError(f"opus falhou: {saida.get('result')}")
    return saida


def gerar(inst, grupo, sistema):
    destino = RUNS / PASTA_TEXTO[grupo] / f"{inst['instance_id']}.md"
    if destino.exists():
        return destino.read_text()
    saida = chamar_opus(sistema, inst["problem_statement"])
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(saida["result"])
    (destino.with_suffix(".json")).write_text(json.dumps(saida, indent=1))
    return saida["result"]


def gerar_spec(inst):
    return gerar(inst, "skill", SKILL.read_text() + INSTRUCAO_GERADOR)


def classificar():
    """ADR 0008: skill do mestrado (Herzig, Tabela III), zero-shot, 1 chamada por issue."""
    saida = RUNS / "tipos.jsonl"
    feitos = {json.loads(l)["instance_id"] for l in saida.read_text().splitlines()} if saida.exists() else set()
    modelo = PROMPT_TIPO.read_text()

    def uma(inst):
        titulo, _, corpo = inst["problem_statement"].strip().partition("\n")  # SWE-bench não separa título e corpo
        prompt = modelo.replace("{examples}", "").replace("{title}", titulo.strip()).replace("{body}", corpo.strip())
        texto = chamar_opus("You label GitHub issue reports. Follow the instructions in the user message.", prompt)["result"]
        m = re.search(r"\{.*\}", texto, re.S)
        try:
            obj = json.loads(m.group(0)) if m else {}
        except json.JSONDecodeError:
            obj = {}
        label = str(obj.get("label", "")).strip().lower()
        return {"instance_id": inst["instance_id"], "label": label if label in ("bug", "feature", "neither", "discard") else "invalid",
                "reasoning": obj.get("reasoning", "")}

    pendentes = [x for x in instancias() if x["instance_id"] not in feitos]
    with ThreadPoolExecutor(8) as ex, open(saida, "a") as f:
        for r in ex.map(uma, pendentes):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            print(r["instance_id"], r["label"], flush=True)


def tipos():
    p = RUNS / "tipos.jsonl"
    return {r["instance_id"]: r["label"] for r in map(json.loads, p.read_text().splitlines())} if p.exists() else {}


def sh(nome, cmd, **kw):
    return subprocess.run(["docker", "exec", nome, "bash", "-lc", cmd], capture_output=True, text=True, **kw)


def resolver(inst, grupo, issue):
    iid = inst["instance_id"]
    pasta = RUNS / grupo / iid
    if (pasta / "patch.diff").exists():
        return
    pasta.mkdir(parents=True, exist_ok=True)
    # ponytail: um download por vez, e só com 12 GB livres (imagens de matplotlib têm 7 GB); trava em arquivo entre processos
    with open(RUNS / ".download.lock", "w") as trava:
        fcntl.flock(trava, fcntl.LOCK_EX)
        while int(subprocess.run(["df", "--output=avail", "-BG", "/"], capture_output=True, text=True).stdout.split()[-1][:-1]) < 12:
            time.sleep(60)
        subprocess.run(["docker", "pull", "-q", inst["image"]], check=True, capture_output=True)
    nome = f"iagen-{grupo}-{iid}".replace("__", "-")
    subprocess.run(["docker", "run", "-d", "--rm", "--name", nome, inst["image"], "sleep", str(LIMITE_S + 600)],
                   check=True, capture_output=True)
    try:
        subprocess.run(["docker", "cp", "-L", str(CLAUDE_BIN), f"{nome}:/usr/local/bin/claude"], check=True)
        inicio = time.time()
        status = "ok"
        try:
            r = subprocess.run(
                ["docker", "exec", "-i", "-e", "CLAUDE_CODE_OAUTH_TOKEN", "-e", "IS_SANDBOX=1",
                 "-e", "DISABLE_AUTOUPDATER=1", "-w", "/testbed", nome,
                 "claude", "-p", "--model", MODELO_RESOLVEDOR, "--output-format", "json",
                 "--dangerously-skip-permissions", "--disallowedTools", "WebFetch", "WebSearch"],
                input=INSTRUCAO_RESOLVEDOR.format(issue=issue), capture_output=True, text=True,
                env=ambiente(), timeout=LIMITE_S)
            (pasta / "saida.json").write_text(r.stdout)
            (pasta / "stderr.txt").write_text(r.stderr)
            # cota esgotada ou falha de login não pode virar "não resolvida": sem patch.diff, a execução é refeita
            if r.returncode != 0 or json.loads(r.stdout or "{}").get("is_error", True):
                raise RuntimeError(f"resolvedor falhou: {(r.stdout or r.stderr)[-300:]}")
        except subprocess.TimeoutExpired:
            status = "tempo"
        duracao = time.time() - inicio
        # ponytail: só arquivos rastreados; scripts novos de reprodução ficam fora do patch e das linhas
        patch = sh(nome, "git diff HEAD").stdout
        (pasta / "patch.diff").write_text(patch)
        for f in sh(nome, "git diff HEAD --name-only").stdout.split():
            if f.endswith(".py"):
                for lado, cmd in (("antes", f"git show HEAD:{f}"), ("depois", f"cat {f}")):
                    alvo = pasta / lado / f
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    alvo.write_text(sh(nome, cmd).stdout)
        (pasta / "meta.json").write_text(json.dumps({"status": status, "duracao_s": duracao}))
    finally:
        subprocess.run(["docker", "stop", "-t", "1", nome], capture_output=True)


def avaliar(inst, grupo):
    iid = inst["instance_id"]
    pasta = RUNS / grupo / iid
    if (pasta / "report.json").exists():
        return json.loads((pasta / "report.json").read_text())
    pasta.mkdir(parents=True, exist_ok=True)
    patch = inst["patch"] if grupo == "oficial" else (pasta / "patch.diff").read_text()
    if not patch.strip():  # agente não mudou nada: avaliador do SWE-bench pula, mas conta como não resolvida
        resultado = {"resolved": False, "patch_vazio": True}
        (pasta / "report.json").write_text(json.dumps(resultado))
        return resultado
    pred = pasta / "pred.jsonl"
    pred.write_text(json.dumps({"instance_id": iid, "model_name_or_path": grupo, "model_patch": patch}) + "\n")
    run_id = f"piloto_{grupo}_{iid}"
    subprocess.run([sys.executable, "-m", "swebench.harness.run_evaluation",
                    "--dataset_name", "SWE-bench/SWE-bench_Lite", "--predictions_path", str(pred),
                    "--instance_ids", iid, "--run_id", run_id, "--max_workers", "1"],
                   cwd=RAIZ, capture_output=True)
    rel = RAIZ / "logs/run_evaluation" / run_id / grupo / iid / "report.json"
    if not rel.exists():
        raise RuntimeError(f"avaliador não gerou relatório para {grupo}/{iid}")
    resultado = json.loads(rel.read_text())[iid]
    (pasta / "report.json").write_text(json.dumps(resultado))
    return resultado


def processar(inst, ordem):
    """Retorna False se a issue foi excluída pelo oráculo."""
    iid = inst["instance_id"]
    # ADR 0003: só entra issue que o patch oficial resolve neste ambiente
    if not avaliar(inst, "oficial").get("resolved"):
        print("   excluída: patch oficial não resolve aqui", flush=True)
        return False
    textos = {"original": inst["problem_statement"], "skill": gerar_spec(inst)}
    # ADR 0004: os dois grupos da issue i antes da i+1, alternando quem vai primeiro
    for grupo in (GRUPOS if ordem % 2 == 1 else GRUPOS[::-1]):
        resolver(inst, grupo, textos[grupo])
        print("  ", grupo, avaliar(inst, grupo).get("resolved"), flush=True)
    return True


def processar_c(inst, ordem):
    """ADR 0009: grupo C só para issues bug/feature que o oráculo aceita."""
    tipo = tipos().get(inst["instance_id"])
    if tipo not in ("bug", "feature") or not avaliar(inst, "oficial").get("resolved"):
        print("   fora do grupo C:", tipo, flush=True)
        return False
    texto = gerar(inst, "literatura", INSTRUCAO_BUG if tipo == "bug" else INSTRUCAO_FEATURE)
    resolver(inst, "literatura", texto)
    print("   literatura", avaliar(inst, "literatura").get("resolved"), flush=True)
    return True


def rodar(n, parte=0, total=1, de_tras_pra_frente=0, etapa=processar):
    incluidas = 0
    lista = list(enumerate(instancias()[:n]))
    for i, inst in (lista[::-1] if de_tras_pra_frente else lista):
        if i % total != parte:  # vários processos em paralelo, posições alternadas da mesma ordem
            continue
        print(time.strftime("%H:%M"), i, inst["instance_id"], flush=True)
        for tentativa in range(8):  # ponytail: espera fixa; cota da assinatura volta em até 5 h
            try:
                incluidas += etapa(inst, incluidas + 1)
                break
            except Exception as e:
                print(f"   erro (tentativa {tentativa + 1}), nova tentativa em 15 min: {e}", flush=True)
                time.sleep(900)
        else:
            print("   pulada depois de 8 tentativas", flush=True)
        subprocess.run(["docker", "image", "rm", inst["image"]], capture_output=True)  # ADR 0003: disco


def ilustrar(iid, grupo="original"):
    """Reexecuta 1 issue registrando cada ação do agente (stream-json), só para ilustrar; não entra nas tabelas."""
    inst = next(x for x in instancias() if x["instance_id"] == iid)
    texto = inst["problem_statement"] if grupo == "original" else (RUNS / PASTA_TEXTO[grupo] / f"{iid}.md").read_text()
    pasta = RUNS / "ilustracao" / grupo
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"iagen-ilustracao-{iid}".replace("__", "-")
    subprocess.run(["docker", "pull", "-q", inst["image"]], check=True, capture_output=True)
    subprocess.run(["docker", "run", "-d", "--rm", "--name", nome, inst["image"], "sleep", "1200"], check=True, capture_output=True)
    try:
        subprocess.run(["docker", "cp", "-L", str(CLAUDE_BIN), f"{nome}:/usr/local/bin/claude"], check=True)
        inicio = time.time()
        r = subprocess.run(
            ["docker", "exec", "-i", "-e", "CLAUDE_CODE_OAUTH_TOKEN", "-e", "IS_SANDBOX=1", "-e", "DISABLE_AUTOUPDATER=1",
             "-w", "/testbed", nome, "claude", "-p", "--model", MODELO_RESOLVEDOR, "--output-format", "stream-json", "--verbose",
             "--dangerously-skip-permissions", "--disallowedTools", "WebFetch", "WebSearch"],
            input=INSTRUCAO_RESOLVEDOR.format(issue=texto), capture_output=True, text=True, env=ambiente(), timeout=LIMITE_S)
        (pasta / f"{iid}.jsonl").write_text(r.stdout)
        (pasta / f"{iid}.patch").write_text(sh(nome, "git diff HEAD").stdout)
        print("segundos:", round(time.time() - inicio, 1))
    finally:
        subprocess.run(["docker", "stop", "-t", "1", nome], capture_output=True)


def linhas(patch):
    mais = sum(1 for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++"))
    menos = sum(1 for l in patch.splitlines() if l.startswith("-") and not l.startswith("---"))
    arquivos = len(re.findall(r"^diff --git", patch, re.M))
    return mais, menos, arquivos


def avisos_ruff(pasta):
    if not pasta.exists():
        return 0
    r = subprocess.run([str(Path(sys.executable).parent / "ruff"), "check", "--isolated", "--output-format", "json", "."],
                       cwd=pasta, capture_output=True, text=True)
    return len(json.loads(r.stdout or "[]"))


def nomes_do_patch(patch):
    """Arquivos e funções/classes que o patch oficial toca (ADR 0005, vazamento)."""
    nomes = set()
    for f in re.findall(r"^diff --git a/(\S+)", patch, re.M):
        nomes |= {f, Path(f).name, f.removesuffix(".py").replace("/", ".")}
    nomes |= set(re.findall(r"^@@.*@@.*?(?:def|class)\s+(\w+)", patch, re.M))
    nomes |= set(re.findall(r"^[+-]\s*(?:def|class)\s+(\w+)", patch, re.M))
    # ponytail: palavra comum curta ("open", "match") não conta como vazamento; lista fixa se precisar de mais rigor
    return {n for n in nomes if n != "__init__.py" and not (n.isalpha() and n.islower() and len(n) < 6)
            and not (n.startswith("__") and n.endswith("__"))}  # métodos especiais (__init__, __mul__) são genéricos


def medir():
    dados = {x["instance_id"]: x for x in load_dataset("SWE-bench/SWE-bench_Lite", split="test")}
    linhas_tab = []
    tipo = tipos()
    for grupo in GRUPOS_MEDIR:
        for pasta in sorted((RUNS / grupo).glob("*/report.json")):
            iid = pasta.parent.name
            p = pasta.parent
            saida = json.loads((p / "saida.json").read_text() or "{}") if (p / "saida.json").exists() else {}
            uso = saida.get("usage", {})
            mais, menos, arqs = linhas((p / "patch.diff").read_text())
            gmais, gmenos, garqs = linhas(dados[iid]["patch"])
            vaz = ""
            if grupo in PASTA_TEXTO:
                spec = (RUNS / PASTA_TEXTO[grupo] / f"{iid}.md").read_text()
                orig = dados[iid]["problem_statement"]
                tem = lambda n, t: re.search(rf"\b{re.escape(n)}\b", t) is not None
                vaz = sum(1 for n in nomes_do_patch(dados[iid]["patch"]) if tem(n, spec) and not tem(n, orig))
            linhas_tab.append({
                "instance_id": iid, "grupo": grupo, "tipo": tipo.get(iid, ""),
                "status": json.loads((p / "meta.json").read_text())["status"],
                "resolvida": json.loads(pasta.read_text()).get("resolved", False),
                "tokens_entrada": uso.get("input_tokens", 0) + uso.get("cache_creation_input_tokens", 0)
                                  + uso.get("cache_read_input_tokens", 0),
                "tokens_saida": uso.get("output_tokens", 0),
                "custo_usd_estimado": saida.get("total_cost_usd", 0),
                "turnos": saida.get("num_turns", 0),
                "duracao_s": round(json.loads((p / "meta.json").read_text())["duracao_s"]),
                "linhas_mais": mais, "linhas_menos": menos, "arquivos": arqs,
                "oficial_mais": gmais, "oficial_menos": gmenos, "oficial_arquivos": garqs,
                "ruff_novos": avisos_ruff(p / "depois") - avisos_ruff(p / "antes"),
                "vazamento_nomes": vaz,
            })
    with open(RUNS / "tabela.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas_tab[0]))
        w.writeheader()
        w.writerows(linhas_tab)
    pares = {r["instance_id"] for r in linhas_tab if r["grupo"] == "skill"} & \
            {r["instance_id"] for r in linhas_tab if r["grupo"] == "original"}
    print("issues pareadas:", len(pares))
    for grupo in GRUPOS_MEDIR:
        g = [r for r in linhas_tab if r["grupo"] == grupo and r["instance_id"] in pares]
        if not g:
            continue
        mediana = lambda k: sorted(r[k] for r in g)[len(g) // 2]
        print(grupo, "resolvidas", sum(r["resolvida"] for r in g), "/", len(g),
              "| mediana tokens entrada", mediana("tokens_entrada"), "saída", mediana("tokens_saida"),
              "| mediana min", round(mediana("duracao_s") / 60, 1), "| mediana linhas +", mediana("linhas_mais"),
              "| ruff novos", sum(r["ruff_novos"] for r in g))


if __name__ == "__main__":
    {"rodar": lambda: rodar(*map(int, sys.argv[2:])), "classificar": classificar,
     "rodar_c": lambda: rodar(*map(int, sys.argv[2:]), etapa=processar_c), "medir": medir,
     "ilustrar": lambda: ilustrar(*sys.argv[2:])}[sys.argv[1]]()
