"""A scripted FunctionCallingLLM: FunctionAgent's `llm` field is Pydantic, so the double must subclass it."""

import itertools

from llama_index.core.base.llms.types import ChatMessage, ChatResponse, LLMMetadata
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.llms.llm import ToolSelection

_ids = itertools.count()


def call(name: str, **kwargs) -> ToolSelection:
    return ToolSelection(tool_id=f"call-{next(_ids)}", tool_name=name, tool_kwargs=kwargs)


class ScriptedLLM(FunctionCallingLLM):
    script: list = []
    seen: list = []

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(is_function_calling_model=True, model_name="scripted")

    async def achat_with_tools(self, tools, user_msg=None, chat_history=None, verbose=False,
                               allow_parallel_tool_calls=False, **kwargs):
        history = chat_history or []
        self.seen.append(history[-1].content if history else None)
        calls = self.script.pop(0) if self.script else []
        return ChatResponse(message=ChatMessage(role="assistant", content="" if calls else "done"), raw={"calls": calls})

    def get_tool_calls_from_response(self, response, error_on_no_tool_call=True, **kwargs):
        return response.raw["calls"]

    def _prepare_chat_with_tools(self, *args, **kwargs):
        raise NotImplementedError

    def chat(self, *args, **kwargs):
        raise NotImplementedError

    async def achat(self, *args, **kwargs):
        raise NotImplementedError

    def complete(self, *args, **kwargs):
        raise NotImplementedError

    async def acomplete(self, *args, **kwargs):
        raise NotImplementedError

    def stream_chat(self, *args, **kwargs):
        raise NotImplementedError

    async def astream_chat(self, *args, **kwargs):
        raise NotImplementedError

    def stream_complete(self, *args, **kwargs):
        raise NotImplementedError

    async def astream_complete(self, *args, **kwargs):
        raise NotImplementedError
