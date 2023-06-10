import os
import requests
from github import Github
import telebot

# GitHub repository URLs and branches
repo_url1 = "https://github.com/MikuX-Dev/Kernel-ysl"
repo_branch1 = "mikasa"
repo_url2 = "https://github.com/lostark13/kernel_xiaomi_cannon"
repo_branch2 = "cannon"

# Telegram bot API credentials
telegram_bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
telegram_chat_id = "YOUR_TELEGRAM_CHAT_ID"

# Initialize GitHub API client
github_token = "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"  # Optional if public repositories
g = Github(github_token)

# Create Telegram bot instance
bot = telebot.TeleBot(telegram_bot_token)

# Function to compare files and check for differences in lines
def compare_files(file1, file2):
    lines1 = open(file1, "r").readlines()
    lines2 = open(file2, "r").readlines()
    diff_lines = []
    
    for i, (line1, line2) in enumerate(zip(lines1, lines2)):
        if line1 != line2:
            diff_lines.append(f"Line {i+1}: {line1.strip()} != {line2.strip()}")
    
    return diff_lines

# Function to compare folders recursively
def compare_folders(folder1, folder2):
    diff_files = []
    for dirpath, dirnames, filenames in os.walk(folder1):
        for filename in filenames:
            file1 = os.path.join(dirpath, filename)
            file2 = os.path.join(folder2, os.path.relpath(file1, folder1))
            if os.path.exists(file2):
                diff_lines = compare_files(file1, file2)
                if diff_lines:
                    diff_files.append(f"File: {file1}\n{'\n'.join(diff_lines)}")
            else:
                diff_files.append(f"File missing: {file1}")
    
    return diff_files

# Create temporary directories to clone repositories
clone_dir1 = "clone1"
clone_dir2 = "clone2"
os.makedirs(clone_dir1, exist_ok=True)
os.makedirs(clone_dir2, exist_ok=True)

# Clone repositories
repo1 = g.get_repo(repo_url1)
repo2 = g.get_repo(repo_url2)
clone_repo1 = repo1.get_archive_link("zipball", ref=repo_branch1)
clone_repo2 = repo2.get_archive_link("zipball", ref=repo_branch2)

# Download and extract repositories
response1 = requests.get(clone_repo1)
response2 = requests.get(clone_repo2)
with open("repo1.zip", "wb") as file1, open("repo2.zip", "wb") as file2:
    file1.write(response1.content)
    file2.write(response2.content)
import zipfile
with zipfile.ZipFile("repo1.zip", "r") as zip_ref1, zipfile.ZipFile("repo2.zip", "r") as zip_ref2:
    zip_ref1.extractall(clone_dir1)
    zip_ref2.extractall(clone_dir2)

# Compare repositories and send report to Telegram bot
diff_report = compare_folders(clone_dir1, clone_dir2)

if diff_report:
    # Send report to Telegram bot
    report_text = "\n\n".join(diff_report)
    bot.send_message(telegram_chat_id, report_text)

# Clean up temporary directories and files
os.remove("repo1.zip")
os.remove("repo2.zip")
os.rmdir(clone_dir1)
os.rmdir(clone_dir2)
