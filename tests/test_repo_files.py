from pathlib import Path


def test_readme_exists():
    assert (Path(__file__).resolve().parents[2] / "README.md").exists()


def test_config_example_exists():
    assert (Path(__file__).resolve().parents[2] / "config.yaml.example").exists()
