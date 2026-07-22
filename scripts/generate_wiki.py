"""
Generate the GitHub Wiki pages for the warera client by introspecting the
public resource namespaces on ``WareraClient``.

Two-layer design:
  * Introspection collects plain data structures (dicts/lists) describing each
    resource, method, parameter, and return-model — no Markdown is built here.
  * Rendering hands that data to Jinja2 templates in ``scripts/templates/`` which
    own all layout and spacing, so Markdown block structure can't be broken by
    string concatenation.

Requires the ``docs`` extra (Jinja2):
    pip install -e ".[docs]"
"""

import inspect
import os
import re
import shutil
import sys
import typing
from typing import Any, get_args, get_origin

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

# Ensure we import the local warera package, not the system-wide installed one
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warera  # noqa: E402

WIKI_DIR = os.path.join(os.path.dirname(__file__), "api-client-py.wiki")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
REPO_URL = "https://github.com/wareraprojects/api-client-py.wiki.git"


# ---------------------------------------------------------------------------
# Introspection helpers (no Markdown here — return plain data)
# ---------------------------------------------------------------------------


def get_pydantic_models_from_type(t: Any, seen: set[Any] | None = None) -> set[type[BaseModel]]:
    if seen is None:
        seen = set()
    models: set[type[BaseModel]] = set()

    # Handle string forward refs implicitly by just ignoring or trying to resolve if we had a namespace
    if type(t) is typing.ForwardRef:
        return models

    origin = get_origin(t)
    args = get_args(t)

    if isinstance(t, type) and issubclass(t, BaseModel):
        if t in seen:
            return models
        seen.add(t)
        models.add(t)
        # Recurse into fields
        for _field_name, field_info in t.model_fields.items():
            if field_info.annotation is not None:
                models.update(get_pydantic_models_from_type(field_info.annotation, seen))
    elif origin:
        if isinstance(origin, type) and issubclass(origin, BaseModel) and origin not in seen:
            seen.add(origin)
            models.add(origin)
            for _field_name, field_info in origin.model_fields.items():
                if field_info.annotation is not None:
                    models.update(get_pydantic_models_from_type(field_info.annotation, seen))
        for arg in args:
            models.update(get_pydantic_models_from_type(arg, seen))

    return models


def md_cell(text: Any) -> str:
    """Escape a value so it is safe inside a Markdown table cell."""
    s = str(text)
    s = s.replace("\r", " ").replace("\n", " ")
    s = s.replace("|", "&#124;")
    return s.strip()


def clean_type_str(t: Any) -> str:
    # simplify type hints for display
    s = str(t)
    s = s.replace("typing.", "").replace("warera.resources.", "").replace("warera.models.", "").replace("warera._enums.", "")
    s = re.sub(r"<class '([^']+)'>", r"\1", s)
    s = s.replace(" | None", "").replace("None | ", "")
    return s


def format_type(t: str) -> str:
    """
    Render a type string as inline code for a table cell.

    We deliberately do NOT emit `<a>` links to model anchors: nested HTML links
    inside a `<code>` cell render inconsistently (raw tags in some previewers)
    and are fragile. `<code>` alone renders everywhere, and `&#124;` decodes to
    a pipe inside the HTML element without breaking the table. Every model is
    documented in the page's own "Data Models" section, so names stay findable.
    """
    return f"<code>{md_cell(t)}</code>"


_SECTION_RE = re.compile(
    r'^(Args|Arguments|Parameters|Returns|Yields|Raises|Example|Examples|Usage|Endpoints|Note|Notes):\s*$'
)


def format_docstring(doc: str | None) -> str:
    """
    Convert a Google/NumPy-style docstring into structured Markdown so it does
    not collapse into one run-on paragraph (H1). Section headers become bold
    labels, ``Args:``/``Endpoints:`` blocks become bullet lists (with
    continuation lines folded into their item), and ``Example:``/``Usage:``
    blocks are fenced as Python code.
    """
    if not doc:
        return ""

    import textwrap

    lines = doc.splitlines()
    out: list[str] = []
    i, n = 0, len(lines)

    while i < n:
        stripped = lines[i].strip()
        section_m = _SECTION_RE.match(stripped)

        if section_m:
            section = section_m.group(1)
            out.append(f"**{section}:**")
            out.append("")
            i += 1
            block = []
            while i < n and (lines[i].strip() == "" or lines[i][:1] in (" ", "\t")):
                block.append(lines[i])
                i += 1
            while block and not block[-1].strip():
                block.pop()

            if section in ("Example", "Examples", "Usage"):
                code = textwrap.dedent("\n".join(block)).strip("\n")
                out.append("```python")
                out.extend(code.splitlines())
                out.append("```")
                out.append("")
            else:
                base_indent: int | None = None
                for b in block:
                    if not b.strip():
                        continue
                    indent = len(b) - len(b.lstrip())
                    text = b.strip()
                    is_bullet = text.startswith("•")
                    if is_bullet:
                        text = text.lstrip("•").strip()
                    if base_indent is None:
                        base_indent = indent
                    if (
                        indent > base_indent
                        and not is_bullet
                        and out
                        and out[-1].startswith("- ")
                    ):
                        out[-1] = out[-1] + " " + text
                    else:
                        out.append(f"- {text}")
                out.append("")
            continue

        if stripped.startswith("•"):
            out.append(f"- {stripped.lstrip('•').strip()}")
        else:
            out.append(stripped)
        i += 1

    result = "\n".join(out)
    result = re.sub(r'\n{3,}', '\n\n', result).strip()
    return result


def _model_field_type(field_info: dict[str, Any]) -> str:
    """Resolve a JSON-schema field entry to a display type string."""
    type_str = field_info.get("type", "any")

    # Handle $ref
    if "$ref" in field_info:
        type_str = field_info["$ref"].split("/")[-1]

    # Handle array items
    if type_str == "array" and "items" in field_info:
        item_type = field_info["items"].get("type", "any")
        if "$ref" in field_info["items"]:
            item_type = field_info["items"]["$ref"].split("/")[-1]
        type_str = f"array[{item_type}]"

    # Handle anyOf / allOf
    if "anyOf" in field_info:
        types = []
        for sub in field_info["anyOf"]:
            if "type" in sub:
                t = sub["type"]
                if t == "null":
                    continue
                if t == "array" and "items" in sub:
                    item_type = sub["items"].get("type", "any")
                    if "$ref" in sub["items"]:
                        item_type = sub["items"]["$ref"].split("/")[-1]
                    t = f"array[{item_type}]"
                types.append(t)
            elif "$ref" in sub:
                types.append(sub["$ref"].split("/")[-1])
        type_str = " | ".join(types) or "any"

    return type_str


def collect_model(model: type[BaseModel]) -> dict[str, Any]:
    """Return a data dict describing a pydantic model's schema."""
    schema = model.model_json_schema()
    props = schema.get("properties", {})
    required = schema.get("required", [])

    fields = []
    for field_name, field_info in props.items():
        type_str = _model_field_type(field_info)
        fields.append(
            {
                "name": md_cell(field_name),
                "type": format_type(type_str),
                "required": "Required" if field_name in required else "Optional",
            }
        )

    return {
        "name": model.__name__,
        "doc": format_docstring(schema.get("description")),
        "fields": fields,
    }


def collect_method(method_name: str, method: Any, resource_name: str) -> dict[str, Any]:
    """Return a data dict describing a single resource method (no model schemas —
    those are collected once per page and rendered separately, see M2)."""
    sig = inspect.signature(method)

    params = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        ptype = clean_type_str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
        default = f"`{param.default}`" if param.default != inspect.Parameter.empty else "*Required*"
        params.append(
            {
                "name": md_cell(name),
                "type": format_type(ptype),
                "default": default,
            }
        )

    return {
        "name": method_name,
        "doc": format_docstring(inspect.getdoc(method)),
        "signature": str(sig),
        "params": params,
    }


def _method_return_type(method: Any) -> Any:
    sig = inspect.signature(method)
    try:
        type_hints = typing.get_type_hints(method)
        return type_hints.get("return", inspect.Signature.empty)
    except Exception:
        return sig.return_annotation


def collect_resource(name: str, res: Any) -> dict[str, Any]:
    """Return a data dict describing a resource namespace, its methods, and the
    de-duplicated set of return models referenced across all its methods."""
    public_methods = []
    for method_name in dir(res):
        if method_name.startswith("_"):
            continue
        method = getattr(res, method_name)
        if not callable(method):
            continue
        public_methods.append((method_name, method))

    # Collect the union of return models across all methods ONCE (M2), so each
    # model is documented a single time per page with a single stable anchor.
    all_models: set[type[BaseModel]] = set()
    for _mname, method in public_methods:
        ret_type = _method_return_type(method)
        if ret_type != inspect.Signature.empty:
            all_models.update(get_pydantic_models_from_type(ret_type))

    models = [collect_model(m) for m in sorted(all_models, key=lambda m: m.__name__)]

    methods = [collect_method(mname, method, name) for mname, method in public_methods]

    return {
        "name": name,
        "class_name": res.__class__.__name__,
        "page_name": f"Resource-{res.__class__.__name__}",
        "doc": format_docstring(inspect.getdoc(res.__class__)),
        "methods": methods,
        "models": models,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _env() -> Environment:
    # Autoescape stays OFF — we emit Markdown, not HTML. trim/lstrip + trailing
    # newline give deterministic block spacing regardless of template layout.
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def run() -> None:
    os.makedirs(WIKI_DIR, exist_ok=True)

    client = warera.WareraClient()
    try:
        _generate(client)
    finally:
        # Close the underlying httpx client so we don't leak an unclosed
        # connection / emit a ResourceWarning at interpreter exit.
        import asyncio
        import contextlib

        with contextlib.suppress(Exception):
            asyncio.run(client.aclose())


def _generate(client: "warera.WareraClient") -> None:
    env = _env()
    resource_tpl = env.get_template("resource_page.md.jinja")
    api_ref_tpl = env.get_template("api_reference.md.jinja")
    sidebar_tpl = env.get_template("sidebar.md.jinja")

    resources = []
    for prop in dir(client):
        if prop.startswith("_") or prop in ["batch", "rate_limit_remaining", "rate_limit_reset", "rate_limit_total"]:
            continue

        attr = getattr(client, prop)
        if hasattr(attr, "__module__") and "warera.resources" in attr.__module__:
            resources.append((prop, attr))

    collected = [collect_resource(name, res) for name, res in sorted(resources, key=lambda x: x[0])]

    for res in collected:
        page_name = res["page_name"]
        print(f"Generating {page_name}.md...")
        md = resource_tpl.render(res=res)
        with open(os.path.join(WIKI_DIR, f"{page_name}.md"), "w", encoding="utf-8") as f:
            f.write(md)

    print("Generating _Sidebar.md...")
    with open(os.path.join(WIKI_DIR, "_Sidebar.md"), "w", encoding="utf-8") as f:
        f.write(sidebar_tpl.render(resources=collected))

    print("Generating API-Reference.md...")
    with open(os.path.join(WIKI_DIR, "API-Reference.md"), "w", encoding="utf-8") as f:
        f.write(api_ref_tpl.render(resources=collected))

    for doc_name in [
        "Home.md", "Introduction.md", "Getting-Started.md",
        "Advanced-Usage.md", "Code-Snippets.md", "FAQ.md",
        "Migration-Guide.md",
    ]:
        main_doc = os.path.join(os.path.dirname(__file__), "..", "wiki", doc_name)
        if os.path.exists(main_doc):
            print(f"Copying {doc_name}...")
            shutil.copy(main_doc, os.path.join(WIKI_DIR, doc_name))

    print("\nGeneration complete!")
    print(f"Check the {WIKI_DIR} directory. You can now cd into it, and manually `git commit` and `git push`.")


if __name__ == "__main__":
    run()
