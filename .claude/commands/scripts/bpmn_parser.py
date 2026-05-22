"""BPMN 2.0 XML parser that outputs JSON process models."""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"

TASK_TYPES = {
    "task",
    "userTask",
    "serviceTask",
    "manualTask",
    "scriptTask",
    "sendTask",
    "receiveTask",
    "businessRuleTask",
}

GATEWAY_TYPES = {
    "exclusiveGateway",
    "parallelGateway",
    "inclusiveGateway",
    "eventBasedGateway",
    "complexGateway",
}

EVENT_TYPES = {
    "startEvent",
    "endEvent",
    "intermediateThrowEvent",
    "intermediateCatchEvent",
    "boundaryEvent",
}


def get_element_tag(tag: str) -> str:
    """Strip namespace from tag if present."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def find_all_with_ns(root: ET.Element, local_name: str, ns: str | None) -> list[ET.Element]:
    """Find all elements matching local_name, handling both namespaced and bare XML."""
    if ns:
        return root.findall(f".//{{{ns}}}{local_name}")
    return root.findall(f".//{local_name}")


def parse_tasks(root: ET.Element, ns: str | None) -> list[dict[str, str]]:
    """Extract all task elements."""
    tasks = []
    for task_type in TASK_TYPES:
        for elem in find_all_with_ns(root, task_type, ns):
            tasks.append({
                "id": elem.get("id", ""),
                "name": elem.get("name", ""),
                "type": task_type,
            })
    return tasks


def parse_gateways(root: ET.Element, ns: str | None) -> list[dict[str, str]]:
    """Extract all gateway elements."""
    gateways = []
    for gw_type in GATEWAY_TYPES:
        for elem in find_all_with_ns(root, gw_type, ns):
            gateways.append({
                "id": elem.get("id", ""),
                "name": elem.get("name", ""),
                "type": gw_type,
            })
    return gateways


def parse_events(root: ET.Element, ns: str | None) -> list[dict[str, str]]:
    """Extract all event elements."""
    events = []
    for event_type in EVENT_TYPES:
        for elem in find_all_with_ns(root, event_type, ns):
            events.append({
                "id": elem.get("id", ""),
                "name": elem.get("name", ""),
                "type": event_type,
            })
    return events


def parse_flows(root: ET.Element, ns: str | None) -> list[dict[str, str]]:
    """Extract all sequence flow elements."""
    flows = []
    for elem in find_all_with_ns(root, "sequenceFlow", ns):
        flow = {
            "id": elem.get("id", ""),
            "from": elem.get("sourceRef", ""),
            "to": elem.get("targetRef", ""),
            "name": elem.get("name", ""),
        }
        flows.append(flow)
    return flows


def parse_lanes(root: ET.Element, ns: str | None) -> list[dict[str, Any]]:
    """Extract all lane elements with their assigned elements."""
    lanes = []
    for lane_set in find_all_with_ns(root, "laneSet", ns):
        for lane in find_all_with_ns(lane_set, "lane", ns):
            elements = []
            for flow_node_ref in find_all_with_ns(lane, "flowNodeRef", ns):
                if flow_node_ref.text:
                    elements.append(flow_node_ref.text.strip())
            lanes.append({
                "id": lane.get("id", ""),
                "name": lane.get("name", ""),
                "elements": elements,
            })
    return lanes


def parse_data_objects(root: ET.Element, ns: str | None) -> list[dict[str, str]]:
    """Extract all data object elements."""
    data_objects = []
    for elem in find_all_with_ns(root, "dataObject", ns):
        data_objects.append({
            "id": elem.get("id", ""),
            "name": elem.get("name", ""),
        })
    for elem in find_all_with_ns(root, "dataObjectReference", ns):
        data_objects.append({
            "id": elem.get("id", ""),
            "name": elem.get("name", ""),
        })
    return data_objects


def parse_bpmn(file_path: str) -> dict[str, Any]:
    """Parse BPMN 2.0 XML file and return process model as dict."""
    path = Path(file_path)

    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"Error: Malformed XML: {e}", file=sys.stderr)
        sys.exit(1)

    root = tree.getroot()

    # Detect namespace
    ns = None
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0][1:]

    # Find process element
    process = None
    if ns:
        process = root.find(f".//{{{ns}}}process")
    else:
        process = root.find(".//process")

    if process is None:
        print("Warning: No BPMN process element found", file=sys.stderr)
        return {
            "process_name": None,
            "tasks": [],
            "gateways": [],
            "flows": [],
            "events": [],
            "lanes": [],
            "data_objects": [],
        }

    process_name = process.get("name")

    return {
        "process_name": process_name,
        "tasks": parse_tasks(root, ns),
        "gateways": parse_gateways(root, ns),
        "flows": parse_flows(root, ns),
        "events": parse_events(root, ns),
        "lanes": parse_lanes(root, ns),
        "data_objects": parse_data_objects(root, ns),
    }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Parse BPMN 2.0 XML files to JSON")
    parser.add_argument("file", help="Path to BPMN XML file")
    args = parser.parse_args()

    result = parse_bpmn(args.file)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
