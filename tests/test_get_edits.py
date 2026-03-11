from pathlib import Path

import getEdits


def write_program(path: Path, lines: list[str]) -> None:
    path.write_text("".join(lines))


def test_compute_shared_and_edits_single_hole(tmp_path: Path) -> None:
    program_o = tmp_path / "O.c"
    program_a = tmp_path / "A.c"
    program_b = tmp_path / "B.c"

    write_program(program_o, ["int main() {\n", "  return 0;\n", "}\n"])
    write_program(program_a, ["int main() {\n", "  return 1;\n", "}\n"])
    write_program(program_b, ["int main() {\n", "  return 2;\n", "}\n"])

    shared, edits_a, edits_o, edits_b = getEdits.compute_shared_and_edits(
        str(program_a),
        str(program_o),
        str(program_b),
    )

    assert shared == ["int main() {\n", None, "}\n"]
    assert edits_a == [(["  return 1;\n"], 1, 2)]
    assert edits_o == [(["  return 0;\n"], 1, 2)]
    assert edits_b == [(["  return 2;\n"], 1, 2)]


def test_apply_inserts_each_edit_block() -> None:
    merged = getEdits.apply(
        [["  return 1;\n"], ["  return 2;\n"]],
        ["int main() {\n", None, "  if (1) {\n", None, "  }\n", "}\n"],
    )

    assert merged == [
        "int main() {\n",
        "  return 1;\n",
        "  if (1) {\n",
        "  return 2;\n",
        "  }\n",
        "}\n",
    ]
