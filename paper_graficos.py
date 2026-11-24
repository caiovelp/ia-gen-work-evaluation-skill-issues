"""Gráfico da RQ1 do paper (pandas + matplotlib, estilo padrão).

Uso: python paper_graficos.py  ->  docs/paper/resultados_rq1.{pdf,png}
Precisa de pandas e matplotlib (não estão no .venv do projeto).
"""
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).parent
RUNS = RAIZ / "runs"
SAPOS = RUNS / "sapos"
GRUPOS = {"skill": "A (skill)", "original": "B (original)", "literatura": "C (literature)"}


def wilson(k, n, z=1.96):
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centro - meia, centro + meia


def resolvido(base, g, i):
    return bool(json.loads((base / g / i / "report.json").read_text()).get("resolved"))


def juiz(g, i):
    f = SAPOS / g / i / "juiz_v2.json"
    return json.loads(f.read_text()).get("veredito") if f.exists() else None


def corpora():
    """{rótulo: {grupo: [bool por issue]}}, sempre as mesmas issues nos três grupos (só bug/feature)."""
    swe = set.intersection(*(set(p.parent.name for p in (RUNS / g).glob("*/report.json")) for g in GRUPOS))
    tarefas = [json.loads(l) for l in (SAPOS / "tarefas.jsonl").read_text().splitlines()]
    estrito = [t["instance_id"] for t in tarefas
               if t["status"] == "ok" and all((SAPOS / g / t["instance_id"] / "report.json").exists() for g in GRUPOS)]
    amplas = [json.loads(l)["instance_id"] for l in (SAPOS / "tarefas_amplas.jsonl").read_text().splitlines()]
    todas = [i for i in amplas if all(juiz(g, i) for g in GRUPOS)]
    return {
        f"SWE-bench Lite\n(n={len(swe)}, tests)": {g: [resolvido(RUNS, g, i) for i in swe] for g in GRUPOS},
        f"SAPOS strict\n(n={len(estrito)}, tests)": {g: [resolvido(SAPOS, g, i) for i in estrito] for g in GRUPOS},
        f"SAPOS all\n(n={len(todas)}, LLM judge)": {g: [juiz(g, i) == "resolve" for i in todas] for g in GRUPOS},
    }


def main():
    taxa, erro_baixo, erro_alto = {}, {}, {}
    for corpus, por_grupo in corpora().items():
        for g, res in por_grupo.items():
            k, n = sum(res), len(res)
            lo, hi = wilson(k, n)
            taxa.setdefault(GRUPOS[g], {})[corpus] = 100 * k / n
            erro_baixo.setdefault(GRUPOS[g], {})[corpus] = 100 * (k / n - lo)
            erro_alto.setdefault(GRUPOS[g], {})[corpus] = 100 * (hi - k / n)
    df = pd.DataFrame(taxa)
    erros = [[pd.DataFrame(erro_baixo)[c].values, pd.DataFrame(erro_alto)[c].values] for c in df.columns]

    ax = df.plot.bar(figsize=(3.4, 2.3), rot=0, yerr=erros, capsize=2, width=0.8,
                     error_kw={"elinewidth": 0.7, "ecolor": "black"})
    for barras in [c for c in ax.containers if hasattr(c, "datavalues")]:
        ax.bar_label(barras, fmt="%.0f", fontsize=6, padding=1)
    ax.set_ylabel("Resolved (%)", fontsize=8)
    ax.set_ylim(0, 100)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6.5, ncol=3, loc="upper right", frameon=False)
    plt.tight_layout(pad=0.2)
    destino = RAIZ / "docs/paper/resultados_rq1"
    plt.savefig(f"{destino}.pdf")
    plt.savefig(f"{destino}.png", dpi=300)
    print(df.round(1))


if __name__ == "__main__":
    main()
