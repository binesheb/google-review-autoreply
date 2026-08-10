from app.knowledge.vector import chunk_text, point_id


def test_chunk_text_overlaps_and_preserves_content():
    text = "A" * 2500
    chunks = chunk_text(text, size=1000, overlap=100)
    assert len(chunks) == 3
    assert "".join(chunks[0][:-100]) == "A" * 900
    assert all(chunk for chunk in chunks)


def test_point_id_is_deterministic():
    assert point_id(10, 2) == point_id(10, 2)
    assert point_id(10, 2) != point_id(10, 3)
