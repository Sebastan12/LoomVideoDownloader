import os
import requests
import yaml
from urllib.parse import urlparse


def download_video(video_id, video_name, folder_path, idx):
    video_filename = f"{idx:03d}_{video_name.replace(' ', '_').lower()}.mp4"
    if os.path.exists(os.path.join(folder_path, video_filename)):
        print(f"Video '{video_name}' already exists, skipping download.")
        return
    url = f"https://www.loom.com/api/campaigns/sessions/{video_id}/transcoded-url"
    try:
        response = requests.post(url)
        response.raise_for_status()
        data = response.json()
        video_url = data.get("url")
        if video_url:
            parsed_url = urlparse(video_url)
            video_extension = os.path.splitext(parsed_url.path)[1]
            video_filename = f"{idx:03d}_{video_name.replace(' ', '_').lower()}{video_extension}"
            with open(os.path.join(folder_path, video_filename), "wb") as f:
                video_response = requests.get(video_url)
                f.write(video_response.content)
            print(f"Video '{video_name}' downloaded as '{video_filename}'")
        else:
            print("Video URL not found in the response.")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")


def generate_md_file(video_name, video_text, folder_path, idx):
    if video_text:
        markdown_filename = f"{idx:03d}_{video_name.replace(' ', '_').lower()}.md"
        if os.path.exists(os.path.join(folder_path, markdown_filename)):
            print(f"Markdown file '{markdown_filename}' already exists, skipping generation.")
            return
        with open(os.path.join(folder_path, markdown_filename), "w") as f:
            f.write(video_text)
        print(f"Markdown file '{markdown_filename}' generated.")


def create_folders(folder_structure, parent_path="", idx=0):
    for folder_name, content in folder_structure.items():
        idx += 1
        folder_path = os.path.join(parent_path, f"{idx:02d}_{folder_name}")
        os.makedirs(folder_path, exist_ok=True)
        if isinstance(content, dict):
            create_folders(content, folder_path, idx)
        elif isinstance(content, list):
            for vid_idx, video_info in enumerate(content, start=1):
                video_name = video_info["name"]
                text = video_info.get("text", "")
                download_video(video_info["id"], video_name, folder_path, vid_idx)
                generate_md_file(video_name, text, folder_path, vid_idx)


def main():
    yaml_file = "folder_structure.yaml"  # Path to your YAML file
    with open(yaml_file, "r", encoding="utf-8") as f:
        folder_structure = yaml.safe_load(f)

    create_folders(folder_structure)


if __name__ == "__main__":
    main()
