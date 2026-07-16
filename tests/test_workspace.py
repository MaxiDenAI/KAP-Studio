
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from kap_studio.domain.models import KapProject
from kap_studio.workspace.engine import WorkspaceEngine

def load_seed():
    path = Path(__file__).resolve().parents[1] / "data" / "photoshop_2023.kap.json"
    return KapProject.model_validate_json(path.read_text(encoding="utf-8"))

def test_workspace_create_open_save():
    engine = WorkspaceEngine()
    project = load_seed()

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "photoshop.kap"
        engine.create(project, path)

        manifest, loaded = engine.open(path)
        assert manifest.revision == 1
        assert loaded.product.name == "Adobe Photoshop"

        loaded.product.version = "2025"
        engine.save(loaded, path)

        manifest2, loaded2 = engine.open(path)
        assert manifest2.revision == 2
        assert loaded2.product.version == "2025"
