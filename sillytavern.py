import os
import re
import json
import zlib
import base64
import struct

def extract_chara_metadata(png_path):
    with open(png_path, 'rb') as f:
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file.")
        while True:
            length_bytes = f.read(4)
            if len(length_bytes) < 4:
                break
            length = struct.unpack(">I", length_bytes)[0]
            chunk_type = f.read(4)
            chunk_data = f.read(length)
            f.read(4)
            if chunk_type == b'tEXt':
                keyword, _, text = chunk_data.partition(b'\x00')
                if keyword.decode('utf-8') == 'chara':
                    return base64.b64decode(text).decode('utf-8')
            elif chunk_type == b'zTXt':
                keyword, rest = chunk_data.split(b'\x00', 1)
                if keyword.decode('utf-8') == 'chara':
                    compression_method = rest[0]
                    if compression_method == 0:
                        compressed_text = rest[1:]
                        decompressed = zlib.decompress(compressed_text)
                        return base64.b64decode(decompressed).decode('utf-8')
    return None

def process_character_metadata(chara_json, user_name):
    """
    Processes the character metadata and returns the character object and prompts.
    """
    try:
        # Replace {{user}} with the user's name, case-insensitive
        chara_json_processed = re.sub(r'\{\{user\}\}', user_name, chara_json, flags=re.IGNORECASE)
        chara_obj = json.loads(chara_json_processed)
        
        # Simplified processing based on the provided example
        talk_prompt = chara_obj.get("talk_prompt", "")
        depth_prompt = chara_obj.get("depth_prompt", "")
        return chara_obj, talk_prompt, depth_prompt
    except json.JSONDecodeError as e:
        print(f"Error decoding character JSON: {e}")
    return None, None, None
