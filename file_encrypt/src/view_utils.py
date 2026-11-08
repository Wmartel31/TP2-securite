import tkinter as tk

from utils import Time


class ViewUtils:
    """
    Classe utilitaire pour les opérations liées à
    l'interface utilisateur (GUI).
    """

    @staticmethod
    def log_message(widget: tk.Text, message: str) -> None:
        """
        Ajoute un message dans un widget Text avec horodatage.

        Paramètres
        ----------
        widget : tk.Text
            Le widget Text où afficher le message.
        message : str
            Le contenu du message à afficher.
        """
        widget.insert("end", f"{Time.now_time()} - {message}\n")
        widget.see("end")
