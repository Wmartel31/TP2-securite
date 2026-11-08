import tkinter as tk
from tkinter import scrolledtext

from controller import AppController

WINDOW_WIDTH = 720
WINDOW_HEIGHT = 500


class App(tk.Tk):
    """
    Classe principale de l'application Tkinter pour la gestion des fichiers
    chiffrés AES-256 CBC.

    Cette classe crée l'interface utilisateur avec les boutons pour générer les clés,
    chiffrer et déchiffrer des fichiers, et afficher l'historique des opérations.
    La logique métier est déléguée à AppController.
    """

    def __init__(self) -> None:
        """
        Initialise l'interface Tkinter, crée les widgets, centre la fenêtre et
        vérifie l'état de la clé via le contrôleur.

        La fenêtre est masquée pendant sa construction puis affichée une fois
        centrée : sur macOS, elle apparaîtrait sinon brièvement à sa position
        par défaut avant d'être déplacée au centre de l'écran.
        """
        super().__init__()
        self.withdraw()
        self.attributes("-alpha", 0.0)

        self.title("8INF138 - TP2")

        self.controller = AppController(self)

        self._create_widgets()
        self._center_window(self, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.controller.check_key_status()

        self.update_idletasks()
        self.deiconify()

        self.after(50, self._reveal_window)

        self.controller.start_key_status_monitor()

    def _create_widgets(self) -> None:
        """
        Crée tous les widgets de l'interface : labels, boutons, cadres et zone
        de log. Configure également la disposition des boutons et des frames.
        """
        self.key_status_label = tk.Label(
            self, text="Vérification du statut de la clé...", fg="blue"
        )

        self.key_status_label.pack(pady=25)

        frame_keys = tk.Frame(self)
        frame_keys.pack(pady=5)

        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="x")

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        self.generate_button = tk.Button(
            main_frame,
            text="Générer clés AES et HMAC",
            height=2,
            command=self.controller.generate_key,
        )

        self.generate_button.grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10)
        )

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        self.encrypt_button = tk.Button(
            main_frame,
            text="Chiffrer un fichier",
            state=tk.DISABLED,
            height=2,
            command=self.controller.encrypt_file,
        )

        self.encrypt_button.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        self.decrypt_button = tk.Button(
            main_frame,
            text="Déchiffrer un fichier",
            state=tk.DISABLED,
            height=2,
            command=self.controller.decrypt_file,
        )

        self.decrypt_button.grid(row=1, column=1, sticky="ew", padx=(5, 0))

        tk.Label(self, text="Historique des fichiers :").pack(pady=(10, 0))

        self.log_list = scrolledtext.ScrolledText(self, width=90, height=15)

        self.log_list.pack(pady=5)
        self.log_list.see("end")

    def _center_window(
        self, window: tk.Tk | tk.Toplevel, width: int, height: int
    ) -> None:
        """
        Dimensionne la fenêtre et la place au milieu de l'écran.

        La position est calculée sans afficher la fenêtre (pas d'appel à
        ``update_idletasks``), ce qui permet de l'appeler alors que la fenêtre
        est encore masquée (``withdraw``).

        Paramètres
        ----------
        window : tk.Tk | tk.Toplevel
            La fenêtre Tkinter à centrer.
        width : int
            Largeur souhaitée de la fenêtre, en pixels.
        height : int
            Hauteur souhaitée de la fenêtre, en pixels.
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x}+{y}")

    def _reveal_window(self) -> None:
        """
        Affiche la fenêtre une fois centrée.

        Sur macOS, le gestionnaire de fenêtres peut placer la fenêtre à sa
        position par défaut lors de deiconify(). On la recentre donc pendant
        qu'elle est encore transparente, puis on la rend visible.
        """
        self._center_window(self, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.update_idletasks()
        self.attributes("-alpha", 1.0)
        self.lift()

    def set_crypto_buttons(self, enabled: bool) -> None:
        """
        Active ou désactive les boutons de chiffrement et déchiffrement.

        Paramètres
        ----------
        enabled : bool
            Si True, active les boutons ; sinon, les désactive.
        """
        state = "normal" if enabled else "disabled"
        self.encrypt_button.config(state=state)
        self.decrypt_button.config(state=state)


if __name__ == "__main__":
    app = App()
    app.mainloop()
