# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Este projeto implementa um pipeline completo de otimização de prompts para conversão de relatos de bugs em User Stories de alta qualidade, utilizando LangChain, LangSmith e técnicas avançadas de Prompt Engineering.

O desafio consiste em:
1. **Fazer pull** de um prompt de baixa qualidade do LangSmith Hub
2. **Refatorar e otimizar** usando técnicas avançadas de Prompt Engineering
3. **Fazer push** do prompt otimizado de volta ao LangSmith Hub
4. **Avaliar a qualidade** através de 5 métricas customizadas
5. **Atingir ≥ 0.9** em todas as métricas

---

## Tecnologias Utilizadas

- **Python 3.12+**
- **LangChain** (0.3.13) — Framework para aplicações LLM
- **LangSmith** (0.2.7) — Plataforma de observabilidade e avaliação
- **OpenAI GPT-4o-mini** — Modelo para geração de respostas
- **OpenAI GPT-4o** — Modelo para avaliação (LLM-as-Judge)
- **YAML** — Formato de serialização dos prompts
- **pytest** — Framework de testes

---

## Técnicas Aplicadas (Fase 2)

### 1. Role Prompting
- Definição de persona: **Product Manager Sênior com 10 anos de experiência**
- Especialidade declarada em metodologias ágeis e transformação de bugs em User Stories
- **Justificativa**: A persona especializada guia o modelo a gerar respostas no formato e tom esperados por equipes de desenvolvimento, aumentando a clareza e profissionalismo.

### 2. Chain of Thought (CoT)
- Raciocínio passo a passo antes da geração:
  1. Identificar persona afetada
  2. Entender ação desejada
  3. Articular valor/benefício
  4. Extrair detalhes técnicos
  5. Definir critérios testáveis
- **Justificativa**: Forçar o modelo a "pensar" antes de responder reduz omissões e melhora a completude da User Story, impactando diretamente o F1-Score.

### 3. Few-shot Learning
- **3 exemplos completos** de entrada/saída:
  - Bug simples (botão não funciona)
  - Bug médio com contexto técnico (endpoint 404)
  - Bug complexo com impacto (vazamento de dados + severidade ALTA)
- **Justificativa**: Exemplos concretos demonstram o formato esperado, regras implícitas e tratamento de edge cases, reduzindo a variação na qualidade das respostas.

### Evolução das Técnicas nas Iterações

| Iteração | Versão | Mudança Principal |
|---|---|---|
| 1 | v2.0 | Prompt inicial com CoT detalhado, 6 passos, 3 exemplos |
| 2 | v2.1 | Regras anti-omissão, Contexto Técnico/Impacto obrigatórios, exemplo complexo do dataset |
| 3 | v2.2 | Simplificação radical — prompt curto e direto, 3 exemplos equilibrados |
| 4 | v2.3 | Ultra-simplificado — 4 instruções, 6 regras, foco máximo em preservação de informações |

---

## Resultados Finais

### Última Avaliação (v2.3)

| Métrica | Score | Meta | Status |
|---|---|---|---|
| F1-Score | 0.75 | ≥ 0.90 | ❌ |
| Clarity | 0.89 | ≥ 0.90 | ❌ |
| Precision | 0.93 | ≥ 0.90 | ✅ |
| Helpfulness | 0.91 | ≥ 0.90 | ✅ |
| Correctness | 0.84 | ≥ 0.90 | ❌ |
| **Média Geral** | **0.86** | ≥ 0.90 | ❌ |

**Status: REPROVADO** — F1-Score e Correctness abaixo da meta.

### Tabela Comparativa: v1 vs v2.3

| Métrica | v1 (Base) | v2.3 (Otimizado) | Delta |
|---|---|---|---|
| F1-Score | 0.48 | 0.75 | +56% |
| Clarity | 0.50 | 0.89 | +78% |
| Precision | 0.46 | 0.93 | +102% |
| Helpfulness | 0.45 | 0.91 | +102% |
| Correctness | 0.52 | 0.84 | +62% |
| **Média** | **0.48** | **0.86** | **+79%** |

### Evolução por Iteração

| Versão | F1 | Clarity | Precision | Helpfulness | Correctness | Média |
|---|---|---|---|---|---|---|
| v2.0 | 0.79 | 0.89 | 0.90 | 0.89 | 0.85 | 0.86 |
| v2.1 | 0.76 | 0.88 | 0.90 | 0.89 | 0.83 | 0.85 |
| v2.2 | 0.74 | 0.88 | 0.90 | 0.89 | 0.82 | 0.85 |
| v2.3 | 0.75 | 0.89 | 0.93 | 0.91 | 0.84 | 0.86 |

> **Observação**: O F1-Score continua abaixo da meta porque o modelo (`gpt-4o-mini`) omite detalhes técnicos do ground truth nos bugs complexos. A próxima iteração deve focar em aumentar a completude da resposta.

---

## Como Executar

### Pré-requisitos

1. Python 3.12+
2. Conta no LangSmith (https://smith.langchain.com)
3. API Key da OpenAI (https://platform.openai.com/api-keys)

### Setup

```bash
# Clonar o repositório
git clone <url-do-repo>
cd mba-ia-pull-evaluation-prompt

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

### Variáveis de Ambiente (.env)

```bash
LANGSMITH_API_KEY=lsv2_pt_...
USERNAME_LANGSMITH_HUB=thuurzz
OPENAI_API_KEY=sk-proj-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
```

> Para descobrir seu `USERNAME_LANGSMITH_HUB`: publique qualquer prompt no LangSmith Hub e verifique a URL (`https://smith.langchain.com/hub/{seu_username}/...`).

### Execução

```bash
# 1. Pull do prompt original
python src/pull_prompts.py

# 2. Editar prompts/bug_to_user_story_v2.yml (otimização)

# 3. Push do prompt otimizado
python src/push_prompts.py

# 4. Avaliação
python src/evaluate.py

# 5. Tracking de avaliações (salva CSV + gera HTML)
python src/track_evaluations.py

# 6. Testes de validação
pytest tests/test_prompts.py -v
```

---

## Sistema de Tracking de Avaliações

Para acompanhar a evolução das métricas por iteração, foi implementado um sistema de tracking que:

1. **Executa a avaliação** automaticamente
2. **Extrai as métricas** da saída do evaluate.py
3. **Salva em CSV** (`results/evaluations.csv`) com timestamp e versão do prompt
4. **Gera relatório HTML** (`results/index.html`) com gráficos e tabela comparativa

### Uso

```bash
# Após cada iteração do prompt
python src/track_evaluations.py

# Abrir relatório no navegador
open results/index.html  # Mac
xdg-open results/index.html  # Linux
```

### Arquivos Gerados

| Arquivo | Descrição |
|---|---|
| `results/evaluations.csv` | Histórico de todas as avaliações em formato CSV |
| `results/index.html` | Relatório visual com gráficos e tabela comparativa |

---

## Estrutura do Projeto

```
mba-ia-pull-evaluation-prompt/
├── .env                          # Variáveis de ambiente (não commitar)
├── .env.example                  # Template de variáveis
├── requirements.txt              # Dependências Python
├── README.md                     # Documentação
├── AGENTS.md                     # Instruções para agentes de IA
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt original (puxado do Hub)
│   └── bug_to_user_story_v2.yml  # Prompt otimizado (criado)
│
├── datasets/
│   └── bug_to_user_story.jsonl   # Dataset de 15 bugs para avaliação
│
├── src/
│   ├── pull_prompts.py           # Script de pull do LangSmith Hub
│   ├── push_prompts.py           # Script de push para o LangSmith Hub
│   ├── evaluate.py               # Script de avaliação (pronto)
│   ├── metrics.py                # Métricas customizadas (pronto)
│   ├── utils.py                  # Funções auxiliares (pronto)
│   └── track_evaluations.py      # Sistema de tracking (implementado)
│
├── tests/
│   └── test_prompts.py           # 6 testes de validação do prompt
│
└── results/
    ├── evaluations.csv           # Histórico de avaliações
    └── index.html                # Relatório visual
```

---

## O que foi Implementado

- ✅ `src/pull_prompts.py` — Pull do prompt `leonanluppi/bug_to_user_story_v1`
- ✅ `src/push_prompts.py` — Push público para `{username}/bug_to_user_story_v2`
- ✅ `prompts/bug_to_user_story_v2.yml` — Prompt otimizado com Few-shot + CoT + Role Prompting
- ✅ `tests/test_prompts.py` — 6 testes de validação (todos passando)
- ✅ `src/track_evaluations.py` — Sistema de tracking de avaliações (CSV + HTML)
- ✅ `README.md` — Documentação completa do processo

## O que Não foi Modificado

- ❌ `src/evaluate.py` (script de avaliação)
- ❌ `src/metrics.py` (métricas customizadas)
- ❌ `src/utils.py` (funções auxiliares)
- ❌ `datasets/bug_to_user_story.jsonl` (dataset de avaliação)

---

## Evidências no LangSmith

- **Prompt otimizado**: https://smith.langchain.com/hub/thuurzz/bug_to_user_story_v2
- **Dashboard de avaliações**: https://smith.langchain.com/projects/meu-desafio-prompts
- **Dataset**: `meu-desafio-prompts-eval` (15 exemplos)

---

## Próximos Passos

Para atingir ≥ 0.9 em todas as métricas, as próximas iterações devem focar em:

1. **Aumentar o F1-Score (0.75 → 0.90)**:
   - O principal gargalo é a **completude** (recall)
   - O modelo omite detalhes técnicos (logs, endpoints, steps to reproduce) presentes no ground truth
   - Estratégia: Adicionar regra explícita "Liste TODOS os detalhes técnicos do bug na seção Contexto Técnico"
   - Considerar aumentar o exemplo few-shot de bug complexo para mostrar preservação completa

2. **Aumentar a Correctness (0.84 → 0.90)**:
   - Depende diretamente do F1-Score (Correctness = (F1 + Precision) / 2)
   - Como Precision já está alta (0.93), focar no F1 resolve ambos

3. **Manter Clarity acima de 0.90**:
   - A clareza está próxima (0.89), pequenos ajustes no formato de saída podem ajudar
   - Considerar adicionar exemplo de formatação mais estruturada

---

## Links Úteis

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangChain Hub](https://smith.langchain.com/hub)

---

## Licença

Projeto desenvolvido para o MBA em Inteligência Artificial — Desafio de Otimização de Prompts.
