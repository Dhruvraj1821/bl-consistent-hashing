"""Plain consistent hashing with virtual nodes (Baseline 1).

A sorted array of (hash_position -> physical_node) mappings supporting
O(log n) lookup via bisect. This is the classic algorithm with no load
bound and no smart placement - everything else in this project is
compared against it.
"""

from __future__ import annotations

import bisect
import hashlib
from typing import Dict, List, Optional


def _hash(value: str) -> int:
    """Stable 64-bit hash used for ring positions and key lookups."""
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()
    return int(digest, 16) % (2**64)


class ConsistentHashRing:
    """Classic consistent hash ring with configurable virtual nodes per physical node."""

    def __init__(self) -> None:
        self._positions: List[int] = []
        self._ring: Dict[int, str] = {}
        self._node_positions: Dict[str, List[int]] = {}

    def add_node(self, node_id: str, num_virtual_nodes: int = 150) -> None:
        if node_id in self._node_positions:
            raise ValueError(f"node {node_id!r} already present in ring")

        positions = []
        for i in range(num_virtual_nodes):
            pos = _hash(f"{node_id}#{i}")
            while pos in self._ring:
                pos = (pos + 1) % (2**64)
            self._ring[pos] = node_id
            bisect.insort(self._positions, pos)
            positions.append(pos)

        self._node_positions[node_id] = positions

    def remove_node(self, node_id: str) -> None:
        if node_id not in self._node_positions:
            raise ValueError(f"node {node_id!r} not present in ring")

        for pos in self._node_positions[node_id]:
            del self._ring[pos]
            idx = bisect.bisect_left(self._positions, pos)
            del self._positions[idx]

        del self._node_positions[node_id]

    def get_node(self, key: str) -> Optional[str]:
        if not self._positions:
            return None
        h = _hash(key)
        idx = bisect.bisect(self._positions, h)
        if idx == len(self._positions):
            idx = 0
        pos = self._positions[idx]
        return self._ring[pos]

    def nodes(self) -> List[str]:
        return list(self._node_positions.keys())

    def positions_for_node(self, node_id: str) -> List[int]:
        return list(self._node_positions.get(node_id, []))

    def __len__(self) -> int:
        return len(self._node_positions)