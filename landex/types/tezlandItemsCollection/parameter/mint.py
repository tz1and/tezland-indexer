# generated by datamodel-codegen:
#   filename:  mint.json

from __future__ import annotations

from typing import Dict, List, Union

from pydantic import BaseModel, Extra


class New(BaseModel):
    class Config:
        extra = Extra.forbid

    metadata: Dict[str, str]
    royalties: Dict[str, str]


class TokenItem(BaseModel):
    class Config:
        extra = Extra.forbid

    new: New


class TokenItem1(BaseModel):
    class Config:
        extra = Extra.forbid

    existing: str


class MintParameterItem(BaseModel):
    class Config:
        extra = Extra.forbid

    to_: str
    amount: str
    token: Union[TokenItem, TokenItem1]


class MintParameter(BaseModel):
    __root__: List[MintParameterItem]
