import asyncio
import chainlit as cl
import re
from src.assistant import IronStoreAssistant

# --------------------------------------------------
# INITIALIZE ASSISTANT
# --------------------------------------------------

@cl.on_chat_start
async def start():

    assistant = await asyncio.to_thread(
        IronStoreAssistant
    )

    cl.user_session.set("assistant", assistant)

    await cl.Message(
        content=(
            "# IronStore Enterprise AI Assistant\n\n"
            "Welcome! Ask me anything about IronStore "
            "internal procedures or product catalogues.\n\n"
            "I will search the available company documents "
            "and provide references to the sources."
        )
    ).send()


# --------------------------------------------------
# HANDLE USER QUESTIONS
# --------------------------------------------------

@cl.on_message
async def main(message: cl.Message):
    question = message.content.strip()

    if not question:
        return

    assistant = cl.user_session.get("assistant")

    if assistant is None:
        await cl.Message(
            content="Assistant initialization failed. Please refresh the page."
        ).send()
        return

    try:
        async with cl.Step(
            name="Searching IronStore knowledge base"
        ) as step:
            step.input = question

            documents = await asyncio.to_thread(
                assistant.retrieve,
                question
            )

            step.output = (
                f"{len(documents)} relevant passages retrieved."
            )

        if not documents:
            await cl.Message(
                content=(
                    "I could not find relevant information "
                    "in the available IronStore documents."
                )
            ).send()
            return

        _, sources = assistant.prepare_context(documents)

        answer = cl.Message(content="")
        await answer.send()

        generated_text = ""

        async for token in assistant.astream_answer(question, documents):
            generated_text += token
            await answer.stream_token(token)

        await answer.update()

        # Extract cited source numbers from the answer
        citation_matches = re.findall(
            r"\[Sources?\s+([0-9,\s]+)\]",
            generated_text,
            re.IGNORECASE
        )

        cited_numbers = {
            number.strip()
            for match in citation_matches
            for number in match.split(",")
            if number.strip().isdigit()
        }

        # Match citations with the actual source registry
        sources_by_label = {
            source["label"]: source
            for source in sources
        }

        cited_labels = {
            f"Source {number}"
            for number in cited_numbers
        }

        unknown_labels = cited_labels - sources_by_label.keys()

        if unknown_labels:
            print(
                f"[Citation Validator] Unknown citations: "
                f"{unknown_labels}"
            )

        cited_sources = [
            sources_by_label[label]
            for label in cited_labels
            if label in sources_by_label
        ]

        # Display only sources actually cited
        if cited_sources:
            source_lines = ["## Sources"]

            for source in sorted(
                cited_sources,
                key=lambda item: int(item["label"].split()[-1])
            ):
                source_lines.append(
                    f"- **[{source['label']}]** "
                    f"{source['filename']} — Page {source['page']}"
                )

            await cl.Message(
                content="\n".join(source_lines)
            ).send()
        else:
            print(
                "[Citation Validator] No valid citations found."
            )


    except Exception as exc:
        print(
            f"ERROR processing question: "
            f"{type(exc).__name__}: {exc}"
        )

        await cl.Message(
            content=(
                "An error occurred while processing your "
                "question. Please check the application terminal."
            )
        ).send()