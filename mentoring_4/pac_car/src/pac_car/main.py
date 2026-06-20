from pac_car.config.settings import load_settings
from pac_car.pipeline.orchestrator import run_pipeline


def main() -> None:
    settings = load_settings()
    summary = run_pipeline(settings)
    if summary.status == "FAILED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
