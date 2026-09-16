import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

SIGNAL_START_RE = re.compile(
    r"(?P<prefix>^|\n)\s*(?P<symbol>#?XAUUSD|GOLD)\s+(?P<side>BUY|SELL)\s+(?P<entry>\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)",
    re.IGNORECASE,
)
MORE_ENTRY_RE = re.compile(r"\bMORE\s+(?P<side>BUY|SELL)\s+(?P<entry>\d+(?:\.\d+)?)", re.IGNORECASE)
TP_RE = re.compile(r"\bTP\s+(?P<price>\d+(?:\.\d+)?)", re.IGNORECASE)
SL_RE = re.compile(r"\bSL\s+(?P<price>\d+(?:\.\d+)?)", re.IGNORECASE)


@dataclass
class Signal:
    symbol: str
    side: str
    entry: Optional[float]
    entry_range: Optional[Tuple[float, float]]
    tps: List[float]
    sl: Optional[float]
    raw_text: str


def _normalize_symbol(raw_symbol: str) -> str:
    return "XAUUSD"


def _parse_entry(entry_text: str) -> Tuple[Optional[float], Optional[Tuple[float, float]]]:
    if "-" in entry_text:
        parts = [p.strip() for p in entry_text.split("-")]
        if len(parts) == 2:
            start = float(parts[0])
            end = float(parts[1])
            return None, (start, end)
    return float(entry_text.strip()), None


def parse_signals(message: str) -> List[Signal]:
    matches = list(SIGNAL_START_RE.finditer(message))
    signals: List[Signal] = []

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(message)
        chunk = message[start:end].strip()

        symbol = _normalize_symbol(match.group("symbol"))
        side = match.group("side").upper()
        entry_text = match.group("entry")
        entry, entry_range = _parse_entry(entry_text)

        more_match = MORE_ENTRY_RE.search(chunk)
        if more_match and more_match.group("side").upper() == side:
            entry = float(more_match.group("entry"))
            entry_range = None

        tps = [float(tp.group("price")) for tp in TP_RE.finditer(chunk)]
        sl_match = SL_RE.search(chunk)
        sl = float(sl_match.group("price")) if sl_match else None

        signals.append(
            Signal(
                symbol=symbol,
                side=side,
                entry=entry,
                entry_range=entry_range,
                tps=tps,
                sl=sl,
                raw_text=chunk,
            )
        )

    return signals
