"""Chain Selection layer (Section 23).

Domain service KHÔNG bao giờ tự khởi tạo SuiAdapter/SolanaAdapter trực tiếp —
luôn đi qua `AdapterResolver.get(chain)`. Đây là điểm DUY NHẤT trong toàn bộ
backend "biết" có bao nhiêu chain đang được hỗ trợ; thêm chain thứ 3 sau này
chỉ cần sửa đúng 1 chỗ ở đây.
"""
from __future__ import annotations

from app.blockchain.interface import BlockchainAdapter
from app.core.config import Settings

SUPPORTED_CHAINS = ("sui", "solana")


class UnsupportedChainError(ValueError):
    pass


class AdapterResolver:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._cache: dict[str, BlockchainAdapter] = {}

    def get(self, chain: str) -> BlockchainAdapter:
        chain = chain.lower()
        if chain not in SUPPORTED_CHAINS:
            raise UnsupportedChainError(
                f"Chain '{chain}' không được hỗ trợ. Chỉ chấp nhận: {', '.join(SUPPORTED_CHAINS)}"
            )
        if chain not in self._cache:
            self._cache[chain] = self._build(chain)
        return self._cache[chain]

    def _build(self, chain: str) -> BlockchainAdapter:
        if chain == "sui":
            from app.blockchain.sui_adapter import SuiAdapter

            return SuiAdapter(self._settings)
        if chain == "solana":
            from app.blockchain.solana_adapter import SolanaAdapter

            return SolanaAdapter(self._settings)
        raise UnsupportedChainError(chain)  # không bao giờ tới đây, đã check ở get()
