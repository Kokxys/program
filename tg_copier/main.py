import asyncio
import logging
from pathlib import Path
from typing import Dict

import yaml

from executor_mt5 import Mt5Executor
from parser import parse_signals
from telegram_listener import TelegramListener

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_channel_map(channels_config) -> Dict[int, float]:
    channel_map: Dict[int, float] = {}
    for channel in channels_config:
        channel_map[int(channel["telegram_id"])] = float(channel["fixed_lot"])
    return channel_map


def main() -> None:
    config_path = Path(__file__).resolve().parent / "config.yaml"
    config = load_config(config_path)

    telegram_cfg = config["telegram"]
    mt5_cfg = config["mt5"]
    channels_cfg = config.get("channels", [])

    channel_map = build_channel_map(channels_cfg)

    executor = Mt5Executor(
        login=int(mt5_cfg["login"]),
        password=str(mt5_cfg["password"]),
        server=str(mt5_cfg["server"]),
        deviation=int(mt5_cfg.get("deviation", 20)),
        magic=int(mt5_cfg.get("magic", 0)),
    )

    if not executor.connect():
        logger.error("Unable to connect to MT5")
        return

    def on_message(channel_id: int, text: str) -> None:
        signals = parse_signals(text)
        if not signals:
            logger.info("No signals detected")
            return
        lot = channel_map.get(channel_id)
        if lot is None:
            logger.warning("No lot size configured for channel %s", channel_id)
            return
        for signal in signals:
            tp = signal.tps[0] if signal.tps else None
            comment = f"TG:{channel_id}"
            executor.execute_trade(
                symbol=signal.symbol,
                side=signal.side,
                lot=lot,
                sl=signal.sl,
                tp=tp,
                comment=comment,
            )

    listener = TelegramListener(
        api_id=int(telegram_cfg["api_id"]),
        api_hash=str(telegram_cfg["api_hash"]),
        session_name=str(telegram_cfg.get("session_name", "tg_copier")),
        channel_ids=channel_map.keys(),
        on_message=on_message,
    )

    try:
        asyncio.run(listener.start())
    finally:
        executor.shutdown()


if __name__ == "__main__":
    main()
