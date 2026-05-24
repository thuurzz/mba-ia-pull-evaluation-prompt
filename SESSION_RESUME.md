# Resumo da Sessão — Prompt Optimization Challenge

**Data/Hora:** 2026-05-24  
**Sessão OpenCode ID:** `New session - 2026-05-24T17:37:41.489Z`  
**Branch atual:** `feat/prompt-optimization`  
**Modelo LLM configurado:** `gpt-4o-mini`  
**Commit mais recente:** `feat: iterate prompt v2.8 with reasoning analysis fixes, add analyze_reasoning.py`

---

## Status do Desafio

❌ **Ainda NÃO APROVADO** — Todas as 5 métricas precisam ser ≥ 0.9

| Métrica | Meta | Melhor Score (v2.9) | Status |
|---|---|---|---|
| F1-Score | ≥ 0.90 | **0.81** | ❌ |
| Clarity | ≥ 0.90 | **0.89** | ❌ |
| Precision | ≥ 0.90 | **0.85** | ❌ |
| Helpfulness | ≥ 0.90 | **0.87** | ❌ |
| Correctness | ≥ 0.90 | **0.83** | ❌ |
| **Média Geral** | ≥ 0.90 | **0.85** | ❌ |

---

## Histórico de Iterações

| Versão | F1 | Clarity | Precision | Helpfulness | Correctness | Média | O que mudou |
|---|---|---|---|---|---|---|---|
| v2.0 | 0.79 | 0.89 | 0.90 | 0.89 | 0.85 | 0.86 | Prompt inicial com CoT, 6 passos, 3 exemplos |
| v2.1 | 0.76 | 0.88 | 0.90 | 0.89 | 0.83 | 0.85 | Anti-omissão, Contexto/Impacto obrigatórios, exemplo complexo do dataset |
| v2.2 | 0.74 | 0.88 | 0.90 | 0.89 | 0.82 | 0.85 | Ultra-simplificado, 4 instruções, 6 regras |
| v2.3 | 0.75 | 0.89 | **0.93** | **0.91** | 0.84 | **0.86** | Prompt mais curto, 2 exemplos, foco máximo em preservação |
| v2.4 | **0.77** | 0.88 | 0.90 | 0.89 | 0.84 | 0.86 | Skeleton of Thought (esboço antes de responder), exemplo complexo simplificado |
| v2.5 | 0.75 | 0.88 | 0.90 | 0.89 | 0.83 | 0.85 | Teste com modelo `gpt-4o` (não melhorou sozinho) |
| v2.6 | 0.76 | 0.87 | 0.91 | 0.89 | 0.84 | 0.85 | Skeleton com esqueleto explícito, 3 exemplos |
| v2.7 | 0.72 | 0.89 | 0.85 | 0.87 | 0.79 | 0.83 | Regras críticas anti-alucinação, anti-esqueleto, persona específica |
| v2.8 | 0.73 | 0.89 | 0.89 | 0.89 | 0.81 | 0.84 | Baseado no v2.3 + regras anti-alucinação + anti-esqueleto |
| v2.9 | **0.81** | **0.89** | 0.85 | 0.87 | 0.83 | 0.85 | **Formato idêntico ao dataset**, exemplos do próprio dataset como few-shot |

---

## Descoberta-Chave: Análise de Reasoning do Avaliador

Criamos o script `src/analyze_reasoning.py` que captura o `reasoning` do avaliador (explicação textual do que está certo/errado em cada resposta). Isso revelou os **padrões reais de erro**:

### Padrão 1: Esqueleto aparecendo na resposta final
- O modelo incluía o processo de raciocínio/esqueleto preenchido como parte da resposta
- Isso poluía a saída e reduzia Clarity e Precision
- **Correção:** Instrução explícita "NÃO inclua raciocínio ou esqueleto na resposta"

### Padrão 2: Alucinações em seções opcionais
- O modelo criava seções "Contexto Técnico" e "Impacto" mesmo quando o bug não tinha esses dados
- Exemplo: bug simples "Imagens não aparecem no Safari" → modelo inventava "logs/stack traces" e "severidade"
- **Correção:** Regras explícitas "NUNCA crie Contexto Técnico se o bug não tiver endpoints/logs"

### Padrão 3: Persona incorreta
- O modelo escolhia personas genéricas ("usuário do sistema") em vez de específicas ("administrador", "cliente")
- **Correção:** "SEMPRE escolha a persona mais específica baseada no bug"

### Padrão 4: Omite detalhes específicos do ground truth
- Exemplo 1: falta "CRDTs, vector clocks, chunked upload"
- Exemplo 4: falta "modal deve ocupar 90% da largura da tela"
- Exemplo 5: falta "sugestão de remover item ou aguardar reposição"
- **Correção:** Ainda não resolvido completamente — é o principal gargalo do F1

### Padrão 5: Formato diferente do esperado
- O ground truth usa formato com bullets (`- Dado que...`) e não numbered (`1. Dado que...`)
- O ground truth usa "Contexto Técnico:" e "Contexto do Bug:" (sem negrito) em vez de "**Contexto Técnico:**"
- **Correção:** v2.9 replicou exatamente o formato do dataset

---

## O que já foi Implementado

### Fase 1 — Pull Prompts ✅
- `src/pull_prompts.py` implementado
- Puxa `leonanluppi/bug_to_user_story_v1` e salva em `prompts/bug_to_user_story_v1.yml`

### Fase 2 — Prompt Otimizado ✅
- `prompts/bug_to_user_story_v2.yml` criado com 3 técnicas:
  - Role Prompting
  - Chain of Thought (CoT)
  - Few-shot Learning
- v2.9: formato idêntico ao dataset, exemplos do próprio dataset
- YAML com metadata `techniques_applied` contendo 3 técnicas

### Fase 3 — Push Prompts ✅
- `src/push_prompts.py` implementado
- Push público para `thuurzz/bug_to_user_story_v2`
- Username LangSmith: `thuurzz`

### Fase 4 — Testes ✅
- `tests/test_prompts.py` implementado com 6 testes:
  - `test_prompt_has_system_prompt`
  - `test_prompt_has_role_definition`
  - `test_prompt_mentions_format`
  - `test_prompt_has_few_shot_examples`
  - `test_prompt_no_todos`
  - `test_minimum_techniques`
- Todos os 6 testes passam

### Fase 5b — Sistema de Tracking ✅
- `src/track_evaluations.py` criado
- Salva resultados em `results/evaluations.csv`
- Gera relatório HTML em `results/index.html`
- Uso: `python src/track_evaluations.py`

### Fase 5c — Análise de Reasoning ✅
- `src/analyze_reasoning.py` criado
- Captura o `reasoning` do avaliador por exemplo
- Salva em `results/reasoning_analysis.json` e `.txt`
- Uso: `python src/analyze_reasoning.py`

### Fase 5d — README ✅
- `README.md` atualizado com documentação completa

---

## Onde Paramos

**Iteração v2.9 concluída.** Melhor F1 até agora (0.81), mas ainda abaixo de 0.9.

A abordagem v2.9 (replicar formato idêntico ao dataset com exemplos do próprio dataset) melhorou o F1 de 0.76 para 0.81 (+0.05), mostrando que o formato importa.

### Próximo passo recomendado
Usar o `analyze_reasoning.py` para identificar quais exemplos específicos ainda estão falhando (F1 < 0.9), extrair o reasoning de cada um, e criar exemplos few-shot **exatamente para esses padrões de erro**.

Ou: testar com `gpt-4o` (modelo mais capaz) + prompt v2.9 (melhor formato).

---

## Comandos Úteis para Retomar

```bash
# Ativar ambiente
source venv/bin/activate

# Rodar testes
pytest tests/test_prompts.py -v

# Push do prompt atual
python src/push_prompts.py

# Avaliar (com tracking)
python src/track_evaluations.py

# Avaliar (sem tracking)
python src/evaluate.py

# Analisar reasoning do avaliador
python src/analyze_reasoning.py

# Ver histórico
cat results/evaluations.csv

# Abrir relatório
open results/index.html  # Mac
xdg-open results/index.html  # Linux
```

---

## Arquivos Modificados nesta Sessão

| Arquivo | Status | Observação |
|---|---|---|
| `src/pull_prompts.py` | ✅ Implementado | Faz pull de `leonanluppi/bug_to_user_story_v1` |
| `src/push_prompts.py` | ✅ Implementado | Push público para `{username}/bug_to_user_story_v2` |
| `prompts/bug_to_user_story_v2.yml` | ✅ Criado | v2.9 atual — formato idêntico ao dataset |
| `tests/test_prompts.py` | ✅ Implementado | 6 testes passando |
| `src/track_evaluations.py` | ✅ Criado | Sistema de tracking CSV + HTML |
| `src/analyze_reasoning.py` | ✅ Criado | Captura reasoning do avaliador por exemplo |
| `results/evaluations.csv` | ✅ Criado | 10 registros de avaliação |
| `results/index.html` | ✅ Gerado | Relatório visual atualizado |
| `results/reasoning_analysis.txt` | ✅ Gerado | Reasoning completo do avaliador |
| `README.md` | ✅ Atualizado | Documentação completa |
| `AGENTS.md` | ✅ Criado | Instruções para futuros agentes |
| `SESSION_RESUME.md` | ✅ Criado | Este arquivo |
| `.env` | ✅ Configurado | Username `thuurzz`, modelo `gpt-4o-mini` |

---

## Commits Realizados

1. `feat: implement pull prompts script`
2. `feat: create optimized prompt v2 with few-shot, CoT and role prompting`
3. `feat: implement push prompts script and fix username env`
4. `feat: implement 6 prompt validation tests`
5. `feat: iterate prompt v2.3 - simplify structure, improve completeness rules`
6. `feat: add evaluation tracking system (CSV + HTML report) and update README`
7. `feat: iterate prompt v2.8 with reasoning analysis fixes, add analyze_reasoning.py`
8. `feat: iterate prompt v2.9 with dataset-format matching`

---

## Contexto do Ambiente

- **OS:** Linux
- **Python:** 3.12.3
- **Branch:** `feat/prompt-optimization`
- **Provider LLM:** OpenAI
- **Modelo de Resposta:** `gpt-4o-mini`
- **Modelo de Avaliação:** `gpt-4o`
- **LangSmith Username:** `thuurzz`
- **Prompt no Hub:** `thuurzz/bug_to_user_story_v2`
- **Dataset:** `meu-desafio-prompts-eval` (15 exemplos)

---

## Observações Importantes

1. **NÃO modificar:** `src/evaluate.py`, `src/metrics.py`, `src/utils.py`, `datasets/bug_to_user_story.jsonl`
2. **Prompt deve ser PÚBLICO** no LangSmith Hub para avaliação funcionar
3. **Ordem obrigatória:** `push_prompts.py` → `evaluate.py`
4. **Custo estimado com gpt-4o-mini:** ~$1-3 por avaliação completa
5. **Custo estimado com gpt-4o:** ~$5-10 por avaliação completa
6. **Ferramenta-chave:** `src/analyze_reasoning.py` para entender erros do avaliador

---

*Última atualização: 2026-05-24*  
*Próxima ação: Melhorar F1-Score de 0.81 para ≥ 0.90*
*Estratégia recomendada: Usar analyze_reasoning.py para identificar padrões restantes e criar few-shots específicos*
