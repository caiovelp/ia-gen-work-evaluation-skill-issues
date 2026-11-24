"""Gera tabelas, números e figura do paper a partir dos dados (ADR 0011).

Uso: python paper_tabelas.py   ->  docs/paper/{numeros,tabela_swebench,tabela_sapos,figura_metodologia}.tex + metodologia.png
"""
import csv
import json
import re
import statistics
from pathlib import Path


RAIZ = Path(__file__).parent
P = RAIZ / "docs/paper"
GRUPOS = ("skill", "original", "literatura")
NOME = {"skill": "A (skill)", "original": "B (original)", "literatura": "C (literatura)"}
PRECO = {"entrada": 2.00, "saida": 10.00, "escrita_1h": 4.00, "escrita_5m": 2.50, "leitura": 0.20}  # Sonnet 5.5, US$/milhão


def br(x, casas=0):
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def custo(saida):
    u = saida["usage"]
    cc = u.get("cache_creation", {})
    return (u["input_tokens"] * PRECO["entrada"] + u["output_tokens"] * PRECO["saida"]
            + cc.get("ephemeral_1h_input_tokens", 0) * PRECO["escrita_1h"] + cc.get("ephemeral_5m_input_tokens", 0) * PRECO["escrita_5m"]
            + u["cache_read_input_tokens"] * PRECO["leitura"]) / 1e6


def arquivos(patch):
    return set(re.findall(r"^diff --git a/(\S+)", patch, re.M))


def resumo(base, ids, oficial):
    """Linhas da tabela para os três grupos nas mesmas issues. oficial[i] = patch do fix oficial."""
    lin = {}
    for g in GRUPOS:
        rep = {i: json.loads((base / g / i / "report.json").read_text()) for i in ids}
        sai = {i: json.loads((base / g / i / "saida.json").read_text() or "{}") for i in ids}
        pat = {i: (base / g / i / "patch.diff").read_text() for i in ids}
        tok = [s["usage"]["input_tokens"] + s["usage"].get("cache_creation_input_tokens", 0) + s["usage"]["cache_read_input_tokens"]
               for s in sai.values() if s.get("usage")]
        n = len(ids)
        resolvidas = sum(bool(r.get("resolved")) for r in rep.values())
        mesmos = sum(bool(arquivos(pat[i])) and arquivos(pat[i]) == arquivos(oficial[i]) for i in ids)
        quebrou = sum(bool(r.get("p2p_falhou") or r.get("tests_status", {}).get("PASS_TO_PASS", {}).get("failure")) for r in rep.values())
        lin[g] = {
            "Resolvidas": f"{resolvidas} ({100 * resolvidas / n:.0f}\\%)",
            "Tokens de entrada (mediana)": br(statistics.median(tok)) if tok else "--",
            "Custo estimado, US\\$ (mediana)": br(statistics.median([custo(s) for s in sai.values() if s.get("usage")]), 3) if tok else "--",
            "Tempo, s (mediana)": br(statistics.median(json.loads((base / g / i / "meta.json").read_text())["duracao_s"] for i in ids)),
            "Mesmos arquivos do fix oficial": f"{mesmos} ({100 * mesmos / n:.0f}\\%)",
            "Quebra teste que passava": f"{quebrou} ({100 * quebrou / n:.0f}\\%)",
        }
    return lin


def tabela(rotulo, legenda, lin, n):
    linhas = [f"\\begin{{table}}[t]\n\\caption{{{legenda}}}\n\\label{{tab:{rotulo}}}\n\\small\n\\begin{{tabular}}{{lrrr}}\n\\toprule",
              " & " + " & ".join(NOME[g] for g in GRUPOS) + r" \\", r"\midrule"]
    for medida in lin["skill"]:
        linhas.append(medida + " & " + " & ".join(lin[g][medida] for g in GRUPOS) + r" \\")
    linhas += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(linhas) + "\n"


def swebench():
    from datasets import load_dataset
    dados = {x["instance_id"]: x for x in load_dataset("SWE-bench/SWE-bench_Lite", split="test")}
    runs = RAIZ / "runs"
    ids = sorted(set(p.parent.name for p in (runs / "literatura").glob("*/report.json"))
                 & set(p.parent.name for p in (runs / "skill").glob("*/report.json"))
                 & set(p.parent.name for p in (runs / "original").glob("*/report.json")))
    lin = resumo(runs, ids, {i: dados[i]["patch"] for i in ids})
    return tabela("swebench", f"SWE-bench Lite: as mesmas {len(ids)} issues bug/feature nos três grupos.", lin, len(ids))


def sapos():
    s = RAIZ / "runs/sapos"
    tarefas = [t for t in map(json.loads, (s / "tarefas.jsonl").read_text().splitlines()) if t["status"] == "ok"] \
        if (s / "tarefas.jsonl").exists() else []
    ids = [t["instance_id"] for t in tarefas
           if all((s / g / t["instance_id"] / "report.json").exists() for g in GRUPOS)]
    numeros = {"SaposN": str(len(tarefas)), "SaposKappa": "[$\\kappa$ a medir]"}
    if not ids:
        return "\\begin{table}[t]\\caption{SAPOS: resultados a preencher.}\\label{tab:sapos}\\end{table}\n", numeros
    oficial = {t["instance_id"]: t["patch"] for t in tarefas}
    return tabela("sapos", f"SAPOS: as mesmas {len(ids)} issues nos três grupos.", resumo(s, ids, oficial), len(ids)), numeros


def figura():
    # figura em TikZ: docs/paper/overview.tex -> overview.pdf (compilar à parte)
    return ("\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{overview.pdf}\n"
            "\\caption{Visão geral do experimento: a mesma issue em três versões, resolvida pelo agente e avaliada por testes ou juiz LLM.}\n"
            "\\label{fig:metodologia}\n\\end{figure}\n")


def sapos_amplo():
    s = RAIZ / "runs/sapos"
    amp = [json.loads(l) for l in (s / "tarefas_amplas.jsonl").read_text().splitlines()]
    def v(g, i):
        f = s / g / i / "juiz_v2.json"
        return json.loads(f.read_text()).get("veredito") if f.exists() else None
    ab = [t["instance_id"] for t in amp if all(v(g, t["instance_id"]) for g in ("skill", "original"))]
    abc = [i for i in ab if v("literatura", i)]
    linha = lambda ids, g: f"{sum(v(g, i) == 'resolve' for i in ids)} ({100 * sum(v(g, i) == 'resolve' for i in ids) / len(ids):.0f}\\%)"
    tab = ("\\begin{table}[t]\n\\caption{SAPOS, nível amplo: resolvidas segundo o juiz LLM ($\\kappa$ 0,76 contra os testes no nível estrito).}\n"
           "\\label{tab:sapos-amplo}\n\\small\n\\begin{tabular}{lrrr}\n\\toprule\n & A (skill) & B (original) & C (literatura) \\\\\n\\midrule\n"
           f"Todas ({len(ab)}) & {linha(ab, 'skill')} & {linha(ab, 'original')} & -- \\\\\n"
           f"Bug/feature ({len(abc)}) & {linha(abc, 'skill')} & {linha(abc, 'original')} & {linha(abc, 'literatura')} \\\\\n"
           "\\bottomrule\n\\end{tabular}\n\\end{table}\n")
    return tab, {"SaposAmploN": str(len(ab))}


if __name__ == "__main__":
    (P / "tabela_swebench.tex").write_text(swebench())
    t, numeros = sapos()
    (P / "tabela_sapos.tex").write_text(t)
    ta, na = sapos_amplo()
    (P / "tabela_sapos_amplo.tex").write_text(ta)
    numeros.update(na)
    (P / "numeros.tex").write_text("".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in numeros.items()))
    (P / "figura_metodologia.tex").write_text(figura())
    print("ok")
