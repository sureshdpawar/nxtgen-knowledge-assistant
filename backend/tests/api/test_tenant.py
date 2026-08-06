from tests.conftest import client


def test_get_tenants():

    response = client.get("/api/v1/tenants")

    assert response.status_code == 200

    assert isinstance(response.json(), list)
    
def test_create_tenant():

    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "Pytest Tenant",
            "slug": "pytest-tenant"
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Pytest Tenant"

    assert body["slug"] == "pytest-tenant"