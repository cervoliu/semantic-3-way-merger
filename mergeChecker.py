import argparse

from checker.conflictChecker import check_merge_conflict_free
from runtime import materialize_symbolic_summaries
from runtime import resolve_case_directory
from runtime import resolve_case_sources
from runtime import resolve_toolchain


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether a merge candidate is semantically conflict free."
    )
    parser.add_argument(
        "case",
        help="Case directory or a path relative to benchmarks/klee, for example safe/1.",
    )
    parser.add_argument("--benchmark-root", help="Override the benchmark root directory.")
    parser.add_argument("--clang", help="Path to the clang executable.")
    parser.add_argument("--klee-source", help="Path to the KLEE source tree.")
    parser.add_argument("--klee-build-dir", help="Path to the KLEE build directory.")
    parser.add_argument("--klee-exe", help="Path to the KLEE executable.")
    parser.add_argument("--workdir", help="Directory used for generated bitcode and KLEE output.")
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
    case_dir = resolve_case_directory(args.case, benchmark_root=toolchain.benchmark_root)
    sources = resolve_case_sources(case_dir, ("O", "A", "B", "M"))
    summaries = materialize_symbolic_summaries(sources, args.workdir, toolchain)
    is_safe = check_merge_conflict_free(
        str(summaries["O"]),
        str(summaries["A"]),
        str(summaries["B"]),
        str(summaries["M"]),
    )
    print("safe" if is_safe else "unsafe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
