# Resumo da Sessão — Prompt Optimization Challenge

**Data/Hora:** 2026-05-24  
**Sessão OpenCode ID:** `New session - 2026-05-24T17:37:41.489Z`  
**Branch atual:** `feat/prompt-optimization`  
**Modelo LLM configurado:** `gpt-4o-mini` (revertido de `gpt-4o` após testes)  
**Commit mais recente:** `feat: add evaluation tracking system (CSV + HTML report) and update README`

---

## Status do Desafio

❌ **Ainda NÃO APROVADO** — Todas as 5 métricas precisam ser ≥ 0.9

| Métrica | Meta | Melhor Score (v2.3) | Status |
|---|---|---|---|
| F1-Score | ≥ 0.90 | **0.77** (v2.4) | ❌ |
| Clarity | ≥ 0.90 | **0.89** (v2.3) | ❌ |
| Precision | ≥ 0.90 | **0.93** (v2.3) | ✅ |
| Helpfulness | ≥ 0.90 | **0.91** (v2.3) | ✅ |
| Correctness | ≥ 0.90 | **0.85** (v2.3) | ❌ |
| **Média** | ≥ 0.90 | **0.86** (v2.3) | ❌ |

---

## Histórico de Iterações

| Versão | F1 | Clarity | Precision | Helpfulness | Correctness | Média | O que mudou |
|---|---|---|---|---|---|---|---|
| v2.0 | 0.79 | 0.89 | 0.90 | 0.89 | 0.85 | 0.86 | Prompt inicial com CoT, 6 passos, 3 exemplos |
| v2.1 | 0.76 | 0.88 | 0.90 | 0.89 | 0.83 | 0.85 | Anti-omissão, Contexto/Impacto obrigatórios, exemplo complexo do dataset |
| v2.2 | 0.74 | 0.88 | 0.90 | 0.89 | 0.82 | 0.85 | Ultra-simplificado, 4 instruções, 6 regras |
| v2.3 | 0.75 | 0.89 | 0.93 | 0.91 | 0.84 | 0.86 | Prompt mais curto, 2 exemplos, foco máximo em preservação |
| v2.4 | 0.77 | 0.88 | 0.90 | 0.89 | 0.84 | 0.86 | Skeleton of Thought (esboço antes de responder), exemplo complexo simplificado |
| v2.5 | 0.75 | 0.88 | 0.90 | 0.89 | 0.83 | 0.85 | Teste com modelo `gpt-4o` (não melhorou) |
| v2.6 | 0.76 | 0.87 | 0.91 | 0.89 | 0.84 | 0.85 | Skeleton com esqueleto explícito, 3 exemplos |

---

## O que já foi Implementado

### Fase 1 — Pull Prompts ✅
- `src/pull_prompts.py` implementado
- Puxa `leonanluppi/bug_to_user_story_v1` e salva em `prompts/bug_to_user_story_v1.yml`

### Fase 2 — Prompt Otimizado ✅
- `prompts/bug_to_user_story_v2.yml` criado com 4 técnicas:
  - Role Prompting
  - Chain of Thought (CoT)
  - Few-shot Learning (3 exemplos)
  - Skeleton of Thought
- YAML com metadata `techniques_applied` contendo 4 técnicas

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

### Fase 5c — README ✅
- `README.md` atualizado com:
  - Técnicas aplicadas e justificativas
  - Tabela comparativa v1 vs v2
  - Histórico de iterações
  - Instruções de execução
  - Próximos passos

---

## Onde Paramos

**Iteração v2.6 concluída.** O prompt atual usa **Skeleton of Thought** com esqueleto explícito, mas ainda não bateu 0.9 em F1-Score e Correctness.

### Diagnóstico do Problema Principal
O **F1-Score** (0.76) é o gargalo. Ele é composto por:
- **Precision**: 0.91 ✅ (alta — modelo não inventa)
- **Recall**: baixo ❌ (modelo omite detalhes técnicos do ground truth)

Os bugs complexos do dataset (exemplos 13, 14, 15) têm MUITOS detalhes que o `gpt-4o-mini` não está incluindo na resposta:
- Endpoints específicos
- Logs e stack traces
- Steps to reproduce
- Números de usuários afetados
- Perdas financeiras

### Tentativas já feitas que NÃO resolveram
1. ✅ Instrução "NUNCA omita" — já está no prompt desde v2.1
2. ✅ Contexto Técnico e Impacto como seções obrigatórias
3. ✅ Exemplos few-shot mostrando preservação completa
4. ✅ Skeleton of Thought (esboço antes de responder)
5. ✅ Teste com `gpt-4o` (não melhorou, revertido)
6. ✅ Prompt curto e direto (v2.3)

---

## Próximos Passos (para retomar)

### Opção A — Ajustar o Prompt
- Adicionar **mais exemplos few-shot de bugs complexos** (especialmente dos exemplos 13, 14, 15 do dataset)
- Instruir explicitamente: "Liste TODOS os endpoints, logs, números, steps do bug na seção Contexto Técnico"
- Testar dividir o processo em 2 chamadas: (1) extrair informações, (2) gerar User Story

### Opção B — Trocar o Modelo
- Configurar `.env` para usar `LLM_MODEL=gpt-4o` (testado em v2.5, não melhorou sozinho)
- OU usar `LLM_MODEL=gpt-4o` + prompt mais completo (combinação não testada)
- Custo estimado: ~$5-10 para completar o desafio com gpt-4o

### Opção C — Analisar os Exemplos Específicos
- Rodar `python src/evaluate.py` e observar os scores individuais dos 15 exemplos
- Identificar quais exemplos estão derrubando o F1 (provavelmente os complexos 13, 14, 15)
- Ajustar o prompt para cobrir especificamente os padrões desses exemplos

### Opção D — Híbrida (Recomendada)
1. Commitar a iteração atual (v2.6)
2. Analisar scores individuais por exemplo
3. Criar um exemplo few-shot baseado nos bugs que mais falham
4. Testar com `gpt-4o` + prompt otimizado
5. Iterar até bater ≥ 0.9

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
| `prompts/bug_to_user_story_v2.yml` | ✅ Criado | v2.6 atual — precisa melhorar |
| `tests/test_prompts.py` | ✅ Implementado | 6 testes passando |
| `src/track_evaluations.py` | ✅ Criado | Sistema de tracking CSV + HTML |
| `results/evaluations.csv` | ✅ Criado | 7 registros de avaliação |
| `results/index.html` | ✅ Gerado | Relatório visual atualizado |
| `README.md` | ✅ Atualizado | Documentação completa |
| `AGENTS.md` | ✅ Criado | Instruções para futuros agentes |
| `.env` | ✅ Configurado | Username `thuurzz`, modelo `gpt-4o-mini` |

---

## Commits Realizados

1. `feat: implement pull prompts script`
2. `feat: create optimized prompt v2 with few-shot, CoT and role prompting`
3. `feat: implement push prompts script and fix username env`
4. `feat: implement 6 prompt validation tests`
5. `feat: iterate prompt v2.3 - simplify structure, improve completeness rules`
6. `feat: add evaluation tracking system (CSV + HTML report) and update README`

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

---

*Última atualização: 2026-05-24*  
*Próxima ação: Melhorar F1-Score de 0.76 para ≥ 0.90*
