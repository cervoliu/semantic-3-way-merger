from pathlib import Path

from runtime import DEFAULT_BENCHMARK_ROOT
from runtime import repo_root
from runtime import resolve_benchmark_root
from runtime import resolve_case_directory
from runtime import resolve_case_sources


def test_repo_root_matches_project_root() -> None:
    assert (repo_root() / "README.md").is_file()


def test_repo_local_benchmarks_are_discoverable() -> None:
    assert resolve_benchmark_root() == DEFAULT_BENCHMARK_ROOT
    case_dir = resolve_case_directory("safe/1")
    assert case_dir == DEFAULT_BENCHMARK_ROOT / "safe" / "1"


def test_case_source_resolution_returns_expected_files() -> None:
    sources = resolve_case_sources(DEFAULT_BENCHMARK_ROOT / "unsafe" / "1", ("O", "A", "B", "M"))

    assert sources["O"] == Path(DEFAULT_BENCHMARK_ROOT / "unsafe" / "1" / "O.c")
    assert sources["A"] == Path(DEFAULT_BENCHMARK_ROOT / "unsafe" / "1" / "A.c")
    assert sources["B"] == Path(DEFAULT_BENCHMARK_ROOT / "unsafe" / "1" / "B.c")
    assert sources["M"] == Path(DEFAULT_BENCHMARK_ROOT / "unsafe" / "1" / "M.c")
