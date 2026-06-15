"""
Script para capturar o reasoning detalhado do avaliador por exemplo.

Uso:
    python src/analyze_reasoning.py

O script:
1. Puxa o prompt do LangSmith Hub
2. Roda cada exemplo do dataset
3. Chama as 3 métricas (F1, Clarity, Precision)
4. Captura o 'reasoning' de cada métrica (explicação do avaliador)
5. Salva em results/reasoning_analysis.json e results/reasoning_analysis.txt

Isso permite identificar padrões de erro e ajustar o prompt.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain import hub

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from evaluate import (
    pull_prompt_from_langsmith,
    evaluate_prompt_on_example,
    get_llm,
    load_dataset_from_jsonl,
)
from metrics import evaluate_f1_score, evaluate_clarity, evaluate_precision

RESULTS_DIR = Path("results")
JSON_FILE = RESULTS_DIR / "reasoning_analysis.json"
TXT_FILE = RESULTS_DIR / "reasoning_analysis.txt"


def main():
    print("=" * 70)
    print("ANÁLISE DE REASONING DO AVALIADOR")
    print("=" * 70)

    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado")
        return 1

    prompt_name = f"{username}/bug_to_user_story_v2"
    dataset_name = f"{os.getenv('LANGSMITH_PROJECT', 'prompt-optimization-challenge-resolved')}-eval"

    # Puxar prompt
    print(f"\nPuxando prompt: {prompt_name}")
    prompt_template = pull_prompt_from_langsmith(prompt_name)

    # Carregar dataset
    client = Client()
    examples = list(client.list_examples(dataset_name=dataset_name))
    print(f"Dataset: {len(examples)} exemplos\n")

    llm = get_llm()

    results = []

    for i, example in enumerate(examples, 1):
        print(f"[{i}/{len(examples)}] Avaliando exemplo {i}...")

        result = evaluate_prompt_on_example(prompt_template, example, llm)
        question = result["question"]
        answer = result["answer"]
        reference = result["reference"]

        if not answer:
            print(f"   ⚠️  Resposta vazia, pulando...")
            continue

        # Avaliar com reasoning
        f1 = evaluate_f1_score(question, answer, reference)
        clarity = evaluate_clarity(question, answer, reference)
        precision = evaluate_precision(question, answer, reference)

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
            }
        }
        results.append(entry)

        print(f"   F1:{f1['score']:.2f} | Clarity:{clarity['score']:.2f} | Precision:{precision['score']:.2f}")

    # Salvar JSON
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ JSON salvo em: {JSON_FILE}")

    # Salvar TXT (formato legível)
    with open(TXT_FILE, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("ANÁLISE DE REASONING - PROMPT OPTIMIZATION\n")
        f.write("=" * 70 + "\n\n")

        for r in results:
            f.write(f"--- EXEMPLO {r['example_index']}/15 ---\n\n")
            f.write(f"BUG REPORT:\n{r['bug_report'][:500]}...\n\n")
            f.write(f"SCORES: F1={r['scores']['f1_score']:.2f} | Clarity={r['scores']['clarity']:.2f} | Precision={r['scores']['precision']:.2f}\n")
            f.write(f"F1 DETALHES: Precision={r['f1_details']['precision']:.2f} | Recall={r['f1_details']['recall']:.2f}\n\n")

            f.write("REASONING F1-Score:\n")
            f.write(f"{r['reasoning']['f1']}\n\n")

            f.write("REASONING Clarity:\n")
            f.write(f"{r['reasoning']['clarity']}\n\n")

            f.write("REASONING Precision:\n")
            f.write(f"{r['reasoning']['precision']}\n\n")

            f.write("=" * 70 + "\n\n")

    print(f"✓ TXT salvo em: {TXT_FILE}")

    # Resumo de problemas comuns
    print("\n" + "=" * 70)
    print("RESUMO DE PROBLEMAS COMUNS")
    print("=" * 70)

    low_f1 = [r for r in results if r["scores"]["f1_score"] < 0.9]
    low_clarity = [r for r in results if r["scores"]["clarity"] < 0.9]
    low_precision = [r for r in results if r["scores"]["precision"] < 0.9]

    print(f"\nExemplos com F1 < 0.9: {len(low_f1)}")
    for r in low_f1:
        print(f"   Exemplo {r['example_index']}: F1={r['scores']['f1_score']:.2f} (Recall={r['f1_details']['recall']:.2f})")

    print(f"\nExemplos com Clarity < 0.9: {len(low_clarity)}")
    for r in low_clarity:
        print(f"   Exemplo {r['example_index']}: Clarity={r['scores']['clarity']:.2f}")

    print(f"\nExemplos com Precision < 0.9: {len(low_precision)}")
    for r in low_precision:
        print(f"   Exemplo {r['example_index']}: Precision={r['scores']['precision']:.2f}")

    print("\n" + "=" * 70)
    print("DICA: Leia results/reasoning_analysis.txt para ver o reasoning completo")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
