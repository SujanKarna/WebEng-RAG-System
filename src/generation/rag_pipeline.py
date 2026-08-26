from typing import List

from src.config.settings import RETRIEVAL_TOP_K
from src.generation.llm_client import LLMClient
from src.generation.prompt_builder import PromptBuilder
from src.retrieval.retriever import Retriever
from src.retrieval.retrieval_models import RetrievedChunk


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.

    Query
        ↓
    Retriever
        ↓
    FAISS + BGE-M3
        ↓
    Retrieved chunks
        ↓
    Prompt builder
        ↓
    Local Qwen LLM
        ↓
    Answer
    """

    def __init__(
        self,
        index_directory: str,
        retriever: Retriever | None = None,
        llm_client: LLMClient | None = None,
        prompt_builder: PromptBuilder | None = None,
    ):

        self.retriever = (
            retriever
            if retriever is not None
            else Retriever(
                index_directory=index_directory
            )
        )

        self.llm_client = (
            llm_client
            if llm_client is not None
            else LLMClient()
        )

        self.prompt_builder = (
            prompt_builder
            if prompt_builder is not None
            else PromptBuilder()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = RETRIEVAL_TOP_K,
    ) -> List[RetrievedChunk]:

        return self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

    def answer(
        self,
        query: str,
        top_k: int = RETRIEVAL_TOP_K,
    ) -> str:

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        chunks = self.retrieve(
            query=query,
            top_k=top_k,
        )

        if not chunks:
            return (
                "Dazu enthält die bereitgestellte "
                "Studienordnung keine ausreichenden "
                "Informationen."
            )

        system_prompt, user_prompt = (
            self.prompt_builder.build(
                query=query,
                chunks=chunks,
            )
        )

        return self.llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def answer_with_sources(
        self,
        query: str,
        top_k: int = RETRIEVAL_TOP_K,
    ) -> tuple[str, List[RetrievedChunk]]:

        chunks = self.retrieve(
            query=query,
            top_k=top_k,
        )

        if not chunks:
            return (
                "Dazu enthält die bereitgestellte "
                "Studienordnung keine ausreichenden "
                "Informationen.",
                [],
            )

        system_prompt, user_prompt = (
            self.prompt_builder.build(
                query=query,
                chunks=chunks,
            )
        )

        answer = self.llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return answer, chunks