from models import BatchSummary, NegativeNewsBatchSummary
import prompts

CONTENT_TYPES = ("entity_search", "negative_search")


def calculate_tokens(text: str) -> int:
    return max(1, len(text)//4)

def split_text(text: str, max_tokens: int) -> list[str]:

    max_chars = max_tokens * 4

    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

def create_batches(sources: dict[str, str], context_size: int) -> list[str]:
    
    batches = []

    current_batch = []
    current_tokens = 0

    for url, content in sources.items():

        if not content:
            continue

        content_tokens = calculate_tokens(content)


        if content_tokens > context_size:

            if current_batch:
                batches.append("\n\n".join(current_batch))

                current_batch = []
                current_tokens = 0

            chunks = split_text(content, max_tokens=context_size)

            for chunk in chunks:

                batches.append(f""" SOURCE URL: {url} 
                                    CONTENT: {chunk}""".strip())

            continue

        source_block = f"""SOURCE URL: {url}
                            CONTENT: {content}""".strip()

        source_tokens = calculate_tokens(source_block)

        if current_tokens + source_tokens <= context_size:

            current_batch.append(source_block)
            current_tokens += source_tokens

        else:

            if current_batch:
                batches.append("\n\n".join(current_batch))

            current_batch = [source_block]
            current_tokens = source_tokens

    if current_batch:
        batches.append("\n\n".join(current_batch))

    return batches

async def summarize(sources: dict[str, str], entity: str, llm , context_size: int = 4000, summary_context_size: int = 3000, content_type: str = CONTENT_TYPES[0]) -> list:

    prompt = prompts.SOURCE_SUMMARY_PROMPT if content_type == CONTENT_TYPES[0] else prompts.NEGATIVE_NEWS_SUMMARY_PROMPT

    prompt_tokens = calculate_tokens(prompt)

    batch_context_size = (context_size - prompt_tokens - 100) 

    batches = create_batches(sources = sources, context_size=batch_context_size)
    
    summaries = []

    remaining_summary_tokens = summary_context_size

    for index, batch in enumerate(batches):

        remaining_batches = len(batches) - index

        output_tokens = max(1, remaining_summary_tokens // remaining_batches)

        prompt = prompt.format(entity = entity, output_tokens = output_tokens)
        prompt += f"""SEARCH RESULT BATCH: {batch}"""

        structured_llm = llm.with_structured_output(BatchSummary) if CONTENT_TYPES[0] else llm.with_structured_output(NegativeNewsBatchSummary)

        structured_llm.bind(options = {"num_predict":output_tokens})

        result = await structured_llm.ainvoke(prompt)

        summaries.append(result)

        actual_tokens = calculate_tokens(result.model_dump_json())

        remaining_summary_tokens = max(0, remaining_summary_tokens - actual_tokens)

    return summaries


async def summarize_sources(sources: dict[str, str], entity: str, llm, context_size: int = 4000, summary_context_size: int = 3000) -> list[BatchSummary]:

    return await summarize(sources, entity, llm, context_size, summary_context_size, CONTENT_TYPES[0])

async def summarize_negative_sources(sources: dict[str, str], entity: str, llm, context_size: int = 4000, summary_context_size: int = 3000) -> list[NegativeNewsBatchSummary]:
    
    return await summarize(sources, entity, llm, context_size, summary_context_size, CONTENT_TYPES[1])
