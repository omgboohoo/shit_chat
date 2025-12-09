# Product Requirements Document: ShitChat v0.1.0

## 1. Introduction

### 1.1. Purpose
This document defines the product requirements for the ShitChat application, a local AI chat client.

### 1.2. Scope
This document covers the core features of the application, including model loading, character integration, the chat interface, and performance monitoring.

## 2. User Persona

The target user for ShitChat is someone who:
*   Is interested in running local large language models (LLMs).
*   Engages in chat and roleplaying with AI.
*   Is comfortable using a command-line interface (CLI).
*   Uses character cards from platforms like SillyTavern.

## 3. Functional Requirements

### 3.1. Model Selection
*   The application must automatically detect `.gguf` model files located in the `/models` directory.
*   If no models are found, the application will automatically download a default model. A progress bar will be displayed during the download.
*   On startup, it must present the user with a numbered list of available models.
*   The user must be able to select a model by entering its corresponding number.

### 3.2. Character Loading
*   The application must support the loading of character data from SillyTavern `.png` character cards.
*   Character loading shall be initiated by the user dragging and dropping a `.png` file into the application's console window.
*   The application must extract the `chara` metadata from the PNG, parse it, and use it to construct the system prompt for the AI.

### 3.3. Chat Interface
*   The application will provide a CLI for user interaction.
*   User input will be prefixed with "You:".
*   AI responses will be prefixed with "AI:".
*   The application must support the following slash commands:
    *   `/c`: Clears the current conversation history.
    *   `/i`: Prints the JSON metadata of the currently loaded character.
    *   `/s`: Selects a character card from the `cards` folder.
    *   `/r`: Rewinds the conversation by removing the last user/AI exchange.
    *   `/m`: Allows the user to select a new model or adjust context size.
    *   `/p`: Toggles the display of performance statistics.

### 3.4. Context Management
*   The application must manage the conversation history to prevent it from exceeding the model's context window (`n_ctx`).
*   The context truncation strategy will always preserve the initial system message.
*   It will then include the most recent user and assistant messages that can fit within the remaining context window.

## 4. Non-Functional Requirements

### 4.1. Performance
*   The application must calculate and display the model's generation speed in tokens per second (Tokens/s).
*   The console title must be dynamically updated to show the current Tokens/s and the percentage of the context window being used.

### 4.2. Usability
*   The application should be simple to run, with a single script to handle setup and execution (`run.bat` for Windows, `run.sh` for Linux).
*   Clear instructions should be provided on startup and in the `README.md` file.

## 5. Future Enhancements

*   Development of a graphical user interface (GUI).
*   Support for additional character card formats.
*   Implementation of more sophisticated context management techniques (e.g., summarization).
*   Ability to save and load chat sessions.
