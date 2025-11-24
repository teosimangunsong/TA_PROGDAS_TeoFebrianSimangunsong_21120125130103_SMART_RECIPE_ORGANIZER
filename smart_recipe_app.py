import customtkinter as ctk
from collections import deque
import random
from PIL import Image, ImageTk 
# --- Tambahan untuk Persistensi Data ---
import json 
import os # Digunakan opsional untuk manajemen file
# ----------------------------------------

# --- MODUL 5 & 6: OBJECT ORIENTED PROGRAMMING I & II ---

class Recipe:
    """Kelas dasar (Parent Class) untuk setiap resep."""
    def __init__(self, name, ingredients, steps, cooking_time):
        self.name = name                      
        self.ingredients = ingredients          
        self.steps = steps                      
        self.cooking_time = cooking_time        
        self.is_favorite = False                

    def display_details(self):
        """Method dasar untuk menampilkan detail resep."""
        details = f"Waktu Masak: {self.cooking_time} menit\n"
        details += f"Bahan-bahan: {', '.join(self.ingredients)}\n"
        details += f"Langkah: {'; '.join(self.steps)}"
        return details
    
    def calculate_prep_time(self, prep_factor=0.2):
        """Menghitung perkiraan waktu persiapan (Method)."""
        return int(self.cooking_time * prep_factor)

class HomemadeRecipe(Recipe):
    """Kelas turunan untuk resep buatan sendiri."""
    def __init__(self, name, ingredients, steps, cooking_time, source="Koleksi Pribadi"):
        super().__init__(name, ingredients, steps, cooking_time)
        self.source = source
        
    def display_details(self):
        base_details = super().display_details()
        return f"{base_details}\nSumber: {self.source}"

class RecipeManager:
    """Mengelola koleksi resep dan struktur data, kini dengan persistensi data."""
    def __init__(self):
        self.data_file = "recipe_data.json" # Nama file data
        self.recipes = {} 
        self.shopping_queue = deque()     
        self.history_stack = []          
        
        # Panggil method untuk memuat data lama saat inisialisasi
        self.is_data_loaded = self.load_data() 

    def add_recipe(self, recipe):
        if recipe.name not in self.recipes:
            self.recipes[recipe.name] = recipe
            return True
        return False

    def add_to_shopping_list(self, item):
        """Menambahkan item ke Queue Daftar Belanja."""
        self.shopping_queue.append(item)

    def remove_from_shopping_list(self):
        """Mengambil item dari Queue (FIFO)."""
        if self.shopping_queue:
            return self.shopping_queue.popleft()
        return None

    def add_to_history(self, recipe_name):
        """Menambahkan resep yang dilihat ke Stack."""
        if recipe_name in self.recipes:
            self.history_stack.append(recipe_name) # Push ke Stack

    # ------------------------------------------------------------------
    # --- FUNGSI PERSISTENSI DATA (JSON I/O) ---
    # ------------------------------------------------------------------

    def save_data(self):
        """Menyimpan data resep dan shopping list ke file JSON."""
        recipes_data = {}
        for name, recipe in self.recipes.items():
            data = {
                "name": recipe.name,
                "ingredients": recipe.ingredients,
                "steps": recipe.steps,
                "cooking_time": recipe.cooking_time,
                # Identifikasi tipe kelas untuk proses loading yang benar
                "type": "HomemadeRecipe" if isinstance(recipe, HomemadeRecipe) else "Recipe",
                "source": getattr(recipe, 'source', None) 
            }
            recipes_data[name] = data

        data_to_save = {
            "recipes": recipes_data,
            # Konversi deque ke list untuk disimpan
            "shopping_queue": list(self.shopping_queue) 
        }

        try:
            with open(self.data_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print("💾 Data saved successfully.")
        except Exception as e:
            print(f"❌ Error saving data: {e}")

    def load_data(self):
        """Memuat data resep dan shopping list dari file JSON."""
        if not os.path.exists(self.data_file):
            print(f"File '{self.data_file}' not found. Starting with initial data.")
            return False
            
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                
                # Memuat Resep
                for name, recipe_data in data.get("recipes", {}).items():
                    # Memilih kelas yang tepat (Polimorfisme)
                    if recipe_data.get("type") == "HomemadeRecipe":
                        recipe_obj = HomemadeRecipe(
                            recipe_data["name"], 
                            recipe_data["ingredients"], 
                            recipe_data["steps"], 
                            recipe_data["cooking_time"],
                            source=recipe_data.get("source", "Koleksi Pribadi")
                        )
                    else:
                        recipe_obj = Recipe(
                            recipe_data["name"], 
                            recipe_data["ingredients"], 
                            recipe_data["steps"], 
                            recipe_data["cooking_time"]
                        )
                    self.recipes[name] = recipe_obj

                # Memuat Queue
                self.shopping_queue = deque(data.get("shopping_queue", []))
            
            print("✅ Data loaded successfully.")
            return True

        except Exception as e:
            print(f"❌ Error decoding JSON file or loading data: {e}. Starting with initial data.")
            return False
            
# -----------------------------------------------------------------

# --- MODUL 8: GUI PROGRAMMING (CUSTOMTKINTER) ---

class App(ctk.CTk):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Pengaturan Jendela Utama
        self.title("SMART RECIPE ORGANIZER") 
        self.geometry("900x700") 
        ctk.set_appearance_mode("Dark") 
        ctk.set_default_color_theme("green") 

        # --- TEMA MODERN, ELEGAN & FUTURISTIK ---
        self.configure(fg_color="#1a1a2e") # Deep Space Blue/Purple
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header Frame 
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent") 
        self.header_frame.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew") 
        self.header_frame.grid_columnconfigure((0, 2), weight=1) 
        self.header_frame.grid_columnconfigure(1, weight=0) 
        
        # Icon & Title Setup
        self.icon_path = "title_icon.png" 
        try:
            pil_image = Image.open(self.icon_path).resize((35, 35), Image.LANCZOS)
            title_icon_image = ctk.CTkImage(pil_image, size=(35, 35))
            self.title_icon_label = ctk.CTkLabel(
                self.header_frame, 
                image=title_icon_image, 
                text="",
                fg_color="transparent"
            )
            self.title_icon_label.grid(row=0, column=1, padx=(0, 10), pady=0, sticky="e") 
        except FileNotFoundError:
            self.title_icon_label = ctk.CTkLabel(
                self.header_frame, 
                text="🚀", 
                font=ctk.CTkFont(size=35, weight="bold"),
                fg_color="transparent"
            )
            self.title_icon_label.grid(row=0, column=1, padx=(0, 10), pady=0, sticky="e")

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="AURA RECIPIES", 
            font=ctk.CTkFont(family="Cascadia Code", size=32, weight="bold"), 
            text_color="#00FFFF" # Cyan neon
        )
        self.title_label.grid(row=0, column=2, padx=(10, 0), pady=0, sticky="w")
        
        # Main Frame 
        self.main_frame = ctk.CTkFrame(self, fg_color="#2e2e4a", corner_radius=20) 
        self.main_frame.grid(row=1, column=0, padx=30, pady=(0, 30), sticky="nsew") 
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Tab View 
        self.tab_view = ctk.CTkTabview(
            self.main_frame, 
            fg_color="#2e2e4a", 
            corner_radius=15,
            segmented_button_fg_color="#3a3a5e", 
            segmented_button_selected_color="#00FFFF", 
            segmented_button_selected_hover_color="#00CCCC",
            segmented_button_unselected_color="#2e2e4a",
            segmented_button_unselected_hover_color="#3a3a5e",
        ) 
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tab_view.add("DATA RECIPES") 
        self.tab_view.add("ADD RECIPE")
        self.tab_view.add("SHOPPING LIST")

        self.setup_recipe_list_tab()
        self.setup_add_recipe_tab()
        self.setup_shopping_tab()
        
    # ----------------------------------------------------------------------------------
    ## 📑 DATA RECIPES
    # ----------------------------------------------------------------------------------

    def setup_recipe_list_tab(self):
        tab = self.tab_view.tab("DATA RECIPES")
        tab.grid_columnconfigure(0, weight=1)
        
        # Frame Pencarian
        search_frame = ctk.CTkFrame(
            tab, 
            fg_color="#3a3a5e", 
            corner_radius=10,
            border_width=2,
            border_color="#00FFFF" 
        )
        search_frame.pack(fill="x", padx=15, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="SEARCH INGREDIENTS...", 
            corner_radius=8,
            fg_color="#1a1a2e", 
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Cascadia Code", size=13)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=8)
        
        self.search_button = ctk.CTkButton(
            search_frame, 
            text="FIND 🔍", 
            command=self.search_recipes,
            corner_radius=8,
            width=100,
            fg_color="#00FFFF", hover_color="#00CCCC", 
            text_color="#1a1a2e", 
            font=ctk.CTkFont(family="Cascadia Code", size=13, weight="bold")
        )
        self.search_button.pack(side="left", padx=(0, 10), pady=8)

        self.history_label = ctk.CTkLabel(
            tab, 
            text="RECENTLY VIEWED : -", 
            text_color="#AAAAAA",
            font=ctk.CTkFont(family="Cascadia Code", size=12)
        )
        self.history_label.pack(pady=(15, 10))
        
        # Scrollable Frame Resep
        self.recipe_list_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent", label_text="")
        self.recipe_list_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.update_recipe_list()

    def update_recipe_list(self, filter_ingredients=None):
        """Memperbarui tampilan daftar resep."""
        for widget in self.recipe_list_frame.winfo_children():
            widget.destroy()
            
        recipes_to_display = self.manager.recipes.values()
        
        for i, recipe in enumerate(recipes_to_display):
            if filter_ingredients and not any(ing.strip().lower() in [r.lower() for r in recipe.ingredients] for ing in filter_ingredients):
                continue
            
            recipe_frame = ctk.CTkFrame(
                self.recipe_list_frame, 
                fg_color="#3a3a5e", 
                corner_radius=12,
                border_width=1,
                border_color="#008B8B" 
            ) 
            recipe_frame.pack(fill="x", padx=8, pady=6)
            
            recipe_label = ctk.CTkLabel(
                recipe_frame, 
                text=recipe.name.upper(), 
                font=ctk.CTkFont(family="Cascadia Code", size=16, weight="bold"),
                text_color="#E0FFFF", 
                anchor="w"
            )
            recipe_label.pack(side="left", padx=15, pady=12, fill="x", expand=True)
            
            detail_button = ctk.CTkButton(
                recipe_frame, 
                text="VIEW DATA ►", 
                command=lambda r=recipe: self.show_recipe_detail(r),
                corner_radius=8,
                fg_color="#4CAF50", hover_color="#45A049", 
                text_color="white",
                font=ctk.CTkFont(family="Cascadia Code", size=13)
            )
            detail_button.pack(side="right", padx=10, pady=10)

    # ----------------------------------------------------------------------------------
    ## 📝 ADD RECIPE
    # ----------------------------------------------------------------------------------

    def setup_add_recipe_tab(self):
        tab = self.tab_view.tab("ADD RECIPE")
        tab.grid_columnconfigure(0, weight=0) 
        tab.grid_columnconfigure(1, weight=1) 
        
        label_keys = {
            "RECIPE NAME:": "Nama Resep:", 
            "INGREDIENTS (COMMA SEPARATED):": "Bahan (dipisahkan koma):", 
            "STEPS (COMMA SEPARATED):": "Langkah (dipisahkan koma):", 
            "COOKING TIME (MINUTES):": "Waktu Masak (menit):"
        }
        
        self.entries = {}
        row_counter = 0
        for label_text, key in label_keys.items():
            label = ctk.CTkLabel(
                tab, 
                text=label_text, 
                anchor="w",
                font=ctk.CTkFont(family="Cascadia Code", size=13, weight="bold"),
                text_color="#E0FFFF"
            )
            label.grid(row=row_counter, column=0, padx=(25, 10), pady=12, sticky="w")
            
            entry = ctk.CTkEntry(
                tab, 
                corner_radius=10, 
                fg_color="#1a1a2e", 
                text_color="#00FFFF", 
                border_color="#008B8B", border_width=1,
                font=ctk.CTkFont(family="Cascadia Code", size=14)
            ) 
            entry.grid(row=row_counter, column=1, padx=(10, 25), pady=12, sticky="ew")
            
            self.entries[key] = entry
            row_counter += 1
            
        self.add_button = ctk.CTkButton(
            tab, 
            text="ADD NEW RECIPE ➕", 
            command=self.add_new_recipe,
            corner_radius=12,
            fg_color="#00FF7F", hover_color="#00E673", 
            text_color="#1a1a2e", 
            font=ctk.CTkFont(family="Cascadia Code", size=15, weight="bold")
        )
        self.add_button.grid(row=row_counter, column=0, columnspan=2, padx=25, pady=(30, 15), sticky="ew")
        row_counter += 1
        
        self.status_label_add = ctk.CTkLabel(
            tab, 
            text="",
            font=ctk.CTkFont(family="Cascadia Code", size=12, weight="bold")
        )
        self.status_label_add.grid(row=row_counter, column=0, columnspan=2, pady=(0, 15))

    # ----------------------------------------------------------------------------------
    ## 🛒 SHOPPING LIST
    # ----------------------------------------------------------------------------------

    def setup_shopping_tab(self):
        tab = self.tab_view.tab("SHOPPING LIST")
        tab.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            tab, 
            text="ITEM QUEUE 🛒", 
            font=ctk.CTkFont(family="Cascadia Code", weight="bold", size=18),
            text_color="#00FFFF"
        ).pack(pady=20)
        
        self.shopping_list_frame = ctk.CTkScrollableFrame(
            tab, 
            corner_radius=15, 
            fg_color="#3a3a5e", 
            border_width=1,
            border_color="#00FFFF"
        )
        self.shopping_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.complete_button = ctk.CTkButton(
            tab, 
            text="MARK AS ACQUIRED ✅", 
            command=self.complete_shopping_item,
            corner_radius=12,
            fg_color="#FF4500", hover_color="#E03E00", 
            text_color="white",
            font=ctk.CTkFont(family="Cascadia Code", size=15, weight="bold")
        )
        self.complete_button.pack(padx=20, pady=20)
        
        self.status_label_shopping = ctk.CTkLabel(
            tab, 
            text="",
            font=ctk.CTkFont(family="Cascadia Code", size=12, weight="bold")
        )
        self.status_label_shopping.pack(pady=(0, 10))

        self.update_shopping_list()

    def update_shopping_list(self):
        """Memperbarui tampilan Queue Daftar Belanja."""
        for widget in self.shopping_list_frame.winfo_children():
            widget.destroy()
            
        if not self.manager.shopping_queue:
            ctk.CTkLabel(
                self.shopping_list_frame, 
                text="NO ITEMS IN QUEUE.\nINITIATE ACQUISITION.", 
                text_color="#888888",
                font=ctk.CTkFont(family="Cascadia Code", size=14),
                pady=20
            ).pack(expand=True)
            return

        for i, item in enumerate(self.manager.shopping_queue):
            bg_color = "#4a4a70" if i == 0 else "transparent" 
            border_color = "#00FFFF" if i == 0 else "#3a3a5e" 
            text_color = "#00FFFF" if i == 0 else "#E0FFFF" 
            
            item_frame = ctk.CTkFrame(
                self.shopping_list_frame,
                fg_color=bg_color,
                corner_radius=8,
                border_width=1,
                border_color=border_color
            )
            item_frame.pack(fill="x", padx=10, pady=4)

            item_label = ctk.CTkLabel(
                item_frame, 
                text=f"► {item.upper()}", 
                anchor="w",
                text_color=text_color,
                font=ctk.CTkFont(family="Cascadia Code", size=14, weight="bold")
            )
            item_label.pack(side="left", padx=15, pady=8, expand=True, fill="x")

    # ----------------------------------------------------------------------------------
    ## ⚙️ Logika Aplikasi
    # ----------------------------------------------------------------------------------
    
    def add_new_recipe(self):
        """Menambahkan resep baru dengan validasi dan pengkondisian."""
        name = self.entries["Nama Resep:"].get()
        ingredients_str = self.entries["Bahan (dipisahkan koma):"].get()
        steps_str = self.entries["Langkah (dipisahkan koma):"].get()
        cooking_time_str = self.entries["Waktu Masak (menit):"].get()
        
        if hasattr(self, 'status_label_shopping'):
            self.status_label_shopping.configure(text="")
        
        if not all([name, ingredients_str, steps_str, cooking_time_str]):
            self.status_label_add.configure(text="❌ DATA INPUT INCOMPLETE. ALL FIELDS REQUIRED.", text_color="#FF4500") 
            return

        try:
            cooking_time = int(cooking_time_str)
        except ValueError:
            self.status_label_add.configure(text="❌ ERROR: COOKING TIME MUST BE NUMERIC.", text_color="#FF4500")
            return
            
        ingredients = [i.strip() for i in ingredients_str.split(',') if i.strip()]
        steps = [s.strip() for s in steps_str.split(',') if s.strip()]
        
        new_recipe = HomemadeRecipe(name, ingredients, steps, cooking_time)
        
        if self.manager.add_recipe(new_recipe):
            if cooking_time > 60:
                 self.status_label_add.configure(text=f"✅ RECIPE ADDED. (LONG DURATION: {cooking_time} MINS)", text_color="#FFFF00") # Kuning neon
            else:
                 self.status_label_add.configure(text="✅ RECIPE ADDED SUCCESSFULLY.", text_color="#00FF7F") # Hijau neon
            for entry in self.entries.values():
                entry.delete(0, 'end')
            self.update_recipe_list()
        else:
            self.status_label_add.configure(text="❌ ERROR: RECIPE NAME ALREADY EXISTS.", text_color="#FF4500")

    def search_recipes(self):
        """Mencari resep berdasarkan bahan (Pengkondisian & Perulangan)."""
        search_query = self.search_entry.get().lower().replace(" ", "")
        if not search_query:
            self.update_recipe_list() 
            return
            
        search_ingredients = [ing.strip() for ing in search_query.split(',') if ing.strip()]
        self.update_recipe_list(filter_ingredients=search_ingredients)
        
    def show_recipe_detail(self, recipe):
        """Menampilkan detail resep dan menambahkan ke Stack. Kini menggunakan CTkTextbox."""
        self.manager.add_to_history(recipe.name) 
        
        latest_history = self.manager.history_stack[-1] if self.manager.history_stack else "NO DATA"
        self.history_label.configure(text=f"RECENTLY VIEWED: {latest_history.upper()}") # Sudah dimodifikasi
        
        # Jendela detail
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(f"RECIPE DATA: {recipe.name.upper()}")
        detail_window.geometry("650x500") # Ukuran jendela diperbesar untuk menampung teks panjang
        detail_window.grab_set() 
        detail_window.configure(fg_color="#1a1a2e") 
        
        prep_time = recipe.calculate_prep_time()
        
        # Format teks detail
        detail_text = (
            f"ACCESS CODE: {recipe.name.upper()}\n"
            f"ESTIMATED PREP TIME: {prep_time} MINS\n"
            f"----------------------------------------\n"
            f"COOKING CYCLE: {recipe.cooking_time} MINS\n"
            f"INGREDIENT MANIFEST: {', '.join(recipe.ingredients).upper()}\n"
            f"EXECUTION PROTOCOL:\n" # Pisahkan header "EXECUTION PROTOCOL"
            f"   {'; '.join(recipe.steps).upper()}\n" # Tambahkan indentasi
            f"ORIGIN SOURCE: {getattr(recipe, 'source', 'PUBLIC ARCHIVE').upper()}"
        )
        
        # --- PERBAIKAN UTAMA: GANTI CTkLabel DENGAN CTkTextbox ---
        self.detail_textbox = ctk.CTkTextbox(
            detail_window,
            width=600,
            height=300, # Atur tinggi untuk memberi ruang scroll jika diperlukan
            wrap="word", # Penting: Memastikan teks melipat pada batas kata
            font=ctk.CTkFont(family="Cascadia Code", size=14),
            text_color="#E0FFFF",
            fg_color="#2e2e4a", # Background sedikit berbeda
            border_color="#00FFFF",
            border_width=1
        )
        self.detail_textbox.pack(padx=25, pady=(25, 15), fill="both", expand=True) 
        
        # Masukkan teks ke dalam Textbox
        self.detail_textbox.delete("0.0", "end") # Hapus isi default
        self.detail_textbox.insert("0.0", detail_text)
        self.detail_textbox.configure(state="disabled") # Nonaktifkan agar pengguna tidak bisa mengedit
        
        # Tombol aksi 
        add_to_queue_button = ctk.CTkButton(
            detail_window, 
            text="ADD TO SHOPPING PROTOCOL 🛒", 
            command=lambda r=recipe: self.add_recipe_ingredients_to_queue(r, detail_window),
            corner_radius=12,
            fg_color="#00FFFF", hover_color="#00CCCC", 
            text_color="#1a1a2e",
            font=ctk.CTkFont(family="Cascadia Code", size=14, weight="bold")
        )
        add_to_queue_button.pack(pady=(0, 20)) # Sesuaikan padding

    def add_recipe_ingredients_to_queue(self, recipe, window):
        """Menambahkan bahan-bahan resep ke Queue."""
        # Gunakan set sementara untuk menghindari duplikat dalam antrian
        current_queue_items = {q_item.strip().upper() for q_item in self.manager.shopping_queue}
        
        for ing in recipe.ingredients:
            ing_upper = ing.strip().upper()
            if ing_upper and ing_upper not in current_queue_items:
                self.manager.add_to_shopping_list(ing)
                current_queue_items.add(ing_upper)

        self.update_shopping_list()
        window.destroy()
        self.tab_view.set("SHOPPING LIST") 
        
    def complete_shopping_item(self):
        """Menyelesaikan item teratas di Queue (FIFO)."""
        if hasattr(self, 'status_label_add'):
            self.status_label_add.configure(text="")
            
        item = self.manager.remove_from_shopping_list() # Popleft dari Queue
        if item:
            self.status_label_shopping.configure(text=f"✅ ACQUISITION COMPLETE: '{item.upper()}'", text_color="#00FF7F")
            self.update_shopping_list()
        else:
            self.status_label_shopping.configure(text="ℹ️ SHOPPING LIST EMPTY. NO TARGETS IDENTIFIED.", text_color="#888888")


# -----------------------------------------------------------------

def on_closing():
    """Fungsi yang dipanggil saat jendela ditutup."""
    manager.save_data()  # Simpan semua data terakhir
    app.destroy()        # Tutup aplikasi

if __name__ == "__main__":
    
    # 1. Inisialisasi Manager (Ini akan otomatis mencoba memuat data)
    manager = RecipeManager()
    
    # 2. Tambahkan data awal hanya jika data tidak berhasil dimuat
    if not manager.is_data_loaded:
        print("Adding initial default recipes and shopping list...")
        
        recipe1 = HomemadeRecipe(
            "Nasi Goreng Spesial", 
            ["nasi", "telur", "bawang merah", "kecap manis", "cabai"],
            ["panaskan minyak", "tumis bumbu", "masukkan nasi", "aduk rata", "sajikan"], 
            20
        )
        recipe2 = Recipe(
            "Omelet Keju Cepat", 
            ["telur", "susu", "keju", "garam"],
            ["kocok telur", "campur semua", "goreng", "lipat"], 
            10
        )
        recipe3 = HomemadeRecipe(
            "Sup Buntut Galaxy", 
            ["buntut sapi", "wortel", "kentang", "bawang bombay", "rempah luar angkasa"],
            ["rebus buntut", "tumis bumbu", "campur semua", "didihkan", "sajikan dengan plasma"],
            90,
            source="Intergalactic Cook Book v2.0"
        )
        
        manager.add_recipe(recipe1)
        manager.add_recipe(recipe2)
        manager.add_recipe(recipe3)
        
        manager.add_to_shopping_list("tepung terigu")
        manager.add_to_shopping_list("ayam fillet")
        manager.add_to_shopping_list("energi kristal")
    
    # 3. Jalankan Aplikasi GUI
    app = App(manager)
    # Kaitkan fungsi on_closing dengan tombol 'X' (close window)
    app.protocol("WM_DELETE_WINDOW", on_closing) 
    app.mainloop()