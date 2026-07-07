import dataclasses

import randomprime_standalone
from randomprime_standalone.config import AppConfig, from_mapping


def test_config_round_trips():
    config = AppConfig(input_iso="game.iso", hud_color="#123456")
    restored = from_mapping(dataclasses.asdict(config))
    assert restored == config
    assert randomprime_standalone.DIST_NAME
