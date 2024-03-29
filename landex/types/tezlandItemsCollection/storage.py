# generated by datamodel-codegen:
#   filename:  storage.json

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra


class Key(BaseModel):
    class Config:
        extra = Extra.forbid

    address: str
    nat: str


class LedgerItem(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key
    value: str


class Key1(BaseModel):
    class Config:
        extra = Extra.forbid

    owner: str
    operator: str
    token_id: str


class Operator(BaseModel):
    class Config:
        extra = Extra.forbid

    key: Key1
    value: Dict[str, Any]


class TokenExtra(BaseModel):
    class Config:
        extra = Extra.forbid

    supply: str
    royalty_info: Dict[str, str]


class TokenMetadata(BaseModel):
    class Config:
        extra = Extra.forbid

    token_id: str
    token_info: Dict[str, str]


class TezlandItemsCollectionStorage(BaseModel):
    class Config:
        extra = Extra.forbid

    adhoc_operators: List[str]
    administrator: str
    last_token_id: str
    ledger: List[LedgerItem]
    metadata: Dict[str, str]
    operators: List[Operator]
    parent: str
    proposed_administrator: Optional[str]
    token_extra: Dict[str, TokenExtra]
    token_metadata: Dict[str, TokenMetadata]
