"""Render the reviewed shift figure from frozen aggregate statistics."""

from __future__ import annotations

import argparse
import json

from brca.compute_guard import require_compute_node
from brca.config import DEFAULT_CONFIG_PATH, PROJECT_ROOT
from brca.manifest import sha256_file
from brca.pipeline import StageRun
from brca.viz.shift import render_shift_figure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()
    require_compute_node("distribution-shift export")
    run = StageRun("06_distribution_shift_export", args.config, allow_dirty=args.allow_dirty)
    directory = run.outputs / "distribution_shift"
    plan_path, result_path = directory / "plan.json", directory / "distribution_shift.json"
    plan, result = json.loads(plan_path.read_text()), json.loads(result_path.read_text())
    if plan["config_sha256"] != run.metadata["config_sha256"]:
        raise ValueError("Shift export uses a different analysis configuration")
    for name, digest in plan["analysis_source_sha256"].items():
        if sha256_file(PROJECT_ROOT / name) != digest:
            raise ValueError(f"Statistical source changed since shift evaluation: {name}")
    for name, digest in plan["frozen_inputs_sha256"].items():
        if sha256_file(name) != digest:
            raise ValueError("Frozen input changed since shift evaluation")
    expected = {str(plan_path): sha256_file(plan_path), str(result_path): sha256_file(result_path)}
    manifests = sorted(
        (run.outputs / "manifests").glob("05_distribution_shift_*.json"), reverse=True
    )
    if not any(
        (candidate := json.loads(path.read_text())).get("status")
        == "post_hoc_distribution_shift_complete"
        and candidate["artifacts_sha256"] == expected
        and sha256_file(candidate["source_archive"]) == candidate["source_sha256"]
        for path in manifests
    ):
        raise ValueError("No successful manifest matches the frozen shift aggregates")
    paths = render_shift_figure(result, plan["settings"], run.config.figures, directory)
    if sha256_file(result_path) != expected[str(result_path)]:
        raise ValueError("Shift aggregates changed during figure export")
    run.finish(paths, status="complete", shift_result_sha256=expected[str(result_path)])
    print(f"Exported {len(paths)} distribution-shift figure artifacts.")


if __name__ == "__main__":
    main()
