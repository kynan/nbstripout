from argparse import ArgumentParser, Namespace
from typing import Any, Dict
from pathlib import Path

import pytest
from nbstripout._nbstripout import setup_commandline
from nbstripout._utils import merge_configuration_file


def assert_namespace(actual_namespace: Namespace, expected_namespace: Namespace):
    actual_namespace_dict = vars(actual_namespace)
    expected_namespace_dict = vars(expected_namespace)
    assert actual_namespace_dict == expected_namespace_dict


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


@pytest.fixture
def parser() -> ArgumentParser:
    return setup_commandline()


def test_no_config_file(test_nb: Path, parser: ArgumentParser) -> None:
    args_str = [str(test_nb)]
    original_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert args == original_args


def test_non_nested_pyproject_toml_empty(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "pyproject.toml").write_text('[tool.other]\nprop="value"\n')
    args_str = [str(test_nb)]
    original_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert args == original_args


def test_non_nested_pyproject_toml_non_empty(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args_str = [str(test_nb)]
    expected_args = parser.parse_args(args_str)
    expected_args.drop_empty_cells = True
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_non_nested_setup_cfg_wrong_section(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    # option seems valid, but not in nbstripout section so skip
    (tmp_path / "setup.cfg").write_text(
        "[other]\ndrop_empty_cells = yes\n",
    )
    args_str = [str(test_nb)]
    expected_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_non_nested_setup_cfg_non_empty(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\ndrop_empty_cells = yes\n",
    )
    args_str = [str(test_nb)]
    expected_args = parser.parse_args(args_str)
    expected_args.drop_empty_cells = True
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_nofiles_pyproject_toml_non_empty(pytester: pytest.Pytester, parser: ArgumentParser) -> None:
    pytester.makepyprojecttoml("[tool.nbstripout]\ndrop_empty_cells=true\n")
    args_str = []
    expected_args = parser.parse_args(args_str)
    expected_args.drop_empty_cells = True
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_nofiles_setup_cfg_empty(pytester: pytest.Pytester, parser: ArgumentParser) -> None:
    Path("setup.cfg").write_text(
        "[nbstripout]\ndrop_empty_cells = yes\n",
    )
    args_str = []
    expected_args = parser.parse_args(args_str)
    expected_args.drop_empty_cells = True
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_nested_file(tmp_path: Path, nested_test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args_str = [str(nested_test_nb)]
    expected_args = parser.parse_args(args_str)
    expected_args.drop_empty_cells = True
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_common_path_nested_file_do_not_load(tmp_path: Path, parser: ArgumentParser) -> None:
    (tmp_path / "nested/file").mkdir(parents=True)
    (tmp_path / "nested/other").mkdir()
    test_nb1 = tmp_path / "nested/file/test_me.ipynb"
    test_nb1.touch()
    test_nb2 = tmp_path / "nested/other/test_me.ipynb"
    test_nb2.touch()

    (tmp_path / "nested/file/pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args_str = [str(test_nb1), str(test_nb2)]
    expected_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_common_path_nested_file_do_load(tmp_path: Path, parser: ArgumentParser) -> None:
    (tmp_path / "nested/file").mkdir(parents=True)
    (tmp_path / "nested/other").mkdir()
    test_nb1 = tmp_path / "nested/file/test_me.ipynb"
    test_nb1.touch()
    test_nb2 = tmp_path / "nested/other/test_me.ipynb"
    test_nb2.touch()

    (tmp_path / "nested/pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells=true\n",
    )
    args_str = [str(test_nb1), str(test_nb2)]
    expected_args = parser.parse_args(args_str)
    expected_args.drop_empty_cells = True
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_continue_search_if_no_config_found(
    tmp_path: Path, nested_test_nb: Path, parser: ArgumentParser
) -> None:
    (tmp_path / "nested/pyproject.toml").write_text(
        '[tool.other]\nprop = "value"\n',
    )
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells = true\n",
    )
    args_str = [str(nested_test_nb)]
    expected_args = parser.parse_args(args_str)
    expected_args.drop_empty_cells = True
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_stop_search_if_config_found(tmp_path: Path, nested_test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "nested/pyproject.toml").write_text(
        "[tool.nbstripout]\n",
    )
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\ndrop_empty_cells = true\n",
    )
    args_str = [str(nested_test_nb)]
    expected_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_dont_load_false(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\ndrop_empty_cells = no\n",
    )
    args_str = [str(test_nb)]
    expected_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_list_value_space_sep_string_pyproject_toml(
    tmp_path: Path, test_nb: Path, parser: ArgumentParser
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.nbstripout]\nextra_keys="foo bar"\n',
    )
    args_str = [str(test_nb)]
    expected_args = parser.parse_args(args_str)
    # Note: current methodology sorts extra_keys alphabetically
    expected_args.extra_keys = "bar foo"
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_list_value_setup_cfg(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\nextra_keys=foo bar\n",
    )
    args_str = [str(test_nb)]
    expected_args = parser.parse_args(args_str)
    # Note: current methodology sorts extra_keys alphabetically
    expected_args.extra_keys = "bar foo"
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_unknown_property(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\nunknown_prop=true\n",
    )
    args_str = [str(test_nb)]
    with pytest.raises(ValueError):
        merge_configuration_file(parser, args_str)


def test_non_bool_value_for_bool_property(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.nbstripout]\ndrop_empty_cells="invalid"\n',
    )
    args_str = [str(test_nb)]
    with pytest.raises(ValueError):
        merge_configuration_file(parser, args_str)


def test_non_bool_value_for_bool_property_in_setup_cfg(
    tmp_path: Path, test_nb: Path, parser: ArgumentParser
) -> None:
    (tmp_path / "setup.cfg").write_text(
        "[nbstripout]\ndrop_empty_cells=ok\n",
    )
    args_str = [str(test_nb)]
    with pytest.raises(ValueError):
        merge_configuration_file(parser, args_str)


def test_non_list_value_for_list_property(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.nbstripout]\nexclude=true\n",
    )

    args_str = [str(test_nb)]
    with pytest.raises(ValueError):
        merge_configuration_file(parser, args_str)


def test_merge_with_cli_additive_str_property(tmp_path: Path, test_nb: Path, parser: ArgumentParser) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.nbstripout]\nextra_keys="foo"\n',
    )
    args_str = [str(test_nb), '--extra-keys=bar']
    expected_args = parser.parse_args(args_str)
    # Note: current methodology sorts extra_keys alphabetically
    expected_args.extra_keys = "bar foo"
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_override_bool_true(pytester: pytest.Pytester, parser: ArgumentParser):
    pytester.makepyprojecttoml("[tool.nbstripout]\ndrop_empty_cells = false\n")
    args_str = ["--drop-empty-cells"]
    expected_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_override_size(pytester: pytest.Pytester, parser: ArgumentParser):
    pytester.makepyprojecttoml("[tool.nbstripout]\nmax_size = 30\n")
    args_str = ["--max-size=40"]
    expected_args = parser.parse_args(args_str)
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)


def test_toml_override_settings(pytester: pytest.Pytester, parser: ArgumentParser):
    pytester.makepyprojecttoml("[tool.nbstripout]\nmax_size = 30\n")
    Path("setup.cfg").write_text(
        "[nbstripout]\nmax_size = 50\n",
    )
    args_str = []
    expected_args = parser.parse_args(args_str)
    expected_args.max_size = 30
    args = merge_configuration_file(parser, args_str)
    assert_namespace(args, expected_args)
