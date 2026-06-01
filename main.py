import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CaptoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FAO")
        self.root.geometry("1300x750")

        # Valeurs de départ / excel M. Meyer
        self.d1_var = tk.DoubleVar(value=38.0)
        self.e_var = tk.DoubleVar(value=2.0)
        self.nb_pt_var = tk.IntVar(value=1000)
        self.sens_var = tk.IntVar(value=-1)
        self.corde_var = tk.DoubleVar(value=0.01)
        self.tol_ang_var = tk.DoubleVar(value=1.0)
        
        self.angle_var = tk.DoubleVar(value=5.0)
        self.longueur_var = tk.DoubleVar(value=50.0)

        self.z_visu_var = tk.DoubleVar(value=0.0)

        self.create_widgets()
        self.update_data()

    def create_widgets(self):
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Les paramètres du profil
        profil_frame = tk.LabelFrame(left_frame, text="Paramètres profil", padx=10, pady=5)
        profil_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(profil_frame, text="d1:").grid(row=0, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.d1_var, width=10).grid(row=0, column=1)

        tk.Label(profil_frame, text="e:").grid(row=1, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.e_var, width=10).grid(row=1, column=1)

        tk.Label(profil_frame, text="nb_pt:").grid(row=2, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.nb_pt_var, width=10).grid(row=2, column=1)

        tk.Label(profil_frame, text="sens:").grid(row=3, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.sens_var, width=10).grid(row=3, column=1)

        tk.Label(profil_frame, text="corde:").grid(row=4, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.corde_var, width=10).grid(row=4, column=1)

        tk.Label(profil_frame, text="tol_ang (°):").grid(row=5, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.tol_ang_var, width=10).grid(row=5, column=1)

        z_frame = tk.LabelFrame(left_frame, text="Paramètres en Z", padx=10, pady=5)
        z_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(z_frame, text="angle (°):").grid(row=0, column=0, sticky="w")
        tk.Entry(z_frame, textvariable=self.angle_var, width=10).grid(row=0, column=1)

        tk.Label(z_frame, text="longueur:").grid(row=1, column=0, sticky="w")
        tk.Entry(z_frame, textvariable=self.longueur_var, width=10).grid(row=1, column=1)

        action_frame = tk.Frame(left_frame, pady=5)
        action_frame.pack(fill=tk.X)

        tk.Label(action_frame, text="Cote Z (Visu):").grid(row=0, column=0, sticky="w")
        tk.Scale(action_frame, variable=self.z_visu_var, from_=0, to=-50, resolution=0.1, orient=tk.HORIZONTAL, command=lambda val: self.update_data()).grid(row=0, column=1, sticky="ew")

        tk.Button(action_frame, text="Actualiser Visu", command=self.update_data, bg="#2196F3", fg="white").grid(row=1, columnspan=2, pady=5, sticky="we")
        
        # Bouton pour ASCII
        tk.Button(action_frame, text="Générer Fichier ASCII (Étape 3)", command=self.generer_etape_3, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).grid(row=2, columnspan=2, pady=10, sticky="we")

        # Le tableau des 1000 points 
        table_frame = tk.LabelFrame(left_frame, text="Tableau des coordonnées")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("i", "X", "Y", "Tx", "Ty", "Nx", "Ny")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=55, anchor="center")
        self.tree.column("i", width=40)
        
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # La zone de visu à droite
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_profile(self, target_z=None):
        # Si on donne pas de Z, on prend celui du curseur
        if target_z is None:
            target_z = self.z_visu_var.get()

        d1 = self.d1_var.get()
        e = self.e_var.get()
        nb_pt = self.nb_pt_var.get()
        angle = np.radians(self.angle_var.get())

        # La dépouille : on réduit le diamètre selon Z
        d1_z = d1 - 2 * abs(target_z) * np.tan(angle)
        e_z = e * (d1_z / d1)

        a = np.linspace(0, 2 * np.pi, nb_pt)

        # Les équations infernales du poly
        x = (d1_z / 2 - e_z * np.cos(3 * a)) * np.cos(a) - 3 * e_z * np.sin(3 * a) * np.sin(a)
        y = (d1_z / 2 - e_z * np.cos(3 * a)) * np.sin(a) + 3 * e_z * np.sin(3 * a) * np.cos(a)

        # Astuce avec np.roll pour choper i+1 et i-1 sans faire une boucle
        x_next, y_next = np.roll(x, -1), np.roll(y, -1)
        x_prev, y_prev = np.roll(x, 1), np.roll(y, 1)

        tx = x_next - x_prev
        ty = y_next - y_prev
        
        # Normalisation
        norm_t = np.sqrt(tx**2 + ty**2)
        tx, ty = tx / norm_t, ty / norm_t

        # La normale tourne à 90° (j'espère que c'est le bon sens)
        nx, ny = ty, -tx

        return x, y, tx, ty, nx, ny

    def update_data(self):
        try:
            x, y, tx, ty, nx, ny = self.calculate_profile()

            self.ax.clear()
            self.ax.plot(x, y, 'b-', linewidth=2, label=f"Profil Z={self.z_visu_var.get():.1f}mm")
            
            # Je n'affiche qu'une normale sur 200 sinon c'est illisible
            step = len(x) // 200
            self.ax.quiver(x[::step], y[::step], nx[::step], ny[::step], 
                           color='r', alpha=0.5, scale=15, label='Normales')

            self.ax.plot(x[0], y[0], 'go', markersize=8, label="Point de départ")
            self.ax.set_aspect('equal')
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.set_title("Géométrie vue du haut")
            self.ax.legend()
            self.canvas.draw()

            # On vide le tableau avant de le re-remplir à nouveau
            self.tree.delete(*self.tree.get_children())
            rows = [(i, f"{x[i]:.4f}", f"{y[i]:.4f}", f"{tx[i]:.4f}", f"{ty[i]:.4f}", f"{nx[i]:.4f}", f"{ny[i]:.4f}") for i in range(len(x))]
            for row in rows:
                self.tree.insert("", tk.END, values=row)

        except Exception as err:
            print("Aïe, ça a crashé :", err)

    def generer_etape_3(self):
        # On découpe en 11 tranches pour l'export
        longueur = self.longueur_var.get()
        z_levels = np.linspace(0, -longueur, 11)
        filename = "profils_capto.ascii"
        
        try:
            with open(filename, "w") as f:
                # On écrit chaque tranche dans le fichier
                for z in z_levels:
                    x, y, _, _, _, _ = self.calculate_profile(target_z=z)
                    for i in range(len(x)):
                        f.write(f"{x[i]:.6f} {y[i]:.6f} {z:.6f}\n")
            
            messagebox.showinfo("C'est dans la boîte", f"Fichier généré !\nenregistré sur le bureau\n\nLe fichier '{filename}' est prêt pour CATIA.")
        except Exception as e:
            messagebox.showerror("Boulette", f"Erreur pendant l'export : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptoGeneratorApp(root)
    root.mainloop()