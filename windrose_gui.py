# -*- coding: utf-8 -*-
import os
import json
import shutil
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from send2trash import send2trash

CONFIG_FILE = "config.json"

root = tk.Tk()
root.title("Windrose Save Manager v1.5 - by sx0Lzc :)")
root.geometry("580x640")

def expand(p):
    return os.path.expandvars(p)

def get_default_paths():
    local = expand(r"%LOCALAPPDATA%")
    official = os.path.join(local, "R5", "Saved", "SaveProfiles")
    modded = os.path.join(local, "R5", "Saved")
    backup = os.path.join(expand(r"%USERPROFILE%"), "Documents", "Game")
    return official, modded, backup

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config():
    data = {
        "official": save_profiles.get(),
        "modded": save_all.get(),
        "backup": backup_root_var.get()
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

cfg = load_config()
default_official, default_mod, default_backup = get_default_paths()

save_profiles = tk.StringVar(value=cfg.get("official", default_official))
save_all = tk.StringVar(value=cfg.get("modded", default_mod))
backup_root_var = tk.StringVar(value=cfg.get("backup", default_backup))

folder_map = {}

def open_folder(path):
    path = expand(path)
    if not os.path.exists(path):
        messagebox.showerror("Error", f"Path not found:\n{path}")
        return
    subprocess.Popen(f'explorer "{path}"')

def browse(var):
    path = filedialog.askdirectory()
    if path:
        var.set(path)
        save_config()

def load_backups():
    listbox.delete(0, tk.END)
    folder_map.clear()

    root_path = expand(backup_root_var.get())
    os.makedirs(root_path, exist_ok=True)

    for f in sorted(os.listdir(root_path), reverse=True):
        full = os.path.join(root_path, f)

        if os.path.isdir(full):
            if os.path.exists(os.path.join(full, "MOD", "Saved")):
                label = f"[MODDED FULL] {f}"
                folder_map[label] = ("MOD", f)
                listbox.insert(tk.END, label)
                listbox.itemconfig(tk.END, fg="red")

            elif os.path.exists(os.path.join(full, "SaveProfiles")):
                label = f"[OFFICIAL] {f}"
                folder_map[label] = ("NON", f)
                listbox.insert(tk.END, label)
                listbox.itemconfig(tk.END, fg="green")

def backup_nonmod():
    src = expand(save_profiles.get())
    root_path = expand(backup_root_var.get())

    if not os.path.exists(src):
        messagebox.showerror("Error", "Official path not found")
        return

    folder = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dst = os.path.join(root_path, folder, "SaveProfiles")

    os.makedirs(dst, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)

    messagebox.showinfo("Success", "Official save backed up!")
    load_backups()

def backup_mod():
    src = expand(save_all.get())
    root_path = expand(backup_root_var.get())

    if not os.path.exists(src):
        messagebox.showerror("Error", "Mod path not found")
        return

    folder = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dst = os.path.join(root_path, folder, "MOD", "Saved")

    os.makedirs(dst, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)

    messagebox.showinfo("Success", "Modded save backed up!")
    load_backups()

# ===== AUTO BACKUP BEFORE RESTORE =====
def auto_backup_before_restore(dst, type_):
    root_path = expand(backup_root_var.get())
    folder = datetime.now().strftime("%Y-%m-%d_%H-%M") + " (Auto)"

    if type_ == "NON":
        dst_path = os.path.join(root_path, folder, "SaveProfiles")
    else:
        dst_path = os.path.join(root_path, folder, "MOD", "Saved")

    if os.path.exists(dst):
        os.makedirs(dst_path, exist_ok=True)
        shutil.copytree(dst, dst_path, dirs_exist_ok=True)

# ===== SAFE RESTORE =====
def restore(type_):
    sel = listbox.get(tk.ACTIVE)

    if sel not in folder_map:
        messagebox.showerror("Error", "No backup selected")
        return

    typ, folder = folder_map[sel]

    if type_ == "NON" and typ != "NON":
        messagebox.showerror("Error", "Please select OFFICIAL backup")
        return

    if type_ == "MOD" and typ != "MOD":
        messagebox.showerror("Error", "Please select MODDED backup")
        return

    if not messagebox.askyesno("Confirm", "Overwrite current save?"):
        return

    messagebox.showwarning("Warning", "Please CLOSE the game before restoring.")

    root_path = expand(backup_root_var.get())

    if typ == "NON":
        src = os.path.join(root_path, folder, "SaveProfiles")
        dst = expand(save_profiles.get())
    else:
        src = os.path.join(root_path, folder, "MOD", "Saved")
        dst = expand(save_all.get())

    if not os.path.exists(src):
        messagebox.showerror("Error", f"Backup not found:\n{src}")
        return

    # ⭐ 自動備份
    try:
        auto_backup_before_restore(dst, type_)
    except Exception as e:
        messagebox.showwarning("Warning", f"Auto backup failed:\n{e}")

    backup_temp = dst + "_backup_temp"

    try:
        if os.path.exists(dst):
            if os.path.exists(backup_temp):
                shutil.rmtree(backup_temp, ignore_errors=True)
            shutil.move(dst, backup_temp)

        shutil.copytree(src, dst)

        if os.path.exists(backup_temp):
            shutil.rmtree(backup_temp, ignore_errors=True)

        messagebox.showinfo("Success", "Restore completed!")

    except Exception as e:
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst, ignore_errors=True)
            if os.path.exists(backup_temp):
                shutil.move(backup_temp, dst)
        except:
            messagebox.showerror("Critical Error", "Restore failed and rollback failed!")
            return

        messagebox.showerror("Error", f"Restore failed.\nOriginal save restored.\n\n{e}")

def delete_backup():
    sel = listbox.get(tk.ACTIVE)

    if sel not in folder_map:
        messagebox.showerror("Error", "No backup selected")
        return

    folder = folder_map[sel][1]
    path = os.path.join(expand(backup_root_var.get()), folder)

    if not os.path.exists(path):
        messagebox.showerror("Error", f"Path not found:\n{path}")
        return

    if messagebox.askyesno("Confirm", f"Delete {folder}?"):
        send2trash(path)
        load_backups()

# ===== UI =====
frame = tk.Frame(root)
frame.pack(pady=5)

tk.Label(frame, text="Official Save (Vanilla)", fg="green").grid(row=0, column=1)
tk.Entry(frame, textvariable=save_profiles, width=50).grid(row=1, column=1)
tk.Button(frame, text="Browse", command=lambda: browse(save_profiles)).grid(row=1, column=2)
tk.Button(frame, text="Open", command=lambda: open_folder(save_profiles.get())).grid(row=1, column=3)

tk.Label(frame, text="Modded Save (FULL)", fg="red").grid(row=2, column=1)
tk.Entry(frame, textvariable=save_all, width=50).grid(row=3, column=1)
tk.Button(frame, text="Browse", command=lambda: browse(save_all)).grid(row=3, column=2)
tk.Button(frame, text="Open", command=lambda: open_folder(save_all.get())).grid(row=3, column=3)

tk.Label(frame, text="Backup Path", fg="blue").grid(row=4, column=1)
tk.Entry(frame, textvariable=backup_root_var, width=50).grid(row=5, column=1)
tk.Button(frame, text="Browse", command=lambda: browse(backup_root_var)).grid(row=5, column=2)
tk.Button(frame, text="Open", command=lambda: open_folder(backup_root_var.get())).grid(row=5, column=3)

top = tk.Frame(root)
top.pack(pady=5)

tk.Button(top, text="Load Saves", command=load_backups).grid(row=0, column=0, padx=5)
tk.Button(top, text="Delete Backup", command=delete_backup).grid(row=0, column=1, padx=5)

listbox = tk.Listbox(root)
listbox.pack(fill="both", expand=True)
listbox.bind("<Double-Button-1>", lambda e: restore("NON") if "[OFFICIAL]" in listbox.get(tk.ACTIVE) else restore("MOD"))

bottom = tk.Frame(root)
bottom.pack()

tk.Button(bottom, text="Backup Official", command=backup_nonmod).grid(row=0, column=0)
tk.Button(bottom, text="Backup Modded", command=backup_mod).grid(row=0, column=1)
tk.Button(bottom, text="Restore Official", command=lambda: restore("NON")).grid(row=1, column=0)
tk.Button(bottom, text="Restore Modded", command=lambda: restore("MOD")).grid(row=1, column=1)

load_backups()
root.mainloop()