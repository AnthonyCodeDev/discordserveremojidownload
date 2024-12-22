import os
import shutil
import requests

class DiscordEmojiDownloader:
    def __init__(self):
        self.token = self.get_token()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

    def get_token(self):
        if os.path.isfile("./token.txt"):
            return open("token.txt").read().strip()
        else:
            token = input("Enter your Discord token: ").strip()
            with open("token.txt", "w") as file:
                file.write(token)
            return token

    @staticmethod
    def restrict(name):
        if os.name == "nt":
            name = name.translate({ord(i): None for i in '\\/:*?"<>|'})
        else:
            name = name.replace("/", "")
        return name if name else "no_name"

    def fetch_guilds(self):
        response = requests.get(
            "https://discord.com/api/v8/users/@me/guilds",
            headers={"authorization": self.token}
        )
        if response.status_code != 200:
            print(f"Failed to fetch guilds: {response.status_code} {response.text}")
            exit(1)
        return response.json()

    def choose_guild(self, guilds):
        for i, guild in enumerate(guilds, start=1):
            print(f"{i} | {guild['name']}")

        choice = input("Choose the guild by number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(guilds):
            selected_guild = guilds[int(choice) - 1]
            return selected_guild["id"], selected_guild["name"]
        else:
            print("Invalid selection")
            exit(1)

    def prepare_folder(self, folder_name):
        folder_path = os.path.join(self.current_dir, folder_name)
        if os.path.isdir(folder_path):
            print(f"Removing existing folder: {folder_path}")
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)
        return folder_path

    def fetch_emojis(self, guild_id):
        response = requests.get(
            f"https://discord.com/api/v8/guilds/{guild_id}/emojis",
            headers={"authorization": self.token}
        )
        if response.status_code != 200:
            print(f"Failed to fetch emojis: {response.status_code} {response.text}")
            exit(1)
        return response.json()

    def download_emojis(self, emojis, folder_path):
        for i, emoji in enumerate(emojis, start=1):
            file_extension = "gif" if emoji["animated"] else "png"
            file_name = f"{emoji['name']}.{file_extension}"
            file_path = os.path.join(folder_path, file_name)

            print(f"Downloading {emoji['name']} ({'animated' if emoji['animated'] else 'static'}) ({i}/{len(emojis)})")
            response = requests.get(f"https://cdn.discordapp.com/emojis/{emoji['id']}.{file_extension}?v=1")
            with open(file_path, "wb") as file:
                file.write(response.content)

        print("Finished downloading all emojis")

    def run(self):
        guilds = self.fetch_guilds()
        guild_id, guild_name = self.choose_guild(guilds)
        folder_name = self.restrict(guild_name)
        folder_path = self.prepare_folder(folder_name)
        emojis = self.fetch_emojis(guild_id)
        self.download_emojis(emojis, folder_path)

if __name__ == "__main__":
    downloader = DiscordEmojiDownloader()
    downloader.run()
