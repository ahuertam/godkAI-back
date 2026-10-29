import json
import os

import pytest

import agent

CONFIG_DIR = os.path.join(os.path.dirname(agent.__file__), "configs")
PROMPTS_DIR = os.path.join(os.path.dirname(agent.__file__), "prompts")


def test_config_json_loads():
    assert agent.CONFIG["agent_name"] == "godKAI"
    assert agent.CONFIG["prompt"] in {"gandalf", "generic"}


@pytest.mark.parametrize("name", sorted(os.listdir(CONFIG_DIR)))
def test_configs_dir_loads(name):
    assert name.endswith(".json")
    with open(os.path.join(CONFIG_DIR, name), encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["agent_name"]
    assert cfg["prompt"]
    assert cfg["llm_model"]


def test_read_prompt_valid_name(monkeypatch):
    monkeypatch.setattr(agent, "CONFIG", {**agent.CONFIG, "prompt": "gandalf"})
    assert "GANDALF" in agent._read_prompt()


def test_read_prompt_unknown_name_falls_back_to_generic(monkeypatch):
    monkeypatch.setattr(agent, "CONFIG", {**agent.CONFIG, "prompt": "no-existe"})
    with open(os.path.join(PROMPTS_DIR, "generic.txt"), encoding="utf-8") as f:
        generic = f.read().strip()
    assert agent._read_prompt() == generic


def test_read_prompt_absolute_path(monkeypatch, tmp_path):
    custom = tmp_path / "custom.txt"
    custom.write_text("prompt externo", encoding="utf-8")
    monkeypatch.setattr(
        agent, "CONFIG", {**agent.CONFIG, "prompt_path": str(custom)}
    )
    assert agent._read_prompt() == "prompt externo"


def test_read_prompt_missing_path_uses_named_prompt(monkeypatch):
    # prompt_path tiene prioridad, pero si no existe se usa el prompt por nombre.
    monkeypatch.setattr(
        agent,
        "CONFIG",
        {**agent.CONFIG, "prompt": "gandalf", "prompt_path": "/no/existe/prompt.txt"},
    )
    assert "GANDALF" in agent._read_prompt()
