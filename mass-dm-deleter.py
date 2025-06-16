import requests
import time
import json
import os
import platform

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def load_token():
    with open("info.json", "r") as f:
        data = json.load(f)
        return data["token"]

def mask_token(token):
    if len(token) < 12:
        return token
    return token[:6] + "********" + token[-6:]

def get_user_id(token):
    url = "https://discord.com/api/v9/users/@me"
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()["id"]
    else:
        print(f"Failed to get user ID: {res.status_code} - {res.text}")
        return None

def delete_message(token, channel_id, message_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0",
    }
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
    res = requests.delete(url, headers=headers)
    if res.status_code == 204:
        print(f"[+] Deleted message {message_id}")
    else:
        print(f"[!] Failed to delete message {message_id}: {res.status_code} - {res.text}")

def delete_own_messages(token, channel_id, own_user_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0",
    }

    print(f"Deleting your own messages in DM channel {channel_id}...")

    before = None
    while True:
        params = {"limit": 100}
        if before:
            params["before"] = before
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print(f"[!] Failed to fetch messages: {res.status_code} - {res.text}")
            break

        messages = res.json()
        if not messages:
            print("[*] No more messages found.")
            break

        own_messages = [m for m in messages if m.get("author", {}).get("id") == own_user_id]
        if not own_messages:
            print("[*] No own messages found in this batch.")
            break

        for msg in own_messages:
            delete_message(token, channel_id, msg["id"])
            time.sleep(0.5)

        before = messages[-1]["id"]

    print(f"[+] Finished deleting own messages in channel {channel_id}.")

def main():
    token = load_token()
    own_user_id = get_user_id(token)
    if not own_user_id:
        print("Cannot proceed without user ID.")
        return

    while True:
        clear_screen()
        print(f"Running on token: {mask_token(token)}\n")
        channel_id = input("Enter the ID of the DM channel to delete your messages from (or type 'exit' to quit): ").strip()
        if channel_id.lower() == 'exit':
            print("Exiting.")
            break
        if not channel_id:
            print("No channel ID entered.")
            time.sleep(2)
            continue
        delete_own_messages(token, channel_id, own_user_id)
        input("\nPress Enter to delete from another channel or type Ctrl+C to exit...")

if __name__ == "__main__":
    main()





## https://github.com/undiagnosing/discord-mass-dm-deleter
## you will need to have a info.json in the root directory with your token in 
