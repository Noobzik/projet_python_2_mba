"""
Script de configuration et vérification de l'environnement.

Ce script vérifie que l'environnement est correctement configuré
et prépare l'application au démarrage.
"""

import sys
from pathlib import Path


def check_python_version() -> bool:
    """
    Vérifie la version de Python.

    Returns
    -------
    bool
        True si la version est compatible
    """
    if sys.version_info < (3, 12):
        print("❌ Python 3.12 ou supérieur est requis")
        print(f"Version actuelle: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True


def check_data_files() -> bool:
    """
    Vérifie la présence des fichiers de données.

    Returns
    -------
    bool
        True si les fichiers requis sont présents
    """
    data_dir: Path = Path(__file__).parent / "data"
    required_files: list[str] = ["transactions_data.csv"]
    optional_files: list[str] = [
        "users_data.csv",
        "cards_data.csv",
        "train_fraud_labels.json",
        "mcc_codes.json",
    ]

    if not data_dir.exists():
        print("❌ Le dossier 'data/' n'existe pas")
        return False

    print("📁 Vérification des fichiers de données...")

    # Vérifier les fichiers requis
    for file in required_files:
        file_path: Path = data_dir / file
        if not file_path.exists():
            print(f"❌ Fichier requis manquant: {file}")
            return False
        print(f"✅ {file} trouvé")

    # Vérifier les fichiers optionnels
    for file in optional_files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"✅ {file} trouvé")
        else:
            print(f"⚠️  {file} manquant (optionnel)")

    return True


def check_dependencies() -> bool:
    """
    Vérifie que les dépendances sont installées.

    Returns
    -------
    bool
        True si toutes les dépendances sont présentes
    """
    required_packages: list[str] = [
        "fastapi",
        "uvicorn",
        "pandas",
        "pydantic",
    ]

    print("📦 Vérification des dépendances...")

    missing_packages: list[str] = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)

    if missing_packages:
        print(
            "\n❌ Installez les dépendances manquantes avec:"
            "\n   pip install -r requirements.txt"
        )
        return False

    return True


def main() -> int:
    """
    Fonction principale de vérification.

    Returns
    -------
    int
        Code de sortie (0 = succès, 1 = échec)
    """
    print("=" * 60)
    print("🔍 Vérification de l'environnement Banking Transactions API")
    print("=" * 60)
    print()

    checks: list[tuple[str, bool]] = [
        ("Version Python", check_python_version()),
        ("Dépendances", check_dependencies()),
        ("Fichiers de données", check_data_files()),
    ]

    print()
    print("=" * 60)
    print("📊 Résumé de la vérification")
    print("=" * 60)

    all_passed: bool = True
    for check_name, passed in checks:
        status: str = "✅ OK" if passed else "❌ ÉCHEC"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 Environnement correctement configuré!")
        print("🚀 Vous pouvez démarrer l'API avec:")
        print("   uvicorn banking_api.main:app --reload")
        return 0
    else:
        print("⚠️  Certaines vérifications ont échoué.")
        print("Corrigez les erreurs ci-dessus avant de démarrer l'API.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
