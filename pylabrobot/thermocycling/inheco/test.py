from tc import InhecoPMSClient, SiLAReturnValue

# Call GetParameters on the thermocycler and print results.
with InhecoPMSClient(endpoint="http://169.254.173.35:7071/ihc") as client:
    rv = SiLAReturnValue(return_code=1, message="Python client test")
    response_payload = (
        "<ResponseData>"
        "<ParameterSet>"
        '<Parameter name="Message">'
        "<String>Hello from Python client</String>"
        "</Parameter>"
        "</ParameterSet>"
        "</ResponseData>"
    )
    resp = client.response_event(
        request_id=1,
        return_value=rv,
        response_data=response_payload,
    )
    print("Sent envelope:")
    print(client._client._last_envelope.decode("utf-8"))
    print("Response:")
    print(resp)