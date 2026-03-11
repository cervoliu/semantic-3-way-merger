import argparse
import tempfile

from checker.conflictChecker import check_merge_conflict_free
from runtime import materialize_symbolic_summaries
from runtime import resolve_case_directory
from runtime import resolve_case_sources
from runtime import resolve_toolchain


DEFAULT_CASES = (
    ("safe/1", True),
    ("unsafe/1", False),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a small end-to-end smoke test suite.")
    parser.add_argument("--benchmark-root", help="Override the benchmark root directory.")
    parser.add_argument("--clang", help="Path to the clang executable.")
    parser.add_argument("--klee-source", help="Path to the KLEE source tree.")
    parser.add_argument("--klee-build-dir", help="Path to the KLEE build directory.")
    parser.add_argument("--klee-exe", help="Path to the KLEE executable.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    toolchain = resolve_toolchain(
        clang=args.clang,
        klee_source=args.klee_source,
        klee_build_dir=args.klee_build_dir,
        klee_exe=args.klee_exe,
        benchmark_root=args.benchmark_root,
    )

    for case, expected in DEFAULT_CASES:
        case_dir = resolve_case_directory(case, benchmark_root=toolchain.benchmark_root)
        sources = resolve_case_sources(case_dir, ("O", "A", "B", "M"))
        with tempfile.TemporaryDirectory(prefix="semantic-merger-smoke-") as workdir:
            summaries = materialize_symbolic_summaries(sources, workdir, toolchain)
            result = check_merge_conflict_free(
                str(summaries["O"]),
                str(summaries["A"]),
                str(summaries["B"]),
                str(summaries["M"]),
            )
        print(f"{case}: expected={expected} actual={result}")
        if result != expected:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
