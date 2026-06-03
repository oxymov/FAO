import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CaptoGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FAO - Générateur Profil Capto & Usinage")
        self.root.geometry("1450x900")

        # Variables Profil
        self.d1_var = tk.DoubleVar(value=38.0)
        self.e_var = tk.DoubleVar(value=2.0)
        self.nb_pt_var = tk.IntVar(value=1000)
        
        # Variables Tolérances
        self.corde_var = tk.DoubleVar(value=0.01)
        self.tol_ang_var = tk.DoubleVar(value=2.0)
        
        # Variables 3D & Outil
        self.angle_var = tk.DoubleVar(value=5.0)
        self.longueur_var = tk.DoubleVar(value=50.0)
        self.rayon_var = tk.DoubleVar(value=5.0)
        self.dist_approche_var = tk.DoubleVar(value=10.0)
        
        # Variables Visu & Export
        self.z_visu_var = tk.DoubleVar(value=0.0)
        self.type_export_var = tk.StringVar(value="piece")
        self.normale_export_var = tk.BooleanVar(value=True)

        self.create_widgets()
        self.update_data()

    def create_widgets(self):
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        def bind_enter(widget):
            widget.bind("<Return>", lambda event: self.update_data())

        # --- PARAMETRES GEOMETRIQUES ---
        profil_frame = tk.LabelFrame(left_frame, text="Géométrie Profil (2D)", padx=10, pady=5)
        profil_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(profil_frame, text="d1 (mm):").grid(row=0, column=0, sticky="w")
        e1 = tk.Entry(profil_frame, textvariable=self.d1_var, width=10); e1.grid(row=0, column=1); bind_enter(e1)
        tk.Label(profil_frame, text="e (Excentricité):").grid(row=1, column=0, sticky="w")
        e2 = tk.Entry(profil_frame, textvariable=self.e_var, width=10); e2.grid(row=1, column=1); bind_enter(e2)
        tk.Label(profil_frame, text="Points initiaux:").grid(row=2, column=0, sticky="w")
        e3 = tk.Entry(profil_frame, textvariable=self.nb_pt_var, width=10); e3.grid(row=2, column=1); bind_enter(e3)

        z_frame = tk.LabelFrame(left_frame, text="Volume & Dépouille (3D)", padx=10, pady=5)
        z_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(z_frame, text="Angle Dépouille (°):").grid(row=0, column=0, sticky="w")
        e4 = tk.Entry(z_frame, textvariable=self.angle_var, width=10); e4.grid(row=0, column=1); bind_enter(e4)
        tk.Label(z_frame, text="Hauteur h (mm):").grid(row=1, column=0, sticky="w")
        e5 = tk.Entry(z_frame, textvariable=self.longueur_var, width=10); e5.grid(row=1, column=1); bind_enter(e5)

        outil_frame = tk.LabelFrame(left_frame, text="Correction Outil (Étape 5 & 6)", padx=10, pady=5)
        outil_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(outil_frame, text="Rayon Outil R (mm):").grid(row=0, column=0, sticky="w")
        e6 = tk.Entry(outil_frame, textvariable=self.rayon_var, width=10); e6.grid(row=0, column=1); bind_enter(e6)
        tk.Label(outil_frame, text="Dist. approche (mm):").grid(row=1, column=0, sticky="w")
        e7 = tk.Entry(outil_frame, textvariable=self.dist_approche_var, width=10); e7.grid(row=1, column=1); bind_enter(e7)

        filtre_frame = tk.LabelFrame(left_frame, text="Filtrage & Tolérances (Étape 4)", padx=10, pady=5)
        filtre_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(filtre_frame, text="Tol. Corde (mm):").grid(row=0, column=0, sticky="w")
        e8 = tk.Entry(filtre_frame, textvariable=self.corde_var, width=10); e8.grid(row=0, column=1); bind_enter(e8)
        tk.Label(filtre_frame, text="Tol. Angle (°):").grid(row=1, column=0, sticky="w")
        e9 = tk.Entry(filtre_frame, textvariable=self.tol_ang_var, width=10); e9.grid(row=1, column=1); bind_enter(e9)
        self.lbl_info_filtre = tk.Label(filtre_frame, text="Points conservés : - / -", fg="#d32f2f", font=("Arial", 9, "bold"))
        self.lbl_info_filtre.grid(row=2, column=0, columnspan=2, pady=5)

        # --- ACTIONS & EXPORT ---
        action_frame = tk.Frame(left_frame, pady=5)
        action_frame.pack(fill=tk.X)
        tk.Label(action_frame, text="Aperçu plan Z:").grid(row=0, column=0, sticky="w")
        self.z_scale = tk.Scale(action_frame, variable=self.z_visu_var, from_=0, to=-self.longueur_var.get(), 
                                resolution=0.1, orient=tk.HORIZONTAL, command=lambda val: self.update_data())
        self.z_scale.grid(row=0, column=1, sticky="ew")
        tk.Button(action_frame, text="Actualiser Visuel", command=self.update_data, bg="#2196F3", fg="white").grid(row=1, columnspan=2, pady=5, sticky="we")

        export_frame = tk.LabelFrame(left_frame, text="Exportation ASCII", padx=10, pady=5)
        export_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Radiobutton(export_frame, text="Profil Pièce brut (CATIA)", variable=self.type_export_var, value="piece").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(export_frame, text="Trajectoire Outil (Usinage)", variable=self.type_export_var, value="outil").grid(row=1, column=0, sticky="w")
        tk.Checkbutton(export_frame, text="Inclure Normales (6 colonnes)", variable=self.normale_export_var).grid(row=2, column=0, sticky="w", pady=(5,0))
        tk.Button(export_frame, text="Générer Fichier ASCII", command=self.generer_fichier_ui, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=3, column=0, pady=10, sticky="we")

        # --- TABLEAU ---
        table_frame = tk.LabelFrame(left_frame, text="Données (Trajectoire Outil Affichée)")
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("Type", "X", "Y", "Z", "Nx", "Ny", "Nz")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=50, anchor="center")
        self.tree.column("Type", width=75)
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # --- GRAPHIQUE ---
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_profile(self, target_z):
        d1 = self.d1_var.get()
        e = self.e_var.get()
        nb_pt = self.nb_pt_var.get()
        angle_depouille = np.radians(self.angle_var.get())
        R = self.rayon_var.get()

        d1_z = d1 + 2 * abs(target_z) * np.tan(angle_depouille)
        e_z = e * (d1_z / d1)
        a = np.linspace(0, 2 * np.pi, nb_pt)
        
        x = (d1_z / 2 - e_z * np.cos(3 * a)) * np.cos(a) - 3 * e_z * np.sin(3 * a) * np.sin(a)
        y = (d1_z / 2 - e_z * np.cos(3 * a)) * np.sin(a) + 3 * e_z * np.sin(3 * a) * np.cos(a)
        z = np.full_like(x, target_z)

        dx = np.gradient(x)
        dy = np.gradient(y)
        norm_2d = np.hypot(dx, dy)
        
        nx_2d = dy / norm_2d
        ny_2d = -dx / norm_2d

        nx_3d = nx_2d * np.cos(angle_depouille)
        ny_3d = ny_2d * np.cos(angle_depouille)
        nz_3d = np.full_like(nx_2d, np.sin(angle_depouille))

        # Centre outil complet (Décalage du rayon)
        xc = x + R * nx_2d
        yc = y + R * ny_2d
        zc = z

        return x, y, z, nx_3d, ny_3d, nz_3d, xc, yc, zc

    def filter_profile(self, x, y, nx, ny, nz):
        intol = self.corde_var.get()
        delta_rad = np.radians(self.tol_ang_var.get())
        kept_indices = [0]
        curr = 0
        N = len(x)

        while curr < N - 1:
            best_valid = curr + 1
            next_idx = curr + 1
            while next_idx < N:
                dot_prod = np.clip(nx[curr]*nx[next_idx] + ny[curr]*ny[next_idx] + nz[curr]*nz[next_idx], -1.0, 1.0)
                if np.arccos(dot_prod) > delta_rad:
                    break
                
                x1, y1 = x[curr], y[curr]
                x2, y2 = x[next_idx], y[next_idx]
                dist_seg = np.hypot(x2 - x1, y2 - y1)
                
                if dist_seg > 1e-8 and next_idx > curr + 1:
                    d_array = np.abs((x2 - x1) * (y[curr+1:next_idx] - y1) - (x[curr+1:next_idx] - x1) * (y2 - y1)) / dist_seg
                    if np.any(d_array > intol):
                        break 
                        
                best_valid = next_idx
                next_idx += 1
                
            curr = best_valid
            kept_indices.append(curr)
            
        if kept_indices[-1] != N - 1:
            kept_indices.append(N - 1)
            
        return kept_indices

    def add_approach_retract(self, xc_f, yc_f, zc_f):
        dist_app = self.dist_approche_var.get()

        tx_start = xc_f[1] - xc_f[0]
        ty_start = yc_f[1] - yc_f[0]
        norm_start = np.hypot(tx_start, ty_start)
        tx_start, ty_start = tx_start / norm_start, ty_start / norm_start

        x_app = xc_f[0] - dist_app * tx_start
        y_app = yc_f[0] - dist_app * ty_start

        tx_end = xc_f[-1] - xc_f[-2]
        ty_end = yc_f[-1] - yc_f[-2]
        norm_end = np.hypot(tx_end, ty_end)
        tx_end, ty_end = tx_end / norm_end, ty_end / norm_end

        x_ret = xc_f[-1] + dist_app * tx_end
        y_ret = yc_f[-1] + dist_app * ty_end

        return x_app, y_app, zc_f[0], x_ret, y_ret, zc_f[-1]

    def update_data(self):
        try:
            self.z_scale.configure(to=-self.longueur_var.get())
            target_z = self.z_visu_var.get()
            
            x, y, z, nx, ny, nz, xc, yc, zc = self.calculate_profile(target_z)
            kept = self.filter_profile(x, y, nx, ny, nz)
            
            self.lbl_info_filtre.config(text=f"Points conservés : {len(kept)} / {len(x)}")
            
            x_f, y_f = x[kept], y[kept]
            xc_f, yc_f, zc_f = xc[kept], yc[kept], zc[kept]
            nx_f, ny_f, nz_f = nx[kept], ny[kept], nz[kept]

            x_app, y_app, z_app, x_ret, y_ret, z_ret = self.add_approach_retract(xc_f, yc_f, zc_f)

            self.ax.clear()
            self.ax.plot(x, y, color='tab:blue', alpha=0.4, linestyle=':', label="Géométrie brute de la pièce")
            self.ax.plot(x_f, y_f, 'b-', linewidth=1.5, label="Profil de contact (Fraise/Pièce)")
            self.ax.plot(xc_f, yc_f, 'r--', linewidth=1.2, label="Trajectoire Point Piloté (Centre outil)")
            self.ax.plot(xc_f, yc_f, 'ro', markersize=3)
            self.ax.plot([x_app, xc_f[0]], [y_app, yc_f[0]], 'g-o', linewidth=2, label="Approche")
            self.ax.plot([xc_f[-1], x_ret], [yc_f[-1], y_ret], 'm-s', linewidth=2, label="Retrait")

            for i in range(0, len(x_f), max(1, len(x_f)//30)):
                self.ax.plot([x_f[i], xc_f[i]], [y_f[i], yc_f[i]], color='gray', alpha=0.5, linewidth=0.8)

            self.ax.set_aspect('equal')
            self.ax.grid(True, linestyle=':', alpha=0.6)
            self.ax.set_title(f"Z = {target_z:.1f} mm | Décalage outil appliqué : +{self.rayon_var.get()} mm")
            self.ax.legend(loc="upper right", fontsize="small")
            self.canvas.draw()

            self.tree.delete(*self.tree.get_children())
            self.tree.insert("", tk.END, values=("APPROCHE", f"{x_app:.3f}", f"{y_app:.3f}", f"{z_app:.3f}", f"{nx_f[0]:.3f}", f"{ny_f[0]:.3f}", f"{nz_f[0]:.3f}"))
            for i in range(len(kept)):
                self.tree.insert("", tk.END, values=("USINAGE", f"{xc_f[i]:.3f}", f"{yc_f[i]:.3f}", f"{zc_f[i]:.3f}", f"{nx_f[i]:.3f}", f"{ny_f[i]:.3f}", f"{nz_f[i]:.3f}"))
            self.tree.insert("", tk.END, values=("RETRAIT", f"{x_ret:.3f}", f"{y_ret:.3f}", f"{z_ret:.3f}", f"{nx_f[-1]:.3f}", f"{ny_f[-1]:.3f}", f"{nz_f[-1]:.3f}"))

        except Exception as err:
            print("Erreur globale détectée :", err)

    def generer_fichier_ui(self):
        mode = self.type_export_var.get()
        avec_normales = self.normale_export_var.get()
        self.generer_fichier(mode, avec_normales)

    def generer_fichier(self, mode, avec_normales):
        longueur = self.longueur_var.get()
        z_levels = np.linspace(0, -longueur, 11)
        
        prefix = "profil_piece" if mode == "piece" else "trajectoire_outil"
        suffix = "6col" if avec_normales else "3col"
        filename = f"{prefix}_{suffix}.ascii"
        
        try:
            total_points = 0
            with open(filename, "w") as f:
                for z_val in z_levels:
                    x, y, z, nx, ny, nz, xc, yc, zc = self.calculate_profile(z_val)
                    kept = self.filter_profile(x, y, nx, ny, nz)
                    
                    if mode == "piece":
                        x_f, y_f, z_f = x[kept], y[kept], z[kept]
                        nx_f, ny_f, nz_f = nx[kept], ny[kept], nz[kept]
                        
                        for idx in range(len(kept)):
                            # Anti-doublon: Ignore le dernier point s'il boucle sur le premier
                            if idx == len(kept) - 1 and np.allclose([x_f[idx], y_f[idx]], [x_f[0], y_f[0]]):
                                continue
                                
                            if avec_normales:
                                f.write(f"{x_f[idx]:.6f} {y_f[idx]:.6f} {z_f[idx]:.6f} {nx_f[idx]:.6f} {ny_f[idx]:.6f} {nz_f[idx]:.6f}\n")
                            else:
                                f.write(f"{x_f[idx]:.6f} {y_f[idx]:.6f} {z_f[idx]:.6f}\n")
                            total_points += 1
                            
                    elif mode == "outil":
                        xc_f, yc_f, zc_f = xc[kept], yc[kept], zc[kept]
                        nx_f, ny_f, nz_f = nx[kept], ny[kept], nz[kept]
                        x_app, y_app, z_app, x_ret, y_ret, z_ret = self.add_approach_retract(xc_f, yc_f, zc_f)
                        
                        # Point d'approche
                        if avec_normales:
                            f.write(f"{x_app:.6f} {y_app:.6f} {z_app:.6f} {nx_f[0]:.6f} {ny_f[0]:.6f} {nz_f[0]:.6f}\n")
                        else:
                            f.write(f"{x_app:.6f} {y_app:.6f} {z_app:.6f}\n")
                        total_points += 1
                        
                        # Trajectoire de coupe
                        for idx in range(len(kept)):
                            if avec_normales:
                                f.write(f"{xc_f[idx]:.6f} {yc_f[idx]:.6f} {zc_f[idx]:.6f} {nx_f[idx]:.6f} {ny_f[idx]:.6f} {nz_f[idx]:.6f}\n")
                            else:
                                f.write(f"{xc_f[idx]:.6f} {yc_f[idx]:.6f} {zc_f[idx]:.6f}\n")
                            total_points += 1
                            
                        # Point de retrait
                        if avec_normales:
                            f.write(f"{x_ret:.6f} {y_ret:.6f} {z_ret:.6f} {nx_f[-1]:.6f} {ny_f[-1]:.6f} {nz_f[-1]:.6f}\n")
                        else:
                            f.write(f"{x_ret:.6f} {y_ret:.6f} {z_ret:.6f}\n")
                        total_points += 1

                    # Ligne vide pour scinder les trajectoires Z
                    f.write("\n")
            
            msg = f"Fichier '{filename}' généré avec succès.\nTotal : {total_points} points."
            if mode == "piece":
                msg += "\n(Points d'approche et doublons retirés pour CATIA)."
            messagebox.showinfo("Exportation Terminée", msg)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec lors de l'écriture : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptoGeneratorApp(root)
    root.mainloop()
