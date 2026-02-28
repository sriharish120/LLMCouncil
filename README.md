# LLM Council

This project implements an "LLM Council" using Streamlit and the OpenRouter API. It creates a chat interface where a user's prompt is debated by multiple LLMs, each playing a specific role (Proposer, Challenger, Clarifier, Skeptic), before a final answer is synthesized.

## Features

- **Multi-LLM Debate System:** Utilizes different LLMs for distinct roles to generate a comprehensive and critically examined response.
- **Streamlit UI:** Provides an interactive and user-friendly web interface for chat.
- **OpenRouter API Integration:** Connects to various LLMs via the OpenRouter platform.
- **API Key Authentication:** Securely handles API key input for OpenRouter.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/LLMCouncil.git
    cd LLMCouncil
    ```
    (Note: Replace `https://github.com/your-username/LLMCouncil.git` with the actual repository URL if it's hosted.)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .env
    ```

3.  **Activate the virtual environment:**
    -   **Windows:**
        ```bash
        .env\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source .env/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Live Demo

You can access the hosted version of the LLM Council application here: [https://llmcouncil-main.streamlit.app/](https://llmcouncil-main.streamlit.app/)
Note: You will need an OpenRouter API key to use the live demo.

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run test.py
    ```

2.  **Enter your OpenRouter API Key:**
    When the application launches in your browser, you will be prompted to enter your OpenRouter API key to authenticate.

3.  **Start Chatting:**
    Once authenticated, you can ask the LLM Council questions and observe their debate process to arrive at a final answer.

## Project Structure

-   `test.py`: The main Streamlit application script containing the LLM Council logic and UI.
-   `requirements.txt`: Lists the Python dependencies required for the project.
-   `README.md`: This file, providing an overview and instructions.

## Contributing

(Add contributing guidelines here if applicable)

## License

(Add license information here if applicable)
