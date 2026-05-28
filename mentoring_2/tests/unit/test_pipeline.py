from paccafe_pipeline.config import PipelineSettings
from paccafe_pipeline.orchestration.pipeline import PipelineRunner, build_pipeline


def test_build_pipeline_creates_runner() -> None:
    settings = PipelineSettings.from_env()

    runner = build_pipeline(settings)

    assert isinstance(runner, PipelineRunner)
    assert runner.name == "data_pipeline_paccafe-source-staging-warehouse"
    assert runner.staging_pipeline.name == "staging"
    assert runner.warehouse_pipeline.name == "warehouse"
    assert len(runner.staging_pipeline.jobs) == 7
    assert len(runner.warehouse_pipeline.jobs) == 2
