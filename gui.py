import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import shutil
import sys
import requests
from decouple import config
import logging
import zipfile
import os
import hashlib
import json
import re


# Configuração básica de logging
logging.basicConfig(filename="modmanager.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ------------------- GitHubReleaseManager -------------------
class GitHubReleaseManager:
    """
    Classe para gerenciar as releases do GitHub.
    """
    BASE_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"

    def __init__(self, owner, repo, token=None):
        self.owner = owner
        self.repo = repo
        self.token = token

    def get_latest_release(self):
        headers = {"Accept": "application/vnd.github+json"}

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        url = self.BASE_URL.format(owner=self.owner, repo=self.repo)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            
            
class FileHashVerifier:
    def __init__(self, directory_to_check, hash_file='hash.fdge'):
        self.directory_to_check = directory_to_check
        self.hash_file = hash_file

    @staticmethod
    def generate_file_hash(filepath):
        """Generate a hash for a file."""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as file:
            buf = file.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def get_hashes_from_directory(self):
        """Generate hashes for all files in the specified directory and its subdirectories."""
        hashes = {}
        for dirpath, dirnames, filenames in os.walk(self.directory_to_check):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                file_hash = self.generate_file_hash(filepath)
                hashes[filepath.replace(self.directory_to_check, '').lstrip(os.sep)] = file_hash
        return hashes

    def load_hashes_from_file(self):
        """Load the hashes from a file."""
        with open(self.hash_file, 'r') as file:
            return json.load(file)

    @staticmethod
    def compare_hashes(stored_hashes, generated_hashes):
        """Compare stored hashes with generated ones."""
        mismatches = {}
        for key, value in generated_hashes.items():
            if key not in stored_hashes or stored_hashes[key] != value:
                if key not in ["hash.fdge", "version.fdge"] and not re.match(r'^v[\d\.]+\.zip$', key):
                    mismatches[key] = value
        return mismatches

    def verify(self):
        stored_hashes = self.load_hashes_from_file()
        generated_hashes = self.get_hashes_from_directory()
        return self.compare_hashes(stored_hashes, generated_hashes)

# ------------------- ModManager -------------------
class ModManager:
    """
    Classe para gerenciar os mods do jogo "Baldur's Gate 3".
    """
    # Aqui, idealmente, você teria um arquivo de configuração onde essas constantes poderiam ser definidas.
    # Por simplicidade, estou mantendo-as aqui.
    # Atualizar o caminho para o diretório _FDGE
    FDGE_DIR = Path("_FDGE")
    MOD_FOLDER_REL_PATH = Path("Larian Studios", "Baldur's Gate 3", "Mods")
    LOCAL_PATH = Path(os.environ['LocalAppData'])
    MOD_FOLDER_ABS_PATH = LOCAL_PATH / MOD_FOLDER_REL_PATH
    NATIVE_MODS_PATH = Path("Bin", "NativeMods")

    REQUIRED_FOLDERS = ['Bin', 'Data', 'Launcher']
    FILES_TO_DELETE = [Path("Bin", "bg3.exe"), Path("Bin", "bg3_dx11.exe"), Path("Bin", "bink2w64.dll")]
    FOLDERS_TO_DELETE = [Path("Bin", "NativeMods"), Path("Data", "Mods"), Path("Data", "Public")]

    RENAMES = {
        Path("Bin", "bink2w64_original.dll"): Path("Bin", "bink2w64.dll"),
        Path("Bin", "bg3.exe.backup"): Path("Bin", "bg3.exe"),
        Path("Bin", "bg3_dx11.exe.backup"): Path("Bin", "bg3_dx11.exe")
    }

    GITHUB_TOKEN = config('GITHUB_TOKEN')

    def __init__(self, root):
        self.root = root
        self.setup_gui()
        logging.info("Inicializando ModManager...")

    def setup_gui(self):
        self.root.title("Gerenciador de Mods - FDGE v7 (Patch #2)")
        icon_path = self.resource_path("favicon.ico")
        self.root.iconbitmap(icon_path)

        self.lbl_status = tk.Label(self.root)
        self.lbl_status.pack(pady=20)

        self.update_gui_loading("Verificando atualizações...")
    
    def update_gui_loading(self, message):
        self.lbl_status.config(text=message)
        self.lbl_status.update()
        
    def initialize_app(self):
        self.FDGE_DIR.mkdir(parents=True, exist_ok=True)  # Garantir que _FDGE exista
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()

        
        self.update_gui_loading("Verificando hash dos arquivos...")
        hash_file = self.FDGE_DIR / "hash.fdge"
        
        differences = False
        
        if hash_file.exists():
            verifier = FileHashVerifier('_FDGE', self.resource_path("_FDGE/hash.fdge"))
            differences = verifier.verify()
            print(differences)
        else:
            differences = True

        if (current_version != latest_version) or differences:
            
            if differences:
                messagebox.showerror("Erro", "Arquivos corrompidos ou ausentes. Baixe a versão mais recente dos mods novamente.")
    
            if current_version != latest_version:
                messagebox.showinfo("Sucesso", "Nova versão disponível. Baixando a versão mais recente dos mods...")
                
                
            # delete old fdge
            if self.FDGE_DIR.exists():
                shutil.rmtree(self.FDGE_DIR)

            # delete old mods
            if self.MOD_FOLDER_ABS_PATH.exists():
                shutil.rmtree(self.MOD_FOLDER_ABS_PATH)
                
            self.update_gui_loading("Baixando a versão mais recente dos mods...")
            # Use a função para baixar a nova versão e descompactar para a pasta FDGE
            self.download_and_extract_latest_mod()
            with open(self.resource_path("_FDGE/version.fdge"), 'w') as f:
                f.write(latest_version)
                
                
        self.show_buttons()
        
        
    def show_buttons(self):
        self.btn_activate = tk.Button(self.root, text="Ativar Mods", command=self.activate_mods)
        self.btn_activate.pack(pady=10)

        self.btn_deactivate = tk.Button(self.root, text="Desativar Mods", command=self.deactivate_mods)
        self.btn_deactivate.pack(pady=10)

        self.check_mods_status()

    @staticmethod
    def resource_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', Path(__file__).parent.absolute())
        return base_path / relative_path

    def download_file_with_progress(self, url, destination):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB

        self.progress_label = tk.Label(self.root, text="Baixando arquivo: 0%")
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        downloaded_size = 0
        with open(destination, 'wb') as file:
            for data in response.iter_content(block_size):
                downloaded_size += len(data)
                file.write(data)
                percentage = (downloaded_size / total_size) * 100
                self.progress_label.config(text=f"Baixando arquivo: {percentage:.2f}%")
                self.progress_bar['value'] = percentage
                self.root.update()

        self.progress_label.destroy()
        self.progress_bar.destroy()


    def check_mods_status(self):
        if self.MOD_FOLDER_ABS_PATH.exists() and self.NATIVE_MODS_PATH.exists():
            self.status_msg = "Mods estão ativados."
            self.btn_activate.config(state=tk.DISABLED)
            self.btn_deactivate.config(state=tk.NORMAL)
            self.lbl_status.config(fg="green")
        elif (self.MOD_FOLDER_ABS_PATH.exists() and not self.NATIVE_MODS_PATH.exists()) or (not self.MOD_FOLDER_ABS_PATH.exists() and self.NATIVE_MODS_PATH.exists()):
            self.status_msg = "Mods estão ativados, mas não estão funcionando."
            self.btn_activate.config(state=tk.DISABLED)
            self.btn_deactivate.config(state=tk.NORMAL)
            self.lbl_status.config(fg="orange")
        else:
            self.status_msg = "Mods estão desativados."
            self.btn_activate.config(state=tk.NORMAL)
            self.btn_deactivate.config(state=tk.DISABLED)
            self.lbl_status.config(fg="red")
        self.lbl_status.config(text=self.status_msg)

    def check_required_folders(self):
        return all(Path(folder).exists() for folder in self.REQUIRED_FOLDERS)

    def activate_mods(self):
        if not self.check_required_folders():
            messagebox.showerror("Erro", "A pasta atual não tem as pastas necessárias (Bin, Data, Launcher).")
            return

        try:
            self._copy_mod_resources()
            self._copy_backup_resources()
            self._create_mods_folder()
            
            messagebox.showinfo("Sucesso", "Mods ativados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao ativar os mods. {e}")

        self.check_mods_status()

    def deactivate_mods(self):
        try:
            self._delete_files()
            self._delete_folders()
            self._restore_backup_resources()
            
            messagebox.showinfo("Sucesso", "Mods desativados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao desativar os mods. {e}")

        self.check_mods_status()
        
    # Métodos auxiliares para refatoração:
    def _copy_mod_resources(self):
        shutil.copytree(self.resource_path("_fdge/_ROOT"), "./", dirs_exist_ok=True)

    def _copy_backup_resources(self):
        shutil.copytree(self.resource_path("_fdge/_BKP"), "Bin", dirs_exist_ok=True)

    def _create_mods_folder(self):
        self.MOD_FOLDER_ABS_PATH.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.resource_path("_fdge/_PAK"), str(self.MOD_FOLDER_ABS_PATH), dirs_exist_ok=True)

    def _delete_files(self):
        for f in self.FILES_TO_DELETE:
            path = Path(f)
            if path.exists():
                path.unlink()

    def _delete_folders(self):
        for d in self.FOLDERS_TO_DELETE:
            path = Path(d)
            if path.exists():
                shutil.rmtree(path)
        if self.MOD_FOLDER_ABS_PATH.exists():
            shutil.rmtree(self.MOD_FOLDER_ABS_PATH)

    def _restore_backup_resources(self):
        if Path("_fdge/_BKP").exists():
            shutil.copytree("_fdge/_BKP", "Bin", dirs_exist_ok=True)
        for old, new in self.RENAMES.items():
            old_path, new_path = Path(old), Path(new)
            if old_path.exists():
                old_path.rename(new_path)
                
    def get_current_version(self):
        version_file = self.FDGE_DIR / "version.fdge"
        if version_file.exists():
            with open(version_file, 'r') as f:
                return f.read().strip()
        return None

    def get_latest_version(self):
        try:
            # Aqui, você está usando a classe já definida GitHubReleaseManager
            token = self.GITHUB_TOKEN
            owner = "arajooj"
            repo = "mods_baldus"
            gh_manager = GitHubReleaseManager(owner, repo, token)
            release_data = gh_manager.get_latest_release()
            return release_data['tag_name']
        except Exception as e:
            logging.error(f"Erro ao tentar obter a versão mais recente: {e}")
            return None
        
        
    def download_and_extract_latest_mod(self):
        self.FDGE_DIR.mkdir(parents=True, exist_ok=True)  # Garantir que _FDGE exista
        try:
            token = self.GITHUB_TOKEN
            owner = "arajooj"
            repo = "mods_baldus"

            gh_manager = GitHubReleaseManager(owner, repo, token)
            release_data = gh_manager.get_latest_release()

            tag_name = release_data['tag_name']
            version_file_path = self.FDGE_DIR / "version.fdge"

            if version_file_path.exists() and version_file_path.read_text().strip() == tag_name:
                logging.info(f"Versão {tag_name} já baixada. Pulando o download.")
                return

            download_url = f"https://github.com/{owner}/{repo}/releases/download/{tag_name}/{tag_name}.zip"
            destination_path = self.FDGE_DIR / f"{tag_name}.zip"

            self.download_file_with_progress(download_url, destination_path)


            # Setup extraction progress UI
            self.progress_label = tk.Label(self.root, text="Extraindo arquivos...")
            self.progress_label.pack(pady=5)

            self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=300, mode='determinate')
            self.progress_bar.pack(pady=10)

            # Extract the ZIP archive
            with zipfile.ZipFile(destination_path, 'r') as zip_ref:
                total_files = len(zip_ref.infolist())
                extracted_files = 0
                for file_info in zip_ref.infolist():
                    extracted_files += 1
                    extraction_progress = (extracted_files / total_files) * 100
                    self.update_extraction_progress(extraction_progress)

                    zip_ref.extract(file_info, self.FDGE_DIR)
            os.remove(destination_path)
            
            if hasattr(self, 'progress_label'):
                self.progress_label.destroy()
            if hasattr(self, 'progress_bar'):
                self.progress_bar.destroy()


            # Escrever a versão no arquivo apenas se o download e a extração forem bem-sucedidos
            with open(version_file_path, "w") as version_file:
                version_file.write(tag_name)

        except Exception as e:
            logging.error(f"Erro ao tentar download_and_extract_latest_mod: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro ao baixar e extrair o mod. {e}")




    def update_extraction_progress(self, progress):
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text=f"Extraindo arquivos: {progress:.2f}%")
        if hasattr(self, 'progress_bar'):
            self.progress_bar.config(value=progress)
        self.root.update()
    
    def center_window(self, width=400, height=200):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.geometry("400x200")
        root.resizable(False, False)

        app = ModManager(root)
        
        app.center_window()  # Centraliza a janela antes de inicializar
        app.initialize_app()

        root.mainloop()

    except Exception as e:
        logging.critical(f"Erro crítico ao executar o aplicativo: {e}")


# Build command (Windows): 
# python -m PyInstaller --onefile --windowed --icon=favicon.ico --distpath=out/dist --workpath=out/build --name="bg3_fdge_modmanager_v7" --log-level=DEBUG --clean gui.py

