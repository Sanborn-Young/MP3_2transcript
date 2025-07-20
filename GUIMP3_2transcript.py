#!/usr/bin/env python3

import os
import sys
import threading
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from dotenv import load_dotenv
import replicate
import re

def load_token():
    # Try multiple locations for .env file
    possible_paths = [
        Path(__file__).parent / '.env',  # Original location (same dir as script)
        Path.cwd() / '.env',             # Current working directory
        Path.home() / '.env',            # User home directory
    ]
    
    env_path = None
    for path in possible_paths:
        if path.exists():
            env_path = path
            break
    
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()  # Let python-dotenv search default locations
    
    token = os.getenv('REPLICATE_API_TOKEN')
    if not token:
        messagebox.showerror("Error", "REPLICATE_API_TOKEN not found in .env")
        sys.exit(1)
    return token


def seconds_to_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02}:{s:02}"
    return f"{m:02}:{s:02}"

def convert_json_to_transcript(json_path):
    """
    Read JSON at json_path, build a speaker-segmented transcript with 5-min timers.
    Returns the transcript text (without saving to file yet).
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Support both possible output locations
    segments = None
    if isinstance(data.get("output"), dict) and "segments" in data["output"]:
        segments = data["output"]["segments"]
    elif "segments" in data:
        segments = data["segments"]
    
    transcript_text = ""
    
    if segments:
        # Find first start time
        earliest = min(
            (seg.get("start", 0) for seg in segments if seg.get("start") is not None),
            default=0
        )
        
        next_timer = (int(earliest) // 300) * 300
        segments = sorted(segments, key=lambda s: s.get("start", 0))
        
        current_speaker = None
        current_text = ""
        
        for seg in segments:
            start = seg.get("start", 0)
            text = seg.get("text", "").strip()
            speaker = seg.get("speaker", "UNKNOWN")
            
            # Insert timer markers
            while start >= next_timer:
                if current_text:
                    transcript_text += f"Speaker {current_speaker}: {current_text.strip()}\n\n"
                    current_text = ""
                transcript_text += f"\n--- [TIMER: {seconds_to_timestamp(next_timer)}] ---\n\n"
                next_timer += 300
            
            # Handle speaker change
            if speaker != current_speaker:
                if current_text:
                    transcript_text += f"Speaker {current_speaker}: {current_text.strip()}\n\n"
                    current_text = ""
                current_speaker = speaker
            
            if text:
                current_text += text + " "
        
        if current_text:
            transcript_text += f"Speaker {current_speaker}: {current_text.strip()}\n"
    else:
        # No diarization segments found → simple notice
        transcript_text = "[No speaker segments found in JSON]\n"
    
    return transcript_text

def extract_speakers(content):
    """Extract unique speaker variables from the transcript content."""
    speakers = set()
    matches = re.findall(r'Speaker (SPEAKER_\d+)', content)
    speakers.update(matches)
    return sorted(list(speakers))

def get_replacements(speakers):
    """Create a dialog to get new names for each speaker, using a dedicated root."""
    dialog_root = tk.Tk()
    dialog_root.withdraw()  # Hide the dialog root
    
    replacements = {}
    for speaker in speakers:
        new_name = simpledialog.askstring("Rename Speaker", f"Enter new name for {speaker} (leave blank to keep original):", parent=dialog_root)
        if new_name:  # Only replace if a new name is provided
            replacements[speaker] = new_name
    
    dialog_root.destroy()
    return replacements

def replace_in_content(content, replacements):
    """Replace entire 'Speaker SPEAKER_XX' with '**NewName**' in the content."""
    for old, new in replacements.items():
        full_old = f"Speaker {old}"
        markdown_new = f"**{new}**"
        content = content.replace(full_old, markdown_new)
    return content

def add_speaker_separation(content, replacements):
    """Insert a newline before each bold speaker name for separation."""
    if not replacements:
        return content
    
    # Get all possible markdown names
    markdown_names = [f"**{new}**" for new in replacements.values()]
    
    lines = content.splitlines()
    separated_lines = []
    
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(name) for name in markdown_names):
            separated_lines.append('')  # Add empty line for separation
        separated_lines.append(line)
    
    return '\n'.join(separated_lines)

def get_speaker_count(parent):
    """Get the number of speakers from user input."""
    while True:
        count_str = simpledialog.askstring(
            "Speaker Count", 
            "How many speakers are in this audio file?\n(Enter a number between 1-10, or leave blank for auto-detection):",
            parent=parent
        )
        
        if count_str is None:  # User cancelled
            return None
        
        if count_str.strip() == "":  # Auto-detection
            return None
        
        try:
            count = int(count_str)
            if 1 <= count <= 10:
                return count
            else:
                messagebox.showwarning("Invalid Input", "Please enter a number between 1 and 10.", parent=parent)
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number.", parent=parent)

def transcribe(mp3_path, speaker_count, status_var, status_win, root):
    status_var.set("Uploading…")
    token = load_token()
    client = replicate.Client(api_token=token)
    
    model = client.models.get("thomasmol/whisper-diarization")
    version = model.versions.list()[0].id
    
    try:
        status_var.set("Transcribing…")
        with open(mp3_path, "rb") as f:
            # Prepare input parameters
            input_params = {"file": f}
            
            # Add num_speakers if specified
            if speaker_count is not None:
                input_params["num_speakers"] = speaker_count
                status_var.set(f"Transcribing with {speaker_count} speakers…")
            
            output = replicate.run(
                f"thomasmol/whisper-diarization:{version}",
                input=input_params
            )
    
    except Exception as e:
        messagebox.showerror("Error", f"Transcription failed:\n{e}", parent=status_win)
        status_win.destroy()
        return

    # Save JSON
    json_path = Path(mp3_path).with_suffix('.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as jf:
            jf.write(json.dumps(output, ensure_ascii=False, indent=2))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save JSON:\n{e}", parent=status_win)
        status_win.destroy()
        return

    status_var.set(f"Saved JSON: {json_path.name}")

    # Prompt for Markdown conversion
    if messagebox.askyesno("Convert to Markdown?", "Would you like to create a .md transcript with speaker renaming?", parent=status_win):
        try:
            # Generate base transcript from JSON
            transcript_content = convert_json_to_transcript(str(json_path))

            # Ask if user wants to rename speakers
            rename = messagebox.askyesno("Rename Speakers", "Do you want to turn speaker variables into names?", parent=status_win)

            if rename:
                speakers = extract_speakers(transcript_content)
                if not speakers:
                    messagebox.showinfo("Info", "No speakers found in the transcript.", parent=status_win)
                else:
                    replacements = get_replacements(speakers)
                    if replacements:
                        transcript_content = replace_in_content(transcript_content, replacements)
                        transcript_content = add_speaker_separation(transcript_content, replacements)

            # Save to .md file
            base = Path(mp3_path).stem
            md_path = Path(mp3_path).with_name(f"{base}.md")
            with open(md_path, 'w', encoding='utf-8') as out:
                out.write(transcript_content)

            messagebox.showinfo("Done", f"Transcript saved to: {md_path.name}", parent=status_win)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert to Markdown:\n{e}", parent=status_win)

    # Short delay to view final status
    status_win.after(1000, lambda: prompt_next(status_win, root))

def prompt_next(status_win, root):
    process_another = messagebox.askyesno("Process Another?", "Would you like to process another file?", parent=status_win)
    status_win.destroy()
    if process_another:
        main(root)  # Restart with existing root to avoid recursion depth issues
    else:
        # FIXED: Properly exit when user chooses not to process another file
        root.quit()
        root.destroy()

def main(existing_root=None):
    if existing_root is None:
        root = tk.Tk()
        root.withdraw()
    else:
        root = existing_root

    mp3_file = filedialog.askopenfilename(
        title="Select an MP3 file",
        filetypes=[("MP3 Files", "*.mp3")],
        parent=root
    )

    if not mp3_file:
        if existing_root is None:
            root.quit()
            root.destroy()
        return  # CHANGED: return instead of sys.exit for cleaner handling

    if not os.path.isfile(mp3_file):
        messagebox.showerror("Error", f"File not found: {mp3_file}", parent=root)
        if existing_root is None:
            root.quit()
            root.destroy()
        return  # CHANGED: return instead of sys.exit

    # NEW: Get speaker count after file selection
    speaker_count = get_speaker_count(root)
    
    # If user cancelled speaker count dialog, exit gracefully
    if speaker_count is None and messagebox.askokcancel("Cancel", "No speaker count specified. Continue with auto-detection?", parent=root) is False:
        if existing_root is None:
            root.quit()
            root.destroy()
        return

    # Create status window
    status_win = tk.Toplevel(root)
    status_win.title("MP3 to Transcript")
    status_var = tk.StringVar(value="Starting…")
    ttk.Label(status_win, textvariable=status_var, padding=10).pack()

    # Start transcription with speaker count
    threading.Thread(
        target=transcribe,
        args=(mp3_file, speaker_count, status_var, status_win, root),
        daemon=True
    ).start()

    status_win.mainloop()

if __name__ == "__main__":
    main()
