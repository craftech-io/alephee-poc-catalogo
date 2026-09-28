"""El único módulo del catálogo que sabe que abajo hay Bedrock."""

import os

from llama_index.llms.bedrock_converse import BedrockConverse

# Converse acepta `us.` y `global.` (verificado 28/09); sin prefijo no hay throughput
# on-demand. `us.` es el que contempla la policy del RuntimeRole.
MODEL_ID_POR_DEFECTO = "us.anthropic.claude-sonnet-5"


def crear_llm(env=os.environ) -> BedrockConverse:
    return BedrockConverse(
        model=env.get("MODEL_ID", MODEL_ID_POR_DEFECTO),
        region_name=env.get("AWS_REGION", "us-east-1"),
        # En local se usa el perfil SSO; en el Runtime no hay perfil y boto3 toma el rol.
        profile_name=env.get("AWS_PROFILE") or None,
        max_tokens=16000,
        system_prompt_caching=True,
        tool_caching=True,
    )


def uso_de(respuesta) -> dict:
    """Tokens de una respuesta de LlamaIndex, con los nombres que usa `agent/llm.py`."""
    kwargs = getattr(respuesta, "additional_kwargs", None) or {}
    return {
        clave: int(kwargs[clave])
        for clave in ("prompt_tokens", "completion_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
        if kwargs.get(clave)
    }
