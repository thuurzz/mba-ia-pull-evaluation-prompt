"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(scope="class")
    def prompt_data(self):
        """Carrega o prompt otimizado v2."""
        return load_prompts("prompts/bug_to_user_story_v2.yml")

    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        v2 = prompt_data.get("bug_to_user_story_v2", {})
        system_prompt = v2.get("system_prompt", "")
        assert system_prompt, "system_prompt está vazio ou não existe"
        assert len(system_prompt.strip()) > 50, "system_prompt muito curto para ser válido"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        v2 = prompt_data.get("bug_to_user_story_v2", {})
        system_prompt = v2.get("system_prompt", "")
        assert "você é" in system_prompt.lower() or "você sera" in system_prompt.lower(), \
            "Prompt não define uma persona clara"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        v2 = prompt_data.get("bug_to_user_story_v2", {})
        system_prompt = v2.get("system_prompt", "")
        assert "markdown" in system_prompt.lower() or "formato" in system_prompt.lower(), \
            "Prompt não menciona formato obrigatório"
        assert "como um" in system_prompt.lower() and "eu quero" in system_prompt.lower(), \
            "Prompt não menciona formato padrão de User Story"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        v2 = prompt_data.get("bug_to_user_story_v2", {})
        system_prompt = v2.get("system_prompt", "")
        assert "exemplo" in system_prompt.lower(), "Prompt não contém exemplos (few-shot)"
        assert "entrada:" in system_prompt.lower() or "entrada :" in system_prompt.lower(), \
            "Prompt não mostra estrutura de entrada nos exemplos"
        assert "saída:" in system_prompt.lower() or "saída :" in system_prompt.lower(), \
            "Prompt não mostra estrutura de saída nos exemplos"

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        import re
        v2 = prompt_data.get("bug_to_user_story_v2", {})
        full_text = v2.get("system_prompt", "") + v2.get("user_prompt", "")
        assert "[TODO]" not in full_text, "Prompt ainda contém [TODO] não resolvido"
        # Verificar TODOs não resolvidos, evitando falsos positivos com palavras como TODOS
        todo_matches = re.findall(r'TODO[:\s]', full_text)
        assert len(todo_matches) == 0, f"Prompt ainda contém {len(todo_matches)} TODO(s) não resolvido(s)"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        v2 = prompt_data.get("bug_to_user_story_v2", {})
        techniques = v2.get("techniques_applied", [])
        assert isinstance(techniques, list), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])