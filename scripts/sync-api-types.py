#!/usr/bin/env python3
"""
API Types Sync Script

Generates TypeScript interfaces from Pydantic models to ensure
type consistency between backend and mobile.

Usage:
    python scripts/sync-api-types.py [--check] [--output DIR]

Options:
    --check     Compare only, don't write (for CI)
    --output    Output directory (default: mobile/types/generated)
"""

import argparse
import ast
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_MODELS = PROJECT_ROOT / "backend" / "app" / "models"
DEFAULT_OUTPUT = PROJECT_ROOT / "mobile" / "types" / "generated"


# Type mappings: Python -> TypeScript
TYPE_MAP = {
    "str": "string",
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "datetime": "string",  # ISO format
    "date": "string",
    "UUID": "string",
    "Any": "any",
    "None": "null",
    "dict": "Record<string, any>",
    "Dict": "Record<string, any>",
}


def python_type_to_typescript(py_type: str) -> str:
    """Convert Python type annotation to TypeScript."""
    py_type = py_type.strip()

    # Handle None/null
    if py_type == "None":
        return "null"

    # Handle union types: str | None, Optional[str]
    if " | " in py_type:
        parts = [python_type_to_typescript(p.strip()) for p in py_type.split(" | ")]
        return " | ".join(parts)

    # Handle Optional[X] -> X | null
    optional_match = re.match(r"Optional\[(.+)\]", py_type)
    if optional_match:
        inner = python_type_to_typescript(optional_match.group(1))
        return f"{inner} | null"

    # Handle list[X] or List[X]
    list_match = re.match(r"[Ll]ist\[(.+)\]", py_type)
    if list_match:
        inner = python_type_to_typescript(list_match.group(1))
        return f"{inner}[]"

    # Handle dict[K, V] or Dict[K, V]
    dict_match = re.match(r"[Dd]ict\[(.+),\s*(.+)\]", py_type)
    if dict_match:
        key_type = python_type_to_typescript(dict_match.group(1))
        val_type = python_type_to_typescript(dict_match.group(2))
        return f"Record<{key_type}, {val_type}>"

    # Direct mapping
    return TYPE_MAP.get(py_type, py_type)


def parse_pydantic_model(file_path: Path) -> list[dict[str, Any]]:
    """Parse Pydantic models from a Python file."""
    with open(file_path) as f:
        content = f.read()

    tree = ast.parse(content)
    models = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if inherits from BaseModel
            bases = [getattr(b, 'id', getattr(b, 'attr', '')) for b in node.bases]
            if 'BaseModel' not in bases:
                continue

            model = {
                "name": node.name,
                "docstring": ast.get_docstring(node) or "",
                "fields": []
            }

            for item in node.body:
                if isinstance(item, ast.AnnAssign) and item.target:
                    field_name = item.target.id if isinstance(item.target, ast.Name) else None
                    if not field_name:
                        continue

                    # Get type annotation
                    type_str = ast.unparse(item.annotation) if item.annotation else "any"

                    # Check if optional (has default value or Field with default)
                    is_optional = False
                    if item.value:
                        # Field(...) means required, Field(None, ...) or = None means optional
                        if isinstance(item.value, ast.Constant) and item.value.value is None:
                            is_optional = True
                        elif isinstance(item.value, ast.Call):
                            # Check Field() arguments
                            func_name = getattr(item.value.func, 'id', '')
                            if func_name == 'Field':
                                # Field(...) - required, Field(None, ...) - optional
                                if item.value.args:
                                    first_arg = item.value.args[0]
                                    if isinstance(first_arg, ast.Constant) and first_arg.value is None:
                                        is_optional = True
                                    elif isinstance(first_arg, ast.Constant) and first_arg.value is ...:
                                        is_optional = False

                    # Check if type itself indicates optional (str | None)
                    if "| None" in type_str or "Optional[" in type_str:
                        is_optional = True

                    model["fields"].append({
                        "name": field_name,
                        "type": type_str,
                        "optional": is_optional
                    })

            if model["fields"]:
                models.append(model)

    return models


def generate_typescript(models: list[dict[str, Any]], module_name: str) -> str:
    """Generate TypeScript interfaces from parsed models."""
    lines = [
        "/**",
        f" * {module_name.title()} Types",
        " *",
        " * Auto-generated from backend Pydantic models.",
        f" * Generated: {datetime.now().isoformat()}",
        " *",
        " * DO NOT EDIT MANUALLY - Run: python scripts/sync-api-types.py",
        " */",
        "",
    ]

    for model in models:
        # Add docstring as comment
        if model["docstring"]:
            lines.append(f"/** {model['docstring']} */")

        lines.append(f"export interface {model['name']} {{")

        for field in model["fields"]:
            ts_type = python_type_to_typescript(field["type"])
            optional_marker = "?" if field["optional"] else ""
            lines.append(f"  {field['name']}{optional_marker}: {ts_type};")

        lines.append("}")
        lines.append("")

    return "\n".join(lines)


def sync_types(output_dir: Path, check_only: bool = False) -> tuple[int, list[str]]:
    """
    Sync all Pydantic models to TypeScript.

    Returns:
        Tuple of (exit_code, list of changed files)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    changed_files = []

    # Process each model file
    for model_file in BACKEND_MODELS.glob("*.py"):
        if model_file.name.startswith("_"):
            continue

        models = parse_pydantic_model(model_file)
        if not models:
            continue

        module_name = model_file.stem
        ts_content = generate_typescript(models, module_name)

        # Convert snake_case to kebab-case for filename
        ts_filename = module_name.replace("_", "-") + ".ts"
        ts_path = output_dir / ts_filename

        # Check if content differs
        if ts_path.exists():
            existing = ts_path.read_text()
            # Compare without timestamp line
            existing_clean = re.sub(r"\* Generated:.*\n", "", existing)
            new_clean = re.sub(r"\* Generated:.*\n", "", ts_content)

            if existing_clean == new_clean:
                continue

        changed_files.append(str(ts_path.relative_to(PROJECT_ROOT)))

        if not check_only:
            ts_path.write_text(ts_content)
            print(f"  Generated: {ts_path.relative_to(PROJECT_ROOT)}")

    # Generate index.ts for exports
    index_content = [
        "/**",
        " * Generated API Types Index",
        " *",
        " * DO NOT EDIT MANUALLY - Run: python scripts/sync-api-types.py",
        " */",
        "",
    ]

    for ts_file in sorted(output_dir.glob("*.ts")):
        if ts_file.name == "index.ts":
            continue
        module = ts_file.stem
        index_content.append(f"export * from './{module}';")

    index_content.append("")
    index_path = output_dir / "index.ts"
    index_text = "\n".join(index_content)

    if not index_path.exists() or index_path.read_text() != index_text:
        changed_files.append(str(index_path.relative_to(PROJECT_ROOT)))
        if not check_only:
            index_path.write_text(index_text)
            print(f"  Generated: {index_path.relative_to(PROJECT_ROOT)}")

    return (1 if check_only and changed_files else 0, changed_files)


def main():
    parser = argparse.ArgumentParser(description="Sync API types from backend to mobile")
    parser.add_argument("--check", action="store_true", help="Check only, don't write")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    args = parser.parse_args()

    print("=" * 50)
    print("API Types Sync")
    print("=" * 50)
    print(f"Source: {BACKEND_MODELS}")
    print(f"Output: {args.output}")
    print(f"Mode: {'Check only' if args.check else 'Generate'}")
    print("-" * 50)

    exit_code, changed = sync_types(args.output, args.check)

    print("-" * 50)
    if changed:
        if args.check:
            print(f"FAIL: {len(changed)} file(s) out of sync:")
            for f in changed:
                print(f"  - {f}")
            print("\nRun 'python scripts/sync-api-types.py' to update.")
        else:
            print(f"SUCCESS: {len(changed)} file(s) updated")
    else:
        print("SUCCESS: All types in sync")

    print("=" * 50)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
