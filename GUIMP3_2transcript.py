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
    """
    Load the REPLICATE_API_TOKEN from a .env file in the current working directory.
    If the file or token is not found, it shows an error and exits.
    """
    if not load_dotenv():
        messagebox.showerror(
            "Configuration Error",
            "Could not find the .env file.\n\nPlease make sure a .env file with your "
            "REPLICATE_API_TOKEN is present in the directory where you are running the command."
        )
        sys.exit(1)

    token = os.getenv('REPLICATE_API_TOKEN')
    if not token:
        messagebox.showerror(
            "Configuration Error",
            "REPLICATE_API_TOKEN not found in the loaded .env file."
        )
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

    segments = data.get("segments")
    if isinstance(data.get("output"), dict):
        segments = data["output"].get("segments")

    transcript_text = ""
    if segments:
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

            while start >= next_timer:
                if current_text:
                    transcript_text += f"Speaker {current_speaker}: {current_text.strip()}\n\n"
                    current_text = ""
                transcript_text += f"\n--- [TIMER: {seconds_to_timestamp(next_timer)}] ---\n\n"
                next_timer += 300

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
        transcript_text = "[No speaker segments found in JSON]\n"

    return transcript_text

def extract_speakers(content):
    speakers = set(re.findall(r'Speaker (SPEAKER_\d+)', content))
    return sorted(list(speakers))

def get_replacements(speakers, parent):
    replacements = {}
    for speaker in speakers:
        new_name = simpledialog.askstring(
            "Rename Speaker", 
            f"Enter new name for {speaker} (leave blank to keep original):", 
            parent=parent
        )
        if new_name:
            replacements[speaker] = new_name
    return replacements

def replace_in_content(content, replacements):
    for old, new in replacements.items():
        content = content.replace(f"Speaker {old}", f"**{new}**")
    return content

def add_speaker_separation(content, replacements):
    if not replacements:
        return content

    markdown_names = {f"**{new}**" for new in replacements.values()}
    lines = content.splitlines()
    separated_lines = []
    
    for line in lines:
        if any(line.strip().startswith(name) for name in markdown_names):
            if separated_lines and separated_lines[-1].strip() != '':
                separated_lines.append('')
        separated_lines.append(line)

    return '\n'.join(separated_lines)

def get_speaker_count(parent):
    while True:
        count_str = simpledialog.askstring(
            "Speaker Count",
            "How many speakers are in this audio file?\n(Enter a number between 1-10, or leave blank for auto-detection):",
            parent=parent
        )
        if count_str is None or count_str.strip() == "":
            return None
        try:
            count = int(count_str)
            if 1 <= count <= 10:
                return count
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
            input_params = {"file": f}
            if speaker_count is not None:
                input_params["num_speakers"] = speaker_count
                status_var.set(f"Transcribing with {speaker_count} speakers…")
            else:
                status_var.set("Transcribing with auto-detected speakers…")

            output = replicate.run(
                f"thomasmol/whisper-diarization:{version}",
                input=input_params
            )
    except Exception as e:
        messagebox.showerror("Error", f"Transcription failed:\n{e}", parent=status_win)
        status_win.destroy()
        return

    json_path = Path(mp3_path).with_suffix('.json')
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump(output, jf, ensure_ascii=False, indent=2)
    status_var.set(f"Saved JSON: {json_path.name}")
    
    if messagebox.askyesno("Convert to Markdown?", "Would you like to create a .md transcript with speaker renaming?", parent=status_win):
        transcript_content = convert_json_to_transcript(str(json_path))
        if messagebox.askyesno("Rename Speakers", "Do you want to turn speaker variables into names?", parent=status_win):
            speakers = extract_speakers(transcript_content)
            if speakers:
                replacements = get_replacements(speakers, status_win)
                if replacements:
                    transcript_content = replace_in_content(transcript_content, replacements)
                    transcript_content = add_speaker_separation(transcript_content, replacements)
            else:
                messagebox.showinfo("Info", "No speakers found to rename.", parent=status_win)
        
        md_path = Path(mp3_path).with_suffix('.md')
        with open(md_path, 'w', encoding='utf-8') as out:
            out.write(transcript_content)
        messagebox.showinfo("Done", f"Transcript saved to: {md_path.name}", parent=status_win)

    status_win.after(1000, lambda: prompt_next(status_win, root))

def prompt_next(status_win, root):
    if messagebox.askyesno("Process Another?", "Would you like to process another file?", parent=status_win):
        status_win.destroy()
        main(root)
    else:
        status_win.destroy()
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
            root.destroy()
        return

    speaker_count = get_speaker_count(root)
    
    status_win = tk.Toplevel(root)
    status_win.title("MP3 to Transcript")
    status_var = tk.StringVar(value="Starting…")
    ttk.Label(status_win, textvariable=status_var, padding=10).pack()

    threading.Thread(
        target=transcribe,
        args=(mp3_file, speaker_count, status_var, status_win, root),
        daemon=True
    ).start()
    
    status_win.mainloop()

if __name__ == "__main__":
    main()
