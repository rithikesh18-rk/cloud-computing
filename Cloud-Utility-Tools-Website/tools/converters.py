"""
Data & Format Converters Module
===============================
Provides data serialization and markup transformation engines:
- JSON <-> YAML bi-directional converter
- JSON <-> CSV tabular converter
- JSON Validator, Formatter & Minifier with syntax diagnostics
- Markdown to HTML preview converter
- Cron Syntax Parser & Next Execution Schedule Engine
"""

import json
import io
import csv
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import yaml

try:
    from croniter import croniter
    HAS_CRONITER = True
except ImportError:
    HAS_CRONITER = False


def json_to_yaml(json_str: str) -> Dict[str, Any]:
    """Convert JSON text to structured YAML."""
    try:
        data = json.loads(json_str)
        yaml_output = yaml.dump(data, sort_keys=False, default_flow_style=False, allow_unicode=True)
        return {"success": True, "output": yaml_output, "data": data}
    except Exception as e:
        return {"success": False, "error": f"JSON parse error: {e}"}


def yaml_to_json(yaml_str: str, indent: int = 2) -> Dict[str, Any]:
    """Convert YAML text to formatted JSON."""
    try:
        data = yaml.safe_load(yaml_str)
        json_output = json.dumps(data, indent=indent, ensure_ascii=False)
        return {"success": True, "output": json_output, "data": data}
    except Exception as e:
        return {"success": False, "error": f"YAML parse error: {e}"}


def json_to_csv(json_input: str) -> Dict[str, Any]:
    """
    Convert JSON array of objects or nested JSON objects to CSV table format.
    """
    try:
        data = json.loads(json_input)
        if isinstance(data, dict):
            # If top-level object, convert items or check if it wraps a list
            for val in data.values():
                if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                    data = val
                    break
            else:
                data = [data]

        if not isinstance(data, list) or len(data) == 0:
            return {"success": False, "error": "JSON input must be a non-empty list of objects."}

        # Collect unique headers across all records
        headers = []
        for row in data:
            if isinstance(row, dict):
                for k in row.keys():
                    if k not in headers:
                        headers.append(k)

        if not headers:
            return {"success": False, "error": "No object keys found to construct CSV headers."}

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in data:
            if isinstance(row, dict):
                writer.writerow(row)

        return {"success": True, "output": output.getvalue(), "headers": headers, "rows": len(data)}
    except Exception as e:
        return {"success": False, "error": f"CSV conversion error: {e}"}


def csv_to_json(csv_str: str, indent: int = 2) -> Dict[str, Any]:
    """Convert CSV tabular string into JSON list of records."""
    try:
        f = io.StringIO(csv_str.strip())
        reader = csv.DictReader(f)
        records = [row for row in reader]
        json_output = json.dumps(records, indent=indent)
        return {"success": True, "output": json_output, "rows": len(records), "data": records}
    except Exception as e:
        return {"success": False, "error": f"CSV parse error: {e}"}


def format_json(json_str: str, indent: int = 2, sort_keys: bool = False, minify: bool = False) -> Dict[str, Any]:
    """Validate, beautify or minify JSON with schema and type breakdown."""
    try:
        data = json.loads(json_str)
        if minify:
            output = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        else:
            output = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)

        # Structure analysis
        data_type = type(data).__name__
        count = len(data) if isinstance(data, (list, dict)) else 1

        return {
            "valid": True,
            "output": output,
            "type": data_type,
            "element_count": count,
            "original_size_bytes": len(json_str.encode("utf-8")),
            "formatted_size_bytes": len(output.encode("utf-8")),
        }
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": str(e),
            "line": e.lineno,
            "column": e.colno,
            "position": e.pos,
        }


def parse_cron(cron_expr: str, num_runs: int = 5) -> Dict[str, Any]:
    """
    Parse a 5 or 6-field standard cron expression.
    Computes human-readable description and next upcoming trigger timestamps.
    """
    clean_expr = cron_expr.strip()
    parts = clean_expr.split()

    if len(parts) not in (5, 6):
        return {
            "valid": False,
            "error": f"Invalid cron expression '{cron_expr}'. Standard cron expects 5 fields: minute hour day-of-month month day-of-week."
        }

    # Field analysis
    fields = {
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }

    # Human translation generator
    descriptions = []
    if parts[0] == "*" and parts[1] == "*":
        descriptions.append("Runs every minute of every hour")
    elif parts[0].startswith("*/"):
        descriptions.append(f"Runs every {parts[0][2:]} minutes")
    elif parts[0] == "0" and parts[1] == "*":
        descriptions.append("Runs at the start of every hour")
    elif parts[0] == "0" and parts[1].startswith("*/"):
        descriptions.append(f"Runs every {parts[1][2:]} hours")
    elif parts[0] == "0" and parts[1] != "*":
        descriptions.append(f"Runs daily at {parts[1].zfill(2)}:00 UTC")
    else:
        descriptions.append(f"Minute {parts[0]}, Hour {parts[1]}")

    if parts[4] not in ("*", "?"):
        dow_names = {"0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed", "4": "Thu", "5": "Fri", "6": "Sat", "7": "Sun"}
        clean_d = dow_names.get(parts[4], parts[4])
        descriptions.append(f"on day-of-week {clean_d}")

    human_description = ", ".join(descriptions)

    # Next execution dates calculation
    next_dates = []
    if HAS_CRONITER:
        try:
            now = datetime.now(timezone.utc)
            iter_cron = croniter(clean_expr, now)
            for _ in range(num_runs):
                nxt = iter_cron.get_next(datetime)
                next_dates.append(nxt.strftime("%Y-%m-%d %H:%M:%S UTC"))
        except Exception as e:
            return {"valid": False, "error": f"Cron computation error: {e}"}
    else:
        next_dates.append("croniter library required for real-time datetime step calculation.")

    return {
        "valid": True,
        "expression": clean_expr,
        "fields": fields,
        "human_description": human_description,
        "next_executions": next_dates,
    }


def render_markdown(md_text: str) -> str:
    """Basic Markdown to HTML converter supporting headings, code, bold, lists."""
    import re
    html = md_text
    # Escape dangerous tags
    html = html.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;")
    # Code blocks
    html = re.sub(r"```([a-zA-Z0-9_]*)\n([\s\S]*?)```", r'<pre><code class="language-\1">\2</code></pre>', html)
    # Inline code
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
    # Headers
    html = re.sub(r"^### (.*)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    # Bold / Italic
    html = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", html)
    # Links
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', html)
    # Line breaks
    html = html.replace("\n", "<br>\n")
    return html
