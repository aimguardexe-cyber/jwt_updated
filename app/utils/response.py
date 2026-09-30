import requests
from app.proto import my_pb2, output_pb2
from app.utils.gen_token import encrypt_message, get_token
from config.settings import AES_KEY, AES_IV
import binascii
import datetime
import uuid
from app.utils.device_data import get_random_profile
import base64

# Global session for connection pooling/keep-alive
session = requests.Session()


def parse_response(response_content):
    # Parse the response to extract key fields
    response_dict = {}
    lines = response_content.split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            response_dict[key.strip()] = value.strip().strip('"')
    return response_dict


def process_token(uid, password):
    token_data = get_token(password, uid)
    if not token_data:
        return {"uid": uid, "error": "Failed to retrieve token"}
    
    # Get dynamic timestamp, ISP and device model profile
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    profile = get_random_profile()

    TEMPLATE_B64 = (
        "GhMyMDI2LTA5LTI4IDE4OjQ3OjQ3IglmcmVlIGZpcmUoAToHMS4xMzIuOEI1QW5kcm9pZCBPUyA5IC8gQVBJLTI4IChTUDFBLjIxMDgxMi4w"
        "MTYvRzk5OEJYWFU0QlVMRilKCEhhbmRoZWxkUgRBVCZUWgRXSUZJYLYKaO4FcgMyNDB6G0FSTXY3IFZGUHYzIE5FT04gfCAyMDAwIHwgNIAB"
        "theKAQ9BZHJlbm8gKFRNKSA1NDCSAStPcGVuR0wgRVMgMy4yICg0LjUuMCAtIEJ1aWxkIDMyLjAuMTAxLjY3OTApmgErR29vZ2xlfDhlNjIz"
        "YzQxLTU1OTAtNGFmZS1hZjI1LTg1MGE1MmEyNGNkMKIBDjExMC4zOC4yNTEuMjIwqgECZW6yASBhNTYxYmVjYjI1Y2NhZTlhOWJhYzBhNmZj"
        "MDQ2N2IxN7oBATTCAQhIYW5kaGVsZMoBEHNhbXN1bmcgU00tRzk5OELSAQJQS+oBQGM4ZGNkMTNlNjExNGFjNzAwMDY2NTU3ZWFhZjEzZmJj"
        "NzU2YzVkYWU2MjAwOTc3MWIwNWEyMTQwMWRhOGM2ZDLwAQHKAgRBVCZU0gIEV0lGScoDIDc0MjhiMjUzZGVmYzE2NDAxOGM2MDRhMWViYmZl"
        "YmRm4AP27gfoA/eYB/ADvj74A5ktgASgzAeIBPbuB5AEoMwHmAT27gfIBAHSBD0vZGF0YS9hcHAvY29tLmR0cy5mcmVlZmlyZXRoLTl2UjZs"
        "OVdZMEpJMkdjOURnYUQ1MkE9PS9saWIvYXJt4AQB6gRfYjhlMGNkNWUyOTVlZWU0MmY1ODYwZDNjODZlNDgzZGR8L2RhdGEvYXBwL2NvbS5k"
        "dHMuZnJlZWZpcmV0aC05dlI2bDlXWTBKSTJHYzlEZ2FENTJBPT0vYmFzZS5hcGvwBAP4BAGKBQIzMpoFCjIwMTkxMjEyMjmoBQOyBQlPcGVu"
        "R0xFUzK4Bf8fwAUE4AXNgwHqBQdhbmRyb2lk8gVwS3FzSFR6VEUxRmNGU0NoK0QzT2licEdURlJFRHBGQ2Z4WHRpbXRGdVBoU3kyR3hhZHNZ"
        "SjluNHhpWmM3bmNnTnNwREF3SlpXcGRXdW1IQ2hNSVNkMjJreXNiRm4zcTM4VUVjUVJ0R29PQ256ckZCMfgF5+QGggYmeyJjdXJfcmF0ZSI6"
        "bnVsbCwic3VwcG9ydF9ldGMyIjpmYWxzZX2IBgGaBgE0ogYBNLIGJUAHEhMHWQ4DT1BVQ1wFFldDbApUDABYI1xABjUXVVsJFT1bBWHABvLR"
        "BcgGAdIGigFodHRwczovL2RsLmJzLmZyZWVmaXJlbW9iaWxlLmNvbS9saXZlL0FCSG90VXBkYXRlcy98aHR0cHM6Ly9jb3JlLWJzLmZyZWVm"
        "aXJlbW9iaWxlLmNvbS9saXZlL0FCSG90VXBkYXRlcy98MjExYzkzMzE2OGY1NTkwMmM3ZGZiZmQ4YzRlMjk1N2TaBhIxLjhlYjdkYzQ5MzZh"
        "YTdjNmE="
    )
    tmpl_bytes = base64.b64decode(TEMPLATE_B64)
    
    game_data = my_pb2.GameData()
    game_data.ParseFromString(tmpl_bytes)
    
    # Update dynamic values
    game_data.timestamp = current_time
    game_data.open_id = token_data["open_id"]
    game_data.access_token = token_data["access_token"]
    game_data.platform_type = 4
    game_data.field_99 = "4"
    game_data.field_100 = b"4"
    

    # Serialize the data
    serialized_data = game_data.SerializeToString()

    # Encrypt the data
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_data)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode("utf-8")

    # Send the encrypted data to the server
    url = "https://loginbp.ppmainecoonghj.com/MajorLogin"
    headers = {
        "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "X-GA-SV": "1790603268",
        "Authorization": "Bearer",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB55",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
    }
    edata = bytes.fromhex(hex_encrypted_data)
    # print(edata)
    try:
        response = session.post(
            url, data=edata, headers=headers, verify=False, timeout=10
        )
        if response.status_code == 200:
            # Try to decrypt the Protobuf response
            # The server response contains a 64-byte header before the protobuf data
            example_msg = output_pb2.Lokesh()
            try:
                # print(response.content)
                example_msg.ParseFromString(response.content[64:])
                # Parse the response to extract key fields
                response_dict = parse_response(str(example_msg))
                # print(response_dict)
                return {
                    "server": response_dict.get("region", "N/A"),
                    "status": response_dict.get("status", "N/A"),
                    "team": "aimguard",
                    "token": response_dict.get("token", "N/A"),
                    "access_token" : game_data.access_token,
                    "uid": uid,
                }
            except Exception as e:
                return {"uid": uid, "error": f"Failed to deserialize the response: {e}"}
        else:
            return {
                "uid": uid,
                "error": f"Failed to get response: HTTP {response.status_code}, {response.reason}",
            }
    except requests.RequestException as e:
        return {"uid": uid, "error": f"An error occurred while making the request: {e}"}
