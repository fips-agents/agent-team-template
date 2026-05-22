"""Tests for BPMN 2.0 XML parser."""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / ".claude" / "commands" / "scripts"
sys.path.insert(0, str(scripts_dir))

from bpmn_parser import parse_bpmn


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_BPMN = FIXTURES_DIR / "sample.bpmn"


def test_parse_sample_bpmn():
    """Parse the sample loan approval BPMN successfully."""
    result = parse_bpmn(str(SAMPLE_BPMN))

    assert result["process_name"] == "Loan Approval Process"
    assert isinstance(result["tasks"], list)
    assert isinstance(result["gateways"], list)
    assert isinstance(result["events"], list)
    assert isinstance(result["flows"], list)
    assert isinstance(result["lanes"], list)
    assert isinstance(result["data_objects"], list)


def test_task_extraction():
    """Verify correct number and types of tasks extracted."""
    result = parse_bpmn(str(SAMPLE_BPMN))
    tasks = result["tasks"]

    assert len(tasks) == 4

    task_names = {t["name"] for t in tasks}
    assert "Submit Application" in task_names
    assert "Generate Offer" in task_names
    assert "Review Offer" in task_names
    assert "Send Rejection" in task_names

    task_types = {t["type"] for t in tasks}
    assert "userTask" in task_types
    assert "serviceTask" in task_types


def test_gateway_extraction():
    """Verify gateway extracted correctly."""
    result = parse_bpmn(str(SAMPLE_BPMN))
    gateways = result["gateways"]

    assert len(gateways) == 1
    assert gateways[0]["name"] == "Credit Check"
    assert gateways[0]["type"] == "exclusiveGateway"
    assert gateways[0]["id"] == "Gateway_CreditCheck"


def test_event_extraction():
    """Verify start and end events extracted."""
    result = parse_bpmn(str(SAMPLE_BPMN))
    events = result["events"]

    assert len(events) == 3

    event_types = {e["type"] for e in events}
    assert "startEvent" in event_types
    assert "endEvent" in event_types

    event_names = {e["name"] for e in events}
    assert "Application Started" in event_names
    assert "Loan Approved" in event_names
    assert "Loan Rejected" in event_names


def test_flow_extraction():
    """Verify sequence flows extracted with correct connections."""
    result = parse_bpmn(str(SAMPLE_BPMN))
    flows = result["flows"]

    assert len(flows) == 7

    # Check specific flow connections
    flow_map = {f["id"]: f for f in flows}

    assert flow_map["Flow_1"]["from"] == "StartEvent_1"
    assert flow_map["Flow_1"]["to"] == "Task_Submit"

    assert flow_map["Flow_Approved"]["from"] == "Gateway_CreditCheck"
    assert flow_map["Flow_Approved"]["to"] == "Task_GenerateOffer"
    assert flow_map["Flow_Approved"]["name"] == "Approved"

    assert flow_map["Flow_Rejected"]["from"] == "Gateway_CreditCheck"
    assert flow_map["Flow_Rejected"]["to"] == "Task_SendRejection"
    assert flow_map["Flow_Rejected"]["name"] == "Rejected"


def test_lane_extraction():
    """Verify lanes extracted with correct element assignments."""
    result = parse_bpmn(str(SAMPLE_BPMN))
    lanes = result["lanes"]

    assert len(lanes) == 2

    lane_map = {l["name"]: l for l in lanes}

    assert "Applicant" in lane_map
    assert "Loan Officer" in lane_map

    applicant_elements = set(lane_map["Applicant"]["elements"])
    assert "StartEvent_1" in applicant_elements
    assert "Task_Submit" in applicant_elements
    assert "Task_ReviewOffer" in applicant_elements

    officer_elements = set(lane_map["Loan Officer"]["elements"])
    assert "Gateway_CreditCheck" in officer_elements
    assert "Task_GenerateOffer" in officer_elements
    assert "Task_SendRejection" in officer_elements


def test_data_object_extraction():
    """Verify data objects extracted."""
    result = parse_bpmn(str(SAMPLE_BPMN))
    data_objects = result["data_objects"]

    assert len(data_objects) == 1
    assert data_objects[0]["name"] == "Application Form"
    assert data_objects[0]["id"] == "DataObject_ApplicationForm"


def test_file_not_found(tmp_path):
    """Handle missing file gracefully."""
    nonexistent = tmp_path / "does_not_exist.bpmn"

    with pytest.raises(SystemExit) as exc_info:
        parse_bpmn(str(nonexistent))

    assert exc_info.value.code == 1


def test_malformed_xml(tmp_path):
    """Handle malformed XML gracefully."""
    malformed = tmp_path / "malformed.bpmn"
    malformed.write_text("<?xml version='1.0'?><broken><unclosed>")

    with pytest.raises(SystemExit) as exc_info:
        parse_bpmn(str(malformed))

    assert exc_info.value.code == 1


def test_valid_xml_no_process(tmp_path):
    """Handle valid XML without BPMN process element."""
    no_process = tmp_path / "no_process.xml"
    no_process.write_text("<?xml version='1.0'?><root><child/></root>")

    result = parse_bpmn(str(no_process))

    assert result["process_name"] is None
    assert result["tasks"] == []
    assert result["gateways"] == []
    assert result["flows"] == []
    assert result["events"] == []
    assert result["lanes"] == []
    assert result["data_objects"] == []


def test_bare_xml_without_namespace(tmp_path):
    """Parse BPMN without namespace prefix."""
    bare_bpmn = tmp_path / "bare.bpmn"
    bare_bpmn.write_text("""<?xml version="1.0"?>
<definitions>
  <process id="Process_1" name="Simple Process">
    <startEvent id="Start_1" name="Start"/>
    <userTask id="Task_1" name="Do Work"/>
    <endEvent id="End_1" name="End"/>
    <sequenceFlow id="Flow_1" sourceRef="Start_1" targetRef="Task_1"/>
    <sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="End_1"/>
  </process>
</definitions>
""")

    result = parse_bpmn(str(bare_bpmn))

    assert result["process_name"] == "Simple Process"
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["name"] == "Do Work"
    assert len(result["events"]) == 2
    assert len(result["flows"]) == 2
