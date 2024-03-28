from pathlib import Path
import re
import json
from operator import itemgetter


BASE_DIR = Path(__file__).resolve().parent.parent

SCRIPT_DIR = BASE_DIR / "script"
SRC_DIR = BASE_DIR / "src"

STAGE_FILES = list(filter(Path.is_file, (SCRIPT_DIR / "stages").glob("**/*")))


def format_level(level):
    split_level = level.splitlines()
    response = []
    max_level_length = len(max(split_level, key=len))
    for each_level in split_level:
        response.append(each_level.ljust(max_level_length))

    return "".join(response)


def main():
    result = []

    def generate_json_list(file_text: str):
        each_level = re.split(r"(;\s[A-Za-z0-9 ]*\n\n)", file_text)
        for index, level in enumerate(each_level):
            single_result_structure = {
                "staticIndexList": [],
                "bricksStartPosition": [],
                "foodPositionList": [],
                "playerStartIndex": 0,
                "boardDimensionRow": 0,
                "boardDimensionColumn": 0,
                "name": "",
            }
            single_result_structure["boardDimensionRow"] = len(
                max(level.splitlines(), key=len)
            )
            single_result_structure["boardDimensionColumn"] = len(level.splitlines())

            if (
                index % 2 == 0
                and level != ""
                and single_result_structure["boardDimensionRow"] <= 15
                and single_result_structure["boardDimensionColumn"] <= 15
            ):
                level = format_level(level)
                for idx, val in enumerate(level):
                    if val == "\n":
                        continue
                    if val == "#":
                        single_result_structure["staticIndexList"].append(idx)
                    if val == "$":
                        single_result_structure["bricksStartPosition"].append(idx)
                    if val == "*":
                        single_result_structure["bricksStartPosition"].append(idx)
                        single_result_structure["foodPositionList"].append(idx)
                    if val == ".":
                        single_result_structure["foodPositionList"].append(idx)
                    if val == "@":
                        single_result_structure["playerStartIndex"] = idx
                    if val == "+":
                        single_result_structure["foodPositionList"].append(idx)
                        single_result_structure["playerStartIndex"] = idx
                single_result_structure["name"] = (
                    each_level[index + 1].split("; ")[1].strip()
                )
                result.append(single_result_structure)

    for stage_file in STAGE_FILES:
        try:
            if stage_file.suffix == ".txt":
                generate_json_list(stage_file.read_text())
        except:  # noqa: E722
            continue

    result = sorted(result, key=itemgetter("boardDimensionRow"))
    Path(SRC_DIR / "data").mkdir(exist_ok=True)
    Path(SRC_DIR / "data" / "stages.json").touch(exist_ok=True)
    Path(SRC_DIR / "data" / "stages.json").write_text(json.dumps(result, indent=2))
    assert len(result) >= 17_991
    print(format(len(result), ","), "Stages generated successfully")
