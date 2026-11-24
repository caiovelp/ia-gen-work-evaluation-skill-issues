"""Apresentação 3 (resultados finais), 7 minutos (ADR 0007): tema das anteriores, fonte mínima 18,
referências em itálico pequeno no rodapé, parciais em 1 slide, só nomes de modelo.

Uso: python sapos_experimento.py medir && python slides_finais.py  ->  docs/apresentacao3/Resultados_Finais.{pptx,pdf}
"""
import json
import re
import statistics
import subprocess
from math import comb
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "docs/apresentacao3"
# Tema "Minimalist Paper Design" (modelo enviado pelo Caio em 2026-11-23): papel bege, texto marrom, serifa clássica
NAVY = RGBColor(0x65, 0x3E, 0x25)                      # marrom do texto e dos ícones (nome antigo mantido)
PAPEL_CAPA, PAPEL_1, PAPEL_2 = RGBColor(0xC7, 0xB5, 0xA5), RGBColor(0xDF, 0xCE, 0xBD), RGBColor(0xDA, 0xD3, 0xC8)
ROXO, AZUL, TEAL = RGBColor(0x6B, 0x44, 0x30), RGBColor(0x94, 0x76, 0x5F), RGBColor(0x66, 0x71, 0x50)  # grupos A, B, C
CARD, CINZA, BRANCO, DESTAQUE = RGBColor(0xEB, 0xE1, 0xD5), RGBColor(0x8C, 0x6E, 0x5A), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xF6, 0xEE, 0xE4)
SERIF, SANS = "Prata", "Montserrat"
MIN = 18  # fonte mínima (regra do Caio)
A, B, C = "skill", "original", "literatura"
COR = {A: ROXO, B: AZUL, C: TEAL}
NOME = {A: "A · Skill", B: "B · Original", C: "C · Literatura"}
PRECO = {"entrada": 2.00, "saida": 10.00, "escrita_1h": 4.00, "escrita_5m": 2.50, "leitura": 0.20}  # Sonnet 5.5, US$/milhão

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(10), Inches(5.625)
VAZIO = prs.slide_layouts[6]


def texto(s, x, y, w, h, t, tam=MIN, cor=NAVY, fonte=SANS, negrito=False, italico=False, alinha=PP_ALIGN.LEFT):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    for i, linha in enumerate(t.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinha
        r = p.add_run()
        r.text = linha
        r.font.size, r.font.name, r.font.bold, r.font.italic, r.font.color.rgb = Pt(tam), fonte, negrito, italico, cor


def forma(s, tipo, x, y, w, h, cor):
    f = s.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h))
    f.fill.solid()
    f.fill.fore_color.rgb = cor
    f.line.fill.background()
    f.shadow.inherit = False
    return f


def caixa(s, x, y, w, h, t, cor, tam=MIN):
    b = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, cor)
    b.adjustments[0] = 0.04
    tf = b.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for k, linha in enumerate(t.split("\n")):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = linha
        r.font.size, r.font.name, r.font.bold, r.font.color.rgb = Pt(tam), SANS, k == 0, BRANCO


def filete(s, x1, y1, x2, y2, cor=None):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = cor or CINZA
    c.line.width = Pt(0.75)


def largura_pol(t, pt, fonte=Path.home() / ".local/share/fonts/tema-papel/Prata-Regular.ttf"):
    from PIL import ImageFont
    return ImageFont.truetype(str(fonte), pt * 10).getlength(t) / 10 / 72  # pontos para polegadas


def pagina(titulo, rodape=None):
    s = prs.slides.add_slide(VAZIO)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = PAPEL_1 if len(prs.slides) % 2 else PAPEL_2
    texto(s, 0.5, 0.25, 9, 0.7, titulo, 28, NAVY, SERIF)
    fim = 0.5 + largura_pol(titulo, 28) + 0.2  # filete fino depois do título, como no modelo
    if fim < 8.0:  # título longo demais: sem filete
        filete(s, fim, 0.6, min(fim + 1.6, 9.5), 0.6)
    if rodape:  # referências: itálico pequeno no rodapé (exceção à fonte mínima)
        texto(s, 0.5, 5.2, 8.2, 0.3, rodape, 9, CINZA, italico=True)
    return s


def seta(s, x1, y1, x2, y2):
    from pptx.enum.shapes import MSO_CONNECTOR
    from pptx.oxml.ns import qn
    from lxml import etree
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = CINZA
    c.line.width = Pt(1.5)
    ln = c.line._get_or_add_ln()
    ln.append(etree.SubElement(ln, qn("a:tailEnd"), type="triangle"))


def numero(s, x, y, w, valor, legenda, cor=NAVY):
    texto(s, x, y, w, 0.8, valor, 40, cor, SERIF, alinha=PP_ALIGN.CENTER)
    texto(s, x, y + 0.85, w, 0.8, legenda, MIN, CINZA, alinha=PP_ALIGN.CENTER)


def tabela(s, x, y, w, linhas, larguras, melhor=()):
    """linhas[0] = cabeçalho com NOME[g]; melhor[i] = 'max'|'min'|None para a linha i+1."""
    t = s.shapes.add_table(len(linhas), len(linhas[0]), Inches(x), Inches(y), Inches(w), Inches(0.5 * len(linhas))).table
    for j, lg in enumerate(larguras):
        t.columns[j].width = Inches(lg)
    for i, linha in enumerate(linhas):
        for j, v in enumerate(linha):
            c = t.cell(i, j)
            c.fill.solid()
            cab = next((g for g, n in NOME.items() if n == linhas[0][j]), None)
            c.fill.fore_color.rgb = (COR[cab] if cab else NAVY) if i == 0 else (CARD if i % 2 else BRANCO)
            c.text = str(v) or " "
            for p in c.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
                for r in p.runs:
                    r.font.size, r.font.name, r.font.bold = Pt(MIN), SANS, i == 0
                    r.font.color.rgb = BRANCO if i == 0 else NAVY
    for i, regra in enumerate(melhor, start=1):
        if not regra:
            continue
        vals = {j: float(m.group(0)) for j in range(1, len(linhas[0]))
                if (m := re.search(r"[\d,.]+", t.cell(i, j).text.replace(".", "").replace(",", ".")))}
        if vals:
            alvo = (max if regra == "max" else min)(vals.values())
            for j, v in vals.items():
                if v == alvo:
                    t.cell(i, j).fill.fore_color.rgb = DESTAQUE
                    for p in t.cell(i, j).text_frame.paragraphs:
                        for r in p.runs:
                            r.font.bold = True


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


def mcnemar(r1, r2, ids):
    a = sum(r1[i] and not r2[i] for i in ids)
    b = sum(r2[i] and not r1[i] for i in ids)
    return a, b, min(1.0, 2 * sum(comb(a + b, j) for j in range(min(a, b) + 1)) / 2 ** (a + b)) if a + b else 1.0


# ---------- dados do SAPOS ----------
S = RAIZ / "runs/sapos"
tarefas = [t for t in map(json.loads, (S / "tarefas.jsonl").read_text().splitlines()) if t["status"] == "ok"]
todas = list(map(json.loads, (S / "tarefas.jsonl").read_text().splitlines()))
tipo = {r["instance_id"]: r["label"] for r in map(json.loads, (S / "tipos.jsonl").read_text().splitlines())}
abc = [t for t in tarefas if all((S / g / t["instance_id"] / "report.json").exists() for g in (A, B, C))]
ab = [t for t in tarefas if all((S / g / t["instance_id"] / "report.json").exists() for g in (A, B))]
res = {g: {t["instance_id"]: bool(json.loads((S / g / t["instance_id"] / "report.json").read_text()).get("resolved"))
           for t in (abc if g == C else ab)} for g in (A, B, C)}
saidas = {g: {t["instance_id"]: json.loads((S / g / t["instance_id"] / "saida.json").read_text() or "{}") for t in abc} for g in (A, B, C)}
ids_abc = [t["instance_id"] for t in abc]
ids_ab = [t["instance_id"] for t in ab]


def med(g, f):
    return statistics.median(f(g, i) for i in ids_abc)


tok = lambda g, i: sum(saidas[g][i]["usage"].get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
seg = lambda g, i: json.loads((S / g / i / "meta.json").read_text())["duracao_s"]
oficial = {t["instance_id"]: t["patch"] for t in tarefas}
mesmos = {g: sum(bool(arquivos((S / g / i / "patch.diff").read_text())) and arquivos((S / g / i / "patch.diff").read_text()) == arquivos(oficial[i]) for i in ids_abc) for g in (A, B, C)}
quebrou = {g: sum(bool(json.loads((S / g / i / "report.json").read_text()).get("p2p_falhou")) for i in ids_abc) for g in (A, B, C)}
n2026 = sum(t["criada"] >= "2026" for t in tarefas)
amplas = [t for t in map(json.loads, (S / "tarefas_amplas.jsonl").read_text().splitlines())]
def juiz(g, i):
    f = S / g / i / "juiz_v2.json"
    return json.loads(f.read_text()).get("veredito") == "resolve" if f.exists() else None
amp_abc = [t["instance_id"] for t in amplas if all(juiz(g, t["instance_id"]) is not None for g in (A, B, C))]
vazios = {g: sum(bool(json.loads((S / g / i / "report.json").read_text()).get("patch_vazio")) for i in ids_abc) for g in (A, B, C)}

# ---------- slides ----------
s = prs.slides.add_slide(VAZIO)
s.background.fill.solid()
s.background.fill.fore_color.rgb = PAPEL_CAPA
moldura = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(0.75), Inches(8.2), Inches(4.1))
moldura.fill.background()
moldura.line.color.rgb = CINZA
moldura.line.width = Pt(0.75)
texto(s, 0.9, 0.3, 8.2, 0.4, "IA para Engenharia de Software", MIN, NAVY, alinha=PP_ALIGN.CENTER)
texto(s, 1.2, 1.3, 7.6, 1.6, "Impacto de Agent Skills na Resolução\nde Issues por IA", 28, NAVY, SERIF, alinha=PP_ALIGN.CENTER)
texto(s, 1.2, 2.95, 7.6, 0.5, "Resultados finais", 20, CINZA, alinha=PP_ALIGN.CENTER)
filete(s, 3.6, 3.65, 6.4, 3.65)
texto(s, 1.2, 3.8, 7.6, 0.4, "Caio Paranhos · Profa. Vania Neves", MIN, NAVY, alinha=PP_ALIGN.CENTER)
texto(s, 0.9, 4.95, 8.2, 0.4, "25 de novembro de 2026", MIN, NAVY, alinha=PP_ALIGN.CENTER)

s = pagina("Pergunta e método", "Osmani (2024) · Bettenburg et al. (FSE 2008) · Heck & Zaidman (RE 2017) · Herzig et al. (ICSE 2013)")
texto(s, 0.5, 0.95, 9, 0.5, "Reescrever a issue ajuda o agente a resolvê-la?", 22, NAVY, negrito=True)
caixa(s, 0.4, 2.675, 1.6, 1.0, "Issue\noriginal", NAVY)
for k, (cor, rot) in enumerate([(ROXO, "A · Skill\nOsmani"), (AZUL, "B · Original"), (TEAL, "C · Literatura\nBettenburg · Heck")]):
    caixa(s, 2.5, 1.55 + k * 1.15, 2.6, 0.95, rot, cor)
caixa(s, 5.6, 2.675, 2.0, 1.0, "Sonnet 5.5\nresolve", AZUL)
caixa(s, 8.0, 2.675, 1.6, 1.0, "Testes\ndo projeto", TEAL)
texto(s, 5.6, 3.9, 4.0, 1.0, "Reescrita: Opus 5.5,\nsó com o texto da issue", MIN, CINZA)
centros = [1.55 + k * 1.15 + 0.475 for k in range(3)]  # centro vertical das caixas A, B, C
for yc in centros:
    seta(s, 2.0, 3.175, 2.5, yc)
    seta(s, 5.1, yc, 5.6, 3.175)
for x1, y1, x2, y2 in [(7.6, 3.175, 8.0, 3.175)]:
    seta(s, x1, y1, x2, y2)

s = pagina("Resultados parciais: SWE-bench Lite", "Jimenez et al. (ICLR 2024)")
numero(s, 0.4, 1.0, 3.0, "71%", "A · Skill", ROXO)
numero(s, 3.5, 1.0, 3.0, "70%", "B · Original", AZUL)
numero(s, 6.6, 1.0, 3.0, "70%", "C · Literatura", TEAL)
texto(s, 0.5, 2.9, 9, 0.5, "Sem diferença entre grupos (269 issues)", 22, NAVY, negrito=True)
texto(s, 0.5, 3.5, 9, 1.4, "Contaminação: reescrita A cita o arquivo do fix em 46 issues\n"
      "74 resolvidas em até 5 passos sem a issue citar o arquivo", MIN, CINZA)

s = pagina("Novo corpus: SAPOS (UFF)", "github.com/gems-uff/sapos")
funil = [("432", "issues fechadas"), ("340", "correção\nem código"), (str(len(amplas)), "rodam no\nambiente atual"),
         (str(len(tarefas)), "teste falha antes,\npassa depois")]
for k, (v, leg) in enumerate(funil):
    numero(s, 0.3 + k * 2.4, 1.2, 2.2, v, leg, TEAL if k == 3 else NAVY)
texto(s, 0.5, 3.6, 9, 1.2, f"Estrito: {len(tarefas)} com testes · Amplo: {len(amplas)} julgadas por LLM\nRuby on Rails · issues em português", MIN, CINZA)

s = pagina("RQ1 · Eficácia")
lin = [["Issues resolvidas", NOME[A], NOME[B], NOME[C]],
       ["SWE-bench Lite (269)", "71%", "70%", "70%"],
       [f"SAPOS estrito, testes ({len(ids_abc)})"] + [f"{sum(res[g][i] for i in ids_abc)} ({100 * sum(res[g][i] for i in ids_abc) / len(ids_abc):.0f}%)" for g in (A, B, C)],
       [f"SAPOS amplo, juiz ({len(amp_abc)})"] + [f"{sum(juiz(g, i) for i in amp_abc)} ({100 * sum(juiz(g, i) for i in amp_abc) / len(amp_abc):.0f}%)" for g in (A, B, C)]]
tabela(s, 0.3, 1.2, 9.4, lin, [3.7, 1.9, 1.9, 1.9], melhor=["max", "max", "max"])
mab = mcnemar(res[A], res[B], ids_ab)
texto(s, 0.5, 3.6, 9, 1.0, "Juiz LLM calibrado nos testes do nível estrito: κ 0,76", MIN, CINZA)

s = pagina("RQ2 e RQ3 · Custo e qualidade (SAPOS)")
lin = [["Mediana por execução", NOME[A], NOME[B], NOME[C]],
       ["Tokens de entrada (mil)"] + [br(med(g, tok) / 1000) for g in (A, B, C)],
       ["Custo estimado (US$)"] + [br(med(g, lambda g_, i: custo(saidas[g_][i])), 2) for g in (A, B, C)],
       ["Tempo (s)"] + [br(med(g, seg)) for g in (A, B, C)],
       ["Arquivos iguais ao fix"] + [f"{mesmos[g]} de {len(ids_abc)}" for g in (A, B, C)],
       ["Agente não mudou nada"] + [f"{vazios[g]} de {len(ids_abc)}" for g in (A, B, C)]]
tabela(s, 0.3, 1.1, 9.4, lin, [3.7, 1.9, 1.9, 1.9], melhor=["min", "min", "min", "max", "min"])

s = pagina("Ameaças à validade")
for k, (rot, cor, corpo) in enumerate([
        ("Coautoria", ROXO, "Correções de\n2026 feitas\ncom Claude"),
        ("Variação", AZUL, "1 execução\npor issue"),
        ("Amostra e juiz", TEAL, f"{len(tarefas)} com testes\n{len(amplas)} com juiz LLM\n(κ 0,76)")]):
    forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.4 + k * 3.12, 1.2, 2.95, 3.6, CARD).adjustments[0] = 0.05
    caixa(s, 0.6 + k * 3.12, 1.4, 2.55, 0.6, rot, cor)
    texto(s, 0.6 + k * 3.12, 2.3, 2.6, 2.4, corpo, MIN, NAVY)

s = pagina("Conclusão")
texto(s, 0.6, 1.2, 8.8, 3.6,
      "Reescrever a issue não mudou a taxa de resolução\n(SWE-bench e SAPOS)\n\n"
      f"Em issues novas a taxa cai de ~70% para ~{100 * sum(res[B][i] for i in ids_abc) / len(ids_abc):.0f}%\n\n"
      "A skill genérica custou mais nos dois corpora", 22, NAVY)

for i, sl in enumerate(prs.slides):
    if i:
        texto(sl, 8.8, 5.15, 0.9, 0.35, f"{i + 1}", MIN, CINZA, alinha=PP_ALIGN.RIGHT)

SAIDA.mkdir(parents=True, exist_ok=True)
pptx = SAIDA / "Resultados_Finais.pptx"
prs.save(pptx)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(SAIDA), str(pptx)], capture_output=True)
print(pptx, "| tarefas:", len(tarefas), "| A×B×C:", len(abc))
