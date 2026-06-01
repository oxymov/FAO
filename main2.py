import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CaptoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FAO - Générateur Profil Capto")
        self.root.geometry("1400x800")

        # Valeurs par défaut
        self.d1_var = tk.DoubleVar(value=38.0)
        self.e_var = tk.DoubleVar(value=2.0)
        self.nb_pt_var = tk.IntVar(value=1000)
        
        # Tolérances (Étape 4)
        self.corde_var = tk.DoubleVar(value=0.01) # intol en mm
        self.tol_ang_var = tk.DoubleVar(value=2.0) # delta en degrés
        
        # Paramètres 3D
        self.angle_var = tk.DoubleVar(value=5.0) # Dépouille
        self.longueur_var = tk.DoubleVar(value=50.0)

        self.z_visu_var = tk.DoubleVar(value=0.0)

        self.create_widgets()
        self.update_data()

    def create_widgets(self):
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Les paramètres du profil
        profil_frame = tk.LabelFrame(left_frame, text="Paramètres 2D", padx=10, pady=5)
        profil_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(profil_frame, text="d1 (mm):").grid(row=0, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.d1_var, width=10).grid(row=0, column=1)

        tk.Label(profil_frame, text="e:").grid(row=1, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.e_var, width=10).grid(row=1, column=1)

        tk.Label(profil_frame, text="Points initiaux:").grid(row=2, column=0, sticky="w")
        tk.Entry(profil_frame, textvariable=self.nb_pt_var, width=10).grid(row=2, column=1)

        # Les paramètres de filtrage (Étape 4)
        filtre_frame = tk.LabelFrame(left_frame, text="Filtrage (Étape 4)", padx=10, pady=5)
        filtre_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(filtre_frame, text="Tol. Corde (mm):").grid(row=0, column=0, sticky="w")
        tk.Entry(filtre_frame, textvariable=self.corde_var, width=10).grid(row=0, column=1)

        tk.Label(filtre_frame, text="Tol. Angle (°):").grid(row=1, column=0, sticky="w")
        tk.Entry(filtre_frame, textvariable=self.tol_ang_var, width=10).grid(row=1, column=1)

        # Les paramètres 3D
        z_frame = tk.LabelFrame(left_frame, text="Paramètres 3D", padx=10, pady=5)
        z_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(z_frame, text="Angle Dépouille (°):").grid(row=0, column=0, sticky="w")
        tk.Entry(z_frame, textvariable=self.angle_var, width=10).grid(row=0, column=1)

        tk.Label(z_frame, text="Longueur h (mm):").grid(row=1, column=0, sticky="w")
        tk.Entry(z_frame, textvariable=self.longueur_var, width=10).grid(row=1, column=1)

        action_frame = tk.Frame(left_frame, pady=5)
        action_frame.pack(fill=tk.X)

        tk.Label(action_frame, text="Cote Z (Visu):").grid(row=0, column=0, sticky="w")
        tk.Scale(action_frame, variable=self.z_visu_var, from_=0, to=-50, resolution=0.1, orient=tk.HORIZONTAL, command=lambda val: self.update_data()).grid(row=0, column=1, sticky="ew")

        tk.Button(action_frame, text="Actualiser Visu", command=self.update_data, bg="#2196F3", fg="white").grid(row=1, columnspan=2, pady=5, sticky="we")
        
        tk.Button(action_frame, text="Générer ASCII (Étapes 3 & 4)", command=self.generer_fichier, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).grid(row=2, columnspan=2, pady=10, sticky="we")

        # Le tableau des points filtrés
        table_frame = tk.LabelFrame(left_frame, text="Coordonnées (Points Filtrés)")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("i", "X", "Y", "Z", "Nx", "Ny", "Nz")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=50, anchor="center")
        self.tree.column("i", width=40)
        
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # La zone de visu
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_profile(self, target_z):
        """Génère les points et normales 3D pour un Z donné."""
        d1 = self.d1_var.get()
        e = self.e_var.get()
        nb_pt = self.nb_pt_var.get()
        angle_depouille = np.radians(self.angle_var.get())

        # Dépouille : le diamètre varie avec Z
        d1_z = d1 - 2 * abs(target_z) * np.tan(angle_depouille)
        e_z = e * (d1_z / d1)

        a = np.linspace(0, 2 * np.pi, nb_pt)

        # Equations du profil polygonal
        x = (d1_z / 2 - e_z * np.cos(3 * a)) * np.cos(a) - 3 * e_z * np.sin(3 * a) * np.sin(a)
        y = (d1_z / 2 - e_z * np.cos(3 * a)) * np.sin(a) + 3 * e_z * np.sin(3 * a) * np.cos(a)
        z = np.full_like(x, target_z)

        # Tangentes
        x_next, y_next = np.roll(x, -1), np.roll(y, -1)
        x_prev, y_prev = np.roll(x, 1), np.roll(y, 1)
        tx = x_next - x_prev
        ty = y_next - y_prev
        
        norm_t = np.sqrt(tx**2 + ty**2)
        tx, ty = tx / norm_t, ty / norm_t

        # Normales 2D
        nx_2d, ny_2d = ty, -tx

        # Étape 2 : Normales 3D incluant la dépouille
        # La normale pointe vers l'extérieur et est inclinée par rapport à Z
        nx_3d = nx_2d * np.cos(angle_depouille)
        ny_3d = ny_2d * np.cos(angle_depouille)
        nz_3d = np.full_like(nx_2d, np.sin(angle_depouille))

        return x, y, z, nx_3d, ny_3d, nz_3d

    def filter_profile(self, x, y, nx, ny, nz):
        """Étape 4 : Filtre le profil selon l'erreur de corde et l'angle."""
        intol = self.corde_var.get()
        delta_rad = np.radians(self.tol_ang_var.get())
        
        kept_indices = [0]
        curr = 0
        N = len(x)

        while curr < N - 1:
            best_valid = curr + 1
            next_idx = curr + 1
            
            while next_idx < N:
                # 1. Vérification angulaire
                dot_prod = nx[curr]*nx[next_idx] + ny[curr]*ny[next_idx] + nz[curr]*nz[next_idx]
                dot_prod = np.clip(dot_prod, -1.0, 1.0)
                angle_diff = np.arccos(dot_prod)
                
                if angle_diff > delta_rad:
                    break
                
                # 2. Vérification de l'erreur de corde
                x1, y1 = x[curr], y[curr]
                x2, y2 = x[next_idx], y[next_idx]
                dist_seg = np.hypot(x2 - x1, y2 - y1)
                
                valid_chord = True
                if dist_seg > 1e-6:
                    for k in range(curr + 1, next_idx):
                        x0, y0 = x[k], y[k]
                        # Distance point à segment en 2D (valide car Z est constant sur un profil)
                        d = abs((x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1)) / dist_seg
                        if d > intol:
                            valid_chord = False
                            break
                            
                if not valid_chord:
                    break
                    
                best_valid = next_idx
                next_idx += 1
                
            # Avancer au point validé
            if best_valid == curr:
                # Sécurité si intol est trop petit
                curr += 1
                kept_indices.append(curr)
            else:
                curr = best_valid
                kept_indices.append(curr)
                
        # S'assurer que le profil est bien fermé
        if kept_indices[-1] != N - 1:
            kept_indices.append(N - 1)
            
        return kept_indices

    def update_data(self):
        try:
            target_z = self.z_visu_var.get()
            x, y, z, nx, ny, nz = self.calculate_profile(target_z)
            
            # Application de l'étape 4 pour la visualisation
            kept_indices = self.filter_profile(x, y, nx, ny, nz)
            
            x_f = x[kept_indices]
            y_f = y[kept_indices]
            nx_f = nx[kept_indices]
            ny_f = ny[kept_indices]
            nz_f = nz[kept_indices]

            # Mise à jour graphique
            self.ax.clear()
            # Affichage du profil brut en fond
            self.ax.plot(x, y, color='lightgray', linestyle='--', label=f"Points d'origine ({len(x)})")
            # Affichage du profil filtré
            self.ax.plot(x_f, y_f, 'b-o', markersize=3, label=f"Profil filtré ({len(x_f)} pts)")
            
            # Affichage des normales sur les points conservés
            self.ax.quiver(x_f, y_f, nx_f, ny_f, color='r', alpha=0.6, scale=15, label='Normales 3D (X,Y)')

            self.ax.plot(x_f[0], y_f[0], 'go', markersize=8, label="Point de départ")
            self.ax.set_aspect('equal')
            self.ax.grid(True, linestyle=':', alpha=0.7)
            self.ax.set_title(f"Visualisation du filtrage à Z={target_z:.1f}mm\nRéduction: {len(x)} -> {len(x_f)} points")
            self.ax.legend(loc="upper right", fontsize="small")
            self.canvas.draw()

            # Mise à jour du tableau avec les points filtrés uniquement
            self.tree.delete(*self.tree.get_children())
            for i, idx in enumerate(kept_indices):
                row = (i, f"{x_f[i]:.4f}", f"{y_f[i]:.4f}", f"{z[idx]:.4f}", f"{nx_f[i]:.4f}", f"{ny_f[i]:.4f}", f"{nz_f[i]:.4f}")
                self.tree.insert("", tk.END, values=row)

        except Exception as err:
            print("Erreur lors de la mise à jour :", err)

    def generer_fichier(self):
        longueur = self.longueur_var.get()
        z_levels = np.linspace(0, -longueur, 11)
        filename = "profils_capto_filtres.ascii"
        
        try:
            total_points = 0
            with open(filename, "w") as f:
                for z_val in z_levels:
                    # On calcule
                    x, y, z, nx, ny, nz = self.calculate_profile(z_val)
                    # On filtre (Étape 4 appliquée à l'export !)
                    kept = self.filter_profile(x, y, nx, ny, nz)
                    
                    # On exporte les points filtrés
                    for idx in kept:
                        # Format classique X Y Z (ajuster si CATIA demande les normales dans ce fichier)
                        f.write(f"{x[idx]:.6f} {y[idx]:.6f} {z[idx]:.6f} {nx[idx]:.6f} {ny[idx]:.6f} {nz[idx]:.6f}\n")
                        total_points += 1
            
            messagebox.showinfo("Export réussi", f"Fichier généré !\n11 profils exportés.\nTotal points : {total_points}\nEnregistré sous : {filename}")
        except Exception as e:
            messagebox.showerror("Erreur d'export", f"Erreur pendant l'export : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptoGeneratorApp(root)
    root.mainloop()