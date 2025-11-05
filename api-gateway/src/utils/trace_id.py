from src.globals import TRACE_ID_HEADER_NAME, REQUEST_ID_HEADER_NAME, STARTUP_PROFILE
import uuid

def add_trace_id(headers: dict) -> None:
    headers[TRACE_ID_HEADER_NAME] = str(uuid.uuid4())

def replace_trace_id(headers: dict) -> None:
    trace_id = headers.pop(TRACE_ID_HEADER_NAME, None)

    if trace_id and STARTUP_PROFILE == "dev":
        headers[REQUEST_ID_HEADER_NAME] = trace_id
