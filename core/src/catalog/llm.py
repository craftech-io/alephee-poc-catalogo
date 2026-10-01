"""The only catalog module that knows Bedrock is underneath.

V1 and V2 receive the LLM already built, so tests pass a fake and swapping the model (for
example Haiku 4.5, decision 6) is a `MODEL_ID` change in the environment, not a code change.
"""

import os

from botocore.exceptions import NoCredentialsError, SSOError, TokenRetrievalError, UnauthorizedSSOTokenError
from llama_index.llms.bedrock_converse import BedrockConverse

# Converse accepts the `us.` and `global.` profiles; the bare model id has no on-demand throughput.
DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-5"
_AUTH_ERRORS = (NoCredentialsError, SSOError, TokenRetrievalError, UnauthorizedSSOTokenError)


def create_llm(env=os.environ) -> BedrockConverse:
    """Build the Bedrock Converse client from the environment (MODEL_ID, AWS_REGION, AWS_PROFILE)."""
    return BedrockConverse(
        model=env.get("MODEL_ID", DEFAULT_MODEL_ID),
        region_name=env.get("AWS_REGION", "us-east-1"),
        # Local runs use the SSO profile; inside the Runtime boto3 takes the role.
        profile_name=env.get("AWS_PROFILE") or None,
        # High ceiling on purpose: an answer cut off at the limit is not a valid Listing.
        max_tokens=16000,
    )


def is_auth_error(exc: BaseException) -> bool:
    """Expired or missing AWS credentials: retrying the next product would fail the same way."""
    # Botocore raises a typed error for missing or SSO credentials, but an expired session token
    # surfaces as a generic ClientError whose message names ExpiredToken.
    return isinstance(exc, _AUTH_ERRORS) or "ExpiredToken" in str(exc)


def auth_error_message(exc: BaseException, profile: str | None) -> str:
    """Shared wording for an expired or missing AWS session, with or without a named profile."""
    hint = f"aws sso login --profile {profile}" if profile else "aws sso login"
    return f"AWS credentials expired or missing ({exc}). Run: {hint}"
