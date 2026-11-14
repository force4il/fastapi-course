import pytest


@pytest.mark.parametrize(
    "email, password, status_code_reg, status_code_log, correct_email",
    [
        ("first@gmail.com", "1234", 200, 200, True),
        ("first@gmail.com", "5678", 409, 401, True),
        ("test", "test", 422, 401, False),
        ("second@mail.com", "hello", 200, 200, True),
    ],
)
async def test_api_auth(
    email: str, password: str, status_code_reg: int, status_code_log: int, correct_email: bool, ac
):
    ac.cookies.clear()
    ac.headers.pop("Authorization", None)

    response_register = await ac.post(
        "auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "test",
            "last_name": "test",
        },
    )
    assert response_register.status_code == status_code_reg
    response_login = await ac.post(
        "auth/login",
        json={
            "email": email,
            "password": password,
            "first_name": "test",
            "last_name": "test",
        },
    )
    if not correct_email:
        assert response_login.status_code == 422
    else:
        assert response_login.status_code == status_code_log
    res_login = response_login.json()
    assert isinstance(res_login, dict)
    assert ("access_token" if status_code_log == 200 else "detail") in res_login

    response_get_me = await ac.get("auth/me")
    assert response_get_me.status_code == status_code_log
    res_get = response_get_me.json()
    if status_code_log == 200:
        assert "id" in res_get and "email" in res_get and "password" not in res_get
    else:
        assert "detail" in res_get

    response_logout = await ac.post("/auth/logout")
    assert response_logout.status_code == status_code_log
    assert "access_token" not in ac.cookies
    res_logout = response_logout.json()
    if status_code_log == 200:
        assert "status" in res_logout
        assert "Успешный выход из системы" == res_logout["status"]
    else:
        assert "detail" in res_logout
