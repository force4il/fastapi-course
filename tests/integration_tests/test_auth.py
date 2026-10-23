from src.services.auth import AuthService


def test_encode_and_decode_access_token():
    data = {"user_id": 1}
    jwt_token = AuthService().create_access_token(data)

    payload = AuthService().decode_token(jwt_token)
    assert payload
    assert payload["user_id"] == data["user_id"]
    



