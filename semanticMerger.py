import argparse
import shutil
from pathlib import Path

from checker.equivalenceChecker import check_program_equivalence
from checker.summaryGenerator import get_merge_summary
import getEdits
from runtime import materialize_symbolic_summaries
from runtime import resolve_case_directory
from runtime import resolve_case_sources
from runtime import resolve_toolchain


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthesize a semantically correct merge from O, A, and B."
    )
    parser.add_argument(
        "case",
        help="Case directory or a path relative to benchmarks/klee, for example unsafe/4.",
    )
    parser.add_argument("--output", help="Path to the generated merged C file.")
    parser.add_argument("--benchmark-root", help="Override the benchmark root directory.")
    parser.add_argument("--clang", help="Path to the clang executable.")
    parser.add_argument("--klee-source", help="Path to the KLEE source tree.")
    parser.add_argument("--klee-build-dir", help="Path to the KLEE build directory.")
    parser.add_argument("--klee-exe", help="Path to the KLEE executable.")
    parser.add_argument("--workdir", help="Directory used for generated bitcode and KLEE output.")
    return parser.parse_args()


def copy_merge_result(source_path: Path, output_path: Path, message: str) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, output_path)
    print(message)
    return 0


def handle_trivial(
    summary_dirs: dict[str, Path],
    sources: dict[str, Path],
    output_path: Path,
) -> int | None:
    if check_program_equivalence(str(summary_dirs["A"]), str(summary_dirs["B"]), verbose=False):
        return copy_merge_result(
            sources["A"],
            output_path,
            "A and B are semantically equivalent, simply adopt either",
        )
    if check_program_equivalence(str(summary_dirs["A"]), str(summary_dirs["O"]), verbose=False):
        return copy_merge_result(
            sources["B"],
            output_path,
            "A and O are semantically equivalent, simply adopt B",
        )
    if check_program_equivalence(str(summary_dirs["B"]), str(summary_dirs["O"]), verbose=False):
        return copy_merge_result(
            sources["A"],
            output_path,
            "B and O are semantically equivalent, simply adopt A",
        )
    return None


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
    sources = resolve_case_sources(case_dir, ("O", "A", "B"))
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output is not None
        else case_dir / "merge.c"
    )

    shared, edits_A, _edits_O, edits_B = getEdits.compute_shared_and_edits(
        str(sources["A"]),
        str(sources["O"]),
        str(sources["B"]),
    )
    summary_dirs = materialize_symbolic_summaries(sources, args.workdir, toolchain)

    trivial_result = handle_trivial(summary_dirs, sources, output_path)
    if trivial_result is not None:
        return trivial_result

    record = get_merge_summary(
        str(summary_dirs["O"]),
        str(summary_dirs["A"]),
        str(summary_dirs["B"]),
    )
    edits_M = [[] for _ in range(len(edits_A))]

    for index, branch in enumerate(record, start=1):
        with open(summary_dirs[branch] / f"coveredline{index}.txt", "r") as handle:
            covered_lines = {int(line.strip()) for line in handle}

        branch_edits = edits_A if branch == "A" else edits_B
        for edit_index, edit in enumerate(branch_edits):
            flag = False
            for line_no in range(edit[1], edit[2]):
                if line_no + 1 in covered_lines:
                    flag = True
                    break
            if flag:
                edits_M[edit_index] = edit[0]

    merged = getEdits.apply(edits_M, shared)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as handle:
        for line in merged:
            handle.write(line)

    print(f"merged file saved to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
