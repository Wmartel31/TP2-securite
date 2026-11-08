import json
import subprocess
import sys
from typing import Optional, Union

from utils import Paths


class WorkerRunner:
    """
    Classe utilitaire pour exécuter
    les workers dans un processus séparé.
    """

    @staticmethod
    def run(
        worker: str,
        action: str,
        input_path: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Union[bool, dict]:
        """
        Exécute un worker en sous-processus.

        Paramètres
        ----------
        worker : str
            Nom du worker (ex. "crypto_worker")
        action : str
            Action à exécuter : "check", "generate", "encrypt", "decrypt"
        input_path : Optional[str]
            Chemin du fichier d'entrée pour encrypt/decrypt
        output_path : Optional[str]
            Chemin du fichier de sortie pour encrypt/decrypt

        Retour
        ------
        bool
            Pour generate / encrypt / decrypt : True si succès, False sinon
        dict[str, bool]
            Pour check : {"exists": True/False}
        """
        worker_path = Paths.get_service_path(worker)
        cmd = [sys.executable, worker_path]

        if action == "check":
            cmd.append("--check")

        elif action == "generate":
            cmd.append("--generate")

        elif action in ("encrypt", "decrypt"):
            if not input_path or not output_path:
                return False
            cmd += [f"--{action}", "--input", input_path, "--output", output_path]
        else:
            return False

        try:
            if action == "check":
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return json.loads(result.stdout)

            subprocess.run(cmd, check=True)
            return True

        except subprocess.CalledProcessError as error:
            print(f"Erreur d'exécution du worker : {error}")
            return False
        except json.JSONDecodeError as error:
            print(f"Erreur de décodage JSON : {error}")
            return False
