"""The only catalog module that knows Bedrock is underneath."""

import os

from botocore.exceptions import NoCredentialsError, SSOError, TokenRetrievalError, UnauthorizedSSOTokenError
from llama_index.llms.bedrock_converse import BedrockConverse

# Converse accepts the `us.` and `global.` profiles; the bare model id has no on-demand throughput.
DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-5"
_AUTH_ERRORS = (NoCredentialsError, SSOError, TokenRetrievalError, UnauthorizedSSOTokenError)


def create_llm(env=os.environ) -> BedrockConverse:
    return BedrockConverse(
        model=env.get("MODEL_ID", DEFAULT_MODEL_ID),
        region_name=env.get("AWS_REGION", "us-east-1"),
        # Local runs use the SSO profile; inside the Runtime boto3 takes the role.
        profile_name=env.get("AWS_PROFILE") or None,
        max_tokens=16000,
    )


def is_auth_error(exc: BaseException) -> bool:
    """Expired or missing AWS credentials: retrying the next product would fail the same way."""
    return isinstance(exc, _AUTH_ERRORS) or "ExpiredToken" in str(exc)
