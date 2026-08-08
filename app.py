""" Gradio Multimodal Web UI with Custom Login/Logout and Multi-User Session Isolation for Agno Investment Agent """

from typing import Generator, Any
import gradio as gr
from agno.media import Image
from main import agente, storage

# Test user credentials
VALID_CREDENTIALS: dict[str, str] = {
    "admin": "admin123",
    "investidor": "investidor123"
}


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


def get_saved_history_by_user(username: str) -> list[dict[str, Any]]:
    """
    Retrieve stored chat history from Agno's SqliteDb for a specific user session.
    """
    if not username:
        return []
    try:
        session_id: str = f"investimentos_{username}"
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
        print(f"Error loading chat history for {username}: {exc}")
        return []


def login_action(username_input: str, password_input: str):
    """
    Validate user login and load past chat history.
    """
    user = (username_input or "").strip()
    password = (password_input or "").strip()

    if user in VALID_CREDENTIALS and VALID_CREDENTIALS[user] == password:
        user_history = get_saved_history_by_user(user)
        badge_text = f"👤 Logado como: **{user}**"
        
        return (
            gr.update(visible=False),  # login_card
            gr.update(visible=True),   # chat_card
            gr.update(visible=True),   # logout_btn
            user,                      # user_state
            badge_text,                # user_badge
            user_history,              # chatbot
            "",                        # error_output
            "",                        # username_input
            ""                         # password_input
        )
    
    return (
        gr.update(visible=True),       # login_card
        gr.update(visible=False),      # chat_card
        gr.update(visible=False),      # logout_btn
        "",                            # user_state
        "",                            # user_badge
        [],                            # chatbot
        "⚠️ **Usuário ou senha incorretos.** Tente novamente.",  # error_output
        username_input,                # username_input
        ""                             # password_input
    )


def logout_action():
    """
    Clear session state and return to login screen.
    """
    return (
        gr.update(visible=True),       # login_card
        gr.update(visible=False),      # chat_card
        gr.update(visible=False),      # logout_btn
        "",                            # user_state
        "",                            # user_badge
        [],                            # chatbot
        "",                            # error_output
        "",                            # username_input
        ""                             # password_input
    )


def add_user_message(message: dict[str, Any], history: list[dict[str, Any]]):
    """
    Immediately display user input in chatbot and clear input box.
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
        "files": file_paths
    })
    return history, gr.update(value=None)


def bot_respond_stream(history: list[dict[str, Any]], username: str):
    """
    Stream agent response for the logged-in user session.
    """
    if not history or history[-1].get("role") != "user":
        yield history
        return

    user_id: str = username.strip() if username else "default_user"
    session_id: str = f"investimentos_{user_id}"

    user_msg_item = history[-1]
    
    # Safely extract text content regardless of data structure (str, list, dict)
    raw_text: str = extract_text_content(user_msg_item.get("raw_text", user_msg_item.get("content", "")))
    file_paths: list[str] = user_msg_item.get("files", []) if isinstance(user_msg_item.get("files"), list) else []

    # Convert attached file paths to Agno Image objects
    agno_images: list[Image] = [Image(filepath=fp) for fp in file_paths]

    # Initialize assistant message chunk in history
    history.append({"role": "assistant", "content": ""})

    # Execute agent query with streaming enabled
    response_stream: Any = agente.run(
        raw_text if raw_text else "Analise os arquivos/imagens em anexo.",
        images=agno_images if agno_images else None,
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
        yield history


# Create Gradio UI using Blocks
with gr.Blocks(title="Agente de Investimentos") as demo:
    user_state = gr.State("")

    # Application Header
    with gr.Row(equal_height=True):
        with gr.Column(scale=8):
            gr.Markdown("## 📈 Agente de Gestão de Investimentos")
            gr.Markdown("Assistente virtual com inteligência financeira, busca web e análise de carteira.")
        with gr.Column(scale=4, elem_id="header_user_area"):
            user_badge = gr.Markdown("")
            logout_btn = gr.Button("🚪 Sair / Logout", variant="secondary", visible=False, size="sm")

    gr.Markdown("---")

    # 1. Login Card (Visible initially)
    with gr.Column(visible=True) as login_card:
        gr.Markdown("### 🔐 Autenticação de Acesso")
        gr.Markdown("Digite suas credenciais para acessar sua sessão isolada de investimentos.")
        
        with gr.Group():
            username_input = gr.Textbox(label="Usuário", placeholder="Ex: admin ou investidor", autofocus=True)
            password_input = gr.Textbox(label="Senha", type="password", placeholder="Sua senha")
            login_btn = gr.Button("🔑 Entrar", variant="primary")
            error_output = gr.Markdown("")

    # 2. Chat Application Card (Hidden initially)
    with gr.Column(visible=False) as chat_card:
        chatbot = gr.Chatbot(height=520)
        
        input_box = gr.MultimodalTextbox(
            placeholder="Digite sua mensagem, anexe arquivos ou cole imagens (Ctrl+V)...",
            show_label=False
        )

    # Login Event Bindings
    login_btn.click(
        fn=login_action,
        inputs=[username_input, password_input],
        outputs=[login_card, chat_card, logout_btn, user_state, user_badge, chatbot, error_output, username_input, password_input]
    )
    password_input.submit(
        fn=login_action,
        inputs=[username_input, password_input],
        outputs=[login_card, chat_card, logout_btn, user_state, user_badge, chatbot, error_output, username_input, password_input]
    )

    # Logout Event Binding
    logout_btn.click(
        fn=logout_action,
        inputs=None,
        outputs=[login_card, chat_card, logout_btn, user_state, user_badge, chatbot, error_output, username_input, password_input]
    )

    # Chat Interaction Event Binding
    input_box.submit(
        fn=add_user_message,
        inputs=[input_box, chatbot],
        outputs=[chatbot, input_box],
        queue=False
    ).then(
        fn=bot_respond_stream,
        inputs=[chatbot, user_state],
        outputs=chatbot
    )


if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(),
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
