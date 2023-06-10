import os
import shutil
import requests
import subprocess
from github import Github
import telebot

# GitHub repository URLs and branches
repo_url1 = "https://github.com/MikuX-Dev/Kernel-ysl"
repo_branch1 = "mikasa"
repo_url2 = "https://github.com/lostark13/kernel_xiaomi_cannon"
repo_branch2 = "cannon"

# Telegram bot API credentials
telegram_bot_token = "6166928181:AAFddZ-KA7-_l6cPfFl7BRDL8Jb4fqmNy7M"
telegram_chat_id = "1780850118"

# Initialize GitHub API client
github_token = "YOUR_PAT_TOKEN"  # Optional if public repositories
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
            diff_lines.append("Line {}: {} != {}".format(i + 1, line1.strip(), line2.strip()))

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
                    diff_files.append("File: {}\n{}".format(file1, "\n".join(diff_lines)))
            else:
                diff_files.append("File missing: {}".format(file1))

    return diff_files

# Compare repositories
clone_dir1 = "clone1"
clone_dir2 = "clone2"
os.makedirs(clone_dir1, exist_ok=True)
os.makedirs(clone_dir2, exist_ok=True)

# Clone and extract repositories
subprocess.run(["git", "clone", "--depth", "1", "--branch", repo_branch1, repo_url1, clone_dir1])
subprocess.run(["git", "clone", "--depth", "1", "--branch", repo_branch2, repo_url2, clone_dir2])

# Compare repositories and send report to Telegram bot
diff_report = compare_folders(os.path.join(clone_dir1, repo_branch1), os.path.join(clone_dir2, repo_branch2))

if diff_report:
    # Send report to Telegram bot
    report_text = "\n\n".join(diff_report)
    bot.send_message(telegram_chat_id, report_text)

# Clean up temporary directories
shutil.rmtree(clone_dir1)
shutil.rmtree(clone_dir2)
