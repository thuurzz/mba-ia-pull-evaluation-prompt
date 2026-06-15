"""
Script para executar avaliação, salvar histórico e reasoning em uma única passada.

Uso:
    python src/track_evaluations.py

O script:
1. Detecta a versão atual do prompt em prompts/bug_to_user_story_v2.yml
2. Usa as mesmas funções de avaliação do evaluate.py, sem alterar evaluate.py
3. Executa o prompt contra o dataset do LangSmith
4. Calcula F1, Clarity, Precision, Helpfulness e Correctness
5. Salva resultados agregados em results/evaluations.csv
6. Gera relatório HTML em results/index.html
7. Salva reasoning por exemplo em results/reasoning_analysis.json e .txt
"""

import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
import yaml

from evaluate import (
    create_evaluation_dataset,
    evaluate_prompt_on_example,
    get_llm,
    pull_prompt_from_langsmith,
)
from metrics import evaluate_clarity, evaluate_f1_score, evaluate_precision

load_dotenv()

RESULTS_DIR = Path("results")
CSV_FILE = RESULTS_DIR / "evaluations.csv"
HTML_FILE = RESULTS_DIR / "index.html"
REASONING_JSON_FILE = RESULTS_DIR / "reasoning_analysis.json"
REASONING_TXT_FILE = RESULTS_DIR / "reasoning_analysis.txt"


def get_prompt_version():
    """Lê a versão atual do prompt v2 do YAML."""
    try:
        with open("prompts/bug_to_user_story_v2.yml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        v2 = data.get("bug_to_user_story_v2", {})
        return v2.get("version", "unknown")
    except Exception:
        return "unknown"


def get_llm_info():
    """Retorna informações do LLM configurado no .env."""
    provider = os.getenv("LLM_PROVIDER", "unknown")
    model = os.getenv("LLM_MODEL", "unknown")
    eval_model = os.getenv("EVAL_MODEL", "unknown")
    return provider, model, eval_model


def format_duration(value):
    """Formata duração para exibição no HTML."""
    if value in (None, ""):
        return "Não medido"
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return "Não medido"
    return f"{seconds:.1f}s"


def run_tracked_evaluation():
    """Executa avaliação completa e retorna métricas agregadas + reasoning."""
    provider, model, eval_model = get_llm_info()
    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    if not username:
        raise RuntimeError("USERNAME_LANGSMITH_HUB não configurado no .env")

    project_name = os.getenv("LANGSMITH_PROJECT", "prompt-optimization-challenge-resolved")
    dataset_name = f"{project_name}-eval"
    prompt_name = f"{username}/bug_to_user_story_v2"
    jsonl_path = "datasets/bug_to_user_story.jsonl"

    print("\n🚀 Iniciando avaliação rastreada...")
    print(f"   ⏱️  Horário de início: {datetime.now().strftime('%H:%M:%S')}")
    print(f"   🤖 Provider: {provider}")
    print(f"   📝 Modelo: {model}")
    print(f"   🔍 Modelo de avaliação: {eval_model}")

    client = Client()

    print(f"\n📚 Preparando dataset: {dataset_name}")
    create_evaluation_dataset(client, dataset_name, jsonl_path)

    print(f"\n📥 Puxando prompt do Hub: {prompt_name}")
    prompt_template = pull_prompt_from_langsmith(prompt_name)

    examples = list(client.list_examples(dataset_name=dataset_name))
    print(f"📊 Dataset carregado: {len(examples)} exemplos")

    llm = get_llm()
    results = []
    f1_scores = []
    clarity_scores = []
    precision_scores = []

    print("\n🧪 Avaliando exemplos...")
    for i, example in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] Avaliando exemplo {i}...")
        result = evaluate_prompt_on_example(prompt_template, example, llm, idx=i, total=len(examples))

        question = result["question"]
        answer = result["answer"]
        reference = result["reference"]

        if not answer:
            print("   ⚠️  Resposta vazia, pulando métricas.")
            continue

        print("   📏 Calculando F1-Score...")
        f1 = evaluate_f1_score(question, answer, reference)
        print("   📏 Calculando Clarity...")
        clarity = evaluate_clarity(question, answer, reference)
        print("   📏 Calculando Precision...")
        precision = evaluate_precision(question, answer, reference)

        f1_scores.append(f1["score"])
        clarity_scores.append(clarity["score"])
        precision_scores.append(precision["score"])

        entry = {
            "example_index": i,
            "bug_report": question,
            "generated_answer": answer,
            "reference": reference,
            "scores": {
                "f1_score": f1["score"],
                "clarity": clarity["score"],
                "precision": precision["score"],
            },
            "reasoning": {
                "f1": f1.get("reasoning", ""),
                "clarity": clarity.get("reasoning", ""),
                "precision": precision.get("reasoning", ""),
            },
            "f1_details": {
                "precision": f1.get("precision", 0),
                "recall": f1.get("recall", 0),
            },
        }
        results.append(entry)

        print(
            f"   ✅ Resultado -> F1:{f1['score']:.2f} | "
            f"Clarity:{clarity['score']:.2f} | Precision:{precision['score']:.2f}"
        )

    avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
    avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0.0
    avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0
    avg_helpfulness = (avg_clarity + avg_precision) / 2
    avg_correctness = (avg_f1 + avg_precision) / 2

    scores = {
        "f1_score": round(avg_f1, 4),
        "clarity": round(avg_clarity, 4),
        "precision": round(avg_precision, 4),
        "helpfulness": round(avg_helpfulness, 4),
        "correctness": round(avg_correctness, 4),
    }
    scores["average"] = round(sum(scores.values()) / len(scores), 4)
    scores["status"] = "APROVADO" if all(value >= 0.9 for value in scores.values() if isinstance(value, float)) else "REPROVADO"

    return scores, results


def save_to_csv(version: str, scores: dict, llm_model: str, duration_seconds: float):
    """Salva os resultados no CSV."""
    RESULTS_DIR.mkdir(exist_ok=True)

    fieldnames = [
        "timestamp",
        "version",
        "llm_model",
        "f1_score",
        "clarity",
        "precision",
        "helpfulness",
        "correctness",
        "average",
        "status",
        "duration_seconds",
    ]

    file_exists = CSV_FILE.exists()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": version,
            "llm_model": llm_model,
            "f1_score": scores.get("f1_score", 0.0),
            "clarity": scores.get("clarity", 0.0),
            "precision": scores.get("precision", 0.0),
            "helpfulness": scores.get("helpfulness", 0.0),
            "correctness": scores.get("correctness", 0.0),
            "average": scores.get("average", 0.0),
            "status": scores.get("status", "REPROVADO"),
            "duration_seconds": round(duration_seconds, 1) if duration_seconds else "",
        })

    print(f"✓ Resultados salvos em: {CSV_FILE}")


def save_reasoning(results):
    """Salva reasoning por exemplo em JSON e TXT."""
    RESULTS_DIR.mkdir(exist_ok=True)

    with open(REASONING_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✓ Reasoning JSON salvo em: {REASONING_JSON_FILE}")

    with open(REASONING_TXT_FILE, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("ANÁLISE DE REASONING - PROMPT OPTIMIZATION\n")
        f.write("=" * 70 + "\n\n")

        for r in results:
            f.write(f"--- EXEMPLO {r['example_index']}/15 ---\n\n")
            f.write(f"BUG REPORT:\n{r['bug_report'][:500]}...\n\n")
            f.write(
                f"SCORES: F1={r['scores']['f1_score']:.2f} | "
                f"Clarity={r['scores']['clarity']:.2f} | "
                f"Precision={r['scores']['precision']:.2f}\n"
            )
            f.write(
                f"F1 DETALHES: Precision={r['f1_details']['precision']:.2f} | "
                f"Recall={r['f1_details']['recall']:.2f}\n\n"
            )
            f.write("REASONING F1-Score:\n")
            f.write(f"{r['reasoning']['f1']}\n\n")
            f.write("REASONING Clarity:\n")
            f.write(f"{r['reasoning']['clarity']}\n\n")
            f.write("REASONING Precision:\n")
            f.write(f"{r['reasoning']['precision']}\n\n")
            f.write("=" * 70 + "\n\n")

    print(f"✓ Reasoning TXT salvo em: {REASONING_TXT_FILE}")


def print_reasoning_summary(results):
    """Exibe resumo de problemas comuns."""
    low_f1 = [r for r in results if r["scores"]["f1_score"] < 0.9]
    low_clarity = [r for r in results if r["scores"]["clarity"] < 0.9]
    low_precision = [r for r in results if r["scores"]["precision"] < 0.9]

    print("\n" + "=" * 70)
    print("RESUMO DE PROBLEMAS COMUNS")
    print("=" * 70)

    print(f"\nExemplos com F1 < 0.9: {len(low_f1)}")
    for r in low_f1:
        print(f"   Exemplo {r['example_index']}: F1={r['scores']['f1_score']:.2f} (Recall={r['f1_details']['recall']:.2f})")

    print(f"\nExemplos com Clarity < 0.9: {len(low_clarity)}")
    for r in low_clarity:
        print(f"   Exemplo {r['example_index']}: Clarity={r['scores']['clarity']:.2f}")

    print(f"\nExemplos com Precision < 0.9: {len(low_precision)}")
    for r in low_precision:
        print(f"   Exemplo {r['example_index']}: Precision={r['scores']['precision']:.2f}")


def generate_html():
    """Gera relatório HTML a partir do CSV."""
    if not CSV_FILE.exists():
        print("❌ Arquivo CSV não encontrado. Execute a avaliação primeiro.")
        return

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for i in range(1, len(rows)):
        prev = rows[i - 1]
        curr = rows[i]
        for metric in ["f1_score", "clarity", "precision", "helpfulness", "correctness", "average"]:
            diff = float(curr[metric]) - float(prev[metric])
            curr[f"{metric}_diff"] = diff
            curr[f"{metric}_trend"] = "up" if diff > 0 else "down" if diff < 0 else "same"

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Avaliações - Prompt Optimization</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; line-height: 1.6; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1, h2 { color: #58a6ff; margin-bottom: 10px; }
        .subtitle { color: #8b949e; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; text-align: center; }
        .card h3 { color: #8b949e; font-size: 0.9em; margin-bottom: 10px; }
        .card .value { font-size: 2em; font-weight: bold; }
        .card .value.pass { color: #3fb950; }
        .card .value.fail { color: #f85149; }
        .card .threshold { font-size: 0.8em; color: #8b949e; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; background: #161b22; border: 1px solid #30363d; border-radius: 8px; overflow: hidden; margin-bottom: 30px; }
        th, td { padding: 12px 15px; text-align: center; border-bottom: 1px solid #30363d; }
        th { background: #21262d; color: #58a6ff; font-weight: 600; font-size: 0.85em; text-transform: uppercase; }
        tr:hover { background: #1c2128; }
        .version { font-weight: bold; color: #58a6ff; }
        .timestamp { color: #8b949e; font-size: 0.9em; }
        .llm { color: #d2a8ff; font-size: 0.85em; }
        .duration { color: #8b949e; font-size: 0.9em; }
        .score { font-weight: bold; }
        .score.pass { color: #3fb950; }
        .score.fail { color: #f85149; }
        .trend { font-size: 0.8em; margin-left: 5px; }
        .trend.up { color: #3fb950; }
        .trend.down { color: #f85149; }
        .trend.same { color: #8b949e; }
        .status { padding: 4px 12px; border-radius: 12px; font-size: 0.85em; font-weight: bold; }
        .status.aprovado { background: #238636; color: white; }
        .status.reprovado { background: #da3633; color: white; }
        .chart-container { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 30px; }
        .metric-row { margin-bottom: 20px; }
        .metric-label { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9em; }
        .bar-bg { background: #21262d; border-radius: 4px; height: 24px; overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 4px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; font-size: 0.8em; font-weight: bold; }
        .bar-fill.pass { background: #238636; }
        .bar-fill.fail { background: #da3633; }
        .footer { text-align: center; color: #8b949e; font-size: 0.85em; margin-top: 30px; padding-top: 20px; border-top: 1px solid #30363d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Avaliações de Prompts</h1>
        <p class="subtitle">Acompanhamento da evolução das métricas por versão do prompt</p>
"""

    if rows:
        latest = rows[-1]
        html += f"""
        <div class="summary">
            <div class="card"><h3>Última Versão</h3><div class="value">{latest['version']}</div></div>
            <div class="card"><h3>LLM</h3><div class="value" style="font-size: 1.1em; color: #d2a8ff;">{latest.get('llm_model', 'N/A')}</div></div>
            <div class="card"><h3>Tempo</h3><div class="value" style="font-size: 1.4em; color: #8b949e;">{format_duration(latest.get('duration_seconds'))}</div></div>
"""
        for label, key in [
            ("F1-Score", "f1_score"),
            ("Clarity", "clarity"),
            ("Precision", "precision"),
            ("Helpfulness", "helpfulness"),
            ("Correctness", "correctness"),
            ("Média Geral", "average"),
        ]:
            value = float(latest[key])
            html += f"""
            <div class="card">
                <h3>{label}</h3>
                <div class="value {'pass' if value >= 0.9 else 'fail'}">{latest[key]}</div>
                <div class="threshold">meta: ≥ 0.90</div>
            </div>
"""
        html += "        </div>\n"

        html += """
        <div class="chart-container">
            <h2>📈 Métricas da Última Execução</h2>
"""
        for label, key in [
            ("F1-Score", "f1_score"),
            ("Clarity", "clarity"),
            ("Precision", "precision"),
            ("Helpfulness", "helpfulness"),
            ("Correctness", "correctness"),
        ]:
            value = float(latest[key])
            html += f"""
            <div class="metric-row">
                <div class="metric-label"><span>{label}</span><span>{latest[key]}</span></div>
                <div class="bar-bg"><div class="bar-fill {'pass' if value >= 0.9 else 'fail'}" style="width: {value * 100}%; min-width: 30px;">{latest[key]}</div></div>
            </div>
"""
        html += "        </div>\n"

    html += """
        <h2>📋 Histórico de Execuções</h2>
        <table>
            <thead>
                <tr>
                    <th>Data/Hora</th><th>Versão</th><th>LLM</th><th>F1</th><th>Clarity</th><th>Precision</th><th>Helpfulness</th><th>Correctness</th><th>Média</th><th>Tempo</th><th>Status</th>
                </tr>
            </thead>
            <tbody>
"""

    def trend_icon(t):
        icons = {"up": "▲", "down": "▼", "same": "●"}
        return f'<span class="trend {t}">{icons.get(t, "")}</span>' if t else ""

    for row in reversed(rows):
        status_class = "aprovado" if row["status"] == "APROVADO" else "reprovado"
        html += f"""
                <tr>
                    <td class="timestamp">{row['timestamp']}</td>
                    <td class="version">{row['version']}</td>
                    <td class="llm">{row.get('llm_model', 'N/A')}</td>
"""
        for metric in ["f1_score", "clarity", "precision", "helpfulness", "correctness", "average"]:
            value = float(row[metric])
            css_class = "pass" if value >= 0.9 else "fail"
            trend = trend_icon(row.get(f"{metric}_trend", ""))
            html += f'                    <td class="score {css_class}">{row[metric]} {trend}</td>\n'
        html += f"""
                    <td class="duration">{format_duration(row.get('duration_seconds'))}</td>
                    <td><span class="status {status_class}">{row['status']}</span></td>
                </tr>
"""

    html += """
            </tbody>
        </table>
        <div class="footer">
            <p>Relatório gerado automaticamente pelo sistema de tracking de avaliações</p>
            <p>Reasoning salvo em <code>results/reasoning_analysis.txt</code></p>
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

    version = get_prompt_version()
    provider, model, _ = get_llm_info()
    llm_full = f"{provider}/{model}"

    print(f"\nVersão do prompt detectada: {version}")
    print(f"LLM configurado: {llm_full}")

    start_time = time.time()
    scores, reasoning_results = run_tracked_evaluation()
    duration = time.time() - start_time
    duration_str = str(timedelta(seconds=int(duration)))

    print(f"\n⏱️  Tempo total de execução: {duration_str} ({duration:.1f}s)")

    print("\n📊 Métricas agregadas:")
    for metric in ["f1_score", "clarity", "precision", "helpfulness", "correctness", "average"]:
        print(f"  - {metric}: {scores[metric]}")
    print(f"  - status: {scores['status']}")

    save_to_csv(version, scores, llm_full, duration)
    save_reasoning(reasoning_results)
    print_reasoning_summary(reasoning_results)
    generate_html()

    print("\n" + "=" * 70)
    print("✅ TRACKING CONCLUÍDO")
    print("=" * 70)
    print("\n📁 Arquivos gerados:")
    print(f"   - CSV: {CSV_FILE}")
    print(f"   - HTML: {HTML_FILE}")
    print(f"   - Reasoning JSON: {REASONING_JSON_FILE}")
    print(f"   - Reasoning TXT: {REASONING_TXT_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
