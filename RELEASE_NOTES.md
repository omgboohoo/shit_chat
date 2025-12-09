# Release Notes

## v0.1.0 (Initial Release)

### Core Features
*   **Local AI Chat**: Fully private, local chat functionality using `llama.cpp`.
*   **Automatic Model Management**: Automatically detects models in the `models/` folder. If none are found, downloads a high-quality default model (`L3-8B-Stheno-v3.2`).
*   **SillyTavern Support**: Full support for `.png` character cards. Drag and drop a card into the terminal to instantly load a new persona.
*   **Persistent Context**: Smart context management that preserves the system prompt while rolling the conversation history to fit the model's window.

### Interface
*   **CLI Interface**: Clean, color-coded terminal interface with distinct colors for User, AI, and narrative actions (text in *asterisks*).
*   **Linux Native**: Optimized specifically for Linux environments.
*   **Performance Counters**: Real-time "Tokens per Second" (TPS) and context usage percentage displayed in the window title.

### Slash Commands
*   `/c` - Clear chat history.
*   `/i` - Inspect current character metadata.
*   `/s` - Select a character card from the library.
*   `/r` - Rewind conversation one step.
*   `/m` - Switch models or change context size.
*   `/p` - Toggle detailed performance stats.

### Technical
*   **Custom Wheels**: Includes a pre-compiled `llama-cpp-python` wheel with CUDA support for Linux, enabling GPU acceleration out of the box.
*   **Easy Launcher**: Includes `run.sh` for one-click setup and execution.
