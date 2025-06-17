# Added import for os to support os.getenv
import os
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import subprocess
import shutil 
from urllib.parse import urlparse

GITHUB_API = "https://api.github.com/repos"
TARGET_REPO = Path( "/Users/krishiv/Desktop/Projects/config-assistant/scripts/temp" )
TARGET_REPO.mkdir(exist_ok=True)

GITHUB_REPO_PATTERN = re.compile(r"https://github\.com/[\w\-]+/[\w\-]+/?")

def fetch_links(url):
    res = requests.get(url)
    res.raise_for_status()
    content = BeautifulSoup(res.text, "html.parser")  

    REPOS = set()

    for a in content.find_all("a", href=True):
        href = a['href'] # type: ignore
        match = GITHUB_REPO_PATTERN.match(href) # type: ignore
        if match:
            cleaned = match.group().rstrip("/")
            REPOS.add(cleaned)
    
    print(f"[+] Passed {len(REPOS)} urls from {url}")
    return sorted(REPOS)

def convert_to_ssh(repo_url):
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    user, repo = parts[0], parts[1]
    return f"git@github.com:{user}/{repo}.git", user, repo 

def find_sketchybar_path(user, repo, branch="main"):
    url = f"{GITHUB_API}/{user}/{repo}/git/trees/{branch}?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=GITHUB_HEADERS)
    
    if resp.status_code == 404 and branch == "main":
        # fallback to master branch
        branch = "master"
        url = f"{GITHUB_API}/{user}/{repo}/git/trees/{branch}?recursive=1"
        resp = requests.get(url, headers=GITHUB_HEADERS)

    if resp.status_code != 200:
        print(f"[!] API error {resp.status_code} for {user}/{repo}")
        return None, None
    
    data = resp.json()
    for item in data.get("tree", []):
        path = item.get("path", "")
        if re.search(r"(?:^|/)(\.config/)?sketchybar/?$", path):
            return path, branch
    return None, branch

def sparse_checkout(repo_ssh, user, sketchybar_path, branch="main"):
    REPO_NAME = user
    REPO_PATH = TARGET_REPO/REPO_NAME
    if REPO_PATH.exists():
        return f"[!]{REPO_NAME} already exists at {REPO_PATH}. Skippiing."

    try:
        subprocess.run(["git", "init", str(REPO_PATH)], check=True)
        subprocess.run(["git", "-C", str(REPO_PATH), "remote", "add", "origin", repo_ssh], check=True)
        subprocess.run(["git", "-C", str(REPO_PATH), "sparse-checkout", "init", "--cone"], check=True)
        subprocess.run(["git", "-C", str(REPO_PATH), "sparse-checkout", "set", str(sketchybar_path)], check=True)
        subprocess.run(["git", "-C", str(REPO_PATH), "pull", "origin", branch], check=True)
                
        checked_path = REPO_PATH/ Path(sketchybar_path)
        if not checked_path.exists():
            print(f"[❌] Sketchybar path not found after checkout in {user}, deleting repo")
            shutil.rmtree(REPO_PATH)
            return
            
        print(f"[✅] Cloned {user} with sketchybar path: {sketchybar_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"[!] Git error cloning {user}: {e}")
        if REPO_PATH.exists():
            shutil.rmtree(REPO_PATH)
    

def main():
   base_url = "https://github.com/FelixKratz/SketchyBar/discussions/47?sort=top" 
   REPOS = fetch_links(base_url)
   for repo in REPOS:
        repo_ssh, user, repo_name = convert_to_ssh(repo)
        sketchy_path, branch = find_sketchybar_path(user, repo_name)
        if sketchy_path is None:
            print(f"[!] No sketchybar path found for {user}/{repo_name}, skipping.")
            continue
        sparse_checkout(repo_ssh, user, sketchy_path)


if __name__ == "__main__":
    main()