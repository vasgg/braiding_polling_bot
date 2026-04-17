import json
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)

_PII_KEYS = frozenset({'phone_number'})


def _mask_pii(obj: object) -> None:
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in _PII_KEYS and isinstance(val, str):
                obj[key] = '***'
            else:
                _mask_pii(val)
    elif isinstance(obj, list):
        for item in obj:
            _mask_pii(item)


class UpdatesDumperMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        if logger.isEnabledFor(logging.DEBUG):
            payload = event.model_dump(exclude_unset=True, mode='json')
            _mask_pii(payload)
            logger.debug(json.dumps(payload, ensure_ascii=False))
        res = await handler(event, data)
        if res is UNHANDLED:
            logger.debug('UNHANDLED')
        return res
