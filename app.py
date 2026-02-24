from __future__ import annotations

import streamlit as st

from thoughtful_agent.agent import ThoughtfulSupportAgent
from thoughtful_agent.presentation import build_response_meta, response_notice


st.set_page_config(page_title="Thoughtful AI Support Agent", page_icon="🤖", layout="centered")

st.title("Thoughtful AI Support Agent")
st.caption("Ask about Thoughtful AI’s agents (EVA, CAM, PHIL) or anything else.")


def render_details(meta: dict[str, object] | None) -> None:
    if not meta:
        return

    with st.expander("Details"):
        source = str(meta.get("source", "unknown")).replace("_", " ").title()
        confidence = meta.get("confidence")
        matched_question = meta.get("matched_question")
        no_direct_match = bool(meta.get("no_direct_match", False))

        st.markdown(f"**Source:** {source}")
        if confidence is not None:
            st.markdown(f"**Confidence:** {confidence}")
        if matched_question:
            st.markdown(f"**Matched Question:** {matched_question}")
        st.markdown(f"**Direct Match Found:** {'No' if no_direct_match else 'Yes'}")

if "agent" not in st.session_state:
    st.session_state.agent = ThoughtfulSupportAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I can answer questions about Thoughtful AI’s agents. What would you like to know?",
            "meta": None,
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        render_details(message.get("meta"))

user_input = st.chat_input("Type your question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "meta": None})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.answer(user_input)
            except Exception:
                response = None

        if response is None:
            st.error("Unexpected error while processing your request. Please try again.")
            assistant_content = "Unexpected error while processing your request. Please try again."
            meta = {
                "source": "error",
                "confidence": None,
                "matched_question": None,
                "no_direct_match": True,
            }
        else:
            notice = response_notice(response)
            if notice is not None:
                level, message = notice
                if level == "info":
                    st.info(message)
                elif level == "warning":
                    st.warning(message)
                elif level == "error":
                    st.error(message)

            st.markdown(response.answer)
            meta = build_response_meta(response)
            assistant_content = response.answer

        render_details(meta)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_content,
            "meta": meta,
        }
    )
