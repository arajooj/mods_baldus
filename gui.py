import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
import shutil
import sys
import requests
from tkinter import ttk, messagebox
from decouple import config


class GitHubReleaseManager:
    BASE_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
    
    def __init__(self, owner, repo, token=None):
        self.owner = owner
        self.repo = repo
        self.token = token
    
    def get_latest_release(self):
        headers = {
            "Accept": "application/vnd.github+json"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        url = self.BASE_URL.format(owner=self.owner, repo=self.repo)
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()



class ModManager:
    MOD_FOLDER_REL_PATH = r"Larian Studios\Baldur's Gate 3\Mods"
    LOCAL_PATH = os.environ['LocalAppData']
    MOD_FOLDER_ABS_PATH = Path(LOCAL_PATH, MOD_FOLDER_REL_PATH)
    NATIVE_MODS_PATH = Path("Bin/NativeMods")
    
    REQUIRED_FOLDERS = ['Bin', 'Data', 'Launcher']
    FILES_TO_DELETE = ["Bin/bg3.exe", "Bin/bg3_dx11.exe", "Bin/bink2w64.dll"]
    FOLDERS_TO_DELETE = ["Bin/NativeMods", "Data/Mods", "Data/Public"]
    
    RENAMES = {
        "Bin/bink2w64_original.dll": "Bin/bink2w64.dll",
        "Bin/bg3.exe.backup": "Bin/bg3.exe",
        "Bin/bg3_dx11.exe.backup": "Bin/bg3_dx11.exe"
    }
    
    GITHUB_TOKEN = config('GITHUB_TOKEN')

    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Mods - FDGE v7 (Patch #2)")

        icon_path = self.resource_path("_fdge/bard_icon_class_bg3.ico")
        self.root.iconbitmap(icon_path)

        self.lbl_status = tk.Label(root)
        self.lbl_status.pack(pady=20)

        self.btn_activate = tk.Button(root, text="Ativar Mods", command=self.activate_mods)
        self.btn_activate.pack(pady=10)

        self.btn_deactivate = tk.Button(root, text="Desativar Mods", command=self.deactivate_mods)
        self.btn_deactivate.pack(pady=10)
        
        self.btn_test_download = tk.Button(root, text="Testar Download", command=self.test_download)
        self.btn_test_download.pack(pady=10)

        self.check_mods_status()

    @staticmethod
    def resource_path(relative_path):
        base_path = getattr(sys, '_MEIPASS', Path(__file__).parent.absolute())
        return base_path / relative_path

    def download_file_with_progress(self, url, destination):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB

        self.progress_label = tk.Label(self.root, text="Baixando arquivo...")
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        downloaded_size = 0
        with open(destination, 'wb') as file:
            for data in response.iter_content(block_size):
                downloaded_size += len(data)
                file.write(data)
                self.progress_bar['value'] = (downloaded_size / total_size) * 100
                self.root.update()

        self.progress_label.destroy()
        self.progress_bar.destroy()
        
    def test_download(self):
        try:
            # Defina o token, o proprietário e o nome do repositório aqui
            token = self.GITHUB_TOKEN
            owner = "arajooj"
            repo = "mods_baldus"
            
            gh_manager = GitHubReleaseManager(owner, repo, token)
            release_data = gh_manager.get_latest_release()
            
            # Aqui, estou supondo que você deseja pegar o URL de download do primeiro ativo.
            download_url = release_data['assets'][0]['browser_download_url']
            
            # Vamos simplesmente exibir o URL por agora. Você pode integrar um download real aqui.
            messagebox.showinfo("URL de Download", download_url)
            
            file_name = download_url.split('/')[-1]
            destination_path = Path.cwd() / file_name

            self.download_file_with_progress(download_url, destination_path)
            
            messagebox.showinfo("Download Completo", f"Arquivo baixado como {file_name}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao obter o URL de download. {e}")
            
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
            shutil.copytree(self.resource_path("_fdge/_ROOT"), "./", dirs_exist_ok=True)
            shutil.copytree(self.resource_path("_fdge/_BKP"), "Bin", dirs_exist_ok=True)

            self.MOD_FOLDER_ABS_PATH.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self.resource_path("_fdge/_PAK"), str(self.MOD_FOLDER_ABS_PATH), dirs_exist_ok=True)
            
            messagebox.showinfo("Sucesso", "Mods ativados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao ativar os mods. {e}")

        self.check_mods_status()

    def deactivate_mods(self):
        try:
            for f in self.FILES_TO_DELETE:
                path = Path(f)
                if path.exists():
                    path.unlink()
            for d in self.FOLDERS_TO_DELETE:
                path = Path(d)
                if path.exists():
                    shutil.rmtree(path)
            if self.MOD_FOLDER_ABS_PATH.exists():
                shutil.rmtree(self.MOD_FOLDER_ABS_PATH)
            if Path("_fdge/_BKP").exists():
                shutil.copytree("_fdge/_BKP", "Bin", dirs_exist_ok=True)
            for old, new in self.RENAMES.items():
                old_path, new_path = Path(old), Path(new)
                if old_path.exists():
                    old_path.rename(new_path)
            
            messagebox.showinfo("Sucesso", "Mods desativados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao desativar os mods. {e}")

        self.check_mods_status()

    def center_window(self, width=400, height=300):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    root.resizable(False, False)

    app = ModManager(root)
    app.center_window()

    root.mainloop()

# Build command (Windows): 
# python -m PyInstaller --onefile --windowed --icon=favicon.ico --add-data="_fdge;_fdge" --distpath=out/dist --workpath=out/build --name="bg3_fdge_modmanager_v7" --log-level=DEBUG --clean gui.py

