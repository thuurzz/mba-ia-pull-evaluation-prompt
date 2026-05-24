# AGENTS.md

## Project Overview

MBA challenge: pull a low-quality prompt from LangSmith Hub, optimize it with advanced prompt engineering techniques, push it back, and evaluate until all metrics hit ≥ 0.9.

## Tech Stack

- Python 3.9+
- LangChain + LangSmith
- LLM providers: OpenAI (`gpt-4o-mini` / `gpt-4o`) or Google Gemini (`gemini-2.5-flash`)
- Prompt format: YAML
- Testing: pytest

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in all required values:
   - `LANGSMITH_API_KEY`
   - `USERNAME_LANGSMITH_HUB` (discover by publishing any prompt in LangSmith Hub, then clicking the lock icon)
   - `OPENAI_API_KEY` or `GOOGLE_API_KEY` (depending on `LLM_PROVIDER`)
   - `LANGSMITH_PROJECT` (optional, defaults to `prompt-optimization-challenge-resolved`)

   **Default provider in `.env.example` is `google` / `gemini-2.5-flash`.** If using OpenAI, uncomment the OpenAI block and comment the Google block.

## Execution Order (Mandatory)

The evaluation script pulls prompts from LangSmith Hub, so push must happen before evaluate.

```bash
# 1. Pull the low-quality prompt from LangSmith
python src/pull_prompts.py

# 2. Manually create/edit prompts/bug_to_user_story_v2.yml

# 3. Push the optimized prompt to LangSmith Hub (must be public)
python src/push_prompts.py

# 4. Evaluate (pulls v2 from Hub, runs against dataset)
python src/evaluate.py
```

## What to Implement vs. Leave Alone

**Implement:**
- `src/pull_prompts.py` — skeleton has `...`, needs body
- `src/push_prompts.py` — skeleton has `...`, needs body
- `prompts/bug_to_user_story_v2.yml` — create from scratch
- `tests/test_prompts.py` — skeleton has `pass`, implement 6 tests
- `README.md` — document techniques used and results

**Do NOT modify:**
- `src/evaluate.py`
- `src/metrics.py`
- `src/utils.py`
- `datasets/bug_to_user_story.jsonl`

## Prompt v2 Requirements

- **Mandatory:** Few-shot learning (2–3 clear input/output examples)
- **At least one additional technique:** Chain of Thought, Tree of Thought, Skeleton of Thought, ReAct, or Role Prompting
- Clear instructions, explicit behavior rules, edge case handling
- Proper System vs User prompt separation
- YAML metadata must list at least 2 techniques in `techniques_applied`

## Evaluation Criteria

All 5 metrics must be ≥ 0.9. Not just the average.

- Helpfulness = (Clarity + Precision) / 2
- Correctness = (F1-Score + Precision) / 2
- F1-Score, Clarity, Precision (base metrics)

Expect 3–5 iterations of edit → push → evaluate.

## Testing

```bash
pytest tests/test_prompts.py
```

Required tests (already defined as stubs):
- `test_prompt_has_system_prompt`
- `test_prompt_has_role_definition`
- `test_prompt_mentions_format`
- `test_prompt_has_few_shot_examples`
- `test_prompt_no_todos`
- `test_minimum_techniques`

## Common Gotchas

- `evaluate.py` requires `USERNAME_LANGSMITH_HUB` to construct the prompt name (`{username}/bug_to_user_story_v2`). Without it, evaluation fails immediately.
- The prompt must be pushed as **public** to LangSmith Hub; private prompts won't be pullable by the evaluation script.
- `src/` is not a package; scripts import from each other directly and rely on being run from the repo root.
- `sys.path.insert` in `tests/test_prompts.py` adds `src/` manually; no `PYTHONPATH` manipulation needed.
