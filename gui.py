import tkinter as tk
from tkinter import messagebox
import os
import shutil
import sys


class ModManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Mods - FDGE v2")

        self.lbl_status = tk.Label(root)
        self.lbl_status.pack(pady=20)

        self.btn_activate = tk.Button(root, text="Ativar Mods", command=self.activate_mods)
        self.btn_activate.pack(pady=10)

        self.btn_deactivate = tk.Button(root, text="Desativar Mods", command=self.deactivate_mods)
        self.btn_deactivate.pack(pady=10)

        self.check_mods_status()
 

    def resource_path(relative_path):
        """ Obtenha o caminho absoluto para o recurso, funciona para dev e para o PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)


    def check_mods_status(self):
        local_path = os.environ['LocalAppData']
        mod_folder = os.path.join(local_path, r"Larian Studios\Baldur's Gate 3\Mods")

        if os.path.exists(mod_folder):
            self.status_msg = "Mods estão ativados."
            self.btn_activate.config(state=tk.DISABLED)
            self.btn_deactivate.config(state=tk.NORMAL)
            self.lbl_status.config(fg="green")
        else:
            self.status_msg = "Mods estão desativados."
            self.btn_activate.config(state=tk.NORMAL)
            self.btn_deactivate.config(state=tk.DISABLED)
            self.lbl_status.config(fg="red")

        self.lbl_status.config(text=self.status_msg)


    def activate_mods(self):
        try:
            # Como não estamos mais verificando a pasta _fdge no sistema de arquivos, 
            # essa verificação pode ser removida ou alterada conforme sua necessidade.
            
            shutil.copytree(ModManager.resource_path("_fdge/_ROOT"), "./", dirs_exist_ok=True)

            local_path = os.environ['LocalAppData']
            mod_folder = os.path.join(local_path, r"Larian Studios\Baldur's Gate 3\Mods")
            if os.path.exists(mod_folder):
                shutil.rmtree(mod_folder)
            os.makedirs(mod_folder)

            if os.path.exists(ModManager.resource_path("_fdge/_BKP")):
                shutil.copytree(ModManager.resource_path("_fdge/_BKP"), "Bin", dirs_exist_ok=True)


            messagebox.showinfo("Sucesso", "Mods ativados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao ativar os mods. {e}")

        self.check_mods_status()

    def deactivate_mods(self):
        try:
            files_to_delete = ["Bin/bg3.exe", "Bin/bg3_dx11.exe", "Bin/bink2w64.dll"]
            folders_to_delete = ["Bin/NativeMods", "Data/Mods", "Data/Public"]

            for f in files_to_delete:
                if os.path.exists(f):
                    os.remove(f)

            for d in folders_to_delete:
                if os.path.exists(d):
                    shutil.rmtree(d)

            local_path = os.environ['LocalAppData']
            mod_folder = os.path.join(local_path, r"Larian Studios\Baldur's Gate 3\Mods")
            if os.path.exists(mod_folder):
                shutil.rmtree(mod_folder)

            if os.path.exists("_fdge/_BKP"):
                shutil.copytree("_fdge/_BKP", "Bin", dirs_exist_ok=True)

            renames = {
                "Bin/bink2w64_original.dll": "Bin/bink2w64.dll",
                "Bin/bg3.exe.backup": "Bin/bg3.exe",
                "Bin/bg3_dx11.exe.backup": "Bin/bg3_dx11.exe"
            }
            for old, new in renames.items():
                if os.path.exists(old):
                    os.rename(old, new)

            messagebox.showinfo("Sucesso", "Mods desativados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao desativar os mods. {e}")

        self.check_mods_status()

if __name__ == "__main__":
    root = tk.Tk()

    # Define a largura x altura inicial da janela. Por exemplo, 400x200.
    root.geometry("400x200")

    # Faz com que a janela não possa ser redimensionada.
    root.resizable(False, False)

    app = ModManager(root)
    root.mainloop()