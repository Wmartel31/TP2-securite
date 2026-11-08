from datetime import datetime


class Time:
    """
    Utilitaires de gestion du temps et de l'horodatage.

    Cette classe fournit des méthodes statiques permettant de générer
    des représentations temporelles normalisées, notamment pour
    l'horodatage des journaux d'événements (logs).
    """

    @staticmethod
    def now_time() -> str:
        """
        Retourne l'horodatage courant formaté.

        L'horodatage est retourné sous la forme :
        ``[YYYY-MM-DD HH:MM:SS]``

        Retours
        -------
        str
            Chaîne représentant la date et l'heure courantes.
        """
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
