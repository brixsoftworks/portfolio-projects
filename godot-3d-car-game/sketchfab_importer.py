#!/usr/bin/env python3
"""
Sketchfab Asset Search & Downloader for Godot 3D
Allows searching top 3D models and downloading them directly into the Godot project.
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import zipfile
import argparse

API_BASE = "https://api.sketchfab.com/v3"

def get_token(args_token=None):
    if args_token:
        return args_token
    return os.environ.get("SKETCHFAB_API_KEY", "").strip()

def search_models(query="car", categories="cars-vehicles", count=10, downloadable=True):
    params = {
        "type": "models",
        "q": query,
        "count": count,
        "downloadable": "true" if downloadable else "false",
        "sort_by": "-likeCount"
    }
    if categories:
        params["categories"] = categories
    
    url = f"{API_BASE}/models?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Godot-Car-Game/1.0"})
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            print(f"\n--- Found {len(results)} Sketchfab Models for '{query}' ---")
            for i, r in enumerate(results, 1):
                name = r.get("name")
                uid = r.get("uid")
                likes = r.get("likeCount", 0)
                author = r.get("user", {}).get("displayName", "Unknown")
                faces = r.get("faceCount", 0)
                license_lbl = r.get("license", {}).get("label", "Unknown")
                url_view = r.get("viewerUrl", "")
                print(f"[{i}] {name}")
                print(f"    UID: {uid}")
                print(f"    Author: {author} | Likes: {likes} | Faces: {faces} | License: {license_lbl}")
                print(f"    Sketchfab URL: {url_view}\n")
            return results
    except Exception as e:
        print(f"Error querying Sketchfab API: {e}", file=sys.stderr)
        return []

def download_model(uid, token=None, output_dir=None):
    token = get_token(token)
    if not token:
        print("\n[!] Error: Sketchfab API token required to download models.", file=sys.stderr)
        print("To get a free token: Log in to sketchfab.com -> Settings -> Password & API -> copy your API token.")
        print("Usage: python3 sketchfab_importer.py download <UID> --token YOUR_TOKEN")
        print("   or: export SKETCHFAB_API_KEY=YOUR_TOKEN\n", file=sys.stderr)
        return False

    if not output_dir:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sketchfab", uid)

    os.makedirs(output_dir, exist_ok=True)
    
    download_url = f"{API_BASE}/models/{uid}/download"
    req = urllib.request.Request(download_url, headers={
        "Authorization": f"Token {token}",
        "User-Agent": "Godot-Car-Game/1.0"
    })

    print(f"Requesting download link for UID: {uid}...")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Failed to obtain download url: {e}", file=sys.stderr)
        return False

    # Check available formats: gltf, glb, source
    format_info = data.get("gltf") or data.get("glb") or data.get("source")
    if not format_info:
        print("No gltf/glb format available for this model.", file=sys.stderr)
        return False

    file_url = format_info.get("url")
    zip_dest = os.path.join(output_dir, "model.zip")
    print(f"Downloading model archive...")
    urllib.request.urlretrieve(file_url, zip_dest)
    
    print(f"Extracting to {output_dir}...")
    with zipfile.ZipFile(zip_dest, "r") as z:
        z.extractall(output_dir)
    os.remove(zip_dest)
    print(f"[+] Successfully downloaded and unpacked model into: {output_dir}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sketchfab Asset Importer for Godot")
    subparsers = parser.add_subparsers(dest="command")
    
    search_p = subparsers.add_parser("search", help="Search Sketchfab models")
    search_p.add_argument("query", nargs="?", default="car", help="Search query")
    search_p.add_argument("--count", type=int, default=10, help="Number of results")
    search_p.add_argument("--category", default="cars-vehicles", help="Category slug")

    down_p = subparsers.add_parser("download", help="Download a Sketchfab model")
    down_p.add_argument("uid", help="Sketchfab Model UID")
    down_p.add_argument("--token", help="Sketchfab API token")
    down_p.add_argument("--out", help="Output directory")

    args = parser.parse_args()
    if args.command == "search":
        search_models(args.query, args.category, args.count)
    elif args.command == "download":
        download_model(args.uid, args.token, args.out)
    else:
        search_models("car", "cars-vehicles", 8)
