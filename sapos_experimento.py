"""Grupos A, B e C nas tarefas do SAPOS (ADR 0011). Reaproveita prompts e chamadas de piloto.py.

Uso:
    python sapos_experimento.py classificar        # tipo de cada tarefa válida + planilha para o Caio conferir
    python sapos_experimento.py rodar [parte total] # gera textos A e C, resolve e avalia os 3 grupos
    python sapos_experimento.py medir              # runs/sapos/tabela.csv
"""
import csv
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import piloto
from piloto import chamar_opus, ambiente, CLAUDE_BIN, MODELO_RESOLVEDOR, LIMITE_S
from sapos_tarefas import docker, sh, subir as subir_base, aplicar, rodar_specs

RAIZ = Path(__file__).parent
S = RAIZ / "runs/sapos"
GRUPOS = ("original", "skill", "literatura")
PASTA_TEXTO = {"skill": "specs", "literatura": "specs_literatura"}

# ADR 0011: reescrita no idioma da issue (português)
EM_PORTUGUES = ("Reply in Portuguese, the language of the original issue. Translate the section headings into Portuguese. "
                "Write \"Não informado na issue original.\" for a section without information.")
INSTRUCAO_A = piloto.SKILL.read_text() + piloto.INSTRUCAO_GERADOR.replace(
    "Reply with the spec in Markdown only, in English.", "Reply with the spec in Markdown only. " + EM_PORTUGUES)
INSTRUCAO_C = {
    "bug": piloto.INSTRUCAO_BUG.replace("Reply with the rewritten report only, in English.", "Reply with the rewritten report only. " + EM_PORTUGUES),
    "feature": piloto.INSTRUCAO_FEATURE.replace("Reply with the rewritten request only, in English.", "Reply with the rewritten request only. " + EM_PORTUGUES),
}
INSTRUCAO_RESOLVEDOR = """You are working in a Ruby on Rails repository at /sapos (current directory).
Resolve the issue below by editing the repository's source code.
Do not modify existing tests. When you are done, stop.

<issue>
{issue}
</issue>
"""
# ADR 0011: o agente não recebe as instruções de agente do repositório nem o histórico posterior à base
LIMPAR = ("cd /sapos && git ls-files CLAUDE.md AGENTS.md .claude .agents .cursor | xargs -r git update-index --skip-worktree "
          "&& rm -rf CLAUDE.md AGENTS.md .claude .agents .cursor && git remote remove origin 2>/dev/null; "
          "git checkout -q -B trabalho && git for-each-ref --format='%(refname)' | grep -v refs/heads/trabalho "
          "| xargs -r -n1 git update-ref -d && git reflog expire --expire=now --all && git gc -q --prune=now")


def tarefas():
    """NIVEL=amplo: as 72 do nível 2 (ADR 0012); senão, as do nível 1 (com FAIL_TO_PASS)."""
    arq = "tarefas_amplas.jsonl" if os.environ.get("NIVEL") == "amplo" else "tarefas.jsonl"
    return [t for t in map(json.loads, (S / arq).read_text().splitlines()) if t["status"] == "ok"]


def tipos():
    p = S / "tipos.jsonl"
    return {r["instance_id"]: r["label"] for r in map(json.loads, p.read_text().splitlines())} if p.exists() else {}


def classificar():
    modelo = piloto.PROMPT_TIPO.read_text()
    feitos = tipos()
    with open(S / "tipos.jsonl", "a") as f:
        for t in tarefas():
            if t["instance_id"] in feitos:
                continue
            titulo, _, corpo = t["problem_statement"].partition("\n")
            prompt = modelo.replace("{examples}", "").replace("{title}", titulo.strip()).replace("{body}", corpo.strip())
            texto = chamar_opus("You label GitHub issue reports. Follow the instructions in the user message.", prompt)["result"]
            m = re.search(r"\{.*\}", texto, re.S)
            obj = json.loads(m.group(0)) if m else {}
            f.write(json.dumps({"instance_id": t["instance_id"], "label": str(obj.get("label", "invalid")).lower(),
                                "reasoning": obj.get("reasoning", "")}, ensure_ascii=False) + "\n")
            f.flush()
    tp = tipos()
    with open(S / "conferencia_tipos.csv", "w", newline="") as f:  # planilha para o Caio
        w = csv.writer(f)
        w.writerow(["issue", "link", "titulo", "tipo_skill", "tipo_caio", "nota"])
        for t in tarefas():
            w.writerow([t["issue"], f"https://github.com/gems-uff/sapos/issues/{t['issue']}",
                        t["problem_statement"].partition("\n")[0], tp.get(t["instance_id"], ""), "", ""])
    print("tipos:", {k: list(tp.values()).count(k) for k in set(tp.values())})


def gerar(t, grupo, tipo):
    destino = S / PASTA_TEXTO[grupo] / f"{t['instance_id']}.md"
    if destino.exists():
        return destino.read_text()
    sistema = INSTRUCAO_A if grupo == "skill" else INSTRUCAO_C[tipo]
    saida = chamar_opus(sistema, t["problem_statement"])
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(saida["result"])
    destino.with_suffix(".json").write_text(json.dumps(saida, indent=1))
    return saida["result"]


def resolver(t, grupo, texto):
    pasta = S / grupo / t["instance_id"]
    if (pasta / "patch.diff").exists():
        return
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"iagen-sapos-{grupo}-{t['issue']}"
    subir_base(nome, t["ruby"], t["base_commit"])
    try:
        r = sh(nome, LIMPAR)
        if r.returncode:
            raise RuntimeError("limpeza: " + r.stderr[-300:])
        docker("cp", "-L", str(CLAUDE_BIN), f"{nome}:/usr/local/bin/claude")
        inicio, status = time.time(), "ok"
        try:
            r = subprocess.run(
                ["docker", "exec", "-i", "-e", "CLAUDE_CODE_OAUTH_TOKEN", "-e", "IS_SANDBOX=1", "-e", "DISABLE_AUTOUPDATER=1",
                 "-w", "/sapos", nome, "claude", "-p", "--model", MODELO_RESOLVEDOR, "--output-format", "json",
                 "--dangerously-skip-permissions", "--disallowedTools", "WebFetch", "WebSearch"],
                input=INSTRUCAO_RESOLVEDOR.format(issue=texto), capture_output=True, text=True, env=ambiente(), timeout=LIMITE_S)
            (pasta / "saida.json").write_text(r.stdout)
            (pasta / "stderr.txt").write_text(r.stderr)
            if r.returncode != 0 or json.loads(r.stdout or "{}").get("is_error", True):
                raise RuntimeError(f"resolvedor falhou: {(r.stdout or r.stderr)[-300:]}")
        except subprocess.TimeoutExpired:
            status = "tempo"
        duracao = time.time() - inicio
        # mudanças rastreadas e arquivos novos fora de spec/, coverage/, tmp/ e log/
        # bytes: modo texto troca \r\n por \n e corrompe patch de arquivo com CRLF
        patch = subprocess.run(["docker", "exec", nome, "bash", "-lc",
                                "cd /sapos && git add -A -- . ':(exclude)coverage' ':(exclude)tmp' ':(exclude)log' "
                                "':(exclude)db/*.sqlite3' && git diff --cached --binary HEAD"], capture_output=True).stdout
        (pasta / "patch.diff").write_bytes(patch)
        (pasta / "meta.json").write_text(json.dumps({"status": status, "duracao_s": duracao}))
    finally:
        docker("stop", "-t", "1", nome, check=False)


def avaliar(t, grupo):
    pasta = S / grupo / t["instance_id"]
    if (pasta / "report.json").exists():
        return json.loads((pasta / "report.json").read_text())
    patch = (pasta / "patch.diff").read_bytes()
    if not patch.strip():
        res = {"resolved": False, "patch_vazio": True}
    else:
        nome = f"iagen-sapos-aval-{grupo}-{t['issue']}"
        subir_base(nome, t["ruby"], t["base_commit"])
        try:
            subprocess.run(["docker", "exec", "-i", nome, "bash", "-lc", "cat > /tmp/agente.patch"], input=patch, check=True)
            # como no SWE-bench: patch do agente sem mexer em spec/, depois os testes da correção oficial.
            # Gemfile.lock fica de fora: o bundle install do ambiente já o regenera (e de novo antes dos testes)
            r = sh(nome, "cd /sapos && git apply --whitespace=nowarn --exclude='spec/*' --exclude=Gemfile.lock /tmp/agente.patch")
            if r.returncode:
                res = {"resolved": False, "patch_nao_aplica": True, "erro": r.stderr[-400:]}
            else:
                aplicar(nome, t["test_patch"], "teste")
                r = rodar_specs(nome, t["spec_files"], "aval")
                if r is None:
                    raise RuntimeError(f"rspec sem resultado em {grupo}/{t['instance_id']}")
                f2p = [k for k in t["FAIL_TO_PASS"] if r.get(k) != "passed"]
                p2p = [k for k in t["PASS_TO_PASS"] if r.get(k) != "passed"]
                res = {"resolved": not f2p and not p2p, "f2p_falhou": f2p, "p2p_falhou": p2p}
        finally:
            docker("stop", "-t", "1", nome, check=False)
    (pasta / "report.json").write_text(json.dumps(res))
    return res


def rodar(parte=0, total=1):
    tp = tipos()
    so = set(filter(None, os.environ.get("SAPOS_SO", "").split(",")))  # opcional: só estas tarefas
    for k, t in enumerate(t for t in tarefas() if not so or t["instance_id"] in so):
        if k % total != parte:
            continue
        tipo = tp.get(t["instance_id"])
        grupos = [g for g in GRUPOS if g != "literatura" or tipo in ("bug", "feature")]
        print(time.strftime("%H:%M"), t["instance_id"], tipo, flush=True)
        for tentativa in range(4):
            try:
                textos = {"original": t["problem_statement"]}
                for g in grupos[1:]:
                    textos[g] = gerar(t, g, tipo)
                for g in (grupos if k % 2 == 0 else grupos[::-1]):  # alterna a ordem, como nos parciais
                    resolver(t, g, textos[g])
                    if t.get("FAIL_TO_PASS"):  # nível 2 sem oráculo de testes: quem decide é o juiz (julgar)
                        print("  ", g, avaliar(t, g).get("resolved"), flush=True)
                break
            except Exception as e:
                print(f"   erro (tentativa {tentativa + 1}): {e}", flush=True)
                time.sleep(300)


JUIZ = """You judge whether a code change resolves a GitHub issue of a Ruby on Rails project.
You receive the issue, the maintainers' official fix (code only, used as a reference, not as the only valid answer)
and a candidate patch. Decide whether the candidate patch resolves what the issue asks:
- "resolve": it fixes the reported problem or implements the requested change, even if differently from the official fix;
- "parcial": it addresses only part of the issue, or is likely to fail in cases the issue or the official fix cover;
- "nao_resolve": it does not address the issue, is empty, or breaks it.
Answer with a single JSON object and nothing else: {"justificativa": "<one or two sentences>", "veredito": "resolve|parcial|nao_resolve"}"""


JUIZ_V2 = """You judge whether a code change resolves a GitHub issue of a Ruby on Rails project. Be strict.
You receive the issue, the maintainers' official fix (code only) and a candidate patch.
Step 1: list the behavior changes in the official fix that the issue requires (ignore pure refactoring, comments,
formatting, unrelated changes). Step 2: for each one, check whether the candidate patch produces the same observable
behavior: same names the rest of the system or the tests would rely on (models, columns, routes, methods, messages,
translations), same cases handled, same edge cases. A different implementation is fine only if the observable behavior
is the same. Step 3: decide:
- "resolve": every required behavior change is present and nothing the issue asks for is missing or broken;
- "parcial": some required behavior is missing, differs, or you are not sure (when in doubt, choose "parcial");
- "nao_resolve": the patch does not address the issue, is empty, or breaks it.
Answer with a single JSON object and nothing else:
{"comportamentos": ["<required behavior: present|missing>", ...], "justificativa": "<one sentence>", "veredito": "resolve|parcial|nao_resolve"}"""


def julgar():
    """Juiz LLM (ADR 0012) em toda execução com patch; cego quanto ao grupo. JUIZ=v2 usa a régua rígida."""
    from concurrent.futures import ThreadPoolExecutor
    v2 = os.environ.get("JUIZ") == "v2"
    trabalhos = []
    for t in tarefas():
        for g in GRUPOS:
            p = S / g / t["instance_id"]
            saida_juiz = p / ("juiz_v2.json" if v2 else "juiz.json")
            if (p / "patch.diff").exists() and not saida_juiz.exists():
                trabalhos.append((t, g, p, saida_juiz))

    def um(trabalho):
        t, g, p, saida_juiz = trabalho
        patch = (p / "patch.diff").read_bytes().decode("utf-8", "replace")
        if not patch.strip():
            res = {"veredito": "nao_resolve", "justificativa": "patch vazio"}
        else:
            entrada = (f"<issue>\n{t['problem_statement']}\n</issue>\n\n<official_fix>\n{t['patch'][:60000]}\n</official_fix>\n\n"
                       f"<candidate_patch>\n{patch[:60000]}\n</candidate_patch>")
            texto = chamar_opus(JUIZ_V2 if v2 else JUIZ, entrada)["result"]
            m = re.search(r"\{.*\}", texto, re.S)
            res = json.loads(m.group(0)) if m else {"veredito": "invalido", "justificativa": texto[:300]}
        saida_juiz.write_text(json.dumps(res, ensure_ascii=False))
        return t["instance_id"], g, res.get("veredito")

    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(um, trabalhos):
            print(*r, flush=True)


def calibrar():
    """Juiz × testes nas execuções do nível 1 (ADR 0012). Metade de teste = issues de número ímpar (fixo, por issue)."""
    import hashlib
    def kappa(pares):
        n = len(pares)
        if not n:
            return float("nan")
        po = sum(a == b for a, b in pares) / n
        pa, pb = sum(a for a, _ in pares) / n, sum(b for _, b in pares) / n
        pe = pa * pb + (1 - pa) * (1 - pb)
        return (po - pe) / (1 - pe) if pe < 1 else float("nan")
    for versao in ("juiz.json", "juiz_v2.json"):
        for rotulo, filtro in (("todas", lambda n: True),
                               ("metade de teste", lambda n: int(hashlib.md5(str(n).encode()).hexdigest(), 16) % 2 == 1)):
            pares, mat = [], {}
            for t in tarefas():
                if not filtro(t["issue"]):
                    continue
                for g in GRUPOS:
                    p = S / g / t["instance_id"]
                    if (p / versao).exists() and (p / "report.json").exists():
                        teste = bool(json.loads((p / "report.json").read_text()).get("resolved"))
                        v = json.loads((p / versao).read_text()).get("veredito")
                        pares.append((teste, v == "resolve"))
                        mat[(teste, v)] = mat.get((teste, v), 0) + 1
            tp = sum(a and b for a, b in pares); fp = sum(b and not a for a, b in pares); fn = sum(a and not b for a, b in pares)
            print(f"{versao:13} {rotulo:15} n={len(pares):3} κ={kappa(pares):.2f} precisão={tp / max(tp + fp, 1):.2f} "
                  f"revocação={tp / max(tp + fn, 1):.2f} | {mat}")


def medir():
    tp = tipos()
    linhas = []
    for t in tarefas():
        for g in GRUPOS:
            p = S / g / t["instance_id"]
            if not (p / "report.json").exists():
                continue
            saida = json.loads((p / "saida.json").read_text() or "{}") if (p / "saida.json").exists() else {}
            u = saida.get("usage", {})
            mais, menos, arqs = piloto.linhas((p / "patch.diff").read_bytes().decode("utf-8", "replace"))
            gm, gn, ga = piloto.linhas(t["patch"])
            linhas.append({"instance_id": t["instance_id"], "issue": t["issue"], "criada": t["criada"], "grupo": g,
                           "tipo": tp.get(t["instance_id"], ""), "resolvida": json.loads((p / "report.json").read_text()).get("resolved"),
                           "tokens_entrada": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
                           "tokens_saida": u.get("output_tokens", 0), "turnos": saida.get("num_turns", 0),
                           "duracao_s": round(json.loads((p / "meta.json").read_text())["duracao_s"]),
                           "linhas_mais": mais, "linhas_menos": menos, "arquivos": arqs,
                           "oficial_mais": gm, "oficial_menos": gn, "oficial_arquivos": ga})
    with open(S / "tabela.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    for g in GRUPOS:
        l = [r for r in linhas if r["grupo"] == g]
        print(g, sum(bool(r["resolvida"]) for r in l), "/", len(l))


if __name__ == "__main__":
    {"classificar": classificar, "medir": medir, "julgar": julgar, "calibrar": calibrar, "rodar": lambda: rodar(*map(int, sys.argv[2:]))}[sys.argv[1]]()
