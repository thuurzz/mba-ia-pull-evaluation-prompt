"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print_section_header(f"PUSH DO PROMPT: {prompt_name}")

        # Criar ChatPromptTemplate a partir dos dados
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")

        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("human", user_prompt))

        prompt_template = ChatPromptTemplate.from_messages(messages)

        # Preparar metadados
        description = prompt_data.get("description", "")
        tags = prompt_data.get("tags", [])
        techniques = prompt_data.get("techniques_applied", [])

        print(f"Enviando para o LangSmith Hub: {prompt_name}")
        print(f"Descrição: {description}")
        print(f"Tags: {', '.join(tags)}")
        print(f"Técnicas: {', '.join(techniques)}")

        # Fazer push para o Hub (público)
        hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags
        )

        print(f"\n✓ Prompt '{prompt_name}' enviado com sucesso!")
        print(f"  Verifique em: https://smith.langchain.com/prompts/{prompt_name}")
        print(f"\n⚠️  IMPORTANTE: Certifique-se de que o prompt está configurado como PÚBLICO no dashboard.")
        return True

    except Exception as e:
        print(f"\n{'=' * 70}")
        print(f"❌ ERRO: Não foi possível fazer push do prompt '{prompt_name}'")
        print(f"{'=' * 70}\n")
        print(f"Erro técnico: {e}\n")
        print("Verifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- USERNAME_LANGSMITH_HUB está configurado corretamente")
        print("- Você tem permissão para publicar no workspace do LangSmith")
        print(f"\n{'=' * 70}\n")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH HUB")

    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    prompt_file = "prompts/bug_to_user_story_v2.yml"

    # Carregar prompt otimizado
    print(f"\nCarregando prompt de: {prompt_file}")
    prompts_data = load_yaml(prompt_file)

    if not prompts_data:
        print(f"❌ Falha ao carregar prompt de {prompt_file}")
        return 1

    # Extrair dados do v2
    prompt_data = prompts_data.get("bug_to_user_story_v2", {})

    if not prompt_data:
        print("❌ Estrutura do YAML inválida. Chave 'bug_to_user_story_v2' não encontrada.")
        return 1

    print(f"✓ Prompt carregado com sucesso")

    # Validar estrutura
    print("\nValidando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Validação falhou:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Validação passou com sucesso")

    # Fazer push
    prompt_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if success:
        print("\n" + "=" * 70)
        print("✅ PROMPT PUBLICADO COM SUCESSO!")
        print("=" * 70)
        print("\nPróximos passos:")
        print("1. Verifique no dashboard se o prompt está PÚBLICO")
        print("2. Execute a avaliação: python src/evaluate.py")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
