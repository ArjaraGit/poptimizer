import pandas as pd
import pytest
import torch

from poptimizer.dl.features import FeatureType, data_params, low

PARAMS = {
    "batch_size": 100,
    "history_days": 8,
    "features": {"Open": {}},
}


@pytest.fixture(scope="module", name="feature")
def make_feature():
    saved_test_days = data_params.FORECAST_DAYS
    data_params.FORECAST_DAYS = 6

    params = data_params.TrainParams(("POGR", "LKOH"), pd.Timestamp("2020-11-03"), PARAMS)
    yield low.Low("POGR", params)

    data_params.FORECAST_DAYS = saved_test_days


class TestLow:
    def test_getitem(self, feature):
        assert feature[0].shape == torch.Size([8])
        assert torch.tensor(26.155 / 28.49 - 1).allclose(feature[0][0])
        assert torch.tensor(23.415 / 28.49 - 1).allclose(feature[0][5])
        assert torch.tensor(22.81 / 28.49 - 1).allclose(feature[0][7])

        assert feature[49].shape == torch.Size([8])
        assert torch.tensor(34.25 / 35.1 - 1).allclose(feature[49][0])
        assert torch.tensor(34.5 / 35.1 - 1).allclose(feature[49][3])
        assert torch.tensor(35.555 / 35.1 - 1).allclose(feature[49][7])

        assert feature[73].shape == torch.Size([8])
        assert torch.tensor(32.9 / 33.05 - 1).allclose(feature[73][0])
        assert torch.tensor(29.875 / 33.05 - 1).allclose(feature[73][5])
        assert torch.tensor(29.2 / 33.05 - 1).allclose(feature[73][7])

    def test_type_and_size(self, feature):
        assert feature.type_and_size == (FeatureType.SEQUENCE, 8)
