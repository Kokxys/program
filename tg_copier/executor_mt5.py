import logging
from typing import Optional

import MetaTrader5 as mt5

logger = logging.getLogger(__name__)


class Mt5Executor:
    def __init__(
        self,
        login: int,
        password: str,
        server: str,
        deviation: int,
        magic: int,
    ) -> None:
        self.login = login
        self.password = password
        self.server = server
        self.deviation = deviation
        self.magic = magic

    def connect(self) -> bool:
        if not mt5.initialize():
            logger.error("MT5 initialize failed: %s", mt5.last_error())
            return False
        if not mt5.login(self.login, password=self.password, server=self.server):
            logger.error("MT5 login failed: %s", mt5.last_error())
            mt5.shutdown()
            return False
        logger.info("MT5 connected")
        return True

    def shutdown(self) -> None:
        mt5.shutdown()
        logger.info("MT5 shutdown")

    def execute_trade(
        self,
        symbol: str,
        side: str,
        lot: float,
        sl: Optional[float],
        tp: Optional[float],
        comment: str,
    ) -> None:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error("Symbol %s not found", symbol)
            return
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error("Failed to select symbol %s", symbol)
                return
        price = mt5.symbol_info_tick(symbol).ask if side == "BUY" else mt5.symbol_info_tick(symbol).bid
        order_type = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": self.deviation,
            "magic": self.magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result is None:
            logger.error("Order send failed: %s", mt5.last_error())
            return
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Order failed retcode=%s", result.retcode)
            return
        logger.info("Order placed successfully: %s", result.order)
