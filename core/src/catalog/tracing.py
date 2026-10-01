"""Langfuse client and LlamaIndex instrumentation, shared by the experiment and the chat tool.

OpenInference turns every LlamaIndex call (workflow steps, agent turns, Bedrock calls) into
OpenTelemetry spans that Langfuse shows as one trace per product, with tokens and latency.
"""

import os

# Instrumenting twice would emit every span twice; the flag makes setup idempotent per process.
_instrumented = False


def langfuse_client(env=os.environ):
    """The Langfuse client, or None when the keys are not configured (tests, offline runs)."""
    if not (env.get("LANGFUSE_PUBLIC_KEY") and env.get("LANGFUSE_SECRET_KEY")):
        return None
    # Imported here so that code paths without Langfuse keys never pay for importing the SDK.
    from langfuse import get_client

    return get_client()


def setup_tracing(env=os.environ):
    """Connect OpenInference spans to Langfuse once per process. Returns the client or None."""
    global _instrumented
    client = langfuse_client(env)
    if client is not None and not _instrumented:
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

        LlamaIndexInstrumentor().instrument()
        _instrumented = True
    return client
