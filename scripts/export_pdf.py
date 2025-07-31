from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from collections import Counter

def save_investment_report(ticker, start_date, end_date, pos, neg, action, amount, num_articles, output_dir, sources=None):
    filename = f"{ticker}_{end_date.date()}_report.pdf"
    filepath = os.path.join(output_dir, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Sentiment Investment Report for {ticker}")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Date Range: {start_date.date()} to {end_date.date()}")
    c.drawString(50, height - 110, f"Articles Analyzed: {num_articles}")
    c.drawString(50, height - 130, f"Positive Words: {pos}")
    c.drawString(50, height - 150, f"Negative Words: {neg}")
    c.drawString(50, height - 170, f"Net Sentiment: {pos - neg}")

    ratio = f"{pos / neg:.2f}" if neg > 0 else "∞"
    c.drawString(50, height - 190, f"Pos:Neg Ratio: {ratio}")

    c.drawString(50, height - 210, f"Decision: {action}")
    if action != "HOLD":
        c.drawString(50, height - 230, f"Investment Allocated: ${amount:.2f}")
    else:
        c.drawString(50, height - 230, f"No investment made.")

    if sources:
        c.drawString(50, height - 260, "Top 5 News Sources:")
        top_sources = Counter(sources).most_common(5)
        for i, (src, count) in enumerate(top_sources):
            c.drawString(70, height - 280 - i * 15, f"- {src} ({count} articles)")

    c.save()
    print(f"[SAVED] PDF report saved to: {filepath}")
