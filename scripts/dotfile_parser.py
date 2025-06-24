import magic 
from pathlib import Path
import shutil
import re
import json 

# Purpose: Walk dotfiles and parse contents to json for each fiel
# Requirements: fetch metadata {language, path, dpendencies, content, purpose}
# Json structure
# {
#   "repo_name": "example-dotfiles",
#   "structure": {
#     "sketchybarrc": {
#       "path": "sketchybarrc",
#       "language": "bash",
#       "dependencies": ["plugins/clock.sh", "plugins/spotify.sh"],
#       "content": "..." 
#       "content_summary": "...",
#       "purpose": ""  <-- AI will fill this
#     },
#     "plugins/clock.sh": {
#       "path": "plugins/clock.sh",
#       "language": "bash",
#       "dependencies": [],
#       "content_summary": "...",
#       "purpose": ""
#     },
#     ...
#   }
# }
# Algorithm:
#     1.) walk all files within the src directlory : pathlib.rglob("*")
#     2.) create JSON template 
#     2.) access the files with read method
#     3.) fetch deetails

SOURCE_RE = re.compile(r'(?:source|\.)\s+(.*)')
SET_SCRIPT_RE = re.compile(r'sketchybar\s+.*script=([^\s]+)')
REQUIRE_RE = re.compile(r'require\s*[("\']([^"\']+)["\')]')

def detect_language(file_path):
    try:
        mime = magic.MimeTypes(mime=True) # type: ignore
        mime_type = mime.from_file(str(file_path))

        if "shellscript" in mime_type:
            return "bash"
        elif "lua" in mime_type:
            return "lua"
        elif "yaml" in mime_type:
            return "yaml"
        elif "python" in mime_type:
            return "python"
        else:
            # If unknown — fall back to extension
            return detect_language_from_extension(file_path)

    except Exception as e:
        # If magic fails — fall back to extension
        return detect_language_from_extension(file_path)

def detect_language_from_extension(file_path):
    ext = file_path.suffix.lower()

    if ext in [".sh", ".bash"]:
        return "bash"
    elif ext == ".lua":
        return "lua"
    elif ext in [".yaml", ".yml"]:
        return "yaml"
    elif ext == ".py":
        return "python"
    elif file_path.name == "sketchybarrc":
        return "bash"  # Sketchybarrc is bash but no extension
    else:
        return "unknown"
    

def detect_dependencies(content, language):
    deps = []

    if language == "bash":
        deps += SOURCE_RE.findall(content)
        deps += SET_SCRIPT_RE.findall(content)

    elif language == "lua":
        deps += REQUIRE_RE.findall(content)

    return deps

def parse_repo(repo_path):
    repo_name = repo_path.name
    print(f"\n[📂] Parsing repo: {repo_name}")

    structure = {}

    for file_path in repo_path.rglob("*"):
        if file_path.is_file():
            try:
                content = file_path.read_text(errors="ignore")
                language = detect_language(file_path)
                dependencies = detect_dependencies(content, language)

                file_entry = {
                    "path": str(file_path.relative_to(repo_path)),
                    "language": language,
                    "dependencies": dependencies,
                    "content": content,
                    "purpose": "",  # to be added by AI pipeline
                    "content_summary": ""  # to be added by AI pipeline
                }

                structure[str(file_path.relative_to(repo_path))] = file_entry

                print(f"[+] Parsed: {file_entry['path']} ({language})")

            except Exception as e:
                print(f"[!] Error parsing {file_path}: {e}")

    # Save as JSON
    out_path = Path("/Users/krishiv/Desktop/Projects/config-assistant/data/configs")
    out_path.mkdir(parents=True, exist_ok=True)
    out_file = out_path / f"{repo_name}.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "repo_name": repo_name,
            "structure": structure
        }, f, indent=2)

    print(f"[✅] Saved parsed JSON to: {out_file}")

# -------- Entry point --------

def main():
    base_path = Path("/Users/krishiv/Desktop/Projects/config-assistant/store/community_configs")

    for repo_dir in base_path.iterdir():
        if repo_dir.is_dir():
            parse_repo(repo_dir)

if __name__ == "__main__":
    main()
