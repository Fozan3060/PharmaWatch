from app.agent.orchestrator import investigate
from tests.fakes.gemini import FakeChat, FakeFunctionCall, FakePart, FakeResponse


async def _collect(gen):
    return [e async for e in gen]


async def test_no_tool_calls_returns_final_immediately():
    chat = FakeChat([FakeResponse([FakePart(text="Nothing to investigate.")])])
    events = await _collect(investigate("hi", chat=chat))

    types = [e.type for e in events]
    assert types == ["started", "thinking", "final"]
    assert events[-1].data["text"] == "Nothing to investigate."


async def test_single_tool_call_then_final():
    chat = FakeChat([
        FakeResponse([
            FakePart(function_call=FakeFunctionCall(
                "drap_price_lookup", {"medicine_name": "Ceftum", "strength": "500mg"}))
        ]),
        FakeResponse([FakePart(text="Found: MRP Rs. 640. No overcharge.")]),
    ])
    events = await _collect(investigate(
        "Charged Rs. 640 for Ceftum 500mg at City Pharmacy", chat=chat))

    types = [e.type for e in events]
    assert types == ["started", "tool_call", "tool_result", "thinking", "final"]
    assert events[1].data["name"] == "drap_price_lookup"
    assert events[2].data["result"]["found"] is True
    assert events[2].data["result"]["mrp_pkr"] == 640


async def test_parallel_tool_calls_in_one_response():
    """Gemini can return multiple function_call parts in a single response."""
    chat = FakeChat([
        FakeResponse([
            FakePart(function_call=FakeFunctionCall(
                "drap_price_lookup", {"medicine_name": "Ceftum", "strength": "500mg"})),
            FakePart(function_call=FakeFunctionCall(
                "spurious_alert_check", {"medicine_name": "Ceftum"})),
        ]),
        FakeResponse([FakePart(text="Done.")]),
    ])
    events = await _collect(investigate("Check Ceftum", chat=chat))
    tool_call_names = [e.data["name"] for e in events if e.type == "tool_call"]
    tool_result_names = [e.data["name"] for e in events if e.type == "tool_result"]
    assert tool_call_names == ["drap_price_lookup", "spurious_alert_check"]
    assert tool_result_names == ["drap_price_lookup", "spurious_alert_check"]


async def test_tool_error_is_streamed_and_passed_back_to_model():
    chat = FakeChat([
        FakeResponse([
            FakePart(function_call=FakeFunctionCall("drap_price_lookup", {"unknown_param": "x"}))
        ]),
        FakeResponse([FakePart(text="Recovered.")]),
    ])
    events = await _collect(investigate("test", chat=chat))
    types = [e.type for e in events]
    assert "tool_error" in types
    assert events[-1].type == "final"
    # The error response must be sent back to the model so it can recover.
    # Sent as a typed Part so the new google-genai SDK accepts it.
    sent_part = chat.sent[1][0]
    assert sent_part.function_response.name == "drap_price_lookup"
    assert sent_part.function_response.response["error"]


async def test_max_tool_calls_terminates_safely():
    """If the model never stops calling tools, the orchestrator emits an error event."""
    runaway = [
        FakeResponse([FakePart(function_call=FakeFunctionCall(
            "drap_price_lookup", {"medicine_name": "Ceftum", "strength": "500mg"}))])
        for _ in range(20)
    ]
    chat = FakeChat(runaway)
    events = await _collect(investigate("test", chat=chat))
    assert events[-1].type == "error"
    assert events[-1].data["reason"] == "max_tool_calls_exceeded"


async def test_event_sequence_is_monotonic():
    chat = FakeChat([
        FakeResponse([FakePart(function_call=FakeFunctionCall(
            "drap_price_lookup", {"medicine_name": "Ceftum"}))]),
        FakeResponse([FakePart(text="ok")]),
    ])
    events = await _collect(investigate("x", chat=chat))
    sequences = [e.sequence for e in events]
    assert sequences == sorted(sequences)
    assert sequences[0] == 1
