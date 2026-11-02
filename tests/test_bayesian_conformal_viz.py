from brca.viz.bayesian_conformal import export_bayesian_conformal_tables


def summary(width, n_cal):
    return {
        "n_cal": n_cal,
        "observable_coverage_lower": 0.91,
        "observable_coverage_upper": 0.96,
        "ipcw_coverage": 0.94,
        "ipcw_coverage_ci": [0.88, 0.98],
        "width_median_months": width,
        "width_q25_months": width - 10,
        "width_q75_months": width + 10,
    }


def pair(width):
    differences = {
        "observable_coverage_lower": {"estimate": 0.01, "ci": [-0.01, 0.03]},
        "observable_coverage_upper": {"estimate": 0.005, "ci": [-0.01, 0.02]},
        "ipcw_coverage": {"estimate": 0.01, "ci": [-0.02, 0.04]},
        "width_median_months": {"estimate": 5.0, "ci": [2.0, 8.0]},
    }
    return {
        "posterior_predictive": summary(width, 0),
        "conformalized": summary(width + 5, 495),
        "paired_conformal_minus_posterior_predictive": {"differences": differences},
    }


def test_exporter_writes_primary_and_every_registered_supplementary_setting(tmp_path):
    settings = {}
    for alpha in (0.2, 0.1, 0.05):
        for horizon in (300.0, 120.0):
            settings[f"alpha{alpha:g}__horizon{horizon:g}"] = {
                "alpha": alpha,
                "nominal_coverage": 1 - alpha,
                "horizon_months": horizon,
                "feature_sets": {
                    "clinical": pair(70.0),
                    "clinical_molecular": pair(68.0),
                },
            }
    report = {
        "n_test": 495,
        "main_comparison": {"alpha": 0.1, "horizon_months": 120.0},
        "settings": settings,
    }

    paths = export_bayesian_conformal_tables(report, tmp_path)

    assert [path.name for path in paths] == [
        "bayesian_conformal_primary_metrics.tex",
        "bayesian_conformal_primary_differences.tex",
        "bayesian_conformal_supplement.tex",
    ]
    primary_metrics, primary_differences, supplement = [path.read_text() for path in paths]
    assert all(
        content.count("{") == content.count("}")
        for content in (primary_metrics, primary_differences, supplement)
    )
    assert "90\\% номинална покриеност" in primary_metrics
    assert "495. Ширината" in primary_metrics
    assert primary_metrics.count("Баесовски предиктивен") == 2
    assert "$n_{cal}=0$" in primary_metrics
    assert "$n_{cal}=495$" in primary_metrics
    assert "S[table-format=2.1]" in primary_metrics
    assert "S[table-format=3.1]" in primary_metrics
    assert (
        len(
            [
                line
                for line in primary_metrics.splitlines()
                if line.startswith(("Клинички", " &")) and line.rstrip().endswith("\\\\")
            ]
        )
        == 4
    )
    assert (
        len(
            [
                line
                for line in primary_differences.splitlines()
                if line.startswith("Клинички") and line.rstrip().endswith("\\\\")
            ]
        )
        == 8
    )
    assert "S[table-format=+3.1]" in primary_differences
    assert (
        len(
            [
                line
                for line in supplement.splitlines()
                if line.lstrip()[:1].isdigit() and line.rstrip().endswith("\\\\")
            ]
        )
        == 12
    )
    assert "95\\% bootstrap интервали" in primary_differences
    assert "300" in supplement and "120" in supplement
