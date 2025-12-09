# ShitChat v0.1.0

ShitChat is a simple, local chat application powered by `llama.cpp` that allows users to interact with AI characters. Features out-of-the-box NVIDIA CUDA acceleration for optimal performance on compatible GPUs.

## Features

*   **NVIDIA CUDA Acceleration:** Out-of-the-box GPU acceleration for NVIDIA graphics cards, automatically compiled and configured during setup.
*   **Automatic Model Download:** If no models are found in the `models` folder, the application will automatically download a default model to get you started.
*   **Multiple Model Support:** Choose from any `.gguf` model placed in the `models` folder.
*   **Character Card Integration:** Load custom characters by dragging and dropping SillyTavern `.png` character cards into the console.
*   **Interactive Chat:** A straightforward command-line interface for chatting with the AI.
*   **Rewind Capability:** Made a mistake? Use `/r` to rewind the conversation one step.
*   **Context Management:** Automatically truncates conversation history to stay within the model's context window.
*   **Performance Metrics:** Displays tokens per second and context usage percentage in the console title. Toggle detailed stats with `/p`.

## Installation

### Linux
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/omgboohoo/shit_chat.git
    cd shit_chat
    ```
2.  **Run the launcher:**
    ```bash
    chmod +x run.sh
    ./run.sh
    ```
    The `run.sh` script will automatically create a virtual environment, install dependencies, and even compile the necessary CUDA drivers for your GPU if needed.

### Windows
1.  **Clone the repository.**
2.  **Run the application** using the `run.bat` script. This will set up the environment and launch the app.

## Usage

1.  Run the application using `run.sh`.
2.  Select a model from the displayed list.
3.  Enter your name.
4.  You can now start chatting with the AI. To load a character, simply drag and drop a `.png` character card file onto the console - it will automatically submit to the AI and start the conversation.

## Commands

*   `/c`: Clears the current conversation history.
*   `/i`: Displays the metadata of the currently loaded character card.
*   `/s`: Load a character card from the `cards` folder.
*   `/r`: Rewind the chat one step (clears the last round of conversation).
*   `/m`: Load a new model or change the context window size.
*   `/p`: Toggle detailed performance counters in the AI response.
