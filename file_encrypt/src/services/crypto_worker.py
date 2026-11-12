import argparse
import json
import os

import keyring
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

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

####
# Tailles (en octets) utilisées par le format des fichiers .dcrypt :
# IV (16) || cryptogramme (multiple de 16) || tag HMAC-SHA256 (32)
####
IV_SIZE = 16
BLOCK_SIZE = 16
TAG_SIZE = 32


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

        # mettre à zéro chaque octet des clés et libérer les références
        if self.aes_key is not None:
            for i in range(len(self.aes_key)):
                self.aes_key[i] = 0

        if self.hmac_key is not None:
            for i in range(len(self.hmac_key)):
                self.hmac_key[i] = 0

        self.aes_key = None
        self.hmac_key = None

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

        key = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)

        if key is None:
            raise RuntimeError("Aucune clé trouvée dans le stockage sécurisé.")
        else:
            aes_key_hex, hmac_key_hex = key.split(":")
            self.aes_key = bytearray.fromhex(aes_key_hex)
            self.hmac_key = bytearray.fromhex(hmac_key_hex)

    def check_key(self):
        """
        Vérifie si une clé existe dans le
        stockage sécurisé via keyring.

        Retourne le résultat au format JSON
        sur la sortie standard (stdout) tel que :
        {"exists": True} ou {"exists": False}
        """

        key = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)

        if key is None:
            is_key = False
        else:
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

        # CLé AES et HMAC de 256 bits
        self.aes_key = bytearray(os.urandom(32))
        self.hmac_key = bytearray(os.urandom(32))

        # Conversion en hexadécimal
        aes_hex = self.aes_key.hex()
        hmac_hex = self.hmac_key.hex()

        # Stockage dans keyring
        keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, aes_hex + ":" + hmac_hex)

        self._clean_memory()

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

        Usage d'IA générative
        ---------------------
        Fonction écrite avec l'aide de Claude (Anthropic), puis relue
        et testée par l'équipe.

        Prompt
        ------
            1. [Conversation Discord avec William collée telle quelle,
               où il demande où j'en suis dans le devoir]
            2. "https://github.com/Wmartel31/TP2-securite"
               (en réponse à Claude qui proposait d'écrire encrypt et
               decrypt à partir du code de William)
        """

        try:
            # 1. Charger les clés (bytearray de 32 octets chacune)
            self._load_keys()

            # 2. Lire le fichier d'entrée
            with open(input_path, "rb") as file:
                plaintext = file.read()

            # 3. Padding PKCS#7 sur des blocs de 128 bits.
            # Un bloc complet est ajouté si la taille est déjà
            # un multiple de 16 octets.
            padder = padding.PKCS7(BLOCK_SIZE * 8).padder()
            padded = padder.update(plaintext) + padder.finalize()

            # 4. IV aléatoire et unique pour chaque chiffrement
            iv = os.urandom(IV_SIZE)

            # 5. Chiffrement AES-256-CBC
            encryptor = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv)).encryptor()
            ciphertext = encryptor.update(padded) + encryptor.finalize()

            # 6. HMAC-SHA256 sur IV + cryptogramme (Encrypt-then-MAC),
            # avec une clé distincte de la clé AES
            mac = hmac.HMAC(self.hmac_key, hashes.SHA256())
            mac.update(iv + ciphertext)
            tag = mac.finalize()

            # 7. Écriture : IV || cryptogramme || tag
            with open(output_path, "wb") as file:
                file.write(iv + ciphertext + tag)

        finally:
            # Les clés sont effacées de la mémoire, même en cas d'erreur
            self._clean_memory()

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

        Usage d'IA générative
        ---------------------
        Fonction écrite avec l'aide de Claude (Anthropic), puis relue
        et testée par l'équipe.

        Prompt
        ------
            1. [Conversation Discord avec William collée telle quelle,
               où il demande où j'en suis dans le devoir]
            2. "https://github.com/Wmartel31/TP2-securite"
               (en réponse à Claude qui proposait d'écrire encrypt et
               decrypt à partir du code de William)
        """

        # Même message pour toutes les erreurs : l'attaquant ne doit
        # pas savoir si c'est le format, le HMAC ou le padding qui
        # a échoué (sinon, risque d'attaque par oracle de padding).
        error_message = "Fichier invalide, corrompu ou HMAC invalide."

        try:
            # 1. Charger les clés
            self._load_keys()

            # 2. Lire le fichier d'entrée
            with open(input_path, "rb") as file:
                data = file.read()

            # 3. Vérifier la validité du fichier : au minimum
            # IV (16) + un bloc (16) + tag (32) = 64 octets, et un
            # cryptogramme dont la taille est un multiple de 16.
            ciphertext_size = len(data) - IV_SIZE - TAG_SIZE
            if ciphertext_size < BLOCK_SIZE or ciphertext_size % BLOCK_SIZE != 0:
                raise RuntimeError(error_message)

            iv = data[:IV_SIZE]
            ciphertext = data[IV_SIZE:-TAG_SIZE]
            tag = data[-TAG_SIZE:]

            # 4. Vérifier le HMAC AVANT tout déchiffrement.
            # verify() compare en temps constant.
            mac = hmac.HMAC(self.hmac_key, hashes.SHA256())
            mac.update(iv + ciphertext)
            try:
                mac.verify(tag)
            except InvalidSignature:
                raise RuntimeError(error_message) from None

            # 5. Déchiffrement AES-256-CBC
            decryptor = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv)).decryptor()
            padded = decryptor.update(ciphertext) + decryptor.finalize()

            # 6. Retirer le padding PKCS#7
            unpadder = padding.PKCS7(BLOCK_SIZE * 8).unpadder()
            try:
                plaintext = unpadder.update(padded) + unpadder.finalize()
            except ValueError:
                raise RuntimeError(error_message) from None

            # 7. Écrire le fichier de sortie, seulement si tout a réussi
            with open(output_path, "wb") as file:
                file.write(plaintext)

        finally:
            # Les clés sont effacées de la mémoire, même en cas d'erreur
            self._clean_memory()


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
