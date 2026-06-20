from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

from pac_car.clients.object_storage_client import MinioClient


@dataclass(frozen=True)
class ModelTrainingResult:
    feature_columns: list[str]
    train_test_split: str
    algorithm: str
    metrics: dict[str, float]
    artifact_file: str
    artifact_uri: str
    prediction_file: str
    prediction_uri: str


class CarSalesMlPipeline:
    """Preprocesses warehouse data, trains a model, and publishes the artifact."""

    NUMERIC_FEATURES = ["year", "brand_car_id", "id_state", "condition", "odometer", "mmr"]
    CATEGORICAL_FEATURES = ["transmission", "color", "interior"]
    TARGET_COLUMN = "selling_price"
    ALGORITHM = "DecisionTreeRegressor"

    def __init__(
        self,
        minio_client: MinioClient,
        artifact_dir: Path,
        logger: logging.Logger,
        *,
        test_size: float,
        random_seed: int,
        mlflow_tracking_uri: str | None = None,
    ) -> None:
        self._minio_client = minio_client
        self._artifact_dir = artifact_dir
        self._logger = logger
        self._test_size = test_size
        self._random_seed = random_seed
        self._mlflow_tracking_uri = mlflow_tracking_uri

    @property
    def feature_columns(self) -> list[str]:
        return self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES

    def train_and_publish(self, dataframe: pd.DataFrame) -> ModelTrainingResult:
        self._logger.info("Training car sales price model")
        model_dataframe = self._prepare_model_dataframe(dataframe)
        if len(model_dataframe) < 5:
            raise ValueError("Warehouse data must contain at least 5 valid rows for modeling")

        features = model_dataframe[self.feature_columns]
        target = model_dataframe[self.TARGET_COLUMN]
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=self._test_size,
            random_state=self._random_seed,
        )

        model = self._build_model()
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        metrics = {
            "r2_score": float(r2_score(y_test, predictions)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
            "mae": float(mean_absolute_error(y_test, predictions)),
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_path = self._save_model(model, timestamp)
        prediction_path = self._save_predictions(x_test, y_test, predictions, timestamp)
        artifact_uri = self._minio_client.upload_file(
            artifact_path,
            object_name=f"models/{artifact_path.name}",
        )
        prediction_uri = self._minio_client.upload_file(
            prediction_path,
            object_name=f"predictions/{prediction_path.name}",
        )
        self._track_with_mlflow(metrics, artifact_path, prediction_path)

        return ModelTrainingResult(
            feature_columns=self.feature_columns,
            train_test_split=f"{1 - self._test_size:.0%}/{self._test_size:.0%}",
            algorithm=self.ALGORITHM,
            metrics=metrics,
            artifact_file=artifact_path.name,
            artifact_uri=artifact_uri,
            prediction_file=prediction_path.name,
            prediction_uri=prediction_uri,
        )

    def _prepare_model_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        required_columns = self.feature_columns + [self.TARGET_COLUMN]
        missing_columns = set(required_columns) - set(dataframe.columns)
        if missing_columns:
            raise ValueError(f"Warehouse data is missing columns: {sorted(missing_columns)}")

        model_dataframe = dataframe[required_columns].copy()
        for column in self.NUMERIC_FEATURES + [self.TARGET_COLUMN]:
            model_dataframe[column] = pd.to_numeric(model_dataframe[column], errors="coerce")

        for column in self.CATEGORICAL_FEATURES:
            model_dataframe[column] = model_dataframe[column].fillna("unknown").astype(str)

        return model_dataframe.dropna(subset=self.NUMERIC_FEATURES + [self.TARGET_COLUMN])

    def _build_model(self) -> Pipeline:
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore"),
                    self.CATEGORICAL_FEATURES,
                ),
                ("numeric", "passthrough", self.NUMERIC_FEATURES),
            ]
        )
        regressor = DecisionTreeRegressor(
            max_depth=8,
            min_samples_leaf=5,
            random_state=self._random_seed,
        )
        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", regressor),
            ]
        )

    def _save_model(self, model: Pipeline, timestamp: str) -> Path:
        self._artifact_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = self._artifact_dir / f"car_sales_decision_tree_{timestamp}.pkl"
        joblib.dump(model, artifact_path)
        self._logger.info("Saved model artifact to %s", artifact_path)
        return artifact_path

    def _save_predictions(
        self,
        features: pd.DataFrame,
        actual_values: pd.Series,
        predictions: np.ndarray,
        timestamp: str,
    ) -> Path:
        self._artifact_dir.mkdir(parents=True, exist_ok=True)
        prediction_path = self._artifact_dir / f"car_sales_predictions_{timestamp}.csv"
        prediction_dataframe = features.copy()
        prediction_dataframe["actual_selling_price"] = actual_values.to_numpy()
        prediction_dataframe["predicted_selling_price"] = predictions
        prediction_dataframe.to_csv(prediction_path, index=False)
        self._logger.info("Saved prediction output to %s", prediction_path)
        return prediction_path

    def _track_with_mlflow(
        self,
        metrics: dict[str, float],
        artifact_path: Path,
        prediction_path: Path,
    ) -> None:
        if not self._mlflow_tracking_uri:
            return

        try:
            import mlflow
        except ImportError:
            self._logger.warning("MLflow tracking URI is configured, but mlflow is not installed")
            return

        mlflow.set_tracking_uri(self._mlflow_tracking_uri)
        mlflow.set_experiment("pac_car_sales_price_prediction")
        with mlflow.start_run(run_name=artifact_path.stem):
            mlflow.log_params(
                {
                    "algorithm": self.ALGORITHM,
                    "test_size": self._test_size,
                    "random_seed": self._random_seed,
                    "numeric_features": ",".join(self.NUMERIC_FEATURES),
                    "categorical_features": ",".join(self.CATEGORICAL_FEATURES),
                }
            )
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(artifact_path), artifact_path="model")
            mlflow.log_artifact(str(prediction_path), artifact_path="predictions")
