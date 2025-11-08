"""Client helper for invoking the Inheco EventReceiver (PMS) service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
import xml.etree.ElementTree as ET

SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
SILA_NS = "http://sila.coop"
XMLNS_NS = "http://www.w3.org/2000/xmlns/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
XSD_NS = "http://www.w3.org/2001/XMLSchema"


@dataclass
class SiLAReturnValue:
  return_code: int
  message: Optional[str] = None
  duration: Optional[str] = None
  device_class: int = 30

  def to_element(self, tag: str = "returnValue") -> ET.Element:
    element = ET.Element(ET.QName(SILA_NS, tag))
    ET.SubElement(element, ET.QName(SILA_NS, "returnCode")).text = str(self.return_code)
    if self.message is not None:
      ET.SubElement(element, ET.QName(SILA_NS, "message")).text = self.message
    if self.duration is not None:
      ET.SubElement(element, ET.QName(SILA_NS, "duration")).text = self.duration
    ET.SubElement(element, ET.QName(SILA_NS, "deviceClass")).text = str(self.device_class)
    return element

  def to_xml(self, tag: str = "returnValue") -> str:
    return ET.tostring(self.to_element(tag), encoding="unicode")


def _build_envelope(payload: ET.Element) -> bytes:
  envelope = ET.Element(ET.QName(SOAP_NS, "Envelope"))
  envelope.set(f"{{{XMLNS_NS}}}xsi", XSI_NS)
  envelope.set(f"{{{XMLNS_NS}}}xsd", XSD_NS)
  body = ET.SubElement(envelope, ET.QName(SOAP_NS, "Body"))
  body.append(payload)
  return ET.tostring(envelope, encoding="utf-8", xml_declaration=True)


class EventReceiverClient:
  """Tiny SOAP client for the EventReceiver endpoints defined in EventReceiver.wsdl."""

  def __init__(self, endpoint: str, *, timeout: float = 5.0) -> None:
    self.endpoint = endpoint
    self.timeout = timeout
    self._last_envelope: Optional[bytes] = None

  def _send(self, action: str, payload: ET.Element) -> str:
    envelope = _build_envelope(payload)
    self._last_envelope = envelope
    headers = {
      "Content-Type": "text/xml; charset=utf-8",
      "SOAPAction": f'"{SILA_NS}/{action}"',
    }
    response = requests.post(
      self.endpoint,
      data=envelope,
      headers=headers,
      timeout=self.timeout,
    )
    response.raise_for_status()
    return response.text

  def response_event(
    self,
    request_id: int,
    *,
    return_value: Optional[SiLAReturnValue] = None,
    response_data: Optional[str] = None,
  ) -> str:
    root = ET.Element(ET.QName(SILA_NS, "ResponseEvent"))
    ET.SubElement(root, ET.QName(SILA_NS, "requestId")).text = str(request_id)
    if return_value is not None:
      root.append(return_value.to_element("returnValue"))
    if response_data is not None:
      ET.SubElement(root, ET.QName(SILA_NS, "responseData")).text = response_data
    return self._send("ResponseEvent", root)

  def data_event(self, request_id: int, data_value: Optional[str] = None) -> str:
    root = ET.Element(ET.QName(SILA_NS, "DataEvent"))
    ET.SubElement(root, ET.QName(SILA_NS, "requestId")).text = str(request_id)
    if data_value is not None:
      ET.SubElement(root, ET.QName(SILA_NS, "dataValue")).text = data_value
    return self._send("DataEvent", root)

  def error_event(
    self,
    request_id: int,
    *,
    return_value: Optional[SiLAReturnValue] = None,
    continuation_task: Optional[str] = None,
  ) -> str:
    root = ET.Element(ET.QName(SILA_NS, "ErrorEvent"))
    ET.SubElement(root, ET.QName(SILA_NS, "requestId")).text = str(request_id)
    if return_value is not None:
      root.append(return_value.to_element("returnValue"))
    if continuation_task is not None:
      ET.SubElement(root, ET.QName(SILA_NS, "continuationTask")).text = continuation_task
    return self._send("ErrorEvent", root)

  def status_event(
    self,
    *,
    device_id: Optional[str] = None,
    return_value: Optional[SiLAReturnValue] = None,
    event_description: Optional[str] = None,
  ) -> str:
    root = ET.Element(ET.QName(SILA_NS, "StatusEvent"))
    root.set(f"{{{XMLNS_NS}}}i", XSI_NS)
    if device_id is not None:
      ET.SubElement(root, ET.QName(SILA_NS, "deviceId")).text = device_id
    if return_value is not None:
      root.append(return_value.to_element("returnValue"))
    if event_description is not None:
      ET.SubElement(root, ET.QName(SILA_NS, "eventDescription")).text = event_description
    return self._send("StatusEvent", root)
