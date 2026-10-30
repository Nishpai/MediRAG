"""Streamlit demo. Run: streamlit run app.py"""

import streamlit as st

import rag

# Voice input is optional, the app works without faster-whisper
try:
    import voice
except ImportError:
    voice = None


@st.cache_resource
def load_everything():
    return rag.load_chunks(), rag.load_embeddings(), rag.load_model(), rag.load_threshold()


def use_recording():
    # Runs when a new recording arrives and puts the transcript in the question box
    audio = st.session_state["recording"]
    if audio is not None:
        st.session_state["question"] = voice.transcribe(audio.getvalue())


st.title("MediRAG: health questions answered from MedlinePlus")
st.warning(rag.DISCLAIMER)

chunks, embeddings, model, threshold = load_everything()
# A question can also come from the link, for example ?q=what+helps+a+migraine
if "question" not in st.session_state:
    st.session_state["question"] = st.query_params.get("q", "")
if voice:
    st.audio_input("Or ask by voice (transcribed on this computer)", key="recording", on_change=use_recording)
else:
    st.caption("Voice input is off. Install requirements-voice.txt to turn it on.")
question = st.text_input("Ask a health question (you can edit the transcript here)", key="question")

if question:
    result = rag.answer(question, model, embeddings, chunks, threshold)
    if not result["found"]:
        st.info(rag.NOT_FOUND)
    else:
        generated = rag.generate_answer(question, result["results"])
        if generated:
            st.subheader("Generated answer (optional, not evaluated)")
            st.write(generated)
        st.subheader("Best matching passages")
        for r in result["results"]:
            st.markdown(rag.format_result(r))
            st.write(r["text"])
