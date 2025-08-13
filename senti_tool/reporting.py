from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

def _chart_sentiment_bars(per_ticker_rows, out_png):
    df = pd.DataFrame(per_ticker_rows)
    plt.figure(figsize=(6,4))
    plt.bar(df['ticker'], df['pos'], label='Positive')
    plt.bar(df['ticker'], df['neg'], bottom=0, label='Negative')
    plt.legend()
    plt.title('Positive / Negative counts')
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()

def generate_pdf(pdf_path, run_ctx: dict, per_ticker_rows: list, top_sources: list):
    os.makedirs(os.path.dirname(pdf_path) or ".", exist_ok=True)
    chart_png = os.path.join(os.path.dirname(pdf_path) or ".", "sentiment_chart.png")
    _chart_sentiment_bars(per_ticker_rows, chart_png)

    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("<b>Sentiment Trader Report</b>", styles['Title']))
    story.append(Paragraph(
        f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Window: {run_ctx.get('from_date')} → {run_ctx.get('to_date')} | "
        f"Cash: ${run_ctx.get('cash'):,.2f} | Threshold: {run_ctx.get('threshold')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))

    tbl_data = [["Ticker","Pos","Neg","Ratio","Direction","Invest ($)"]]
    for r in per_ticker_rows:
        tbl_data.append([r['ticker'], r['pos'], r['neg'], f"{r['ratio']:.2f}", r['direction'], f"{r['invest']:,.2f}"])
    tbl = Table(tbl_data, hAlign='LEFT')
    tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.lightgrey),
                             ('GRID',(0,0),(-1,-1), 0.5, colors.grey),
                             ('FONT',(0,0),(-1,0),'Helvetica-Bold'),
                             ('ALIGN',(1,1),(-1,-1),'CENTER')]))
    story.append(tbl); story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Top 5 Sources</b>", styles['Heading3']))
    if top_sources:
        src_tbl = Table([["Source","Count"]] + [[s,c] for s,c in top_sources[:5]], hAlign='LEFT')
        src_tbl.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey),
                                     ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
        story.append(src_tbl)
    else:
        story.append(Paragraph("No sources collected.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>Sentiment Counts</b>", styles['Heading3']))
    if os.path.exists(chart_png):
        story.append(Image(chart_png, width=5.5*inch, height=3.4*inch))

    doc = SimpleDocTemplate(pdf_path, pagesize=LETTER, leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    doc.build(story)
