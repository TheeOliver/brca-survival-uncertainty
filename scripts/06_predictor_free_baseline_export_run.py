"""Stage 06: re-export stored predictor-free baseline metrics, without recomputation."""

from __future__ import annotations

import argparse
import json

from brca.compute_guard import require_compute_node
from brca.config import DEFAULT_CONFIG_PATH
from brca.manifest import sha256_file
from brca.pipeline import StageRun
from brca.viz.predictor_free import export_predictor_free_baseline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()
    require_compute_node("stage 06 (predictor-free export)")
    run = StageRun("06_predictor_free_baseline_export", args.config, allow_dirty=args.allow_dirty)
    directory = run.outputs / "predictor_free_baseline"
    plan_path, results_path = directory / "plan.json", directory / "results.json"
    plan = json.loads(plan_path.read_text())
    result = json.loads(results_path.read_text())
    source_manifest = None
    for path in sorted(
        (run.outputs / "manifests").glob("05_predictor_free_baseline_*.json"), reverse=True
    ):
        manifest = json.loads(path.read_text())
        if (
            manifest.get("status") == "post_hoc_exploratory_complete"
            and manifest["artifacts_sha256"].get(str(plan_path)) == sha256_file(plan_path)
            and manifest["artifacts_sha256"].get(str(results_path)) == sha256_file(results_path)
            and sha256_file(manifest["source_archive"]) == manifest["source_sha256"]
        ):
            source_manifest = path
            break
    if source_manifest is None:
        raise ValueError("No successful source manifest matches the stored baseline results.")
    if plan["config_sha256"] != run.metadata["config_sha256"]:
        raise ValueError("Baseline results were generated with a different default configuration.")

    artifacts = export_predictor_free_baseline(result, run.outputs, run.config)
    inputs = [plan_path, results_path, source_manifest]
    run.finish(
        [*inputs, *artifacts],
        status="aggregate_metrics_only_export_complete",
        source_metrics_manifest=str(source_manifest),
        input_artifacts_sha256={str(path): sha256_file(path) for path in inputs},
        test_data_read=False,
    )
    print(f"Re-exported predictor-free baseline table and figure: {artifacts[0]}", flush=True)


if __name__ == "__main__":
    main()
