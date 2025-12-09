import sys
import time

import os
import re
import json
import sys
import termios
import tty
import select
import gc
import requests
from tqdm import tqdm
from llama_cpp import Llama, llama_cpp
from colorama import init, Fore, Style
from sillytavern import extract_chara_metadata, process_character_metadata

def set_console_title(title):
    try:
        sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()
    except Exception:
        pass

init()
# Set console title
set_console_title("ShitChat")

def get_llama_cpp_version():
    """
    Finds the llama.cpp version from the .whl file in the llama.cpp folder.
    """
    try:
        files = os.listdir("llama.cpp")
        for f in files:
            if f.endswith(".whl"):
                match = re.search(r"llama_cpp_python-([\d.]+)-", f)
                if match:
                    return match.group(1)
    except FileNotFoundError:
        return None
    return None

llama_cpp_version = get_llama_cpp_version()
if llama_cpp_version:
    print(f"\nUsing llama.cpp v{llama_cpp_version}.\n")
base_title = "ShitChat"
__version__ = "0.1.0"

def download_model(url, file_path):
    """
    Downloads a file from a URL and displays a progress bar.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        total_size = int(response.headers.get('content-length', 0))
        
        with open(file_path, 'wb') as f, tqdm(
            desc=os.path.basename(file_path),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                bar.update(size)
        print(f"\nModel downloaded successfully to {file_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\nError downloading model: {e}")
        # Clean up partially downloaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        return False
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
        # Clean up partially downloaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        return False

def choose_model():
    """
    Prompts the user to choose a model from the models folder.
    If no models are found, downloads a default model.
    """
    model_dir = "models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    models = [f for f in os.listdir(model_dir) if f.endswith(".gguf")]
    if not models:
        print("No models found in the models folder.")
        print("Downloading default model: L3-8B-Stheno-v3.2-Q4_K_M.gguf")
        
        default_model_url = "https://huggingface.co/bartowski/L3-8B-Stheno-v3.2-GGUF/resolve/main/L3-8B-Stheno-v3.2-Q4_K_M.gguf"
        default_model_name = "L3-8B-Stheno-v3.2-Q4_K_M.gguf"
        model_path = os.path.join(model_dir, default_model_name)
        
        if not download_model(default_model_url, model_path):
            print("Failed to download the default model. Please check your internet connection or download a model manually.")
            return None
        
        # After download, re-scan the models directory
        models = [f for f in os.listdir(model_dir) if f.endswith(".gguf")]

    if not models:
        print("Still no models found after attempting to download. Exiting.")
        return None

    if len(models) == 1:
        return os.path.join(model_dir, models[0])
        
    print("Please choose a model:")
    print()
    for i, model in enumerate(models):
        print(f"{i + 1}: {model}")
        
    while True:
        try:
            print()
            choice_input = input("Enter the number of the model you want to use (press Enter for 1): ")
            if not choice_input.strip():
                choice = 1
            else:
                choice = int(choice_input)
            if 1 <= choice <= len(models):
                return os.path.join(model_dir, models[choice - 1])
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

def get_n_ctx():
    """
    Prompts the user to enter the context window size.
    """
    while True:
        try:
            #print()
            n_ctx_input = input("Enter context window size (n_ctx), press Enter for default (8192): ")
            if not n_ctx_input:
                return 8192
            n_ctx = int(n_ctx_input)
            if n_ctx > 0:
                return n_ctx
            else:
                print("Invalid input. Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def load_model():
    """
    Lets the user choose a model and context size, then loads the model.
    """
    model_path = choose_model()
    if not model_path:
        return None
    
    n_ctx = get_n_ctx()
    
    return Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_gpu_layers=-1,
        verbose=True,
        chat_format="llama-3",
    )

# Initialize the Llama model
llm = load_model()
if not llm:
    sys.exit()

# Set initial verbose setting (performance counters disabled by default)
llm.verbose = False

def choose_character():
    """
    Prompts the user to choose a character card from the cards folder.
    """
    card_dir = "cards"
    if not os.path.exists(card_dir):
        print("No 'cards' folder found.")
        return None

    cards = [f for f in os.listdir(card_dir) if f.endswith(".png")]
    if not cards:
        print("No character cards found in the 'cards' folder.")
        return None

    print("Please choose a character card:")
    print()
    for i, card in enumerate(cards):
        print(f"{i + 1}: {card}")
        
    while True:
        try:
            print()
            choice_input = input("Enter the number of the card you want to use (press Enter for 1): ")
            if not choice_input.strip():
                choice = 1
            else:
                choice = int(choice_input)
            if 1 <= choice <= len(cards):
                return os.path.join(card_dir, cards[choice - 1])
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

def truncate_context(messages, max_tokens):
    """
    Truncates the context to fit within the model's context window.
    Keeps the system message and recent conversation history.
    """
    if len(messages) <= 2:  # System + user message
        return messages
    
    # Always keep the system message
    system_message = messages[0]
    other_messages = messages[1:]
    
    # Calculate precise token count
    def count_tokens(text):
        if not text:
            return 0
        try:
            return len(llm.tokenize(text.encode('utf-8', errors='ignore'), add_bos=False))
        except Exception:
            return len(text) // 4

    # Calculate system message tokens
    system_tokens = count_tokens(system_message.get("content", ""))
    available_tokens = max_tokens - system_tokens - 100  # Leave some buffer
    
    # Keep recent messages that fit
    truncated_messages = [system_message]
    current_tokens = 0
    
    # Start from the most recent messages and work backwards
    for message in reversed(other_messages):
        message_tokens = count_tokens(message.get("content", ""))
        if current_tokens + message_tokens <= available_tokens:
            truncated_messages.insert(1, message)
            current_tokens += message_tokens
        else:
            break
    
    return truncated_messages


class NonBlockingRaw:
    """A context manager to enter raw terminal mode."""
    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

def check_interrupt():
    """
    Cross-platform function to check if interrupt was requested.
    Returns True if a key was pressed, False otherwise.
    """
    # Check if there's data available on stdin
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def chat():
    """
    Starts an interactive chat session with the user.
    """
    global llm
    show_perf_counters = False  # Performance counter toggle (default disabled)
    header_text = (
        "'/c' - Clear chat history\n"
        "'/i' - View character card details\n"
        "'/s' - Load a Sillytavern character card from cards folder (or drag drop)\n"
        "'/r' - Rewind chat one step\n"
        "'/m' - Load a new model and/or context size\n"
        "'/p' - Toggle detailed performance counters in AI reply\n"
        "'enter' - Force AI to continue\n"
        "'any key' - Interrupt AI response\n"
    )
    header_lines = header_text.count('\n') + 1
    last_known_size = (0, 0)

    def setup_screen():
        """Clears screen, prints header, and sets up scroll region."""
        nonlocal last_known_size
        os.system('clear')
        try:
            columns, rows = os.get_terminal_size()
            last_known_size = (columns, rows)
            # Use a white background for the header
            for line in header_text.split('\n'):
                print(f"\x1b[42m\x1b[30m{line.ljust(columns)}\x1b[0m")

            # Set scroll region
            # sys.stdout.write(f"\x1b[{header_lines + 1};{rows}r")
            # Move cursor to start of scroll region
            # sys.stdout.write(f"\x1b[{header_lines + 1};1H")
        except OSError:
            # os.get_terminal_size() can fail if not in a real terminal
            last_known_size = (80, 24) # Default size
            print(header_text)
            pass

    def update_header_and_scroll_region():
        """Updates header and scroll region without clearing screen."""
        try:
            columns, rows = os.get_terminal_size()
            
            # Save cursor position
            sys.stdout.write("\x1b[s")
            
            # Redraw header
            for i, line in enumerate(header_text.split('\n')):
                sys.stdout.write(f"\x1b[{i + 1};1H") # Move to line i+1, column 1
                sys.stdout.write(f"\x1b[42m\x1b[30m{line.ljust(columns)}\x1b[0m")
            
            # Update scroll region
            # sys.stdout.write(f"\x1b[{header_lines + 1};{rows}r")
            
            # Restore cursor position
            sys.stdout.write("\x1b[u")
            sys.stdout.flush()

        except OSError:
            pass

    def check_resize():
        nonlocal last_known_size
        try:
            current_size = os.get_terminal_size()
            if current_size != last_known_size:
                last_known_size = current_size
                update_header_and_scroll_region()
        except OSError:
            pass

    os.system('clear')
    os.system('clear')
    print(f"\nShitChat v{__version__} by Dan Bailey\n")
    user_name = input("Please enter your name (press Enter for Dan): ")
    if not user_name.strip():
        user_name = "Dan"
    
    setup_screen()
    print(f"\nWelcome, {user_name}!")
    messages = []
    first_prompt = True
    current_character = None
    
    def load_character(card_path, user_name):
        chara_json = extract_chara_metadata(card_path)
        if not chara_json:
            print("No 'chara' metadata found in PNG.")
            return None, None

        chara_obj, talk_prompt, depth_prompt = process_character_metadata(chara_json, user_name)
        if not chara_obj:
            print("Failed to process character metadata.")
            return None, None

        setup_screen()
        print(f"\nSillyTavern PNG Character Card Loaded. Waiting for AI Response...")

        data_section = chara_obj.get('data', chara_obj)
        modified_data_json_string = json.dumps(data_section)
        system_prompt = f"{talk_prompt}{depth_prompt}roleplay the following scene defined in the json. do not break from your character\\n{modified_data_json_string}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ""}
        ]
        return messages, chara_obj

    while True:
        check_resize()
        # Add a blank line for spacing after AI response (only if performance counters disabled)
        if not show_perf_counters:
            print()
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip().strip('"')
        
        should_continue = False

        # Handle PNG drag and drop
        if user_input.lower().endswith(".png") and os.path.exists(user_input):
            new_messages, new_character = load_character(user_input, user_name)
            if new_messages:
                messages = new_messages
                current_character = new_character
                should_continue = True
        
        elif user_input.lower() == '/c':
            messages = []
            setup_screen()
            print(f"\nWelcome, {user_name}!")
            continue

        elif user_input.lower() == '/s':
            card_path = choose_character()
            if card_path:
                new_messages, new_character = load_character(card_path, user_name)
                if new_messages:
                    messages = new_messages
                    current_character = new_character
                    should_continue = True
            if not should_continue:
                continue

        elif user_input.lower() == '/i':
            if current_character:
                print(json.dumps(current_character, indent=2))
            else:
                print("No character card is currently loaded.")
            continue

        elif user_input.lower() == '/m':
            print("\nLoading new model...")
            
            # Free the backend and unload the old model
            llama_cpp.llama_backend_free()
            del llm
            gc.collect()

            # Re-initialize the backend
            llama_cpp.llama_backend_init()

            new_llm = load_model()
            if new_llm:
                llm = new_llm
                llm.verbose = show_perf_counters  # Apply current performance counter setting
                print("New model loaded successfully.")
                setup_screen()
            else:
                print("Failed to load new model. The application will now exit.")
                sys.exit()
            continue

        elif user_input.lower() == '/r':
            if len(messages) >= 2:
                messages = messages[:-2]
                setup_screen()
                print("\nRewound one step.")
                # Reprint the conversation history
                for i, msg in enumerate(messages):
                    if msg['role'] == 'system':
                        continue
                    
                    if msg['role'] == 'user':
                        print(f"\n{Fore.GREEN}You: {Style.RESET_ALL}{msg['content']}")
                    elif msg['role'] == 'assistant':
                        print(f"\n{Fore.CYAN}AI: {Style.RESET_ALL}", end="")
                        content = msg['content']
                        in_yellow_block = False
                        for char in content:
                            if char == '*':
                                in_yellow_block = not in_yellow_block
                                print(f"{Fore.YELLOW}{char}{Style.RESET_ALL}", end="")
                            else:
                                if in_yellow_block:
                                    print(f"{Fore.YELLOW}{char}{Style.RESET_ALL}", end="")
                                else:
                                    print(char, end="")
                        print() # ensure newline after message

            else:
                print(f"\nNot enough history to rewind.")
            continue

        elif user_input.lower() == '/p':
            show_perf_counters = not show_perf_counters
            llm.verbose = show_perf_counters
            status = "enabled" if show_perf_counters else "disabled"
            print(f"\nPerformance counters {status}.")
            if show_perf_counters:
                print()
                print("Performance counter parameters explained:")
                print("• prompt eval time = Time to process input prompt (tokens/sec)")
                print("• eval time = Time to generate response (tokens/sec)")
                print("• total time = Total processing time")
                print("• graphs reused = Number of computation graphs reused for efficiency")
                print("• prefix-match hit = Number of tokens matched from previous context")
                print()
            continue

        if should_continue or not user_input.strip():
            # Overwrite the "You: " prompt line from input()
            print(f"\x1b[1A\x1b[2K{Fore.GREEN}You: {Style.RESET_ALL}continue")
            user_input = "continue"
        
        # Add a blank line for spacing before AI response
        print()

        if first_prompt:
            llm.verbose = False
            first_prompt = False
        
        # Only append user message if it's not a PNG file path
        if not (user_input.lower().endswith(".png") and os.path.exists(user_input)):
            messages.append({"role": "user", "content": user_input})
        
        # Truncate context if it's getting too long
        messages = truncate_context(messages, llm.n_ctx() - 500) # Leave a buffer
        
        start_time = time.time()
        try:
            stream = llm.create_chat_completion(
                messages=messages,
                stream=True,
            )
        except ValueError as e:
            if "exceed context window" in str(e):
                print(f"{Fore.RED}Context window exceeded. Truncating conversation history...{Style.RESET_ALL}")
                # More aggressive truncation
                messages = truncate_context(messages, llm.n_ctx() // 2)
                try:
                    stream = llm.create_chat_completion(
                        messages=messages,
                        stream=True,
                    )
                except ValueError as e2:
                    print(f"{Fore.RED}Error: {e2}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Please use '/clear' to reset the conversation.{Style.RESET_ALL}")
                    continue
            else:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                continue
        
        assistant_response = ""
        token_count = 0
        in_yellow_block = False
        print(f"{Fore.CYAN}AI: {Style.RESET_ALL}", end="")
        sys.stdout.flush()

        if llm:
            base_total_tokens = sum(len(llm.tokenize(m.get("content", "").encode('utf-8', errors='ignore'), add_bos=False)) for m in messages)
        else:
            base_total_tokens = sum(len(m.get("content", "")) // 4 for m in messages)
            
        max_tokens = llm.n_ctx()
        
        was_interrupted = False
        # Use a context manager to handle terminal mode safely
        with NonBlockingRaw():
            for output in stream:
                if check_interrupt():
                    # Consume the character from the buffer to prevent it from affecting the next input()
                    sys.stdin.read(1)   # Consume on Linux
                    
                    print(f"\n{Fore.YELLOW}[Interrupted]{Style.RESET_ALL}")
                    was_interrupted = True
                    break
                text = output["choices"][0]["delta"].get("content")
                if text:
                    assistant_response += text
                    token_count += 1
                    for char in text:
                        if char == '*':
                            in_yellow_block = not in_yellow_block
                        else:
                            if in_yellow_block:
                                print(f"{Fore.YELLOW}{char}{Style.RESET_ALL}", end="")
                            else:
                                print(char, end="")
                    sys.stdout.flush()
                    
                    # Real-time stats update for console title
                    duration = time.time() - start_time
                    tokens_per_second = token_count / duration if duration > 0 else 0
                    
                    # Calculate current total tokens accurately
                    current_response_tokens = len(llm.tokenize(assistant_response.encode('utf-8', errors='ignore'), add_bos=False))
                    total_tokens = base_total_tokens + current_response_tokens
                    context_percent = (total_tokens / max_tokens) * 100 if max_tokens > 0 else 0
                    
                    # Update console title
                    set_console_title(f"tps: {tokens_per_second:.2f} - ctx: {context_percent:.2f}%")
        
        if not was_interrupted:
            print()
        
        messages.append({"role": "assistant", "content": assistant_response})
        
        
        # Final update after loop finishes
        end_time = time.time()
        duration = end_time - start_time
        tokens_per_second = token_count / duration if duration > 0 else 0
        
        # Recalculate context usage accurately
        total_tokens = sum(len(llm.tokenize(m.get("content", "").encode('utf-8', errors='ignore'), add_bos=False)) for m in messages)
        context_percent = (total_tokens / max_tokens) * 100 if max_tokens > 0 else 0
        
        # Update console title
        set_console_title(f"tps: {tokens_per_second:.2f} - ctx: {context_percent:.2f}%")
        

if __name__ == "__main__":
    chat()
