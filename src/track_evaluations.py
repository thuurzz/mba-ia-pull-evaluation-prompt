"""
Script para capturar e salvar resultados de avaliações em CSV.

Uso:
    python src/track_evaluations.py

O script:
1. Detecta a versão atual do prompt em prompts/bug_to_user_story_v2.yml
2. Executa src/evaluate.py e captura a saída
3. Extrai as métricas (F1, Clarity, Precision, Helpfulness, Correctness)
4. Salva em results/evaluations.csv com timestamp
5. Gera relatório HTML em results/index.html

Isso permite acompanhar a evolução das métricas por iteração.
"""

import os
import sys
import re
import csv
import subprocess
from datetime import datetime
from pathlib import Path

import yaml

RESULTS_DIR = Path("results")
CSV_FILE = RESULTS_DIR / "evaluations.csv"
HTML_FILE = RESULTS_DIR / "index.html"


def get_prompt_version():
    """Lê a versão atual do prompt v2 do YAML."""
    try:
        with open("prompts/bug_to_user_story_v2.yml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        v2 = data.get("bug_to_user_story_v2", {})
        return v2.get("version", "unknown")
    except Exception:
        return "unknown"


def run_evaluation():
    """Executa o evaluate.py e retorna a saída completa."""
    print("Executando avaliação...")
    try:
        result = subprocess.run(
            [sys.executable, "src/evaluate.py"],
            capture_output=True,
            text=True,
            timeout=600,
        )
        return result.stdout + result.stderr
    except Exception as e:
        print(f"Erro ao executar evaluate.py: {e}")
        return ""


def extract_scores(output: str):
    """Extrai as métricas da saída do evaluate.py."""
    scores = {}

    # F1-Score
    match = re.search(r"F1-Score:\s+([\d.]+)", output)
    if match:
        scores["f1_score"] = float(match.group(1))

    # Clarity
    match = re.search(r"Clarity:\s+([\d.]+)", output)
    if match:
        scores["clarity"] = float(match.group(1))

    # Precision
    match = re.search(r"Precision:\s+([\d.]+)", output)
    if match:
        scores["precision"] = float(match.group(1))

    # Helpfulness
    match = re.search(r"Helpfulness:\s+([\d.]+)", output)
    if match:
        scores["helpfulness"] = float(match.group(1))

    # Correctness
    match = re.search(r"Correctness:\s+([\d.]+)", output)
    if match:
        scores["correctness"] = float(match.group(1))

    # Média Geral
    match = re.search(r"MÉDIA GERAL:\s+([\d.]+)", output)
    if match:
        scores["average"] = float(match.group(1))

    # Status
    if "STATUS: APROVADO" in output:
        scores["status"] = "APROVADO"
    else:
        scores["status"] = "REPROVADO"

    return scores


def save_to_csv(version: str, scores: dict):
    """Salva os resultados no CSV."""
    RESULTS_DIR.mkdir(exist_ok=True)

    fieldnames = [
        "timestamp",
        "version",
        "f1_score",
        "clarity",
        "precision",
        "helpfulness",
        "correctness",
        "average",
        "status",
    ]

    file_exists = CSV_FILE.exists()

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": version,
            "f1_score": scores.get("f1_score", 0.0),
            "clarity": scores.get("clarity", 0.0),
            "precision": scores.get("precision", 0.0),
            "helpfulness": scores.get("helpfulness", 0.0),
            "correctness": scores.get("correctness", 0.0),
            "average": scores.get("average", 0.0),
            "status": scores.get("status", "REPROVADO"),
        }
        writer.writerow(row)

    print(f"✓ Resultados salvos em: {CSV_FILE}")


def generate_html():
    """Gera relatório HTML a partir do CSV."""
    if not CSV_FILE.exists():
        print("❌ Arquivo CSV não encontrado. Execute a avaliação primeiro.")
        return

    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Calcular variações (comparação com anterior)
    for i in range(1, len(rows)):
        prev = rows[i - 1]
        curr = rows[i]
        for metric in ["f1_score", "clarity", "precision", "helpfulness", "correctness", "average"]:
            diff = float(curr[metric]) - float(prev[metric])
            curr[f"{metric}_diff"] = diff
            if diff > 0:
                curr[f"{metric}_trend"] = "up"
            elif diff < 0:
                curr[f"{metric}_trend"] = "down"
            else:
                curr[f"{metric}_trend"] = "same"

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Avaliações - Prompt Optimization</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #58a6ff; margin-bottom: 10px; }
        .subtitle { color: #8b949e; margin-bottom: 30px; }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .card h3 { color: #8b949e; font-size: 0.9em; margin-bottom: 10px; }
        .card .value { font-size: 2em; font-weight: bold; }
        .card .value.pass { color: #3fb950; }
        .card .value.fail { color: #f85149; }
        .card .threshold { font-size: 0.8em; color: #8b949e; margin-top: 5px; }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 30px;
        }
        th, td {
            padding: 12px 15px;
            text-align: center;
            border-bottom: 1px solid #30363d;
        }
        th {
            background: #21262d;
            color: #58a6ff;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
        }
        tr:hover { background: #1c2128; }
        .version { font-weight: bold; color: #58a6ff; }
        .timestamp { color: #8b949e; font-size: 0.9em; }
        .score { font-weight: bold; }
        .score.pass { color: #3fb950; }
        .score.fail { color: #f85149; }
        .trend { font-size: 0.8em; margin-left: 5px; }
        .trend.up { color: #3fb950; }
        .trend.down { color: #f85149; }
        .trend.same { color: #8b949e; }
        .status {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .status.aprovado { background: #238636; color: white; }
        .status.reprovado { background: #da3633; color: white; }
        .chart-container {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .chart-container h2 { color: #58a6ff; margin-bottom: 15px; }
        .metric-row {
            margin-bottom: 20px;
        }
        .metric-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        .bar-bg {
            background: #21262d;
            border-radius: 4px;
            height: 24px;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .bar-fill.pass { background: #238636; }
        .bar-fill.fail { background: #da3633; }
        .footer {
            text-align: center;
            color: #8b949e;
            font-size: 0.85em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #30363d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Avaliações de Prompts</h1>
        <p class="subtitle">Acompanhamento da evolução das métricas por versão do prompt</p>
"""

    # Última execução (resumo)
    if rows:
        latest = rows[-1]
        html += f"""
        <div class="summary">
            <div class="card">
                <h3>Última Versão</h3>
                <div class="value">{latest['version']}</div>
            </div>
            <div class="card">
                <h3>F1-Score</h3>
                <div class="value {'pass' if float(latest['f1_score']) >= 0.9 else 'fail'}">{latest['f1_score']}</div>
                <div class="threshold">meta: ≥ 0.90</div>
            </div>
            <div class="card">
                <h3>Clarity</h3>
                <div class="value {'pass' if float(latest['clarity']) >= 0.9 else 'fail'}">{latest['clarity']}</div>
                <div class="threshold">meta: ≥ 0.90</div>
            </div>
            <div class="card">
                <h3>Precision</h3>
                <div class="value {'pass' if float(latest['precision']) >= 0.9 else 'fail'}">{latest['precision']}</div>
                <div class="threshold">meta: ≥ 0.90</div>
            </div>
            <div class="card">
                <h3>Helpfulness</h3>
                <div class="value {'pass' if float(latest['helpfulness']) >= 0.9 else 'fail'}">{latest['helpfulness']}</div>
                <div class="threshold">meta: ≥ 0.90</div>
            </div>
            <div class="card">
                <h3>Correctness</h3>
                <div class="value {'pass' if float(latest['correctness']) >= 0.9 else 'fail'}">{latest['correctness']}</div>
                <div class="threshold">meta: ≥ 0.90</div>
            </div>
            <div class="card">
                <h3>Média Geral</h3>
                <div class="value {'pass' if float(latest['average']) >= 0.9 else 'fail'}">{latest['average']}</div>
                <div class="threshold">meta: ≥ 0.90</div>
            </div>
        </div>
"""

        # Gráfico de barras da última execução
        html += """
        <div class="chart-container">
            <h2>📈 Métricas da Última Execução</h2>
"""
        metrics = [
            ("F1-Score", latest["f1_score"]),
            ("Clarity", latest["clarity"]),
            ("Precision", latest["precision"]),
            ("Helpfulness", latest["helpfulness"]),
            ("Correctness", latest["correctness"]),
        ]
        for label, value in metrics:
            pct = float(value) * 100
            status = "pass" if float(value) >= 0.9 else "fail"
            html += f"""
            <div class="metric-row">
                <div class="metric-label">
                    <span>{label}</span>
                    <span>{value}</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill {status}" style="width: {pct}%; min-width: 30px;">{value}</div>
                </div>
            </div>
"""
        html += "        </div>\n"

    # Tabela histórica
    html += """
        <h2>📋 Histórico de Execuções</h2>
        <table>
            <thead>
                <tr>
                    <th>Data/Hora</th>
                    <th>Versão</th>
                    <th>F1-Score</th>
                    <th>Clarity</th>
                    <th>Precision</th>
                    <th>Helpfulness</th>
                    <th>Correctness</th>
                    <th>Média</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""

    for row in reversed(rows):  # Mais recente primeiro
        trend_f1 = row.get("f1_score_trend", "")
        trend_clarity = row.get("clarity_trend", "")
        trend_precision = row.get("precision_trend", "")
        trend_helpfulness = row.get("helpfulness_trend", "")
        trend_correctness = row.get("correctness_trend", "")
        trend_avg = row.get("average_trend", "")

        def trend_icon(t):
            icons = {"up": "▲", "down": "▼", "same": "●"}
            return f'<span class="trend {t}">{icons.get(t, "")}</span>' if t else ""

        status_class = "aprovado" if row["status"] == "APROVADO" else "reprovado"

        html += f"""
                <tr>
                    <td class="timestamp">{row['timestamp']}</td>
                    <td class="version">{row['version']}</td>
                    <td class="score {'pass' if float(row['f1_score']) >= 0.9 else 'fail'}">{row['f1_score']} {trend_icon(trend_f1)}</td>
                    <td class="score {'pass' if float(row['clarity']) >= 0.9 else 'fail'}">{row['clarity']} {trend_icon(trend_clarity)}</td>
                    <td class="score {'pass' if float(row['precision']) >= 0.9 else 'fail'}">{row['precision']} {trend_icon(trend_precision)}</td>
                    <td class="score {'pass' if float(row['helpfulness']) >= 0.9 else 'fail'}">{row['helpfulness']} {trend_icon(trend_helpfulness)}</td>
                    <td class="score {'pass' if float(row['correctness']) >= 0.9 else 'fail'}">{row['correctness']} {trend_icon(trend_correctness)}</td>
                    <td class="score {'pass' if float(row['average']) >= 0.9 else 'fail'}">{row['average']} {trend_icon(trend_avg)}</td>
                    <td><span class="status {status_class}">{row['status']}</span></td>
                </tr>
"""

    html += """
            </tbody>
        </table>

        <div class="footer">
            <p>Relatório gerado automaticamente pelo sistema de tracking de avaliações</p>
            <p>Atualize rodando: <code>python src/track_evaluations.py</code></p>
        </div>
    </div>
</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Relatório HTML gerado em: {HTML_FILE}")


def main():
    print("=" * 70)
    print("TRACKING DE AVALIAÇÕES")
    print("=" * 70)

    # Detectar versão do prompt
    version = get_prompt_version()
    print(f"\nVersão do prompt detectada: {version}")

    # Executar avaliação
    output = run_evaluation()

    if not output:
        print("❌ Falha ao executar avaliação")
        return 1

    # Extrair scores
    scores = extract_scores(output)

    if not scores:
        print("❌ Não foi possível extrair métricas da saída")
        return 1

    print("\nMétricas extraídas:")
    for metric, value in scores.items():
        if metric != "status":
            print(f"  - {metric}: {value}")
    print(f"  - status: {scores.get('status', 'REPROVADO')}")

    # Salvar no CSV
    save_to_csv(version, scores)

    # Gerar HTML
    generate_html()

    print("\n" + "=" * 70)
    print("✅ TRACKING CONCLUÍDO")
    print("=" * 70)
    print(f"\n📁 Arquivos gerados:")
    print(f"   - CSV: {CSV_FILE}")
    print(f"   - HTML: {HTML_FILE}")
    print(f"\n🌐 Abra {HTML_FILE} no navegador para visualizar o relatório.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
