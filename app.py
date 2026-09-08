""" Gradio Multimodal & Voice Web UI for Agno Investment Agent """

from typing import Generator, Any
import os
import uuid
import tempfile
import asyncio
import gradio as gr
import edge_tts
from agno.media import Image, Audio
from main import agente, storage


def extract_text_content(val: Any) -> str:
    """
    Safely extract string text from any Gradio content value (str, list, dict, tuple).
    """
    if isinstance(val, str):
        return val.strip()
    if isinstance(val, list):
        parts: list[str] = []
        for item in val:
            if isinstance(item, str):
                parts.append(item.strip())
            elif isinstance(item, dict):
                parts.append(str(item.get("text", item.get("content", ""))).strip())
        return " ".join(parts).strip()
    if isinstance(val, dict):
        return str(val.get("text", val.get("content", ""))).strip()
    return str(val).strip() if val is not None else ""


def generate_voice_response(text: str) -> str | None:
    """
    Synthesize text response to MP3 audio using edge-tts (pt-BR-AntonioNeural).
    """
    if not text or not text.strip():
        return None
    try:
        clean_text: str = text.replace("*", "").replace("#", "").replace("`", "").replace("~", "").strip()
        if len(clean_text) > 500:
            clean_text = clean_text[:500] + "... Para a resposta completa, confira o texto no chat."

        temp_audio_path: str = os.path.join(tempfile.gettempdir(), f"agent_voice_{uuid.uuid4().hex[:8]}.mp3")

        async def run_tts():
            communicate = edge_tts.Communicate(clean_text, "pt-BR-AntonioNeural")
            await communicate.save(temp_audio_path)

        asyncio.run(run_tts())
        return temp_audio_path
    except Exception as exc:
        print(f"Error generating TTS audio: {exc}")
        return None


def get_saved_history(session_id: str = "investimentos") -> list[dict[str, Any]]:
    """
    Retrieve stored chat history from Agno's SqliteDb.
    """
    try:
        session = storage.get_session(session_id=session_id)
        if not session:
            return []
        
        messages = session.get_chat_history()
        history: list[dict[str, Any]] = []
        
        for msg in messages:
            if msg.content and msg.role in ("user", "assistant"):
                history.append({"role": msg.role, "content": extract_text_content(msg.content)})
                
        return history
    except Exception as exc:
        print(f"Error loading chat history: {exc}")
        return []


def add_user_message(message: dict[str, Any], history: list[dict[str, Any]]):
    """
    Immediately display user text input in chatbot and clear input box.
    """
    history = history or []
    text_content: str = message.get("text", "").strip() if isinstance(message, dict) else str(message).strip()
    file_paths: list[str] = message.get("files", []) if isinstance(message, dict) else []

    if not text_content and not file_paths:
        return history, gr.update(value=None)

    display_content = text_content
    if file_paths:
        display_content = f"{text_content}\n📎 *[ {len(file_paths)} arquivo(s) anexado(s) ]*" if text_content else f"📎 *[ {len(file_paths)} arquivo(s) anexado(s) ]*"

    history.append({
        "role": "user",
        "content": display_content,
        "raw_text": text_content,
        "files": file_paths,
        "audio_file": None
    })
    return history, gr.update(value=None)


def add_user_audio_message(audio_filepath: str, history: list[dict[str, Any]]):
    """
    Immediately display user recorded microphone audio in chatbot and clear audio input recorder.
    """
    history = history or []
    if not audio_filepath:
        return history, gr.update(value=None)

    history.append({
        "role": "user",
        "content": "🎙️ *[ Mensagem de Voz Enviada ]*",
        "raw_text": "Responda à pergunta enviada por áudio.",
        "files": [],
        "audio_file": audio_filepath
    })
    return history, gr.update(value=None)


def bot_respond_stream(
    history: list[dict[str, Any]],
    enable_voice: bool = False
) -> Generator[tuple[list[dict[str, Any]], Any], None, None]:
    """
    Stream agent text response and optionally generate voice TTS audio playback.
    """
    if not history or history[-1].get("role") != "user":
        yield history, gr.update(visible=False, value=None)
        return

    session_id: str = "investimentos"
    user_msg_item: dict[str, Any] = history[-1]
    
    raw_text: str = extract_text_content(user_msg_item.get("raw_text", user_msg_item.get("content", "")))
    file_paths: list[str] = user_msg_item.get("files", []) if isinstance(user_msg_item.get("files"), list) else []
    audio_filepath: str | None = user_msg_item.get("audio_file")

    agno_images: list[Image] = [Image(filepath=fp) for fp in file_paths]
    agno_audio: list[Audio] | None = [Audio(filepath=audio_filepath)] if audio_filepath else None

    history.append({"role": "assistant", "content": ""})

    response_stream: Any = agente.run(
        raw_text if raw_text else "Analise a mensagem de voz/arquivo recebido.",
        images=agno_images if agno_images else None,
        audio=agno_audio,
        stream=True,
        session_id=session_id
    )

    accumulated_text: str = ""
    for chunk in response_stream:
        if hasattr(chunk, "content") and chunk.content is not None:
            accumulated_text += str(chunk.content)
        elif isinstance(chunk, str):
            accumulated_text += chunk
        
        history[-1]["content"] = accumulated_text
        yield history, gr.update(visible=False, value=None)

    if enable_voice:
        voice_audio_path: str | None = generate_voice_response(accumulated_text)
        if voice_audio_path:
            yield history, gr.update(visible=True, value=voice_audio_path)
        else:
            yield history, gr.update(visible=False, value=None)
    else:
        yield history, gr.update(visible=False, value=None)


CUSTOM_CSS: str = """
/* Maximize chatbot vertical view while leaving space for controls and footer */
.main-chatbot {
    height: calc(100vh - 250px) !important;
    min-height: 480px !important;
}

/* Compact Audio Player styling */
.compact-audio-container {
    max-height: 50px !important;
    min-height: 40px !important;
    padding: 0px !important;
    margin: 2px 0px !important;
}
.compact-audio-container audio {
    height: 36px !important;
}
.audio-control-row {
    align-items: center;
    margin-top: 4px;
    margin-bottom: 4px;
}
"""

with gr.Blocks(title="Agente de Investimentos", fill_height=True) as demo:
    chatbot = gr.Chatbot(
        value=get_saved_history,
        elem_classes=["main-chatbot"]
    )

    # Audio Controls Row: Checkbox on the left, Compact Audio player on the right
    with gr.Row(elem_classes=["audio-control-row"], equal_height=True):
        with gr.Column(scale=5):
            enable_voice_checkbox = gr.Checkbox(
                label="🔊 Gerar e reproduzir áudio da resposta",
                value=False,
                interactive=True
            )
        with gr.Column(scale=7):
            audio_output = gr.Audio(
                label="",
                autoplay=True,
                visible=False,
                elem_classes=["compact-audio-container"],
                container=False
            )

    # User Input Row
    with gr.Row():
        with gr.Column(scale=8):
            input_box = gr.MultimodalTextbox(
                placeholder="Digite sua mensagem, anexe arquivos ou cole imagens (Ctrl+V)...",
                show_label=False
            )
        with gr.Column(scale=4):
            mic_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Gravar Voz (Microfone)")

    # Event Bindings
    input_box.submit(
        fn=add_user_message,
        inputs=[input_box, chatbot],
        outputs=[chatbot, input_box],
        queue=False
    ).then(
        fn=bot_respond_stream,
        inputs=[chatbot, enable_voice_checkbox],
        outputs=[chatbot, audio_output]
    )

    mic_input.change(
        fn=add_user_audio_message,
        inputs=[mic_input, chatbot],
        outputs=[chatbot, mic_input],
        queue=False
    ).then(
        fn=bot_respond_stream,
        inputs=[chatbot, enable_voice_checkbox],
        outputs=[chatbot, audio_output]
    )


if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS,
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )

