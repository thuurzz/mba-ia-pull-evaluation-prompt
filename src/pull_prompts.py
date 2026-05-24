"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do LangSmith Hub e salva localmente."""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return False

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = "prompts/bug_to_user_story_v1.yml"

    try:
        print(f"\nBaixando prompt: {prompt_name}")
        prompt = hub.pull(prompt_name)
        print(f"✓ Prompt '{prompt_name}' baixado com sucesso")

        # Extrair mensagens do prompt template
        messages = []
        for msg in prompt.messages:
            if hasattr(msg, "prompt") and hasattr(msg.prompt, "template"):
                if hasattr(msg, "type") and msg.type == "system":
                    messages.append({"role": "system", "content": msg.prompt.template})
                else:
                    messages.append({"role": "user", "content": msg.prompt.template})
            elif hasattr(msg, "template"):
                messages.append({"role": "user", "content": msg.template})

        # Extrair variáveis de entrada
        input_variables = list(prompt.input_variables) if hasattr(prompt, "input_variables") else []

        # Montar estrutura YAML
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": next((m["content"] for m in messages if m["role"] == "system"), ""),
                "user_prompt": next((m["content"] for m in messages if m["role"] == "user"), ""),
                "input_variables": input_variables,
                "version": "v1",
                "source": prompt_name
            }
        }

        # Salvar arquivo YAML
        if save_yaml(prompt_data, output_path):
            print(f"✓ Prompt salvo em: {output_path}")
            return True
        else:
            print(f"❌ Falha ao salvar prompt em: {output_path}")
            return False

    except Exception as e:
        print(f"\n{'=' * 70}")
        print(f"❌ ERRO: Não foi possível fazer pull do prompt '{prompt_name}'")
        print(f"{'=' * 70}\n")
        print(f"Erro técnico: {e}\n")
        print("Verifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- Você tem acesso ao workspace do LangSmith")
        print("- Sua conexão com a internet está funcionando")
        print(f"\n{'=' * 70}\n")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
