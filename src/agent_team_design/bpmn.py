"""BPMN 2.0 XML parser that extracts process models."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"

TASK_TYPES = {
    "task", "userTask", "serviceTask", "manualTask",
    "scriptTask", "sendTask", "receiveTask", "businessRuleTask",
}

GATEWAY_TYPES = {
    "exclusiveGateway", "parallelGateway", "inclusiveGateway",
    "eventBasedGateway", "complexGateway",
}

EVENT_TYPES = {
    "startEvent", "endEvent", "intermediateThrowEvent",
    "intermediateCatchEvent", "boundaryEvent",
}


def _find_all(root: ET.Element, local_name: str, ns: str | None) -> list[ET.Element]:
    if ns:
        return root.findall(f".//{{{ns}}}{local_name}")
    return root.findall(f".//{local_name}")


def _parse_typed_elements(
    root: ET.Element, ns: str | None, type_names: set[str],
) -> list[dict[str, str]]:
    elements = []
    for type_name in type_names:
        for elem in _find_all(root, type_name, ns):
            elements.append({
                "id": elem.get("id", ""),
                "name": elem.get("name", ""),
                "type": type_name,
            })
    return elements


def _parse_flows(root: ET.Element, ns: str | None) -> list[dict[str, str]]:
    flows = []
    for elem in _find_all(root, "sequenceFlow", ns):
        flows.append({
            "id": elem.get("id", ""),
            "from": elem.get("sourceRef", ""),
            "to": elem.get("targetRef", ""),
            "name": elem.get("name", ""),
        })
    return flows


def _parse_lanes(root: ET.Element, ns: str | None) -> list[dict[str, Any]]:
    lanes = []
    for lane_set in _find_all(root, "laneSet", ns):
        for lane in _find_all(lane_set, "lane", ns):
            elements = []
            for ref in _find_all(lane, "flowNodeRef", ns):
                if ref.text:
                    elements.append(ref.text.strip())
            lanes.append({
                "id": lane.get("id", ""),
                "name": lane.get("name", ""),
                "elements": elements,
            })
    return lanes


def _parse_data_objects(root: ET.Element, ns: str | None) -> list[dict[str, str]]:
    data_objects = []
    for tag in ("dataObject", "dataObjectReference"):
        for elem in _find_all(root, tag, ns):
            data_objects.append({
                "id": elem.get("id", ""),
                "name": elem.get("name", ""),
            })
    return data_objects


def _detect_namespace(root: ET.Element) -> str | None:
    if root.tag.startswith("{"):
        return root.tag.split("}")[0][1:]
    return None


def _empty_result() -> dict[str, Any]:
    return {
        "process_name": None,
        "tasks": [],
        "gateways": [],
        "flows": [],
        "events": [],
        "lanes": [],
        "data_objects": [],
    }


def parse_bpmn(file_path: str) -> dict[str, Any]:
    """Parse a BPMN 2.0 XML file and return a structured process model.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the XML is malformed or contains no BPMN process.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        raise ValueError(f"Malformed XML: {e}") from e

    root = tree.getroot()
    ns = _detect_namespace(root)

    process = (
        root.find(f".//{{{ns}}}process") if ns
        else root.find(".//process")
    )

    if process is None:
        return _empty_result()

    return {
        "process_name": process.get("name"),
        "tasks": _parse_typed_elements(root, ns, TASK_TYPES),
        "gateways": _parse_typed_elements(root, ns, GATEWAY_TYPES),
        "flows": _parse_flows(root, ns),
        "events": _parse_typed_elements(root, ns, EVENT_TYPES),
        "lanes": _parse_lanes(root, ns),
        "data_objects": _parse_data_objects(root, ns),
    }
