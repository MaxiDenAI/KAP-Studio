
from pathlib import Path
from tempfile import TemporaryDirectory

from kap_studio.domain.models import Product, KapProject
from kap_studio.domain.journey_factory import build_standard_journey
from kap_studio.workspace.engine import WorkspaceEngine

def make_project():
    product = Product(
        id="PROD-TEST", name="Test Product", version="2026",
        manufacturer="Test", category="Creative", archetype="Creator",
        accent="#1AA3FF", audience="Designers", promise="Create", journey=[]
    )
    product.journey = build_standard_journey(product)
    return KapProject(product=product, marketplace_profiles=["Wildberries"])

def test_create_open_save():
    engine = WorkspaceEngine()
    project = make_project()
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.kap"
        engine.create(project, path)
        manifest, loaded = engine.open(path)
        assert manifest.revision == 1
        assert loaded.product.name == "Test Product"
        loaded.product.version = "2027"
        engine.save(loaded, path)
        manifest2, loaded2 = engine.open(path)
        assert manifest2.revision == 2
        assert loaded2.product.version == "2027"
