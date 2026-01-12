import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess

DATA_FILE = "data.json"

class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HSC 2026 Resource Manager")
        self.root.geometry("900x700")
        
        # Load Data
        self.db = self.load_db()

        # --- TreeView Layout ---
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.tree.heading("#0", text="HSC Resource Library (Notes / PYQ)", anchor="w")
        
        # --- Control Panel ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        # Main Buttons
        ttk.Button(btn_frame, text="➕ Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Add File/Link", command=self.add_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Rename", command=self.rename_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        
        # Utility Buttons
        ttk.Button(btn_frame, text="🚀 Publish Web", command=self.publish_site).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_tree).pack(side=tk.RIGHT, padx=5)

        self.refresh_tree()

    def load_db(self):
        if not os.path.exists(DATA_FILE):
            initial_db = {"Notes": {"children": {}}, "PYQ": {"children": {}}}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(initial_db, f, indent=4, ensure_ascii=False)
            return initial_db
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_db(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.db, f, indent=4, ensure_ascii=False)
        self.refresh_tree()

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.insert_nodes("", self.db)

    def insert_nodes(self, parent, data_dict):
        # Sort so folders appear above files
        items = sorted(data_dict.items(), key=lambda x: ("link" in x[1]))
        for key, value in items:
            prefix = "📂 " if "children" in value else "📄 "
            node_id = self.tree.insert(parent, "end", text=f"{prefix}{key}", open=False)
            if "children" in value:
                self.insert_nodes(node_id, value["children"])

    def get_selection_info(self):
        """Helper to get path and reference to the selected item in DB"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select an item in the list.")
            return None, None, None

        path = []
        curr = selected[0]
        while curr:
            text = self.tree.item(curr, "text")[3:] # Remove emoji prefix
            path.insert(0, text)
            curr = self.tree.parent(curr)
        
        # Traverse DB to find parent and current target
        parent_ptr = None
        target_ptr = self.db
        last_key = None

        for p in path:
            parent_ptr = target_ptr
            last_key = p
            if "children" in target_ptr:
                target_ptr = target_ptr["children"][p]
            else:
                target_ptr = target_ptr[p]
        
        return parent_ptr, last_key, target_ptr

    def add_folder(self):
        parent_ptr, key, target = self.get_selection_info()
        if not target: return
        
        if "link" in target:
            messagebox.showerror("Error", "Cannot add a folder inside a file.")
            return

        name = simpledialog.askstring("New Folder", "Enter Folder Name:")
        if name:
            if "children" not in target: target["children"] = {}
            target["children"][name] = {"children": {}}
            self.save_db()

    def add_file(self):
        parent_ptr, key, target = self.get_selection_info()
        if not target: return
        
        if "link" in target:
            messagebox.showerror("Error", "Select a folder, not a file, to add resources.")
            return

        name = simpledialog.askstring("New File", "Enter Resource Name:")
        url = simpledialog.askstring("New File", "Paste Link (URL):")
        if name and url:
            if "children" not in target: target["children"] = {}
            target["children"][name] = {"link": url}
            self.save_db()

    def rename_item(self):
        parent_ptr, key, target = self.get_selection_info()
        if not target: return
        
        if key in ["Notes", "PYQ"]:
            messagebox.showerror("Error", "Root categories cannot be renamed.")
            return

        new_name = simpledialog.askstring("Rename", f"Enter new name for '{key}':")
        if new_name:
            # Determine if we are at root level or nested
            container = parent_ptr["children"] if "children" in parent_ptr else parent_ptr
            container[new_name] = container.pop(key)
            self.save_db()

    def delete_item(self):
        parent_ptr, key, target = self.get_selection_info()
        if not target: return
        
        if key in ["Notes", "PYQ"]:
            messagebox.showerror("Error", "Root categories cannot be deleted.")
            return

        if messagebox.askyesno("Confirm", f"Delete '{key}' and all its contents?"):
            container = parent_ptr["children"] if "children" in parent_ptr else parent_ptr
            del container[key]
            self.save_db()

    def publish_site(self):
        try:
            # Runs the generation script automatically
            subprocess.run(["python", "generate_dashboard.py"], check=True)
            messagebox.showinfo("Success", "Web Dashboard re-generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run generator: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseGUI(root)
    root.mainloop()