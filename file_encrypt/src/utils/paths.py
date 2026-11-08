import os


class Paths:
    """
    Utilitaires de résolution des chemins du projet.

    Cette classe fournit des méthodes statiques permettant de
    localiser dynamiquement des composants du projet indépendamment
    du répertoire courant d'exécution.
    """

    @staticmethod
    def get_service_path(name: str) -> str:
        """
        Construit et retourne le chemin absolu d'un service du projet.

        Cette méthode permet de localiser un script de service situé
        dans le répertoire ``services`` du projet.

        Paramètres
        ----------
        name : str
            Nom du service (sans extension `.py`).

        Retours
        -------
        str
            Chemin absolu vers le fichier du service demandé.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "..", "services", f"{name}.py")
