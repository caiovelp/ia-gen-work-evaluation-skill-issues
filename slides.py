"""Apresentação 2 (resultados parciais), no estilo do PDF da proposta (ADR 0007).

Uso: python piloto.py medir && python slides.py
Saída: docs/apresentacao2/Resultados_Parciais.pptx e .pdf
"""
import csv
import json
import statistics
import subprocess
from pathlib import Path

from datasets import load_dataset
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

RAIZ = Path(__file__).parent
RUNS = RAIZ / "runs"
SAIDA = RAIZ / "docs/apresentacao2"

NAVY, ROXO_C, TEAL_C = RGBColor(0x1B, 0x1F, 0x3B), RGBColor(0x2B, 0x28, 0x5F), RGBColor(0x1A, 0x36, 0x4B)
ROXO, AZUL, TEAL = RGBColor(0x6D, 0x4F, 0xF2), RGBColor(0x42, 0x8B, 0xE3), RGBColor(0x17, 0xA3, 0x98)
CARD, CINZA, BRANCO, VERMELHO = RGBColor(0xF4, 0xF5, 0xF9), RGBColor(0x80, 0x84, 0x96), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xE0, 0x4B, 0x4B)
SERIF, SANS = "Caladea", "Carlito"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(10), Inches(5.625)
VAZIO = prs.slide_layouts[6]


def texto(slide, x, y, w, h, t, tam=14, cor=NAVY, fonte=SANS, negrito=False, italico=False, alinha=PP_ALIGN.LEFT):
    caixa = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = caixa.text_frame
    tf.word_wrap = True
    for i, linha in enumerate(t.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinha
        r = p.add_run()
        r.text = linha
        r.font.size, r.font.name, r.font.bold, r.font.italic = Pt(tam), fonte, negrito, italico
        r.font.color.rgb = cor
    return caixa


def forma(slide, tipo, x, y, w, h, cor):
    s = slide.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = cor
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def fundo(slide, cor):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = cor


def capa(titulo, sub):
    s = prs.slides.add_slide(VAZIO)
    fundo(s, NAVY)
    forma(s, MSO_SHAPE.OVAL, 7.3, -1.6, 3.6, 3.6, ROXO_C)
    forma(s, MSO_SHAPE.OVAL, 8.2, 3.6, 2.8, 2.8, TEAL_C)
    texto(s, 0.6, 0.75, 7, 0.4, "IA para Engenharia de Software", 12, CINZA)
    texto(s, 0.6, 1.4, 7.2, 1.4, titulo, 28, BRANCO, SERIF, True)
    texto(s, 0.6, 3.0, 7, 0.4, sub, 14, CINZA, italico=True)
    texto(s, 0.6, 4.1, 5, 0.3, "Caio Paranhos", 13, BRANCO, negrito=True)
    texto(s, 0.6, 4.4, 5, 0.3, "Profa. Vania Neves", 12, CINZA)


def pagina(titulo, sub=None):
    s = prs.slides.add_slide(VAZIO)
    fundo(s, BRANCO)
    texto(s, 0.5, 0.3, 9, 0.6, titulo, 24, NAVY, SERIF, True)
    if sub:
        texto(s, 0.5, 0.85, 9, 0.35, sub, 13, CINZA, italico=True)
    return s


def cartao(s, x, y, w, h, rotulo, cor, corpo, tam=14):
    forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, CARD).adjustments[0] = 0.04
    pill = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.2, y + 0.2, 0.25 + 0.085 * len(rotulo), 0.3, cor)
    pill.adjustments[0] = 0.2
    tf = pill.text_frame
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = rotulo
    r.font.size, r.font.name, r.font.bold, r.font.color.rgb = Pt(11), SANS, True, BRANCO
    texto(s, x + 0.2, y + 0.65, w - 0.4, h - 0.8, corpo, tam)


def numero(s, x, y, w, valor, legenda, cor=NAVY):
    texto(s, x, y, w, 0.7, valor, 34, cor, SERIF, True, alinha=PP_ALIGN.CENTER)
    texto(s, x, y + 0.75, w, 0.6, legenda, 12, CINZA, alinha=PP_ALIGN.CENTER)


def tabela(s, x, y, w, linhas, larguras):
    t = s.shapes.add_table(len(linhas), len(linhas[0]), Inches(x), Inches(y), Inches(w), Inches(0.38 * len(linhas))).table
    for j, lg in enumerate(larguras):
        t.columns[j].width = Inches(lg)
    for i, linha in enumerate(linhas):
        for j, v in enumerate(linha):
            c = t.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = NAVY if i == 0 else (CARD if i % 2 else BRANCO)
            c.text = str(v) or " "
            for par in c.text_frame.paragraphs:
                par.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
                for r in par.runs:
                    r.font.size, r.font.name = Pt(13), SANS
                    r.font.bold = i == 0 or j == 0
                    r.font.color.rgb = BRANCO if i == 0 else NAVY


def med(valores):
    return statistics.median(valores) if valores else 0


def fmt(v):
    return f"{v:,.0f}".replace(",", ".")


# ---------- dados ----------
import re
from piloto import nomes_do_patch, tipos

A, B, C = "skill", "original", "literatura"  # nomes das pastas em runs/
COR = {A: ROXO, B: AZUL, C: TEAL}
NOME = {A: "Grupo A · Skill", B: "Grupo B · Original", C: "Grupo C · Literatura"}
tab = list(csv.DictReader(open(RUNS / "tabela.csv")))
for r in tab:
    r["resolvida"] = r["resolvida"] == "True"
R = {g: {r["instance_id"]: r for r in tab if r["grupo"] == g} for g in (A, B, C)}
tipo = tipos()
dados = {x["instance_id"]: x for x in load_dataset("SWE-bench/SWE-bench_Lite", split="test")}
ab = sorted(set(R[A]) & set(R[B]))                      # 296: A e B
abc = sorted(set(ab) & set(R[C]))                       # bug/feature com os três grupos
por_tipo = {t: [i for i in ab if tipo.get(i) == t] for t in ("bug", "feature", "neither", "discard")}
excluidas = sum(not json.loads(p.read_text()).get("resolved") for p in (RUNS / "oficial").glob("*/report.json"))
num = lambda g, k, ids: [float(R[g][i][k]) for i in ids]
resolvidas = lambda g, ids: sum(R[g][i]["resolvida"] for i in ids)

# completude das issues originais: seção do texto do grupo C marcada "Not provided" = item ausente na original
ITENS_BUG = ["Steps to reproduce", "Observed behavior", "Expected behavior", "Stack trace / error output",
             "Test case", "Code example", "Version and environment"]
ITENS_FEATURE = ["Product version", "Rationale", "Use case or scenario", "Possible solution"]
def secoes(i):
    t = (RUNS / "specs_literatura" / f"{i}.md").read_text()
    partes = re.split(r"^## +(.+)$", t, flags=re.M)
    return {partes[k].strip(): partes[k + 1] for k in range(1, len(partes) - 1, 2)}
def presenca(ids, itens):
    sec = [secoes(i) for i in ids if (RUNS / "specs_literatura" / f"{i}.md").exists()]
    return len(sec), {it: sum(it in s_ and "not provided in the original" not in s_[it].lower() for s_ in sec) for it in itens}

tem = lambda nome, t: re.search(rf"\b{re.escape(nome)}\b", t) is not None
eh_arquivo = lambda x: "/" in x or x.endswith(".py") or "." in x
def vazamento(pasta, ids):
    v = {i: [x for x in nomes_do_patch(dados[i]["patch"])
             if tem(x, (RUNS / pasta / f"{i}.md").read_text()) and not tem(x, dados[i]["problem_statement"])] for i in ids}
    return sum(any(eh_arquivo(x) for x in l) for l in v.values()), sum(any(not eh_arquivo(x) for x in l) for l in v.values())

PRECO = {"entrada": 2.00, "saida": 10.00, "escrita_1h": 4.00, "escrita_5m": 2.50, "leitura": 0.20}  # Sonnet 5.5, US$/milhão, tabela oficial


def custo_oficial(g, i):
    u = json.loads((RUNS / g / i / "saida.json").read_text())["usage"]
    cc = u.get("cache_creation", {})
    return (u["input_tokens"] * PRECO["entrada"] + u["output_tokens"] * PRECO["saida"]
            + cc.get("ephemeral_1h_input_tokens", 0) * PRECO["escrita_1h"]
            + cc.get("ephemeral_5m_input_tokens", 0) * PRECO["escrita_5m"]
            + u["cache_read_input_tokens"] * PRECO["leitura"]) / 1e6


def mcnemar(g1, g2, ids):
    from math import comb
    a = sum(R[g1][i]["resolvida"] and not R[g2][i]["resolvida"] for i in ids)
    b = sum(R[g2][i]["resolvida"] and not R[g1][i]["resolvida"] for i in ids)
    return a, b, min(1.0, 2 * sum(comb(a + b, j) for j in range(min(a, b) + 1)) / 2 ** (a + b))


def tabela_grupos(s, x, y, w, primeira, linhas, grupos, larguras):
    tabela(s, x, y, w, [[primeira] + [NOME[g] if g in NOME else g for g in grupos]] + linhas, larguras)
    t = s.shapes[-1].table
    for j, g in enumerate(grupos, start=1):
        if g in COR:
            t.cell(0, j).fill.fore_color.rgb = COR[g]
    return t

# ---------- slides ----------
from pptx.enum.shapes import MSO_CONNECTOR
from pptx.oxml.ns import qn
from lxml import etree

DESTAQUE = RGBColor(0xE3, 0xF5, 0xF2)


def seta(s, x1, y1, x2, y2, ponta=True):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = CINZA
    c.line.width = Pt(1.5)
    if ponta:
        ln = c.line._get_or_add_ln()
        ln.append(etree.SubElement(ln, qn("a:tailEnd"), type="triangle"))


def caixa(s, x, y, w, h, t, cor, tam=10):
    b = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, cor)
    b.adjustments[0] = 0.08
    tf = b.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for k, linha in enumerate(t.split("\n")):
        par = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        par.alignment = PP_ALIGN.CENTER
        r_ = par.add_run()
        r_.text = linha
        r_.font.size, r_.font.name, r_.font.bold, r_.font.color.rgb = Pt(tam), SANS, k == 0, BRANCO


def destacar(t, melhor):
    """melhor[i] = 'max' | 'min' | None para a linha i+1 da tabela; pinta a(s) melhor(es) célula(s)."""
    for i, regra in enumerate(melhor, start=1):
        if not regra:
            continue
        vals = {}
        for j in range(1, len(t.columns)):
            m = re.search(r"[\d.,]+", t.cell(i, j).text.replace(".", "").replace(",", "."))
            if m and t.cell(0, j).text in NOME.values():
                vals[j] = float(m.group(0))
        if not vals:
            continue
        alvo = (max if regra == "max" else min)(vals.values())
        for j, v in vals.items():
            if v == alvo:
                c = t.cell(i, j)
                c.fill.fore_color.rgb = DESTAQUE
                for par in c.text_frame.paragraphs:
                    for r_ in par.runs:
                        r_.font.bold = True


def fonte_tabela(t, tam):
    for row in t.rows:
        for c in row.cells:
            for par in c.text_frame.paragraphs:
                for r_ in par.runs:
                    r_.font.size = Pt(tam)


capa("Impacto de Agent Skills na Resolução de\nIssues por IA", "Resultados parciais")

# 1 · o que mudou
s = pagina("O que mudou desde a proposta, e por quê")
tabela(s, 0.4, 1.15, 9.2, [
    ["", "Proposta", "Agora", "Por quê"],
    ["Agente resolvedor", "Google Antigravity\ncom Gemini", "Sonnet 5.5", "Cota gratuita do Gemini não\ncobre ~860 execuções; há\nassinatura do Claude"],
    ["Agente da reescrita", "LLM de alto desempenho\naplica a skill inteira", "Opus 5.5 aplica só a 1ª etapa\nda skill: escrever a\nespecificação da issue",
     "A skill tem 4 etapas e para em\ncada uma esperando aprovação\nhumana; aqui não há humano"],
    ["Grupos de análise", "A · skill\nB · original", "A · skill\nB · original\nC · critérios da literatura", "A skill não segue critérios de\nqualidade de bug (Bettenburg)\nnem de feature (Heck)"],
], [1.7, 2.0, 2.6, 2.9])
fonte_tabela(s.shapes[-1].table, 11)
texto(s, 0.4, 4.75, 9.2, 0.4, f"Oráculo mantido (testes do SWE-bench). {excluidas} issues saíram porque nem o fix oficial "
      "passa neste ambiente (testes de rede do requests).", 10, CINZA, italico=True)

# 2 · fluxo
s = pagina("Metodologia")
painel = forma(s, MSO_SHAPE.RECTANGLE, 0.3, 1.0, 9.4, 2.9, CARD)
caixa(s, 0.45, 2.05, 1.2, 0.8, "SWE-bench Lite\n300 issues", NAVY)
seta(s, 1.65, 2.45, 1.9, 2.45)
caixa(s, 1.9, 2.05, 1.35, 0.8, "Classificação\nbug ou feature", NAVY, 9)
seta(s, 3.25, 2.45, 3.45, 2.45, ponta=False)
seta(s, 3.45, 1.5, 3.45, 3.4, ponta=False)
linhas_fluxo = [(1.15, ROXO, "Grupo A\nskill"), (2.05, AZUL, "Grupo B\noriginal"), (2.95, TEAL, "Grupo C\nliteratura")]
for y, cor, rot in linhas_fluxo:
    seta(s, 3.45, y + 0.35, 3.65, y + 0.35)
    caixa(s, 3.65, y, 1.6, 0.7, rot, cor, 9)
    seta(s, 5.25, y + 0.35, 5.5, y + 0.35)
    caixa(s, 5.5, y, 1.6, 0.7, "Agente resolve\n(Sonnet 5.5)", AZUL, 9)
    seta(s, 7.1, y + 0.35, 7.3, y + 0.35)
    caixa(s, 7.3, y, 1.05, 0.7, "Testes do\nSWE-bench", TEAL, 9)
    seta(s, 8.35, y + 0.35, 8.55, y + 0.35, ponta=False)
seta(s, 8.55, 1.5, 8.55, 3.3, ponta=False)
seta(s, 8.55, 2.4, 8.65, 2.4)
caixa(s, 8.65, 1.95, 0.95, 0.9, "Resultados", TEAL, 10)
for k, (rot, sub, cor) in enumerate([("Amostrar", "300 issues", CINZA), ("Classificar", "bug ou feature", NAVY),
                                     ("Gerar", "3 versões da issue", ROXO), ("Resolver", "agente sem humano", AZUL),
                                     ("Medir", "RQ1, RQ2, RQ3", TEAL)]):
    x = 0.4 + k * 1.9
    b = forma(s, MSO_SHAPE.OVAL, x, 4.1, 0.3, 0.3, cor)
    b.text_frame.text = str(k + 1)
    b.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    b.text_frame.paragraphs[0].runs[0].font.size, b.text_frame.paragraphs[0].runs[0].font.color.rgb = Pt(10), BRANCO
    texto(s, x + 0.35, 4.05, 1.5, 0.3, rot, 12, NAVY, negrito=True)
    texto(s, x, 4.45, 1.85, 0.6, sub, 10, CINZA)

# 3 · classificação
s = pagina("Classificação das issues", f"O SWE-bench Lite não traz o tipo da issue · 300 issues, {excluidas} desconsideradas, {len(ab)} classificadas")
numero(s, 0.6, 1.15, 2.8, fmt(len(por_tipo["bug"])), "bug", TEAL)
numero(s, 3.6, 1.15, 2.8, fmt(len(por_tipo["feature"])), "feature", ROXO)
numero(s, 6.6, 1.15, 2.8, fmt(len(por_tipo["neither"]) + len(por_tipo["discard"])), "nenhum dos dois", CINZA)
cartao(s, 0.4, 2.65, 2.9, 2.35, "Por que só bug e feature", ROXO,
       "São os tipos com critérios\nde qualidade de issue que\nuso no mestrado:\nbug → Bettenburg et al. (2008)\nfeature → Heck & Zaidman (2017)", 10)
cartao(s, 3.5, 2.65, 2.7, 2.35, f"{excluidas} desconsideradas", VERMELHO,
       "Nem o fix oficial passa nos\ntestes neste ambiente: os\ntestes do requests dependem\nde rede. Sem oráculo\nconfiável, saem da análise.", 10)
cartao(s, 6.4, 2.65, 3.2, 2.35, "Como classificamos", AZUL,
       "Skill criada no mestrado a partir\nde Herzig, Just & Zeller (ICSE\n2013, Tabela III); prompt no molde\nde Colavito et al. (MSR 2024).\n"
       "Opus 5.5, zero-shot. Contra 96\nissues anotadas: κ 0,714 · bug\nP 1,00 R 0,64 · feature P 0,81 R 0,87", 10)

# 4 · como cada grupo é
s = pagina("Como cada grupo é", "Reescrita: Opus 5.5, vê só o texto da issue, nunca o repositório nem o fix")
cartao(s, 0.4, 1.3, 2.95, 3.3, NOME[A], ROXO,
       "Reescrita com a skill\nSpec-Driven Development\n(Osmani), só a fase\nSpecify.\n\nTodas as 296 issues.", 12)
cartao(s, 3.525, 1.3, 2.95, 3.3, NOME[B], AZUL, "Baseline: texto original\ndo SWE-bench, sem\nreescrita.\n\nTodas as 296 issues.", 12)
cartao(s, 6.65, 1.3, 2.95, 3.3, NOME[C], TEAL,
       "Reescrita com os itens de\nqualidade da literatura,\nno lugar do molde do\nOsmani:\nbug → Bettenburg (2008)\nfeature → Heck (2017)\n\nSó as 269 bug/feature.", 12)

# 5 · a mesma issue nos três grupos
EX = "pallets__flask-4045"
s = pagina("A mesma issue em cada grupo", "pallets/flask-4045 · bug")
txt_a = (RUNS / "specs" / f"{EX}.md").read_text()
txt_c = (RUNS / "specs_literatura" / f"{EX}.md").read_text()
sec_a = re.findall(r"^## +(.+)$", txt_a, re.M)
sec_c = secoes(EX)
cartao(s, 0.4, 1.2, 2.95, 3.85, f"A · {len(txt_a):,} caracteres".replace(",", "."), ROXO, "\n".join(sec_a), 10)
cartao(s, 3.525, 1.2, 2.95, 3.85, f"B · {len(dados[EX]['problem_statement'])} caracteres", AZUL,
       dados[EX]["problem_statement"].strip(), 10)
cartao(s, 6.65, 1.2, 2.95, 3.85, f"C · {len(txt_c):,} caracteres".replace(",", "."), TEAL,
       "\n".join(("✓ " if "not provided in the original" not in v.lower() else "✗ ") + k for k, v in sec_c.items())
       + "\n\n✗ = \"Not provided in the\noriginal report\"", 10)

# 6 · RQ1
s = pagina("RQ1 · Eficácia", "Issue resolvida = o patch do agente passa nos testes do SWE-bench · mesmas issues nos três grupos")
linhas_rq1, regra = [], []
for t_, rot in (("bug", "Bug"), ("feature", "Feature")):
    ids = [i for i in abc if tipo.get(i) == t_]
    linhas_rq1.append([f"{rot} ({len(ids)})"] + [f"{resolvidas(g, ids)} ({100 * resolvidas(g, ids) / len(ids):.0f}%)" for g in (A, B, C)])
    regra.append("max")
linhas_rq1.append([f"Bug + feature ({len(abc)})"] + [f"{resolvidas(g, abc)} ({100 * resolvidas(g, abc) / len(abc):.0f}%)" for g in (A, B, C)])
regra.append("max")
nei = por_tipo["neither"] + por_tipo["discard"]
linhas_rq1.append([f"Nenhum dos dois ({len(nei)})"] + [f"{resolvidas(g, nei)} ({100 * resolvidas(g, nei) / len(nei):.0f}%)" for g in (A, B)] + ["—"])
regra.append("max")
t = tabela_grupos(s, 0.4, 1.3, 9.2, "Tipo (issues)", linhas_rq1, (A, B, C), [2.6, 2.2, 2.2, 2.2])
destacar(t, regra)
texto(s, 0.4, 3.6, 9.2, 0.4, "Destaque = melhor resultado da linha.", 10, CINZA, italico=True)

# 7 · RQ2
s = pagina("RQ2 · Eficiência e custo", f"Mediana por execução · issues bug + feature ({len(abc)}) · menor é melhor")
t = tabela_grupos(s, 0.4, 1.3, 9.2, "", [
    ["Tokens de entrada (com cache)"] + [fmt(med(num(g, "tokens_entrada", abc))) for g in (A, B, C)],
    ["Tokens de saída"] + [fmt(med(num(g, "tokens_saida", abc))) for g in (A, B, C)],
    ["Tempo (s)"] + [fmt(med(num(g, "duracao_s", abc))) for g in (A, B, C)],
    ["Custo estimado (US$)"] + [f"{med([custo_oficial(g, i) for i in abc]):.3f}".replace(".", ",") for g in (A, B, C)],
], (A, B, C), [2.9, 2.1, 2.1, 2.1])
destacar(t, ["min"] * 4)
texto(s, 0.4, 3.45, 9.2, 0.3, "Como o custo estimado é calculado", 12, NAVY, negrito=True)
tabela(s, 0.4, 3.8, 9.2, [["Tipo de token", "Entrada", "Saída", "Escrita no cache", "Leitura do cache"],
                          ["US$ por milhão (Sonnet 5.5)", "2,00", "10,00", "4,00", "0,20"]], [2.9, 1.5, 1.5, 1.65, 1.65])
fonte_tabela(s.shapes[-1].table, 11)
texto(s, 0.4, 4.6, 9.2, 0.5, "Custo = soma de cada tipo de token × preço oficial da API da Anthropic (out/2026); escrita no cache "
      "com validade de 1 h. Só o agente que resolve: não inclui a reescrita do Opus (A e C). Na assinatura, o gasto real é cota.",
      10, CINZA, italico=True)

# 8 · RQ3
arq = lambda pt: set(re.findall(r"^diff --git a/(\S+)", pt, re.M))
mesmos = {g: sum(bool(arq((RUNS / g / i / "patch.diff").read_text())) and
                 arq((RUNS / g / i / "patch.diff").read_text()) == arq(dados[i]["patch"]) for i in abc) for g in (A, B, C)}
quebrou = {g: sum(bool(json.loads((RUNS / g / i / "report.json").read_text()).get("tests_status", {})
                       .get("PASS_TO_PASS", {}).get("failure")) for i in abc) for g in (A, B, C)}
s = pagina("RQ3 · Qualidade do patch", f"Issues bug + feature ({len(abc)}) · patch oficial como referência")
t = tabela_grupos(s, 0.4, 1.3, 9.2, "", [
    ["Mexe nos mesmos arquivos do fix oficial"] + [f"{mesmos[g]} ({100 * mesmos[g] / len(abc):.0f}%)" for g in (A, B, C)] + ["—"],
    ["Quebra teste que passava antes"] + [f"{quebrou[g]} ({100 * quebrou[g] / len(abc):.0f}%)" for g in (A, B, C)] + ["—"],
    ["Linhas adicionadas (mediana)"] + [fmt(med(num(g, "linhas_mais", abc))) for g in (A, B, C)] + [fmt(med(num(B, "oficial_mais", abc)))],
    ["Linhas removidas (mediana)"] + [fmt(med(num(g, "linhas_menos", abc))) for g in (A, B, C)] + [fmt(med(num(B, "oficial_menos", abc)))],
    ["Arquivos tocados (mediana)"] + [fmt(med(num(g, "arquivos", abc))) for g in (A, B, C)] + [fmt(med(num(B, "oficial_arquivos", abc)))],
], (A, B, C, "Patch oficial"), [3.0, 1.55, 1.55, 1.55, 1.55])
destacar(t, ["max", "min", None, None, None])
texto(s, 0.4, 4.3, 9.2, 0.4, "Destaque = melhor resultado da linha. Tamanho do patch não tem \"melhor\": compara-se com o oficial.",
      10, CINZA, italico=True)

# 9 · ameaças
s = pagina("Ameaças medidas", f"Issues bug + feature ({len(abc)})")
va = vazamento("specs", abc)
vc = vazamento("specs_literatura", abc)
cartao(s, 0.4, 1.15, 2.95, 3.9, "Vazamento · reescrita", ROXO,
       f"Reescrita cita arquivo do fix\noficial que a issue não cita:\nA {va[0]} · C {vc[0]} de {len(abc)}\n\n"
       "Por quê: o Opus não vê o\nrepositório; o nome só pode\nvir da memória. O molde do\nOsmani pede \"Estrutura do\nprojeto\" e \"Comandos\".", 11)
def cita_arquivo(i):
    ps = dados[i]["problem_statement"].lower()
    return any(x.lower() in ps for f in re.findall(r"^diff --git a/(\S+)", dados[i]["patch"], re.M)
               for x in (f, Path(f).name, Path(f).stem if len(Path(f).stem) > 5 else f, f.removesuffix(".py").replace("/", ".")))
rapidas = [i for i in abc if float(R[B][i]["turnos"]) <= 5 and R[B][i]["resolvida"]]
sem_pista = [i for i in rapidas if not cita_arquivo(i)]
cartao(s, 3.525, 1.15, 2.95, 3.9, "Memória · resolvedor", AZUL,
       f"{len(rapidas)} de {len(abc)} originais resolvidas\nem até 5 passos do agente;\nem {len(sem_pista)} delas a issue nem\ncita o arquivo corrigido.\n\n"
       "Por quê: sem pista no texto\ne sem procurar, o agente\nvai direto ao lugar do fix\n(exemplo no próximo slide).", 11)
cartao(s, 6.65, 1.15, 2.95, 3.9, "Classificação", TEAL,
       "κ 0,714 medido em issues\nescritas por agentes\n(mestrado).\n\n"
       "Em issues humanas do\nSWE-bench a concordância\nnunca foi medida.", 11)

# 10 · próximos passos
# 10 · exemplo de iteração (reexecução com registro de cada passo)
EXI = "pytest-dev__pytest-5221"
passos = [json.loads(l) for l in (RUNS / "ilustracao/original" / f"{EXI}.jsonl").read_text().splitlines() if l.strip()]
seg = next(e for e in passos if e.get("type") == "result")["duration_ms"] / 1000
s = pagina("O agente vai direto ao código", f"pytest-dev/pytest-5221 · Grupo B (issue original) · reexecução registrada passo a passo · {seg:.0f} s")
cartao(s, 0.4, 1.15, 3.3, 3.9, f"Issue · {len(dados[EXI]['problem_statement'])} caracteres", AZUL,
       dados[EXI]["problem_statement"].strip() + "\n\nNão cita nenhum arquivo\nnem função.", 11)
linhas_passos = [
    ("1", "Busca a função _showfixtures_main\nem src/_pytest/python.py", "Nenhum dos dois nomes está na issue;\nnão houve busca antes"),
    ("2", "Escreve: \"Upstream format:\nname [scope] -- path\"", "Cita o formato da versão real\ndo pytest (upstream)"),
    ("3", "Edita o arquivo (+4 −2 linhas)", ""),
    ("4", "Encerra sem rodar os testes", "Passa nos testes do SWE-bench"),
]
for k, (n_, acao, obs) in enumerate(linhas_passos):
    y = 1.2 + k * 0.95
    b = forma(s, MSO_SHAPE.OVAL, 4.0, y + 0.1, 0.35, 0.35, AZUL)
    b.text_frame.text = n_
    b.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    b.text_frame.paragraphs[0].runs[0].font.size, b.text_frame.paragraphs[0].runs[0].font.color.rgb = Pt(11), BRANCO
    texto(s, 4.5, y, 2.7, 0.8, acao, 11, NAVY, negrito=True)
    texto(s, 7.2, y, 2.5, 0.8, obs, 10, TEAL if k == 3 else CINZA, italico=True)

s = pagina("Para os resultados finais")
cartao(s, 0.4, 1.15, 4.5, 3.9, "Trocar o corpus", ROXO,
       "SWE-bench (2023) está no treino dos modelos:\na reescrita vaza o fix e o agente parece lembrar.\n\n"
       "SWE-rebench e SWE-bench-Live usam issues\ncriadas depois do corte de treino.", 12)
cartao(s, 5.1, 1.15, 4.5, 3.9, "Repetições", AZUL,
       "O agente não é determinístico: a mesma issue\npode passar numa tentativa e falhar noutra.\n\n"
       "3 a 5 tentativas por issue medem essa\nvariação (o SWE-rebench usa 5).", 12)

for i, sl in enumerate(prs.slides):
    if i:
        texto(sl, 8.6, 5.15, 1.0, 0.3, f"{i} / {len(prs.slides) - 1}", 10, CINZA, alinha=PP_ALIGN.RIGHT)

SAIDA.mkdir(parents=True, exist_ok=True)
pptx = SAIDA / "Resultados_Parciais.pptx"
prs.save(pptx)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(SAIDA), str(pptx)], capture_output=True)
print(pptx, "| A×B:", len(ab), "| A×B×C:", len(abc))
