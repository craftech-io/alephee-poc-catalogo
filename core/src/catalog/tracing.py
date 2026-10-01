"""Langfuse client and LlamaIndex instrumentation, shared by the experiment and the chat tool."""

import os

_instrumented = False


def langfuse_client(env=os.environ):
    """The Langfuse client, or None when the keys are not configured (tests, offline runs)."""
    if not (env.get("LANGFUSE_PUBLIC_KEY") and env.get("LANGFUSE_SECRET_KEY")):
        return None
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
