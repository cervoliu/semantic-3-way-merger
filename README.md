This repository contains a toy semantic merge checker for simple C programs.
It looks for semantic merge conflicts that escape syntax-based merge tools and
compiler errors, and it can synthesize a semantic merge in some cases.

The implementation uses LLVM bitcode, the custom KLEE fork in
`third_party/klee`, and Z3. Benchmarks now live in `benchmarks/klee`, so the
repository no longer depends on a separate `~/merge-benchmark` checkout.

## Layout

- `benchmarks/klee/`: safe, unsafe, and buggy benchmark cases
- `third_party/klee/`: custom KLEE fork as a git submodule
- `third_party/klee-build/`: recommended out-of-tree KLEE build directory
- `checker/`: SMT-based equivalence, conflict, and summary logic
- `mergeChecker.py`: CLI for semantic conflict checking
- `semanticMerger.py`: CLI for merge synthesis
- `eqRunner.py`: CLI for semantic equivalence checking

## Dependencies

- Python 3.12 and `uv`
- CMake and Ninja
- LLVM/Clang 13
- Z3 headers and libraries
- zlib, libxml2, and sqlite3 development libraries

The verified KLEE build in this repository uses LLVM 13 explicitly. The build
commands below assume an LLVM 13 installation rooted at `~/.local/llvm-13`:

- `~/.local/llvm-13/bin/clang`
- `~/.local/llvm-13/bin/clang++`
- `~/.local/llvm-13/lib/cmake/llvm`

If your LLVM 13 installation lives elsewhere, set `LLVM13_ROOT` accordingly or
pass explicit paths on the CMake command line.

## Setup

1. Initialize the submodule:

```bash
git submodule update --init --recursive
```

2. Build KLEE. The repository defaults to `third_party/klee-build/bin/klee`.
   The following minimal build was verified for this repository and is enough
   for `mergeChecker.py`, `semanticMerger.py`, and the smoke tests:

```bash
LLVM13_ROOT=${LLVM13_ROOT:-$HOME/.local/llvm-13}

cmake -S third_party/klee -B third_party/klee-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_COMPILER="$LLVM13_ROOT/bin/clang" \
  -DCMAKE_CXX_COMPILER="$LLVM13_ROOT/bin/clang++" \
  -DLLVMCC="$LLVM13_ROOT/bin/clang" \
  -DLLVMCXX="$LLVM13_ROOT/bin/clang++" \
  -DLLVM_DIR="$LLVM13_ROOT/lib/cmake/llvm" \
  -DENABLE_SOLVER_Z3=ON \
  -DENABLE_SOLVER_STP=OFF \
  -DENABLE_SOLVER_METASMT=OFF \
  -DENABLE_POSIX_RUNTIME=OFF \
  -DENABLE_UNIT_TESTS=OFF \
  -DENABLE_SYSTEM_TESTS=OFF \
  -DENABLE_TCMALLOC=OFF \
  -DENABLE_DOCS=OFF \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

cmake --build third_party/klee-build -j"$(nproc)"
```

   If you want KLEE's unit tests, system tests, or POSIX runtime, you will also
   need additional dependencies such as `googletest` and `klee-uclibc`, and you
   should reconfigure with the corresponding flags enabled.

3. Create the Python environment:

```bash
uv sync --dev
```

## Tool Resolution

The Python entry points now prefer repo-local paths and command-line
configuration over hardcoded home-directory locations.

- Benchmarks: `benchmarks/klee`
- KLEE source: `third_party/klee`
- KLEE build: `third_party/klee-build`
- Clang: discovered from `--clang`, `SEMANTIC_MERGER_CLANG`, `CLANG`, or PATH

Supported environment overrides:

- `SEMANTIC_MERGER_BENCHMARK_ROOT`
- `SEMANTIC_MERGER_KLEE_SOURCE`
- `SEMANTIC_MERGER_KLEE_BUILD_DIR`
- `SEMANTIC_MERGER_KLEE_EXE`
- `SEMANTIC_MERGER_CLANG`

## Usage

Check whether a benchmark merge candidate is safe:

```bash
uv run python mergeChecker.py safe/1
```

Generate a merge result for a case:

```bash
uv run python semanticMerger.py unsafe/4
```

Check equivalence between two source files:

```bash
uv run python eqRunner.py benchmarks/klee/safe/1/A.c benchmarks/klee/safe/1/B.c
```

Run the smoke tests:

```bash
uv run pytest
uv run python -m scripts.smoke_test --clang "$LLVM13_ROOT/bin/clang"
```
