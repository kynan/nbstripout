from typing import Any

import pytest
from nbstripout._utils import merge_configuration_file
from argparse import Namespace
from pathlib import Path


def assert_namespace(namespace: Namespace, expected_props: dict[str, Any]):
    keys = (prop for prop in dir(namespace) if not prop.startswith("_"))
    actual_props = {key: getattr(namespace, key) for key in keys}
    assert actual_props == expected_props


@pytest.fixture
def test_nb(tmp_path: Path) -> Path:
    test_nb = tmp_path / "test_me.ipynb"
    test_nb.touch()
    return test_nb


@pytest.fixture
def nested_test_nb(tmp_path: Path) -> Path:
    (tmp_path / "nested/file").mkdir(parents=True)
    test_nb = tmp_path / "nested/file/test_me.ipynb"
    test_nb.touch()
    return test_nb


def test_no_config_file(tmp_path: Path, test_nb: Path) -> None:

    original_args = {"files": [test_nb]}
    args = Namespace(**original_args)
    assert merge_configuration_file(args)
    assert_namespace(args, original_args)


def test_non_nested_pyproject_toml_empty(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[tool.other]\nprop="value"\n')
    args = Namespace(files=[test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files})


def test_non_nested_pyproject_toml_non_empty(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args = Namespace(files=[test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "drop_empty_cells": True})


def test_non_nested_setup_cfg_non_empty(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[other]\ndrop_empty_cells = yes\n",
    )
    args = Namespace(files=[test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files})


def test_non_nested_setup_cfg_empty(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\ndrop_empty_cells = yes\n",
    )
    args = Namespace(files=[test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "drop_empty_cells": True})


def test_nested_file(tmp_path: Path, nested_test_nb: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args = Namespace(files=[nested_test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "drop_empty_cells": True})


def test_common_path_nested_file_do_not_load(tmp_path: Path) -> None:
    (tmp_path / "nested/file").mkdir(parents=True)
    (tmp_path / "nested/other").mkdir()
    test_nb1 = tmp_path / "nested/file/test_me.ipynb"
    test_nb1.touch()
    test_nb2 = tmp_path / "nested/other/test_me.ipynb"
    test_nb2.touch()

    (tmp_path / "nested/file/pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args = Namespace(files=[test_nb1, test_nb2])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files})


def test_common_path_nested_file_do_load(tmp_path: Path) -> None:
    (tmp_path / "nested/file").mkdir(parents=True)
    (tmp_path / "nested/other").mkdir()
    test_nb1 = tmp_path / "nested/file/test_me.ipynb"
    test_nb1.touch()
    test_nb2 = tmp_path / "nested/other/test_me.ipynb"
    test_nb2.touch()

    (tmp_path / "nested/pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args = Namespace(files=[test_nb1, test_nb2])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "drop_empty_cells": True})


def test_continue_search_if_no_config_found(
    tmp_path: Path, nested_test_nb: Path
) -> None:
    (tmp_path / "nested/pyproject.toml").write_text(
        '[tool.other]\nprop = "value"\n',
    )
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells = true\n",
    )
    args = Namespace(files=[nested_test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "drop_empty_cells": True})


def test_stop_search_if_config_found(tmp_path: Path, nested_test_nb: Path) -> None:
    (tmp_path / "nested/pyproject.toml").write_text(
        "[tool.nbstripout]\n",
    )
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells = true\n",
    )
    args = Namespace(files=[nested_test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files})


def test_dont_load_false(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\ndrop_empty_cells = no\n",
    )
    args = Namespace(files=[test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files})


def test_list_value_space_sep_string_pyproject_toml(
    tmp_path: Path, test_nb: Path
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.nbstripout]\nextra_keys="foo bar"\n',
    )
    args = Namespace(files=[test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "extra_keys": "foo bar"})


def test_list_value_setup_cfg(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\nextra_keys=foo bar\n",
    )
    args = Namespace(files=[test_nb])
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "extra_keys": "foo bar"})


def test_unknown_property(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\nunknown_prop=true\n",
    )
    args = Namespace(files=[test_nb])
    with pytest.raises(ValueError):
        merge_configuration_file(args)


def test_non_bool_value_for_bool_property(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.nbstripout]\ndrop_empty_cells="invalid"\n',
    )
    args = Namespace(files=[test_nb])
    with pytest.raises(ValueError):
        merge_configuration_file(args)


def test_non_bool_value_for_bool_property_in_setup_cfg(
    tmp_path: Path, test_nb: Path
) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\ndrop_empty_cells=ok\n",
    )
    args = Namespace(files=[test_nb])
    with pytest.raises(ValueError):
        merge_configuration_file(args)


def test_non_list_value_for_list_property(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\nexclude=true\n",
    )
    args = Namespace(files=[test_nb])
    with pytest.raises(ValueError):
        merge_configuration_file(args)


def test_merge_with_cli_additive_str_property(tmp_path: Path, test_nb: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.nbstripout]\nextra_keys="foo"\n',
    )
    args = Namespace(files=[test_nb], extra_keys="bar")
    assert merge_configuration_file(args)
    assert_namespace(args, {"files": args.files, "extra_keys": "bar foo"})
