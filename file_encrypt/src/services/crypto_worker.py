import argparse
import json
import os

import keyring

####
#
# Ajouter les imports manquants pour compléter le TP.
# Il s'agit de classes de la librairie cryptography.
# Vous n'avez rien à installer de plus. Tout devrait déjà
# être fait si vous avez réalisé correctement les étapes
# de configuration du TP (voir README.md)
#
# Exemple :
# from cryptography.hazmat.<...> import <...>
#
####

####
# Constantes pour keyring
# Vous ne devez pas modifier ces valeurs.
####
SERVICE_NAME = "UQAC-8INF138"
ACCOUNT_NAME = "TP2-APP"


class CryptoWorker:
    """
    Classe de gestion des opérations cryptographiques.

    Consigne générale : compléter les fonctions
    marquées d'un "TODO" sans utiliser de dépendances
    supplémentaires en vous aidant des "docstrings".
    """

    def __init__(self) -> None:
        self.aes_key = None
        self.hmac_key = None

    def _clean_memory(self) -> None:
        """
        Efface les variables aes_key et hmac_key
        qui contiennent les clés de la mémoire.

        Chaque octet des tableaux où
        sont stockés les clés doivent être mis à 0
        Les références doivent être libérées.

        Vous savez que cette fonction est
        à usage interne uniquement, à vous de
        déterminer quand et comment l'appeler.
        """

        # TODO: compléter la fonction.

        print("DEBUG: Nettoyage mémoire (fonction à implémenter pour le TP)")

    def _load_keys(self) -> None:
        """
        Charge les clés depuis le stockage sécurisé
        en utilisant la librairie keyring.

        Les clés doivent être converties
        en tableaux d'octets depuis
        leur représentation hexadécimale.

        Raises
        ------
        RuntimeError
            Si aucune clé n'est trouvée dans
            le stockage sécurisé.
        """

        # TODO: compléter la fonction.

        print("DEBUG: Chargement des clés (fonction à implémenter pour le TP)")

    def check_key(self):
        """
        Vérifie si une clé existe dans le
        stockage sécurisé via keyring.

        Retourne le résultat au format JSON
        sur la sortie standard (stdout) tel que :
        {"exists": True} ou {"exists": False}
        """

        # TODO: compléter la fonction.

        # Exemple de retour attendu (hardcodé
        # ici pour l'exemple).
        # Vous pouvez passer is_key à True ou
        # False pour tester le comportement
        # des autres parties de l'application.
        is_key = True
        print(json.dumps({"exists": bool(is_key)}))

    def generate_key(self) -> None:
        """
        Génère des clés AES et HMAC et les enregistre
        dans le stockage sécurisé via keyring.

        les clés doivent être initialisées en tant que tableaux
        d'octets de 256 bits aléatoires.

        Elles sont ensuite converties en hexadécimal
        et stockées dans keyring au format : <aes_hex>:<hmac_hex>
        """

        # TODO: compléter la fonction.

        print("DEBUG: Génération de clé (fonction à implémenter pour le TP)")

    def encrypt(self, input_path: str, output_path: str) -> None:
        """
        Chiffre un fichier avec AES-256-CBC
        et ajoute une authentification HMAC-SHA256.

        Paramètres
        ----------
        input_path : str
            Chemin du fichier à chiffrer.
        output_path : str
            Chemin du fichier chiffré de sortie.

        Étapes
        ------
        1. Charger les clés
        2. Lire le fichier d'entrée
        3. Appliquer un padding PKCS#7
        4. Générer IV aléatoire
        5. Chiffrer avec AES-256-CBC
        6. Calculer HMAC sur IV + ciphertext
        7. Écrire IV + ciphertext + HMAC dans le fichier de sortie
        """

        # TODO: compléter la fonction.

        print(
            f"DEBUG: Chiffrement de {input_path} vers {output_path} (fonction à implémenter pour le TP)"
        )

    def decrypt(self, input_path: str, output_path: str) -> None:
        """
        Déchiffre un fichier chiffré par
        AES-256-CBC et authentifié avec HMAC-SHA256.

        Paramètres
        ----------
        input_path : str
            Chemin du fichier chiffré.
        output_path : str
            Chemin du fichier déchiffré de sortie.

        Raises
        ------
        RuntimeError
            Si le fichier est invalide,
            corrompu ou si HMAC invalide.

        Étapes
        ------
        1. Charger les clés
        2. Lire le fichier d'entrée
        3. Vérifier la validité du fichier
        3. Vérifier HMAC
        4. Déchiffrer avec AES-256-CBC
        5. Dépadder avec PKCS#7
        6. Écrire les données déchiffrée
           dans le fichier de sortie
        """

        # TODO: compléter la fonction.

        print(
            f"DEBUG: Déchiffrement de {input_path} vers {output_path} (fonction à implémenter pour le TP)"
        )


def main() -> None:
    """
    Point d'entrée CLI du worker.

    Utilise argparse pour gérer les opérations :
    - check: vérifier existence clé
    - generate: générer clé AES/HMAC
    - encrypt: chiffrer un fichier
    - decrypt: déchiffrer un fichier

    Vous n'avez pas à modifier cette fonction.
    """
    parser = argparse.ArgumentParser(
        description="Worker des opérations cryptographiques"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--check", action="store_true")
    group.add_argument("-g", "--generate", action="store_true")
    group.add_argument("-e", "--encrypt", action="store_true")
    group.add_argument("-d", "--decrypt", action="store_true")

    parser.add_argument("--input", "-i", type=str)
    parser.add_argument("--output", "-o", type=str)

    args = parser.parse_args()

    worker = CryptoWorker()

    if args.check:
        if args.input or args.output:
            parser.error("Les paramètres input et output ne sont pas requis")
        worker.check_key()

    elif args.generate:
        if args.input or args.output:
            parser.error("Les paramètres input et output ne sont pas requis")
        worker.generate_key()

    elif args.encrypt:
        if not args.input or not args.output:
            parser.error("Les paramètres input et output sont requis")
        worker.encrypt(args.input, args.output)

    elif args.decrypt:
        if not args.input or not args.output:
            parser.error("Les paramètres input et output sont requis")
        worker.decrypt(args.input, args.output)


if __name__ == "__main__":
    main()
