"""Tests pour le module main.py.
Tests pour couvrir les lignes non couvertes du gestionnaire lifespan et de la fonction run.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestMain:
    """Tests pour le module principal."""

    def test_root_endpoint(self) -> None:
        """Tester l'endpoint racine."""
        # Import dynamique pour éviter la circularité
        from banking_api.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "redoc" in data


class TestLifespanCoverage:
    """Tests pour couvrir les lignes du gestionnaire lifespan."""

    @pytest.mark.asyncio
    async def test_lifespan_success_path(self) -> None:
        """Tester le chemin de succès du gestionnaire lifespan.

        Couvre les lignes 33-35 : chargement réussi des données.
        """
        # Import dynamique pour éviter la circularité
        from banking_api.main import lifespan

        # Mock du DataLoader pour simuler un chargement réussi
        with patch("banking_api.main.DataLoader") as mock_data_loader_class:
            mock_loader = MagicMock()
            mock_data_loader_class.return_value = mock_loader
            mock_loader.load_data.return_value = None  # Succès

            # Mock de print pour capturer les sorties
            with patch("builtins.print") as mock_print:
                # Créer une app mock pour le test
                mock_app = MagicMock()

                # Tester le gestionnaire lifespan
                async with lifespan(mock_app):
                    # Vérifier que load_data a été appelé
                    mock_loader.load_data.assert_called_once()

                # Vérifier les messages imprimés
                mock_print.assert_any_call("Dataset chargé avec succès")
                mock_print.assert_any_call("Arrêt de l'application")

    @pytest.mark.asyncio
    async def test_lifespan_exception_path(self) -> None:
        """Tester le chemin d'exception du gestionnaire lifespan.

        Couvre la ligne 37-39 : gestion d'erreur lors du chargement.
        """
        from banking_api.main import lifespan

        # Mock du DataLoader pour simuler une erreur
        with patch("banking_api.main.DataLoader") as mock_data_loader_class:
            mock_loader = MagicMock()
            mock_data_loader_class.return_value = mock_loader

            # Simuler une exception lors du chargement
            test_error = Exception("Erreur de test")
            mock_loader.load_data.side_effect = test_error

            # Mock de print pour capturer les sorties
            with patch("builtins.print") as mock_print:
                # Créer une app mock pour le test
                mock_app = MagicMock()

                # Tester le gestionnaire lifespan avec exception
                async with lifespan(mock_app):
                    pass

                # Vérifier que l'erreur a été gérée et imprimée
                mock_print.assert_any_call(
                    "Avertissement : impossible de charger le dataset : Erreur de test"
                )
                mock_print.assert_any_call("Arrêt de l'application")


class TestRunFunctionCoverage:
    """Tests pour couvrir la fonction run."""

    def test_run_function(self) -> None:
        """Tester la fonction run.

        Couvre les lignes 91-92 : import uvicorn et appel uvicorn.run.
        """
        # Mock de uvicorn au niveau du module sys.modules car il est importé localement

        from banking_api.main import run

        with patch.dict("sys.modules", {"uvicorn": MagicMock()}) as mock_modules:
            mock_uvicorn = mock_modules["uvicorn"]

            # Appeler la fonction run
            run()

            # Vérifier que uvicorn.run a été appelé avec les bons paramètres
            mock_uvicorn.run.assert_called_once_with(
                "banking_api.main:app", host="0.0.0.0", port=8000, reload=True
            )

    def test_main_entry_point_line96(self) -> None:
        """Tester le point d'entrée principal pour couvrir ligne 96.

        Couvre la ligne 96 : if __name__ == "__main__":
        """
        import importlib.util
        import sys
        from unittest.mock import MagicMock

        # Charger le module main comme si c'était le script principal
        spec = importlib.util.spec_from_file_location("__main__", "banking_api/main.py")
        main_module = importlib.util.module_from_spec(spec)

        # Mock uvicorn pour éviter le démarrage du serveur
        with patch.dict("sys.modules", {"uvicorn": MagicMock()}) as mock_modules:
            mock_uvicorn = mock_modules["uvicorn"]

            # Simuler l'exécution en tant que script principal
            original_main = sys.modules.get("__main__")
            sys.modules["__main__"] = main_module
            main_module.__name__ = "__main__"

            try:
                # Exécuter le module (cela va déclencher if __name__ == "__main__":)
                spec.loader.exec_module(main_module)

                # Vérifier que uvicorn.run a été appelé (ligne après 96)
                mock_uvicorn.run.assert_called_once()

            finally:
                # Restaurer l'état original
                if original_main is not None:
                    sys.modules["__main__"] = original_main
                elif "__main__" in sys.modules:
                    del sys.modules["__main__"]


class TestAppConfiguration:
    """Tests pour vérifier la configuration de l'application."""

    def test_app_routes_registered(self) -> None:
        """Tester que toutes les routes sont enregistrées."""
        from banking_api.main import app

        client = TestClient(app)

        # Tester quelques endpoints pour vérifier que les routers sont bien inclus
        response = client.get("/")
        assert response.status_code == 200

        # Test que l'application FastAPI est bien configurée
        assert app.title is not None
        assert app.version is not None
