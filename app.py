from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import pandas as pd
from googletrans import Translator

BASE_DIR = Path(__file__).resolve().parent
STATIC = BASE_DIR / 'static'

app = Flask(__name__, static_folder=str(STATIC))
translator = Translator(service_urls=['translate.googleapis.com'])

# ---------- Carregamento dos dados ----------
CSV_MAP = {
    'oportunidades': 'oportunidades_por_setor.csv',
    'saas':          'mercado_saas_brasil.csv',
    'meddic':        'funil_vendas_meddic.csv',
    'roi_auto':      'roi_por_automacao.csv'
}
dataframes = {k: pd.read_csv(STATIC / v) for k, v in CSV_MAP.items()}

# ---------- Utilitário de tradução ----------
def tr(text: str, lang: str) -> str:
    """Retorna texto traduzido se lang == 'pt'."""
    if lang == 'pt':
        try:
            return translator.translate(text, dest='pt').text
        except Exception:
            # fallback simples em caso de quota / erro de rede
            return text
    return text

# ---------- Template base ----------
BASE_HTML = """
<!doctype html>
<html lang="{{ 'pt-BR' if lang=='pt' else 'en-GB' }}">
<head>
  <meta charset="utf-8">
  <title>DataSolutions Pro</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
<header class="header">
  <div class="container flex justify-between items-center py-8">
     <h1>DataSolutions Pro</h1>
     <nav>
       <a href="{{ url_for('home', lang='en') }}">English&nbsp;(UK)</a> |
       <a href="{{ url_for('home', lang='pt') }}">Português&nbsp;(BR)</a>
     </nav>
  </div>
</header>

<main class="container my-16">
  {{ body|safe }}
</main>

<footer class="footer text-center py-16">
  © {{ year }} DataSolutions Pro
</footer>
</body>
</html>
"""

# ---------- Rotas ----------
@app.route("/")
def root():
    return redirect(url_for('home', lang='en'))

@app.route("/<lang>", methods=['GET', 'POST'])
def home(lang: str):
    if lang not in ("en", "pt"):
        return redirect(url_for('home', lang='en'))

    # ---- Se calculo de ROI via form POST ----
    roi_out = {}
    if request.method == 'POST':
        try:
            employees      = float(request.form['employees'])
            hours_weekly   = float(request.form['hours_weekly'])
            cost_per_hour  = float(request.form['cost_per_hour'])
            investment     = float(request.form['investment'])
        except (KeyError, ValueError):
            employees = hours_weekly = cost_per_hour = investment = 0

        annual_saving = employees * hours_weekly * cost_per_hour * 52 * 0.7
        payback_years = investment / annual_saving if annual_saving else 0
        roi_pct       = ((annual_saving - investment) / investment) * 100 if investment else 0
        roi_out       = {
            'saving': annual_saving,
            'payback': payback_years,
            'roi': roi_pct
        }

    # ---- Corpo principal ----
    body_html = render_template_string("""
<h2>{{ tr('Market Opportunities by Sector', lang) }}</h2>
<table>
  <thead><tr><th>{{ tr('Sector',lang) }}</th><th>Score</th></tr></thead>
  <tbody>
    {% for r in df_op.itertuples() %}
    <tr><td>{{ r.Setor }}</td><td>{{ r.Oportunidade_Score }}</td></tr>
    {% endfor %}
  </tbody>
</table>

<h2 class="mt-16">{{ tr('ROI Simulator', lang) }}</h2>
<form method="post" class="grid-form">
  <label>{{ tr('Employees',lang) }}<br><input name="employees" required></label>
  <label>{{ tr('Manual Hours / Week per Employee',lang) }}<br><input name="hours_weekly" required></label>
  <label>{{ tr('Cost per Hour (BRL)',lang) }}<br><input name="cost_per_hour" required></label>
  <label>{{ tr('Initial Investment (BRL)',lang) }}<br><input name="investment" value="150000" required></label>
  <button type="submit" class="btn btn--primary">{{ tr('Calculate',lang) }}</button>
</form>

{% if roi %}
<div class="roi__resultado">
  <p>{{ tr('Annual Saving',lang) }}: R$ {{ '{:,.0f}'.format(roi.saving) }}</p>
  <p>{{ tr('Payback',lang) }}: {{ '{:.1f}'.format(roi.payback) }} {{ tr('years',lang) }}</p>
  <p>ROI: {{ '{:.1f}'.format(roi.roi) }} %</p>
</div>
{% endif %}
""", df_op=dataframes['oportunidades'], roi=roi_out, lang=lang, tr=tr)

    rendered = render_template_string(
        BASE_HTML,
        body=body_html,
        lang=lang,
        year=datetime.now().year
    )
    return rendered

# ---------- Rota para servir favicon (opcional) ----------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(STATIC, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ---------- Execução  ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
