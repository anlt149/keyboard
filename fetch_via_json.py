#!/usr/bin/env python3

import urllib.request
import json
import os
import sys

def main():
    if len(sys.argv) > 1:
        keyboard_name = sys.argv[1].lower()
    else:
        keyboard_name = input("Enter keyboard name to search for (e.g. zoom65): ").lower().strip()
    
    if not keyboard_name:
        print("Keyboard name cannot be empty.")
        sys.exit(1)

    print(f"Fetching repository tree from the-via/keyboards...")
    url = "https://api.github.com/repos/the-via/keyboards/git/trees/master?recursive=1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching repository data: {e}")
        sys.exit(1)
        
    tree = data.get('tree', [])
    
    # Filter JSON files in src/ or v3/ directories
    json_files = [item['path'] for item in tree if item['path'].endswith('.json') and ('src/' in item['path'] or 'v3/' in item['path'])]
    
    # Search for the keyboard name in the path
    matches = [path for path in json_files if keyboard_name in path.lower()]
    
    if not matches:
        print(f"No VIA JSON found for '{keyboard_name}'.")
        print("Note: The keyboard might not be merged into the official VIA repository yet.")
        sys.exit(0)
        
    print(f"\nFound {len(matches)} matching file(s):")
    for i, match in enumerate(matches):
        print(f"[{i + 1}] {match}")
        
    print()
    if len(matches) > 1:
        choice = input("Enter the number of the file to download (or 'all' for all): ")
        if choice.lower() == 'all':
            selected = matches
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(matches):
                    selected = [matches[idx]]
                else:
                    print("Invalid selection.")
                    sys.exit(1)
            except ValueError:
                print("Invalid input.")
                sys.exit(1)
    else:
        selected = matches
        print(f"Auto-selecting the only match: {selected[0]}")
        
    download_dir = os.path.expanduser("~/code/keyboard")
    os.makedirs(download_dir, exist_ok=True)
    
    for path in selected:
        raw_url = f"https://raw.githubusercontent.com/the-via/keyboards/master/{path}"
        filename = os.path.basename(path)
        dest = os.path.join(download_dir, filename)
        
        # Avoid overwriting existing files without warning if they have the same name
        if os.path.exists(dest):
            base, ext = os.path.splitext(filename)
            dest = os.path.join(download_dir, f"{path.replace('/', '_')}")
            
        print(f"Downloading {raw_url} ...")
        try:
            req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read()
                with open(dest, 'wb') as f:
                    f.write(content)
            print(f"Success! Saved to {dest}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

if __name__ == "__main__":
    main()
