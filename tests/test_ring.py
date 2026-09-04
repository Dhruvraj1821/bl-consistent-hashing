import random
from collections import Counter

from chash.ring import ConsistentHashRing


def make_ring(node_ids, num_virtual_nodes=150):
    ring = ConsistentHashRing()
    for node_id in node_ids:
        ring.add_node(node_id, num_virtual_nodes=num_virtual_nodes)
    return ring


def test_add_node_and_lookup_consistency():
    ring = make_ring(["A", "B", "C"])
    keys = [f"key-{i}" for i in range(500)]

    first_pass = {k: ring.get_node(k) for k in keys}
    second_pass = {k: ring.get_node(k) for k in keys}

    assert first_pass == second_pass
    assert all(v in {"A", "B", "C"} for v in first_pass.values())


def test_remove_node_only_reassigns_its_own_keys():
    ring = make_ring(["A", "B", "C", "D"])
    keys = [f"key-{i}" for i in range(2000)]

    before = {k: ring.get_node(k) for k in keys}
    ring.remove_node("C")
    after = {k: ring.get_node(k) for k in keys}

    for k in keys:
        if before[k] != "C":
            assert after[k] == before[k], f"key {k} moved unexpectedly"
        else:
            assert after[k] != "C"
            assert after[k] in {"A", "B", "D"}


def test_load_distribution_is_roughly_even_with_many_virtual_nodes():
    random.seed(42)
    ring = make_ring(["A", "B", "C", "D"], num_virtual_nodes=200)
    keys = [f"key-{i}" for i in range(20000)]

    counts = Counter(ring.get_node(k) for k in keys)
    total = sum(counts.values())
    expected = total / 4

    for node in ["A", "B", "C", "D"]:
        share = counts[node]
        assert abs(share - expected) / expected < 0.20, (
            f"node {node} got {share}, expected ~{expected}"
        )


def test_add_duplicate_node_raises():
    ring = make_ring(["A"])
    try:
        ring.add_node("A")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_remove_unknown_node_raises():
    ring = make_ring(["A"])
    try:
        ring.remove_node("Z")
        assert False, "expected ValueError"
    except ValueError:
        pass