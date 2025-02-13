import os
import shutil
import requests

class DiscordEmojiDownloader:
    """
    Classe permettant de télécharger les emojis d'un serveur Discord.
    
    Utilise un token Discord pour interroger l'API Discord et récupérer
    la liste des serveurs (guilds) et leurs emojis.
    """

    def __init__(self):
        """
        Initialise l'instance en récupérant le token Discord et en définissant
        le répertoire courant où les fichiers seront sauvegardés.
        """
        self.token = self.get_token()  # Récupère le token via un fichier ou input
        self.current_dir = os.path.dirname(os.path.abspath(__file__))  # Répertoire du script

    def get_token(self):
        """
        Récupère le token Discord depuis le fichier 'token.txt' s'il existe, 
        sinon demande à l'utilisateur de le saisir et le sauvegarde.
        
        Returns:
            str: Le token Discord.
        """
        if os.path.isfile("./token.txt"):
            # Si le fichier existe, lire le token et le retourner
            with open("token.txt", "r") as file:
                return file.read().strip()
        else:
            # Sinon, demander le token à l'utilisateur et le sauvegarder dans 'token.txt'
            token = input("Enter your Discord token: ").strip()
            with open("token.txt", "w") as file:
                file.write(token)
            return token

    @staticmethod
    def restrict(name):
        """
        Nettoie le nom pour le rendre compatible avec le système de fichiers.
        
        Args:
            name (str): Nom original qui peut contenir des caractères non valides.
            
        Returns:
            str: Nom nettoyé, ou "no_name" si le nom devient vide après nettoyage.
        """
        if os.name == "nt":
            # Sur Windows, retirer les caractères interdits (\ / : * ? " < > |)
            name = name.translate({ord(i): None for i in '\\/:*?"<>|'})
        else:
            # Sur les systèmes Unix, retirer les slashs
            name = name.replace("/", "")
        return name if name else "no_name"

    def fetch_guilds(self):
        """
        Récupère la liste des serveurs (guilds) auxquels l'utilisateur appartient via l'API Discord.
        
        Returns:
            list: Liste de dictionnaires représentant les guilds.
        
        Exit:
            Quitte le programme si la requête échoue.
        """
        response = requests.get(
            "https://discord.com/api/v8/users/@me/guilds",
            headers={"authorization": self.token}
        )
        if response.status_code != 200:
            print(f"Failed to fetch guilds: {response.status_code} {response.text}")
            exit(1)
        return response.json()

    def choose_guild(self, guilds):
        """
        Affiche la liste des guilds et permet à l'utilisateur de sélectionner un serveur.
        
        Args:
            guilds (list): Liste des guilds obtenue via fetch_guilds.
            
        Returns:
            tuple: (guild_id, guild_name) du serveur sélectionné.
        
        Exit:
            Quitte le programme si la sélection est invalide.
        """
        # Afficher chaque guild avec un numéro correspondant
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
        """
        Crée un dossier pour sauvegarder les emojis téléchargés.
        Si le dossier existe déjà, il est supprimé pour éviter les conflits.
        
        Args:
            folder_name (str): Nom du dossier à créer.
            
        Returns:
            str: Chemin absolu du dossier créé.
        """
        folder_path = os.path.join(self.current_dir, folder_name)
        if os.path.isdir(folder_path):
            # Supprimer le dossier existant
            print(f"Removing existing folder: {folder_path}")
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)
        return folder_path

    def fetch_emojis(self, guild_id):
        """
        Récupère la liste des emojis du serveur spécifié via l'API Discord.
        
        Args:
            guild_id (str): Identifiant du serveur.
            
        Returns:
            list: Liste de dictionnaires représentant les emojis.
            
        Exit:
            Quitte le programme si la requête échoue.
        """
        response = requests.get(
            f"https://discord.com/api/v8/guilds/{guild_id}/emojis",
            headers={"authorization": self.token}
        )
        if response.status_code != 200:
            print(f"Failed to fetch emojis: {response.status_code} {response.text}")
            exit(1)
        return response.json()

    def download_emojis(self, emojis, folder_path):
        """
        Télécharge chaque emoji dans le dossier spécifié.
        
        Args:
            emojis (list): Liste des emojis récupérés via fetch_emojis.
            folder_path (str): Chemin du dossier où enregistrer les emojis.
            
        Side Effects:
            Crée des fichiers images (png ou gif) pour chaque emoji.
        """
        for i, emoji in enumerate(emojis, start=1):
            # Choisir l'extension du fichier en fonction de l'animation
            file_extension = "gif" if emoji.get("animated", False) else "png"
            file_name = f"{emoji['name']}.{file_extension}"
            file_path = os.path.join(folder_path, file_name)

            print(f"Downloading {emoji['name']} ({'animated' if emoji.get('animated', False) else 'static'}) ({i}/{len(emojis)})")
            # Télécharger l'emoji depuis le CDN Discord
            response = requests.get(f"https://cdn.discordapp.com/emojis/{emoji['id']}.{file_extension}?v=1")
            with open(file_path, "wb") as file:
                file.write(response.content)

        print("Finished downloading all emojis")

    def run(self):
        """
        Exécute l'ensemble du processus de téléchargement des emojis :
            1. Récupère la liste des guilds.
            2. Permet à l'utilisateur de choisir un guild.
            3. Prépare un dossier pour les emojis.
            4. Récupère et télécharge les emojis du guild sélectionné.
        """
        guilds = self.fetch_guilds()
        guild_id, guild_name = self.choose_guild(guilds)
        folder_name = self.restrict(guild_name)
        folder_path = self.prepare_folder(folder_name)
        emojis = self.fetch_emojis(guild_id)
        self.download_emojis(emojis, folder_path)

if __name__ == "__main__":
    # Créer une instance du téléchargeur et lancer le processus
    downloader = DiscordEmojiDownloader()
    downloader.run()
