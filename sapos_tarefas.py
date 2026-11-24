"""Monta tarefas no molde do SWE-bench a partir das issues do SAPOS (ADR 0011).

Para cada candidata (mexe em teste e código, criada de 2024 em diante):
  1. junta os commits da issue sobre o commit base (cherry-pick sem commitar) e separa
     a correção em patch de teste (spec/) e patch de código (o "fix oficial");
  2. no container da época: aplica só o patch de teste e roda os specs tocados (antes);
     aplica o patch de código e roda de novo (depois);
  3. FAIL_TO_PASS = falhava antes e passa depois; PASS_TO_PASS = passava e continua.
Fica só a tarefa com ao menos um FAIL_TO_PASS.

Uso: GITHUB_TOKEN=... python sapos_tarefas.py CLONE_LOCAL   ->  runs/sapos/tarefas.jsonl
"""
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "runs/sapos"
CLONE = Path(sys.argv[1]) if len(sys.argv) > 1 else None
IMAGEM = {"3.4": "iagen-sapos:ruby-3.4.10", "3.2": "iagen-sapos:ruby-3.2.5", "3.2.11": "iagen-sapos:ruby-3.2.11"}
VERSAO = {"3.4": "3.4.10", "3.2": "3.2.5", "3.2.11": "3.2.11"}


def git(*args, cwd=None, check=True):
    # bytes + decode: modo texto do Python troca \r\n por \n e corrompe patch de arquivo com CRLF
    r = subprocess.run(["git", "-C", str(cwd or CLONE), *args], capture_output=True, check=check)
    return r.stdout.decode("utf-8", "surrogateescape")


def docker(*args, check=True, **kw):
    return subprocess.run(["docker", *args], capture_output=True, text=True, check=check, **kw)


def sh(nome, cmd, timeout=3600):
    return docker("exec", nome, "bash", "-lc", cmd, check=False, timeout=timeout)


def issue_texto(numero):
    req = urllib.request.Request(f"https://api.github.com/repos/gems-uff/sapos/issues/{numero}",
                                 headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"})
    i = json.load(urllib.request.urlopen(req))
    return f"{i['title']}\n{i.get('body') or ''}".strip()


def commits_da_issue(numero):
    """Commits do ramo principal que citam #numero no assunto, em ordem cronológica."""
    log = git("log", "--reverse", "--format=%H%x00%s", "HEAD")
    return [sha for sha, assunto in (l.split("\x00", 1) for l in log.splitlines())
            if str(numero) in re.findall(r"#(\d+)\b", assunto)]


def montar_patches(base, commits):
    """Cherry-pick dos commits da issue sobre a base, sem commitar; None se houver conflito."""
    with tempfile.TemporaryDirectory() as wt:
        git("worktree", "add", "--detach", wt, base)
        try:
            r = subprocess.run(["git", "-C", wt, "cherry-pick", "-n", *commits], capture_output=True, text=True)
            if r.returncode != 0:
                # plano B: diff acumulado base..último commit, só nos arquivos tocados pelos commits da issue
                # (pode trazer mudanças de outras issues nesses arquivos; marcado na tarefa)
                subprocess.run(["git", "-C", wt, "cherry-pick", "--abort"], capture_output=True)
                subprocess.run(["git", "-C", wt, "reset", "-q", "--hard", base], capture_output=True)
                tocados = sorted({f for c in commits for f in git("show", "--name-only", "--format=", c).split()})
                subprocess.run(["git", "-C", wt, "checkout", commits[-1], "--", *tocados], capture_output=True)
                for f in tocados:  # arquivo removido no fim da série
                    if not git("ls-tree", commits[-1], "--", f).strip():
                        subprocess.run(["git", "-C", wt, "rm", "-q", "--ignore-unmatch", "--", f], capture_output=True)
                subprocess.run(["git", "-C", wt, "add", "-A"], capture_output=True)
                montar_patches.metodo = "diff acumulado"
            else:
                montar_patches.metodo = "cherry-pick"
            teste = git("diff", "--cached", "--binary", "HEAD", "--", "spec", cwd=wt) or git("diff", "--binary", "HEAD", "--", "spec", cwd=wt)
            codigo = git("diff", "--cached", "--binary", "HEAD", "--", ".", ":(exclude)spec", cwd=wt) or git("diff", "--binary", "HEAD", "--", ".", ":(exclude)spec", cwd=wt)
            arquivos = (git("diff", "--cached", "--name-only", "HEAD", "--", "spec", cwd=wt) or git("diff", "--name-only", "HEAD", "--", "spec", cwd=wt)).split()
            return teste, codigo, [a for a in arquivos if a.endswith("_spec.rb")]
        finally:
            git("worktree", "remove", "--force", wt, check=False)


def preparar_volumes():
    docker("volume", "create", "sapos-mirror")
    for v in VERSAO.values():
        docker("volume", "create", f"sapos-bundle-{v}")
    r = docker("run", "--rm", "-v", "sapos-mirror:/mirror", IMAGEM["3.4"], "bash", "-lc",
               "test -d /mirror/sapos.git && git -C /mirror/sapos.git fetch -q origin '+refs/heads/*:refs/heads/*' "
               "|| git clone -q --mirror https://github.com/gems-uff/sapos.git /mirror/sapos.git", check=False)
    if r.returncode:
        raise RuntimeError(r.stderr[-500:])


def subir(nome, familia, base):
    """Container da época com o SAPOS no commit base e as gems instaladas."""
    docker("run", "-d", "--rm", "--name", nome, "-v", "sapos-mirror:/mirror:ro",
           "-v", f"sapos-bundle-{VERSAO[familia]}:/bundle", IMAGEM[familia], "sleep", "14400")
    cmds = [
        f"git clone -q /mirror/sapos.git /sapos && cd /sapos && git checkout -q {base}",
        # ponytail: versão de patch do Ruby fixada pela imagem (3.2.1/3.2.11 rodam em 3.2.5)
        f"cd /sapos && echo {VERSAO[familia]} > .ruby-version && git update-index --assume-unchanged .ruby-version",
        "cd /sapos && (bundle install --quiet --jobs 8 || bundle install --jobs 8)",
        # como o CI: configs locais vêm dos .example (database.yml etc.); testes em SQLite
        "cd /sapos && find config -name '*.example' | while read f; do t=${f%.example}; [ -e $t ] || cp $f $t; done",
        "cd /sapos && bundle exec rails db:schema:load",
        # configs locais e banco de teste ficam fora de qualquer diff
        "cd /sapos && git status --porcelain --untracked-files=all | sed -n 's/^?? //p' >> .git/info/exclude",
    ]
    for c in cmds:
        r = sh(nome, c)
        if r.returncode:
            raise RuntimeError(f"{c[:60]}: {(r.stderr or r.stdout)[-800:]}")


def rodar_specs(nome, arquivos, saida):
    # o patch pode trazer gem nova ou migração: instala e recarrega o schema antes de testar
    sh(nome, "cd /sapos && bundle install --quiet --jobs 8 && bundle exec rails db:schema:load >/dev/null 2>&1")
    sh(nome, f"cd /sapos && timeout 2400 bundle exec rspec {' '.join(arquivos)} --format json --out /tmp/{saida}.json "
             f">/tmp/{saida}.log 2>&1")
    bruto = sh(nome, f"cat /tmp/{saida}.json").stdout
    if not bruto.strip():
        return None
    return {e["id"]: e["status"] for e in json.loads(bruto)["examples"]}


def aplicar(nome, patch, rotulo):
    docker("exec", "-i", nome, "bash", "-lc", f"cat > /tmp/{rotulo}.patch", input=patch)
    return sh(nome, f"cd /sapos && git apply --whitespace=nowarn /tmp/{rotulo}.patch").returncode == 0


def validar(c):
    numero = c["issue"]
    base = c["commit_base"]
    rv = git("show", f"{base}:.ruby-version").strip()
    familia = rv if rv in IMAGEM else ("3.4" if rv.startswith("3.4") else "3.2")  # Gemfile pode travar o patch (~> 3.2.11)
    commits = commits_da_issue(numero)
    patches = montar_patches(base, commits)
    tarefa = {"instance_id": f"sapos-{numero}", "issue": int(numero), "criada": c["criada"], "base_commit": base,
              "ruby": familia, "commits": commits}
    tarefa["metodo_patch"] = getattr(montar_patches, "metodo", "cherry-pick")
    if patches is None:
        return {**tarefa, "status": "conflito no cherry-pick"}
    teste, codigo, specs = patches
    if not specs or not codigo.strip():
        return {**tarefa, "status": "sem spec ou sem código"}
    nome = f"iagen-sapos-val-{numero}"
    try:
        subir(nome, familia, base)
        if not aplicar(nome, teste, "teste"):
            return {**tarefa, "status": "patch de teste não aplica"}
        existentes = [s for s in specs if sh(nome, f"test -f /sapos/{s}").returncode == 0]
        antes = rodar_specs(nome, existentes, "antes")
        if not aplicar(nome, codigo, "codigo"):
            return {**tarefa, "status": "patch de código não aplica"}
        depois = rodar_specs(nome, existentes, "depois")
    except RuntimeError as e:
        return {**tarefa, "status": f"ambiente: {e}"[:400]}
    finally:
        docker("stop", "-t", "1", nome, check=False)
    if antes is None or depois is None:
        return {**tarefa, "status": "rspec não gerou resultado"}
    f2p = sorted(k for k, v in depois.items() if v == "passed" and antes.get(k) != "passed")
    p2p = sorted(k for k, v in depois.items() if v == "passed" and antes.get(k) == "passed")
    return {**tarefa, "status": "ok" if f2p else "sem FAIL_TO_PASS", "problem_statement": issue_texto(numero),
            "test_patch": teste, "patch": codigo, "spec_files": existentes, "FAIL_TO_PASS": f2p, "PASS_TO_PASS": p2p,
            "falhas_depois": sorted(k for k, v in depois.items() if v == "failed")}


def candidatas(incluir=()):
    """De 2024 em diante, mais as issues pedidas explicitamente (ADR 0011: antigas com base em Ruby 3.2/3.4)."""
    return [r for r in csv.DictReader(open(SAIDA / "candidatas.csv"))
            if r["mexe_teste"] == "True" and r["mexe_codigo"] == "True" and r["commit_base"]
            and (r["criada"] >= "2024" or r["issue"] in incluir)]


def main():
    preparar_volumes()
    destino = SAIDA / "tarefas.jsonl"
    feitas = {json.loads(l)["issue"] for l in destino.read_text().splitlines()} if destino.exists() else set()
    filtro = set(sys.argv[2:])  # opcional: só estas issues
    for c in candidatas(filtro):
        if int(c["issue"]) in feitas or (filtro and c["issue"] not in filtro):
            continue
        t = validar(c)
        with open(destino, "a") as f:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
        print(t["instance_id"], t["status"], len(t.get("FAIL_TO_PASS", [])), "F2P", flush=True)





def montar_amplas():
    """Nível 2 (ADR 0012): issues com correção em código e base em Ruby 3.2/3.4, com ou sem teste.
    Reaproveita as tarefas do nível 1; as demais ganham só o fix oficial (código), sem oráculo de testes."""
    estritas = {t["issue"]: t for t in map(json.loads, (SAIDA / "tarefas.jsonl").read_text().splitlines()) if t["status"] == "ok"}
    destino = SAIDA / "tarefas_amplas.jsonl"
    feitas = {json.loads(l)["issue"] for l in destino.read_text().splitlines()} if destino.exists() else set()
    for c in csv.DictReader(open(SAIDA / "candidatas.csv")):
        n = int(c["issue"])
        if n in feitas or c["fechada_por"] == "nenhum" or c["motivo"] != "COMPLETED" or c["mexe_codigo"] != "True" or not c["commit_base"]:
            continue
        rv = git("show", f"{c['commit_base']}:.ruby-version", check=False).strip()  # base antiga não tem o arquivo
        if rv[:3] not in ("3.2", "3.4"):
            continue
        if n in estritas:
            t = {**estritas[n], "nivel": 1}
        else:
            familia = rv if rv in IMAGEM else ("3.4" if rv.startswith("3.4") else "3.2")
            commits = commits_da_issue(n)
            patches = montar_patches(c["commit_base"], commits) if commits else None
            if not patches or not patches[1].strip():
                continue
            t = {"instance_id": f"sapos-{n}", "issue": n, "criada": c["criada"], "base_commit": c["commit_base"], "ruby": familia,
                 "commits": commits, "metodo_patch": getattr(montar_patches, "metodo", "cherry-pick"), "status": "ok",
                 "problem_statement": issue_texto(n), "patch": patches[1], "nivel": 2}
        with open(destino, "a") as f:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
        print(t["instance_id"], "nível", t["nivel"], flush=True)


if __name__ == "__main__":
    montar_amplas() if os.environ.get("NIVEL") == "amplo" else main()
