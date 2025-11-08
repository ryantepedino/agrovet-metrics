from datetime import date
import os
from sqlalchemy.orm import Session
from textwrap import wrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from app.models.fazenda import Fazenda
from app.services.kpi import compute_kpis_for_farm


def build_pdf_report(db: Session, fazenda_id: int, inicio: date, fim: date) -> str:
    """
    Gera o relatório reprodutivo em PDF com base nas métricas da fazenda.
    Inclui interpretação automática dos indicadores.
    """

    # Busca a fazenda
    farm = db.get(Fazenda, fazenda_id)
    if not farm:
        raise ValueError("Fazenda não encontrada")

    # Calcula os KPIs
    k = compute_kpis_for_farm(db, fazenda_id, inicio, fim)

    # Cria diretório de saída
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"Relatorio_Fazenda_{farm.id}_{inicio}_{fim}.pdf")

    # Inicializa o PDF
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4

    # ==========================================================
    # Cabeçalho
    # ==========================================================
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, h - 2 * cm, f"Relatório Reprodutivo - {farm.nome}")
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, h - 2.7 * cm, f"Período: {inicio} a {fim}")

    # ==========================================================
    # KPIs
    # ==========================================================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, h - 4 * cm, "KPIs")
    c.setFont("Helvetica", 11)
    kpi_lines = [
        f"TS (Inseminadas/Aptas): {k['kpis']['TS']} %",
        f"TC (Gestantes/Inseminadas): {k['kpis']['TC']} %",
        f"TP (TS x TC): {k['kpis']['TP']} %",
        f"Partos realizados: {k['totais']['partos_realizados']}",
        f"Partos previstos: {k['totais']['partos_previstos']}",
    ]
    y = h - 4.7 * cm
    for line in kpi_lines:
        c.drawString(2.2 * cm, y, line)
        y -= 0.6 * cm

    # ==========================================================
    # Tabela de totais
    # ==========================================================
    data = [
        ["Aptas", "Inseminadas", "Gestantes", "Partos Realizados", "Partos Previstos"],
        [
            str(k["totais"]["aptas"]),
            str(k["totais"]["inseminadas"]),
            str(k["totais"]["gestantes"]),
            str(k["totais"]["partos_realizados"]),
            str(k["totais"]["partos_previstos"]),
        ],
    ]
    table_x = 2 * cm
    table_y = h - 9 * cm
    col_w = [3.2 * cm, 3.2 * cm, 3.2 * cm, 3.6 * cm, 3.6 * cm]
    row_h = 1 * cm

    # Cabeçalho da tabela
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(table_x, table_y, sum(col_w), row_h, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    for i, text in enumerate(data[0]):
        c.drawString(table_x + sum(col_w[:i]) + 0.2 * cm, table_y + 0.3 * cm, text)

    # Linhas de dados
    c.setFont("Helvetica", 10)
    for i, text in enumerate(data[1]):
        c.drawString(table_x + sum(col_w[:i]) + 0.2 * cm, table_y - 0.7 * cm, text)
    c.rect(table_x, table_y - row_h, sum(col_w), 2 * row_h, fill=False)

    # ==========================================================
    # Interpretação automática
    # ==========================================================
    ts, tc, tp = k['kpis']['TS'], k['kpis']['TC'], k['kpis']['TP']
    texto = (
        f"A Fazenda {farm.nome} apresenta uma Taxa de Serviço (TS) de {ts}%, "
        f"Taxa de Concepção (TC) de {tc}% e Taxa de Prenhez (TP) de {tp}%. "
        "Esses valores indicam desempenho reprodutivo compatível com sistemas "
        "de inseminação artificial convencionais. A análise conjunta dos índices "
        "permite ao médico-veterinário avaliar a eficiência do manejo reprodutivo "
        "e planejar ações corretivas para melhorar a taxa de prenhez."
    )

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, h - 12 * cm, "Interpretação automática:")
    c.setFont("Helvetica-Oblique", 9)
    y_text = h - 12.7 * cm
    for line in wrap(texto, 95):
        c.drawString(2.2 * cm, y_text, line)
        y_text -= 0.5 * cm

    # ==========================================================
    # Rodapé
    # ==========================================================
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(2 * cm, 1.5 * cm, "Gerado automaticamente por AgroVet Metrics (MVP)")

    c.showPage()
    c.save()
    return path

    # ==========================================================
# Exportação em Excel (XLSX)
# ==========================================================
from openpyxl import Workbook

def build_xlsx_export(db: Session, fazenda_id: int, inicio: date, fim: date) -> str:
    """
    Gera o relatório reprodutivo em formato Excel (XLSX).
    Contém os mesmos dados e KPIs usados no PDF.
    """
    farm = db.get(Fazenda, fazenda_id)
    if not farm:
        raise ValueError("Fazenda não encontrada")

    k = compute_kpis_for_farm(db, fazenda_id, inicio, fim)

    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"Export_Fazenda_{farm.id}_{inicio}_{fim}.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Resumo"

    headers = [
        "Fazenda",
        "Período Início",
        "Período Fim",
        "TS (%)",
        "TC (%)",
        "TP (%)",
        "Partos Realizados",
        "Partos Previstos",
        "Aptas",
        "Inseminadas",
        "Gestantes",
    ]
    ws.append(headers)

    ws.append([
        farm.nome,
        str(inicio),
        str(fim),
        k["kpis"]["TS"],
        k["kpis"]["TC"],
        k["kpis"]["TP"],
        k["totais"]["partos_realizados"],
        k["totais"]["partos_previstos"],
        k["totais"]["aptas"],
        k["totais"]["inseminadas"],
        k["totais"]["gestantes"],
    ])

    # Ajuste de largura das colunas
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col if cell.value)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2

    wb.save(path)
    return path

