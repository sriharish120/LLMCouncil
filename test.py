import streamlit as st
import requests
import time

# ==========================================
# CONFIG
# ==========================================

API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "Proposer": "openai/gpt-4o-mini",
    "Challenger": "anthropic/claude-3-haiku",
    "Clarifier": "meta-llama/llama-3-8b-instruct",
    "Skeptic": "upstage/solar-pro-3:free",
    "Final": "qwen/qwen3-vl-30b-a3b-thinking"
}

# ==========================================
# API KEY AUTH
# ==========================================

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def validate_api_key(key):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 5
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        return response.status_code == 200
    except:
        return False


if not st.session_state.authenticated:

    st.set_page_config(page_title="LLM Council Login", layout="centered")
    st.title("🔐 Enter OpenRouter API Key")

    api_input = st.text_input("API Key", type="password")

    if st.button("Validate Key"):

        if not api_input.strip():
            st.error("Please enter an API key.")
        else:
            with st.spinner("Validating key..."):
                if validate_api_key(api_input):
                    st.session_state.api_key = api_input
                    st.session_state.authenticated = True
                    st.success("API Key validated successfully!")
                    st.rerun()
                else:
                    st.error("Invalid API key or insufficient permissions.")

    st.stop()

# ==========================================
# SAFETY HELPERS
# ==========================================

def safe_trim(text, max_chars):
    if not text:
        return ""
    return text[-max_chars:] if len(text) > max_chars else text


def safe_content(text):
    if not text or text.strip() == "":
        return "Model returned empty content."
    return text


# ==========================================
# UNIVERSAL MODEL CALL
# ==========================================

def call_model(model, messages, max_tokens=700):

    try:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {st.session_state.api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            return None, f"{model} failed ({response.status_code})"

        data = response.json()

        if "choices" not in data or not data["choices"]:
            return None, f"{model} returned empty response"

        content = data["choices"][0]["message"]["content"]
        content = safe_content(content)

        return content, None

    except Exception as e:
        return None, str(e)


# ==========================================
# COUNCIL LOGIC
# ==========================================

def run_council(user_prompt):

    results = {}

    proposer_prompt = f"Answer clearly and thoroughly:\n\n{user_prompt}"
    response, error = call_model(
        MODELS["Proposer"],
        [{"role": "user", "content": proposer_prompt}],
        max_tokens=900
    )
    results["Proposer"] = response or error

    challenger_prompt = f"Critically challenge this answer:\n\n{safe_trim(results['Proposer'], 6000)}"
    response, error = call_model(
        MODELS["Challenger"],
        [{"role": "user", "content": challenger_prompt}],
        max_tokens=800
    )
    results["Challenger"] = response or error

    clarifier_input = f"""
Resolve contradictions and clarify:

Proposer:
{safe_trim(results['Proposer'], 4000)}

Challenger:
{safe_trim(results['Challenger'], 4000)}
"""
    response, error = call_model(
        MODELS["Clarifier"],
        [{"role": "user", "content": clarifier_input}],
        max_tokens=800
    )
    results["Clarifier"] = response or error

    skeptic_prompt = f"""
Find weaknesses or hidden assumptions in:

{safe_trim(results['Clarifier'], 3000)}
"""
    response, error = call_model(
        MODELS["Skeptic"],
        [{"role": "user", "content": skeptic_prompt}],
        max_tokens=1000
    )
    results["Skeptic"] = response or error

    final_prompt = f"""
Create the best possible final answer using all discussion below.

Proposer:
{safe_trim(results['Proposer'], 3000)}

Challenger:
{safe_trim(results['Challenger'], 3000)}

Clarifier:
{safe_trim(results['Clarifier'], 3000)}

Skeptic:
{safe_trim(results['Skeptic'], 3000)}
"""
    response, error = call_model(
        MODELS["Final"],
        [{"role": "user", "content": final_prompt}],
        max_tokens=5000
    )
    results["Final"] = response or error

    return results


# ==========================================
# PRO CHAT UI
# ==========================================

# ==========================================
# PRO CHAT UI (FIXED USER DISPLAY)
# ==========================================

st.set_page_config(page_title="LLM Council", layout="centered")

st.markdown("""
<style>
.user-bubble {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 14px 18px;
    border-radius: 18px;
    color: #ffffff;
    margin-bottom: 10px;
}

.assistant-bubble {
    background: #1f2937;
    padding: 16px 20px;
    border-radius: 18px;
    margin-bottom: 10px;
    color: #f1f5f9;
    line-height: 1.6;
}

.role-title {
    font-weight: 600;
    margin-top: 10px;
    color: #60a5fa;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 LLM Council")

# Initialize history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages FIRST
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
        st.markdown(f"<div class='{bubble_class}'>{message['content']}</div>", unsafe_allow_html=True)

        if message.get("debate"):
            with st.expander("View Council Debate"):
                for role, text in message["debate"].items():
                    st.markdown(f"<div class='role-title'>{role}</div>", unsafe_allow_html=True)
                    st.write(text)
                    st.divider()

# Chat input
user_input = st.chat_input("Ask the Council something...")

if user_input:

    # 1️⃣ Immediately show user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)

    # Save user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # 2️⃣ Generate assistant response
    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner("Council debating..."):
            results = run_council(user_input)

        final_answer = results.get("Final", "No response")

        # Typing animation
        placeholder = st.empty()
        typed = ""

        for char in final_answer:
            typed += char
            placeholder.markdown(
                f"<div class='assistant-bubble'>{typed}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.002)

        # Debate dropdown
        with st.expander("View Council Debate"):
            for role in ["Proposer", "Challenger", "Clarifier", "Skeptic"]:
                st.markdown(f"<div class='role-title'>{role}</div>", unsafe_allow_html=True)
                st.write(results.get(role))
                st.divider()

    # Save assistant message
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": final_answer,
        "debate": {
            "Proposer": results.get("Proposer"),
            "Challenger": results.get("Challenger"),
            "Clarifier": results.get("Clarifier"),
            "Skeptic": results.get("Skeptic"),
        }
    })