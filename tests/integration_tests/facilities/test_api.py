async def test_get_facilities(ac):
    response = await ac.get("/facilities")
    assert response.status_code == 200


async def test_add_facilities(ac):
    facility_title = "Wi Fi"

    response = await ac.post("/facilities", json={"title": facility_title})
    res = response.json()

    assert response.status_code == 200
    assert isinstance(res, dict)
    assert "data" in res
    assert res["data"]["title"] == facility_title
