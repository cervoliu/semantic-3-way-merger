from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "klee"
DEFAULT_KLEE_SOURCE = REPO_ROOT / "third_party" / "klee"
DEFAULT_KLEE_BUILD = REPO_ROOT / "third_party" / "klee-build"

LLVM_COMPILE_ARGS = (
    "-emit-llvm",
    "-c",
    "-g",
    "-O0",
    "-Xclang",
    "-disable-O0-optnone",
)

KLEE_OPTIONS = (
    "--solver-backend=z3",
    "--use-query-log=solver:kquery",
    "--write-exec-tree",
    "--write-sym-paths",
    "--write-no-tests",
)


@dataclass(frozen=True)
class Toolchain:
    clang: Path
    klee: Path
    klee_include: Path
    benchmark_root: Path


def _normalize_path(path_like: str | os.PathLike[str] | None) -> Path | None:
    if path_like is None:
        return None
    return Path(path_like).expanduser().resolve()


def _first_existing_file(candidates: Iterable[str | os.PathLike[str] | None]) -> Path | None:
    for candidate in candidates:
        path = _normalize_path(candidate)
        if path is not None and path.is_file():
            return path
    return None


def _first_existing_dir(candidates: Iterable[str | os.PathLike[str] | None]) -> Path | None:
    for candidate in candidates:
        path = _normalize_path(candidate)
        if path is not None and path.is_dir():
            return path
    return None


def repo_root() -> Path:
    return REPO_ROOT


def resolve_benchmark_root(benchmark_root: str | os.PathLike[str] | None = None) -> Path:
    path = _first_existing_dir(
        (
            benchmark_root,
            os.environ.get("SEMANTIC_MERGER_BENCHMARK_ROOT"),
            DEFAULT_BENCHMARK_ROOT,
        )
    )
    if path is None:
        raise FileNotFoundError(
            "Unable to locate benchmark root. Pass --benchmark-root or set "
            "SEMANTIC_MERGER_BENCHMARK_ROOT."
        )
    return path


def resolve_clang(clang: str | os.PathLike[str] | None = None) -> Path:
    candidates = [
        clang,
        os.environ.get("SEMANTIC_MERGER_CLANG"),
        os.environ.get("CLANG"),
    ]
    for name in ("clang-13", "clang", "clang-14", "clang-12"):
        located = shutil.which(name)
        if located is not None:
            candidates.append(located)

    path = _first_existing_file(candidates)
    if path is None:
        raise FileNotFoundError(
            "Unable to locate clang. Pass --clang or set SEMANTIC_MERGER_CLANG."
        )
    return path


def resolve_klee_source(klee_source: str | os.PathLike[str] | None = None) -> Path:
    path = _first_existing_dir(
        (
            klee_source,
            os.environ.get("SEMANTIC_MERGER_KLEE_SOURCE"),
            DEFAULT_KLEE_SOURCE,
        )
    )
    if path is None or not (path / "include").is_dir():
        raise FileNotFoundError(
            "Unable to locate the KLEE source tree. Pass --klee-source or set "
            "SEMANTIC_MERGER_KLEE_SOURCE."
        )
    return path


def resolve_klee_executable(
    klee_exe: str | os.PathLike[str] | None = None,
    klee_build_dir: str | os.PathLike[str] | None = None,
    klee_source: str | os.PathLike[str] | None = None,
) -> Path:
    source_dir = _normalize_path(klee_source) if klee_source is not None else DEFAULT_KLEE_SOURCE
    build_dir = _normalize_path(klee_build_dir)
    env_build_dir = _normalize_path(
        os.environ.get("SEMANTIC_MERGER_KLEE_BUILD_DIR") or os.environ.get("KLEE_BUILD_DIR")
    )

    candidates = [
        klee_exe,
        os.environ.get("SEMANTIC_MERGER_KLEE_EXE"),
        os.environ.get("KLEE_EXE"),
    ]
    for candidate_dir in (build_dir, env_build_dir, DEFAULT_KLEE_BUILD, source_dir / "build"):
        if candidate_dir is not None:
            candidates.append(candidate_dir / "bin" / "klee")

    located = shutil.which("klee")
    if located is not None:
        candidates.append(located)

    path = _first_existing_file(candidates)
    if path is None:
        raise FileNotFoundError(
            "Unable to locate the KLEE executable. Pass --klee-exe, pass "
            "--klee-build-dir, or set SEMANTIC_MERGER_KLEE_EXE."
        )
    return path


def resolve_toolchain(
    clang: str | os.PathLike[str] | None = None,
    klee_source: str | os.PathLike[str] | None = None,
    klee_build_dir: str | os.PathLike[str] | None = None,
    klee_exe: str | os.PathLike[str] | None = None,
    benchmark_root: str | os.PathLike[str] | None = None,
) -> Toolchain:
    source_dir = resolve_klee_source(klee_source)
    return Toolchain(
        clang=resolve_clang(clang),
        klee=resolve_klee_executable(klee_exe=klee_exe, klee_build_dir=klee_build_dir, klee_source=source_dir),
        klee_include=source_dir / "include",
        benchmark_root=resolve_benchmark_root(benchmark_root),
    )


def resolve_case_directory(
    case: str | os.PathLike[str],
    benchmark_root: str | os.PathLike[str] | None = None,
) -> Path:
    candidate = _normalize_path(case)
    if candidate is not None and candidate.is_dir():
        return candidate

    benchmark_dir = resolve_benchmark_root(benchmark_root)
    benchmark_case = (benchmark_dir / Path(case)).resolve()
    if benchmark_case.is_dir():
        return benchmark_case

    raise FileNotFoundError(
        f"Unable to locate case directory '{case}'. Pass an absolute path or a path relative to "
        f"{benchmark_dir}."
    )


def resolve_case_sources(case_dir: str | os.PathLike[str], names: Iterable[str]) -> dict[str, Path]:
    directory = _normalize_path(case_dir)
    if directory is None or not directory.is_dir():
        raise FileNotFoundError(f"Case directory not found: {case_dir}")

    sources: dict[str, Path] = {}
    for name in names:
        source_path = directory / f"{name}.c"
        if not source_path.is_file():
            raise FileNotFoundError(f"Source file {name} not found: {source_path}")
        sources[name] = source_path
    return sources


def prepare_workdir(workdir: str | os.PathLike[str] | None = None) -> Path:
    path = _normalize_path(workdir) if workdir is not None else (REPO_ROOT / "tmp")
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    return path


def compile_to_bitcode(source_path: Path, output_path: Path, toolchain: Toolchain) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(toolchain.clang),
            "-I",
            str(toolchain.klee_include),
            *LLVM_COMPILE_ARGS,
            str(source_path),
            "-o",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def run_klee(bitcode_path: Path, output_dir: Path, toolchain: Toolchain) -> None:
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(toolchain.klee),
            *KLEE_OPTIONS,
            f"--output-dir={output_dir}",
            str(bitcode_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def materialize_symbolic_summaries(
    sources: Mapping[str, Path],
    workdir: str | os.PathLike[str] | None,
    toolchain: Toolchain,
) -> dict[str, Path]:
    target_dir = prepare_workdir(workdir)
    summary_dirs: dict[str, Path] = {}
    for name, source_path in sources.items():
        bitcode_path = target_dir / f"{name}.bc"
        compile_to_bitcode(source_path, bitcode_path, toolchain)
        summary_dir = target_dir / name
        run_klee(bitcode_path, summary_dir, toolchain)
        summary_dirs[name] = summary_dir
    return summary_dirs
