"""Issues fechadas do SAPOS que dariam uma tarefa no molde do SWE-bench (ADR 0010).

Critérios 1 e 2 do SWE-bench: a issue foi fechada por um PR (ou commit) e esse PR mexe em teste
e em código. O critério 3 (teste falha antes do fix e passa depois) exige rodar o projeto.

No SAPOS quase nenhuma issue tem PR ligado formalmente; os commits citam a issue na mensagem
("Issue #560: ..."). Por isso a ligação principal vem de um clone local (git log do ramo principal).

Uso: GITHUB_TOKEN=... python sapos_candidatas.py CAMINHO_DO_CLONE   ->  runs/sapos/candidatas.csv
"""
import csv
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = ("gems-uff", "sapos")
SAIDA = Path(__file__).parent / "runs/sapos"
TESTE = re.compile(r"(^|/)(spec|test|features)/|_spec\.rb$|_test\.rb$")
TOKEN = os.environ["GITHUB_TOKEN"]

CONSULTA = """
query($dono: String!, $nome: String!, $depois: String) {
  repository(owner: $dono, name: $nome) {
    issues(states: CLOSED, first: 50, after: $depois, orderBy: {field: CREATED_AT, direction: ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title createdAt closedAt stateReason
        labels(first: 20) { nodes { name } }
        closedByPullRequestsReferences(first: 5, includeClosedPrs: true) {
          nodes { number merged files(first: 100) { nodes { path } } }
        }
        timelineItems(itemTypes: [CLOSED_EVENT], last: 1) {
          nodes { ... on ClosedEvent { closer {
            __typename
            ... on PullRequest { number merged files(first: 100) { nodes { path } } }
            ... on Commit { oid }
          } } }
        }
      }
    }
  }
}"""


def pedir(url, corpo=None):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None,
                                 headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def arquivos_do_commit(sha):
    return [f["filename"] for f in pedir(f"https://api.github.com/repos/{REPO[0]}/{REPO[1]}/commits/{sha}").get("files", [])]


def commits_por_issue(clone):
    """{issue: [(sha, assunto, [arquivos])]} para commits do ramo principal que citam #N no assunto."""
    log = subprocess.run(["git", "-C", clone, "log", "--reverse", "--format=%x01%H%x00%s", "--name-only", "HEAD"],
                         capture_output=True, text=True, check=True).stdout
    por = {}
    for bloco in log.split("\x01")[1:]:
        cab, _, resto = bloco.partition("\n")
        sha, assunto = cab.split("\x00", 1)
        arqs = [a for a in resto.split("\n") if a]
        for n in set(re.findall(r"#(\d+)\b", assunto)):
            por.setdefault(int(n), []).append((sha, assunto, arqs))
    return por


def main():
    por_commit = commits_por_issue(sys.argv[1])
    issues, depois = [], None
    while True:
        d = pedir("https://api.github.com/graphql", {"query": CONSULTA, "variables": {"dono": REPO[0], "nome": REPO[1], "depois": depois}})
        bloco = d["data"]["repository"]["issues"]
        issues += bloco["nodes"]
        if not bloco["pageInfo"]["hasNextPage"]:
            break
        depois = bloco["pageInfo"]["endCursor"]

    linhas = []
    for i in issues:
        # quem fechou: PR ligado à issue (merged primeiro) ou o "closer" do evento de fechamento
        prs = [p for p in i["closedByPullRequestsReferences"]["nodes"]]
        closer = (i["timelineItems"]["nodes"] or [{}])[-1].get("closer") or {}
        if closer.get("__typename") == "PullRequest" and closer["number"] not in [p["number"] for p in prs]:
            prs.append(closer)
        prs.sort(key=lambda p: not p["merged"])
        if prs:
            fonte, ref, merged = "PR", f"#{prs[0]['number']}", prs[0]["merged"]
            arqs = [f["path"] for f in prs[0]["files"]["nodes"]]
        elif closer.get("__typename") == "Commit":
            fonte, ref, merged = "commit", closer["oid"][:10], True
            arqs = arquivos_do_commit(closer["oid"])
        else:
            fonte, ref, merged, arqs = "nenhum", "", False, []
        cits = por_commit.get(i["number"], [])
        if fonte == "nenhum" and cits:  # ligação pela mensagem do commit
            fonte, ref, merged = "mensagem de commit", f"{len(cits)} commits", True
            arqs = sorted({a for _, _, fs in cits for a in fs})
        testes = [a for a in arqs if TESTE.search(a)]
        codigo = [a for a in arqs if not TESTE.search(a)]
        linhas.append({
            "issue": i["number"], "titulo": i["title"], "criada": i["createdAt"][:10], "fechada": i["closedAt"][:10],
            "motivo": i["stateReason"], "labels": ";".join(l["name"] for l in i["labels"]["nodes"]),
            "fechada_por": fonte, "ref": ref, "merged": merged,
            "mexe_teste": bool(testes), "mexe_codigo": bool(codigo), "arquivos_teste": ";".join(testes),
            "commit_base": subprocess.run(["git", "-C", sys.argv[1], "rev-parse", f"{cits[0][0]}^"], capture_output=True,
                                          text=True).stdout.strip()[:10] if cits else "",
            "commits_reproduzir": sum("reproduz" in a.lower() for _, a, _ in cits),
        })
    SAIDA.mkdir(parents=True, exist_ok=True)
    with open(SAIDA / "candidatas.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    print(len(linhas), "issues fechadas ->", SAIDA / "candidatas.csv")


if __name__ == "__main__":
    main()
