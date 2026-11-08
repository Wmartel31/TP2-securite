import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from services import WorkerRunner
from view_utils import ViewUtils

# Intervalle (ms) entre deux vérifications automatiques du statut de la clé.
KEY_STATUS_POLL_INTERVAL_MS = 500

# Intervalle (ms) de scrutation de la fin d'une vérification en arrière-plan.
KEY_STATUS_RESULT_POLL_MS = 50


class AppController:
    """
    Contrôleur de l'application Tkinter pour la gestion des fichiers chiffrés.

    Cette classe encapsule toute la logique métier liée à l'interface utilisateur.
    Elle interagit avec WorkerRunner pour les opérations cryptographiques et
    met à jour l'interface via l'objet Tkinter app.
    """

    def __init__(self, app: tk.Tk) -> None:
        """
        Initialise le contrôleur avec l'instance Tkinter de l'application.

        Paramètres
        ----------
        app : tk.Tk
            Instance de l'application Tkinter à contrôler.
        """
        self.app = app

        # Dernier statut affiché (None tant qu'aucune vérification n'a abouti).
        self._key_exists: bool | None = None

        # Incrémenté à chaque vérification synchrone : permet d'ignorer le
        # résultat d'une vérification en arrière-plan lancée avant celle-ci.
        self._status_version = 0

        self._check_running = False

    def check_key_status(self) -> None:
        """
        Vérifie l'existence d'une clé AES+HMAC dans le stockage sécurisé.

        Met à jour l'interface utilisateur en fonction du résultat :
            - Affiche un message de statut
            - Active/désactive les boutons de chiffrement/déchiffrement
            - Active/désactive le bouton de génération de clé
        """
        self._status_version += 1

        result = WorkerRunner.run("crypto_worker", "check")

        self._apply_key_status(isinstance(result, dict) and bool(result.get("exists")))

    def start_key_status_monitor(self) -> None:
        """
        Démarre la surveillance en temps réel du statut de la clé.

        Le stockage sécurisé ne signale pas à l'application l'ajout ou la
        suppression d'une entrée par un outil externe (p. ex. Keychain Access
        ou le Credential Manager). Le statut est donc revérifié :
            - périodiquement, toutes les KEY_STATUS_POLL_INTERVAL_MS ms ;
            - dès que la fenêtre reprend le focus.

        Chaque vérification s'exécute dans un thread séparé afin de ne pas
        bloquer l'interface ; l'interface n'est modifiée que depuis le thread
        principal de Tkinter.
        """
        self.app.bind("<FocusIn>", self._on_focus_in, add="+")
        self._poll_key_status()

    def _poll_key_status(self) -> None:
        """
        Lance une vérification en arrière-plan puis replanifie la suivante.
        """
        self._refresh_key_status_async()
        self.app.after(KEY_STATUS_POLL_INTERVAL_MS, self._poll_key_status)

    def _on_focus_in(self, _event: tk.Event) -> None:
        """
        Revérifie le statut de la clé lorsque la fenêtre reprend le focus.
        """
        self._refresh_key_status_async()

    def _refresh_key_status_async(self) -> None:
        """
        Vérifie l'existence de la clé dans un thread séparé.

        Ne fait rien si une vérification est déjà en cours.
        """
        if self._check_running:
            return

        self._check_running = True

        version = self._status_version
        outcome: dict = {}

        def worker() -> None:
            outcome["result"] = WorkerRunner.run("crypto_worker", "check")

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        self.app.after(
            KEY_STATUS_RESULT_POLL_MS,
            self._collect_key_status,
            thread,
            outcome,
            version,
        )

    def _collect_key_status(
        self, thread: threading.Thread, outcome: dict, version: int
    ) -> None:
        """
        Récupère, dans le thread principal, le résultat d'une vérification
        lancée en arrière-plan et met à jour l'interface si nécessaire.

        Le résultat est ignoré si le worker a échoué ou si une vérification
        synchrone plus récente a eu lieu entre-temps (p. ex. après la
        génération d'une clé).
        """
        if thread.is_alive():
            self.app.after(
                KEY_STATUS_RESULT_POLL_MS,
                self._collect_key_status,
                thread,
                outcome,
                version,
            )
            return

        self._check_running = False

        result = outcome.get("result")

        if version != self._status_version or not isinstance(result, dict):
            return

        self._apply_key_status(bool(result.get("exists")))

    def _apply_key_status(self, exists: bool) -> None:
        """
        Met à jour l'interface selon la présence ou non d'une clé.

        L'interface n'est modifiée que si le statut a changé depuis le
        dernier affichage.

        Paramètres
        ----------
        exists : bool
            True si une clé est présente dans le stockage sécurisé.
        """
        if exists == self._key_exists:
            return

        self._key_exists = exists

        if exists:
            self.app.key_status_label.config(
                text="Clé disponible dans le stockage sécurisé", fg="green"
            )

            self.app.generate_button.config(state="disabled")
            self.app.set_crypto_buttons(True)
        else:
            self.app.key_status_label.config(
                text="Aucune clé trouvée. Générer une nouvelle clé !", fg="red"
            )

            self.app.generate_button.config(state="normal")
            self.app.set_crypto_buttons(False)

    def generate_key(self) -> None:
        """
        Génère une nouvelle clé AES+HMAC.

        Après la génération :
            - Vérifie le statut de la clé
            - Met à jour l'interface utilisateur
            - Affiche un message d'information ou d'erreur selon le résultat
        """
        if WorkerRunner.run("crypto_worker", "generate"):
            self.check_key_status()

            messagebox.showinfo(
                "Succès", "Clé générée et sauvegardée dans le stockage sécurisé."
            )
        else:
            messagebox.showerror("Erreur", "Impossible de générer une clé.")

    def encrypt_file(self) -> None:
        """
        Lance le processus de chiffrement d'un fichier sélectionné par l'utilisateur.

        Étapes :
            1. Demande à l'utilisateur de sélectionner un fichier à chiffrer.
            2. Vérifie que le fichier n'est pas déjà chiffré (.dcrypt).
            3. Demande à l'utilisateur le chemin de sortie.
            4. Appelle WorkerRunner pour chiffrer le fichier.
            5. Affiche un message d'erreur ou enregistre l'opération dans le log.
        """
        input_file = filedialog.askopenfilename(
            title="Sélectionner un fichier à chiffrer"
        )

        if not input_file:
            return

        if input_file.lower().endswith(".dcrypt"):
            messagebox.showerror("Erreur", "Le fichier a déjà été chiffré.")
            return

        output_file = filedialog.asksaveasfilename(
            title="Enregistrer le fichier chiffré",
            initialfile=os.path.basename(input_file) + ".dcrypt",
        )

        if not output_file:
            return

        if WorkerRunner.run("crypto_worker", "encrypt", input_file, output_file):
            ViewUtils.log_message(self.app.log_list, f"Chiffrement : {output_file}")
        else:
            messagebox.showerror("Erreur", "Impossible de chiffrer le fichier")

    def decrypt_file(self) -> None:
        """
        Lance le processus de déchiffrement d'un fichier sélectionné par l'utilisateur.

        Étapes :
            1. Demande à l'utilisateur de sélectionner un fichier chiffré (.dcrypt).
            2. Propose un nom de fichier de sortie par défaut.
            3. Appelle WorkerRunner pour déchiffrer le fichier.
            4. Affiche un message d'erreur ou enregistre l'opération dans le log.
        """
        input_file = filedialog.askopenfilename(
            title="Sélectionner un fichier à déchiffrer",
            filetypes=[("Fichiers chiffrés", "*.dcrypt")],
        )

        if not input_file:
            return

        default_name = os.path.basename(input_file).replace(".dcrypt", "")

        output_file = filedialog.asksaveasfilename(
            title="Enregistrer le fichier déchiffré", initialfile=default_name
        )

        if not output_file:
            return

        if WorkerRunner.run("crypto_worker", "decrypt", input_file, output_file):
            ViewUtils.log_message(self.app.log_list, f"Déchiffrement : {output_file}")
        else:
            messagebox.showerror("Erreur", "Impossible de déchiffrer le fichier")
