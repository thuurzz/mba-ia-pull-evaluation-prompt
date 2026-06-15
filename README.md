# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Este projeto implementa um pipeline completo de otimização de prompts para conversão de relatos de bugs em User Stories de alta qualidade, utilizando LangChain, LangSmith e técnicas avançadas de Prompt Engineering.

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.8 (80%) em todas as métricas de avaliação

---

## Tecnologias Utilizadas

- **Python 3.12+**
- **LangChain** (0.3.13) — Framework para aplicações LLM
- **LangSmith** (0.2.7) — Plataforma de observabilidade e avaliação
- **OpenAI GPT-4.1** — Modelo final para geração de respostas
- **OpenAI GPT-4o-mini / GPT-4o** — Modelos para iterações iniciais
- **Ollama Local** — gemma4:12b, llama3.1:8b para iterações locais
- **YAML** — Formato de serialização dos prompts
- **pytest** — Framework de testes

---

## Técnicas Aplicadas (Fase 2)

### 1. Role Prompting

- Definição de persona: **Product Manager Sênior com 10 anos de experiência**
- Especialidade declarada em metodologias ágeis e transformação de bugs em User Stories
- **Justificativa**: A persona especializada guia o modelo a gerar respostas no formato e tom esperados por equipes de desenvolvimento, aumentando a clareza e profissionalismo.
- **Exemplo no prompt**:
  ```yaml
  system_prompt: |
    Você é um Product Manager Sênior especialista em metodologias ágeis.
    Transforme relatos de bugs em User Stories no formato padrão.
  ```

### 2. Chain of Thought (CoT)

- Raciocínio passo a passo antes da geração:
  1. Identificar persona afetada
  2. Entender ação desejada
  3. Articular valor/benefício
  4. Extrair detalhes técnicos
  5. Definir critérios testáveis
- **Justificativa**: Forçar o modelo a "pensar" antes de responder reduz omissões e melhora a completude da User Story, impactando diretamente o F1-Score.
- **Exemplo no prompt**:
  ```yaml
  RACIOCÍNIO (pense passo a passo, mas NÃO mostre na resposta):
    1. Identifique a persona mais específica afetada pelo bug.
    2. Extraia TODAS as informações técnicas do bug.
    3. Extraia TODAS as informações de impacto.
    4. Determine o valor META para cada critério de aceitação.
    5. Mapeie cada item para a seção correta da User Story.
    6. Remova redundâncias.
    7. Verifique se algum detalhe ficou de fora.
    8. Gere a resposta final no formato abaixo.
  ```

### 3. Few-shot Learning

- **6 exemplos completos** de entrada/saída cobrindo todos os tipos de bugs:
  - Bug simples (botão não funciona)
  - Bug médio com contexto técnico (endpoint segurança)
  - Bug complexo com impacto (carrinho + estoque)
  - Bug de performance (relatório SQL)
  - Bug de modal/z-index com acessibilidade
  - Bug de webhook com logs
- **Justificativa**: Exemplos concretos demonstram o formato esperado, regras implícitas e tratamento de edge cases, reduzindo a variação na qualidade das respostas.
- **Exemplo no prompt**: 6 exemplos completos no `system_prompt`, cobrindo bugs simples, médio, complexo, performance, modal/z-index e webhook. Ver linhas 70–197 do `bug_to_user_story_v2.yml`.
  ```yaml
  EXEMPLOS:
    ---
    Entrada: "Botão de adicionar ao carrinho não funciona no produto ID 1234."
    Saída:
      Como um cliente navegando na loja, eu quero...
      Critérios de Aceitação:
        - Dado que estou visualizando um produto
        - Quando clico no botão "Adicionar ao Carrinho"
        - Então o produto deve ser adicionado ao carrinho
    ---
    Entrada: "Endpoint /api/users/:id retorna dados sem validar permissões..."
    Saída:
      Como o sistema, eu quero validar permissões...
      Critérios de Aceitação:
        - Dado que sou um usuário comum
        - Quando tento acessar GET /api/users/:id de outro usuário
        - Então devo receber HTTP 403 Forbidden
  ```

### 4. Self-Refinement (Critique-and-Revise)
Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

---

- Revisão mental de clareza antes da resposta final
- Checks: bullet único por ideia, sem repetição, comportamento vs implementação, bugs simples sem seções extras
- **Justificativa**: Força o modelo a revisar a própria saída, melhorando Clarity sem perder completude.
- **Exemplo no prompt**:
  ```yaml
  REVISÃO DE CLAREZA (faça mentalmente antes de responder, mas NÃO mostre):
    - Cada bullet tem uma única ideia?
    - Existe informação repetida em mais de uma seção?
    - Critérios de Aceitação descrevem comportamento esperado?
    - Contexto Técnico contém apenas detalhes técnicos objetivos?
    - Bugs simples ficaram sem seções extras desnecessárias?
  ```

### 5. Output Constraints / Format Control

- Regras explícitas de formatação: bullets curtos, seções separadas, subtítulos por problema em bugs complexos
- **Justificativa**: Restrições de formato garantem saída limpa e estruturada, aumentando Clarity e Precision.
- **Exemplo no prompt**:
  ```yaml
  FORMATO DE SAÍDA (siga exatamente este formato):
    Como um [persona específica], eu quero [ação desejada], para que [benefício real].
    Critérios de Aceitação:
      - Dado que [contexto]
      - Quando [ação]
      - Então [resultado]
      - E [resultado adicional] (se houver)
    Se o bug tiver detalhes técnicos, adicione:
    Contexto Técnico:
      - [Detalhe técnico 1]
    Se o bug tiver dados de impacto, adicione:
    Contexto do Bug:
      - [Dado de impacto 1]
  ```

### Evolução das Técnicas nas Iterações

| Iteração | Versão | Mudança Principal                                                                             |
| ---------- | ------- | ---------------------------------------------------------------------------------------------- |
| 1          | v2.0    | Prompt inicial com CoT detalhado, 6 passos, 3 exemplos                                         |
| 2          | v2.1    | Regras anti-omissão, Contexto Técnico/Impacto obrigatórios, exemplo complexo do dataset     |
| 3          | v2.2    | Simplificação radical — prompt curto e direto, 3 exemplos equilibrados                      |
| 4          | v2.3    | Ultra-simplificado — 4 instruções, 6 regras, foco máximo em preservação de informações |

---

## Resultados Finais

### ✅ Última Avaliação APROVADA (v2.15)

| Métrica               | Score          | Meta    | Status |
| ---------------------- | -------------- | ------- | ------ |
| F1-Score               | **0.94** | ≥ 0.90 | ✅     |
| Clarity                | **0.91** | ≥ 0.90 | ✅     |
| Precision              | **0.93** | ≥ 0.90 | ✅     |
| Helpfulness            | **0.92** | ≥ 0.90 | ✅     |
| Correctness            | **0.94** | ≥ 0.90 | ✅     |
| **Média Geral** | **0.93** | ≥ 0.90 | ✅     |

**Status: ✅ APROVADO** — Todas as 5 métricas ≥ 0.90.

- **Prompt**: `v2.15`
- **Modelo**: `openai/gpt-4.1`
- **Tempo**: 109.3s
- **Data**: 2026-06-14

### Screenshots de Evidência

**Dashboard com métricas:**
![Testes pytest passando](results/screenshots/teste_pytest_passando.png)

**Métricas finais aprovadas no LangSmith:**
![Métricas finais aprovadas](results/screenshots/metricas_finais_aprovadas.png)

### Tabela Comparativa: v1 vs v2.15

| Métrica         | v1 (Base)      | v2.15 (Final)  | Delta          |
| ---------------- | -------------- | -------------- | -------------- |
| F1-Score         | 0.48           | **0.94** | +96%           |
| Clarity          | 0.50           | **0.91** | +82%           |
| Precision        | 0.46           | **0.93** | +102%          |
| Helpfulness      | 0.45           | **0.92** | +104%          |
| Correctness      | 0.52           | **0.94** | +81%           |
| **Média** | **0.48** | **0.93** | **+94%** |

### Evolução por Iteração

| Versão         | F1             | Clarity        | Precision      | Helpfulness    | Correctness    | Média         | Modelo            | Status       |
| --------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- | ----------------- | ------------ |
| v2.0            | 0.79           | 0.89           | 0.90           | 0.89           | 0.85           | 0.86           | gpt-4o-mini       | ❌           |
| v2.1            | 0.76           | 0.88           | 0.90           | 0.89           | 0.83           | 0.85           | gpt-4o-mini       | ❌           |
| v2.2            | 0.74           | 0.88           | 0.90           | 0.89           | 0.82           | 0.85           | gpt-4o-mini       | ❌           |
| v2.3            | 0.75           | 0.89           | 0.93           | 0.91           | 0.84           | 0.86           | gpt-4o-mini       | ❌           |
| v2.4            | 0.77           | 0.88           | 0.91           | 0.90           | 0.84           | 0.86           | gpt-4o-mini       | ❌           |
| v2.5            | 0.78           | 0.88           | 0.91           | 0.90           | 0.85           | 0.86           | gpt-4o-mini       | ❌           |
| v2.6            | 0.78           | 0.88           | 0.91           | 0.90           | 0.85           | 0.86           | gpt-4o-mini       | ❌           |
| v2.7            | 0.77           | 0.88           | 0.90           | 0.89           | 0.84           | 0.86           | gpt-4o-mini       | ❌           |
| v2.8            | 0.78           | 0.87           | 0.91           | 0.89           | 0.84           | 0.86           | gpt-4o-mini       | ❌           |
| v2.9            | 0.79           | 0.89           | 0.91           | 0.90           | 0.85           | 0.87           | gpt-4o-mini       | ❌           |
| v2.10           | 0.79           | 0.88           | 0.91           | 0.90           | 0.85           | 0.87           | gpt-4o-mini       | ❌           |
| v2.11           | 0.79           | 0.88           | 0.91           | 0.90           | 0.85           | 0.87           | gpt-4o-mini       | ❌           |
| v2.12           | 0.80           | 0.87           | 0.91           | 0.89           | 0.85           | 0.86           | gpt-4o-mini       | ❌           |
| v2.12           | 0.79           | 0.87           | 0.90           | 0.89           | 0.85           | 0.86           | gpt-5-mini        | ❌           |
| v2.13           | 0.94           | 0.88           | 0.94           | 0.91           | 0.94           | 0.92           | gpt-4.1           | ❌           |
| v2.14           | 0.94           | 0.88           | 0.94           | 0.91           | 0.94           | 0.92           | gpt-4.1           | ❌           |
| **v2.15** | **0.94** | **0.91** | **0.93** | **0.92** | **0.94** | **0.93** | **gpt-4.1** | **✅** |

> **Observação**: O salto de qualidade ocorreu ao mudar do `gpt-4o-mini` para o `gpt-4.1` e refinar regras de clareza (Self-Refinement + Output Constraints). O F1-Score pulou de 0.80 para 0.94 — ganho de +17.5%.

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
LLM_MODEL=gpt-4.1          # ou gemini-2.5-flash
EVAL_MODEL=gpt-4o          # modelo avaliador (LLM-as-Judge)
OLLAMA_BASE_URL=http://localhost:11434  # opcional, para testes locais
```

> Para descobrir seu `USERNAME_LANGSMITH_HUB`: publique qualquer prompt no LangSmith Hub e verifique a URL (`https://smith.langchain.com/hub/{seu_username}/...`).

### Execução

```bash
# 1. Pull do prompt original
python src/pull_prompts.py

# 2. Editar prompts/bug_to_user_story_v2.yml (otimização)

# 3. Push do prompt otimizado
python src/push_prompts.py

# 4. Avaliação com tracking (salva CSV + gera HTML + reasoning)
python src/track_evaluations.py
- Espera-se 3-5 iterações.
- Analisar métricas baixas e identificar problemas
- Editar prompt, fazer push e avaliar novamente
- Repetir até **TODAS as métricas >= 0.8**

# NOTA: track_evaluations.py executa evaluate.py internamente,
# extrai métricas, salva CSV e gera relatório HTML automaticamente.
# evaluate.py sozinho não salva resultados.

# 5. Análise detalhada de reasoning (opcional)
python src/analyze_reasoning.py

# 6. Testes de validação
pytest tests/test_prompts.py -v
```

---
```
- Helpfulness >= 0.8
- Correctness >= 0.8
- F1-Score >= 0.8
- Clarity >= 0.8
- Precision >= 0.8

MÉDIA das 5 métricas >= 0.8
```

**IMPORTANTE:** TODAS as 5 métricas devem estar >= 0.8, não apenas a média!

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

| Arquivo                             | Descrição                                          |
| ----------------------------------- | ---------------------------------------------------- |
| `results/evaluations.csv`         | Histórico de todas as avaliações em formato CSV   |
| `results/index.html`              | Relatório visual com gráficos e tabela comparativa |
| `results/reasoning_analysis.json` | Análise de reasoning por exemplo (formato JSON)     |
| `results/reasoning_analysis.txt`  | Análise de reasoning por exemplo (formato legível) |

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
│   ├── track_evaluations.py      # Sistema de tracking (CSV + HTML + reasoning)
│   └── analyze_reasoning.py      # Análise detalhada de reasoning por exemplo
│
├── tests/
│   └── test_prompts.py           # 6 testes de validação do prompt
│
└── results/
    ├── evaluations.csv           # Histórico de avaliações
    └── index.html                # Relatório visual
│   └── test_prompts.py       # Testes de validação (implementar)
```

**O que você deve implementar:**

- `prompts/bug_to_user_story_v2.yml` — Criar do zero com seu prompt otimizado
- `src/pull_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `src/push_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `tests/test_prompts.py` — Implementar os 6 testes de validação (esqueleto já existe)
- `README.md` — Documentar seu processo de otimização

**O que já vem pronto (não alterar):**

- `src/evaluate.py` — Script de avaliação completo
- `src/metrics.py` — 5 métricas implementadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
- `src/utils.py` — Funções auxiliares
- `datasets/bug_to_user_story.jsonl` — Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- Suporte multi-provider (OpenAI e Gemini)

## Repositórios úteis

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/mba-ia-prompt-engineering)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## O que foi Implementado

- ✅ `src/pull_prompts.py` — Pull do prompt `leonanluppi/bug_to_user_story_v1`
- ✅ `src/push_prompts.py` — Push público para `{username}/bug_to_user_story_v2`
- ✅ `prompts/bug_to_user_story_v2.yml` — Prompt otimizado com Few-shot + CoT + Role Prompting
- ✅ `tests/test_prompts.py` — 6 testes de validação (todos passando)
- ✅ `src/track_evaluations.py` — Sistema de tracking de avaliações (CSV + HTML + JSON reasoning)
- ✅ `src/analyze_reasoning.py` — Análise detalhada de reasoning por exemplo (JSON + TXT)
- ✅ Suporte Ollama (`langchain_community.ChatOllama`) — testes locais
- ✅ Tratamento de temperatura para gpt-5/o1/o3 (força temperature=1)
- ✅ Colunas `llm_model` e `duration_seconds` no CSV
- ✅ README.md — Documentação completa do processo

## O que Não foi Modificado

- ❌ `src/evaluate.py` (script de avaliação)
- ❌ `src/metrics.py` (métricas customizadas)
- ❌ `src/utils.py` (funções auxiliares)
- ❌ `datasets/bug_to_user_story.jsonl` (dataset de avaliação)

---

## Evidências no LangSmith

- **Prompt v2.15 (Aprovado)**: https://smith.langchain.com/hub/thuurzz/bug_to_user_story_v2
- **Projeto de Avaliação**: https://smith.langchain.com/o/8c231a3a-0917-46da-80bb-9fc3ee81db4a/projects/meu-desafio-prompts
- **Dataset**: https://smith.langchain.com/o/8c231a3a-0917-46da-80bb-9fc3ee81db4a/datasets/meu-desafio-prompts-eval (15 exemplos)

---

## Próximos Passos

✅ **DESAFIO CONCLUÍDO** — Todas as 5 métricas atingiram ≥ 0.90 com o prompt `v2.15` e modelo `gpt-4.1`.

### Lições Aprendidas

1. **Modelo importa mais do que prompt**: `gpt-4o-mini` estagnou em F1~0.80 mesmo após 12 iterações de refinamento. `gpt-4.1` saltou para 0.94 na primeira execução.
2. **Clareza ≠ Completude**: Focar só em clareza reduz F1 (omissão de detalhes). Solução: separar regras de clareza (Self-Refinement) de regras de completude (CoT técnico).
3. **Few-shot é poderoso**: 6 exemplos cobrindo todos os tipos de bugs foi o diferencial para F1-Score alto.
4. **Iteração rápida**: ~15 iterações com tracking CSV permitiu identificar rapidamente o que funcionava.
5. **Ollama como sandbox local**: testar ideias com modelos locais (gemma4, llama3.1) reduziu custo de API em iterações iniciais.

---

## Links Úteis

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangChain Hub](https://smith.langchain.com/hub)
## Entregável

**1. Repositório público no GitHub** (fork do repositório base) contendo:

- Todo o código-fonte implementado
- Arquivo `prompts/bug_to_user_story_v2.yml` 100% preenchido e funcional
- Arquivo `README.md` atualizado

**2. README.md deve conter:**

**A) Seção "Técnicas Aplicadas (Fase 2)":**

- Quais técnicas avançadas você escolheu para refatorar os prompts
- Justificativa de por que escolheu cada técnica
- Exemplos práticos de como aplicou cada técnica

**B) Seção "Resultados Finais":**

- Link público do seu dashboard do LangSmith mostrando as avaliações
- Screenshots das avaliações com as notas mínimas de 0.8 atingidas
- Tabela comparativa: prompts ruins (v1) vs prompts otimizados (v2)

**C) Seção "Como Executar":**

- Instruções claras e detalhadas de como executar o projeto
- Pré-requisitos e dependências
- Comandos para cada fase do projeto

**3. Evidências no LangSmith:**

- Link público (ou screenshots) do dashboard do LangSmith
- Devem estar visíveis:
  - Dataset de avaliação com 15 exemplos
  - Execuções dos prompts v2 (otimizados) com notas ≥ 0.8
  - Tracing detalhado de pelo menos 3 exemplos

---

## Licença

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de bugs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.8 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final
