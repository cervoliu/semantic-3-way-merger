import argparse
from pathlib import Path

from checker.equivalenceChecker import check_program_equivalence
from runtime import materialize_symbolic_summaries
from runtime import resolve_toolchain


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check semantic equivalence of two C programs.")
    parser.add_argument("source_a", help="Path to the first source file.")
    parser.add_argument("source_b", help="Path to the second source file.")
    parser.add_argument("--clang", help="Path to the clang executable.")
    parser.add_argument("--klee-source", help="Path to the KLEE source tree.")
    parser.add_argument("--klee-build-dir", help="Path to the KLEE build directory.")
    parser.add_argument("--klee-exe", help="Path to the KLEE executable.")
    parser.add_argument("--benchmark-root", help="Override the benchmark root directory.")
    parser.add_argument("--workdir", help="Directory used for generated bitcode and KLEE output.")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-path diagnostic output from the equivalence checker.",
    )
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
    sources = {
        "A": Path(args.source_a).expanduser().resolve(),
        "B": Path(args.source_b).expanduser().resolve(),
    }
    for name, path in sources.items():
        if not path.is_file():
            raise FileNotFoundError(f"Source file {name} not found: {path}")

    summaries = materialize_symbolic_summaries(sources, args.workdir, toolchain)
    is_equivalent = check_program_equivalence(
        str(summaries["A"]),
        str(summaries["B"]),
        verbose=not args.quiet,
    )
    print("Equivalence" if is_equivalent else "Not Equivalent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
