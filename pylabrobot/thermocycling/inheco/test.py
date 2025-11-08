from tc import InhecoPMSClient, SiLAReturnValue
from tc import ThermoCycler

with InhecoPMSClient(endpoint="http://169.254.173.35:7071/ihc") as client:
    rv = SiLAReturnValue(return_code=1, message="Python client test", device_class=30)
    resp = client.status_event(
        device_id="python-client",
        return_value=rv,
        event_description="Connectivity check from tc.ipynb",
    )
    print("Sent envelope:")
    print(client._client._last_envelope.decode("utf-8"))
    print("Response:")
    print(resp)

    # Call GetParameters on the thermocycler (SOAP interface) and print results.
    tc = ThermoCycler(ip="169.254.173.35")
    params = tc.get_parameters(
        pms_client=client,
        send_status_event=True,
        status_event_description="GetParameters hook from test.py",
    )
    print("Parsed ThermoCyclerParameters:")
    print(params)