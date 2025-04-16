def render_html_section(title, chunks, translations, summary):
    rows = "\n".join(
        f"<tr><td>{o.replace('\n', '<br>')}</td><td>{t.replace('\n', '<br>')}</td></tr>"
        for o, t in zip(chunks, translations)
    )

    return f"""
    <h2>{title}</h2>
    <table style="width:100%; border-collapse:collapse; margin-bottom: 40px;">
        <tr>
            <th style="width:50%; border-bottom: 2px solid #333;">Original</th>
            <th style="width:50%; border-bottom: 2px solid #333;">Translation</th>
        </tr>
        {rows}
    </table>
    <h3>📌 요약</h3>
    <p style="background:#f0f0f0; padding:15px; border-left: 5px solid #333;">{summary.replace('\n', '<br>')}</p>
    <hr style="margin:50px 0;">
    """


def render_html_document(sections):
    body = "\n".join(
        render_html_section(title, chunks, translations, summary)
        for (title, chunks, translations, summary) in sections
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Earnings Call 번역</title>
<style>
    body {{ font-family: Arial; margin: 40px; background-color: #fdfdfd; }}
    h1 {{ text-align: center; }}
    h2 {{ margin-top: 50px; color: #003366; }}
    h3 {{ color: #333; }}
    table {{ border: 1px solid #ddd; width: 100%; border-collapse: collapse; }}
    th {{ background: #f0f0f0; padding: 10px; border-bottom: 2px solid #ccc; }}
    td {{ padding: 10px; border-bottom: 1px dotted #ccc; vertical-align: top; }}
    p {{ line-height: 1.6; }}
    hr {{ margin: 50px 0; border: none; border-top: 1px solid #ccc; }}
    .back-button {{
        display: inline-block;
        background-color: #007acc;
        color: white;
        padding: 10px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }}
</style>
</head><body>
<a href="../../index.html" class="back-button">← 목록으로 돌아가기</a>
<h1>📄 Earnings Call Transcript 번역 결과</h1>
{body}
</body></html>"""