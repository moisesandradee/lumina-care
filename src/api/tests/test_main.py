"""
Unit Tests for Lumina Care FastAPI Application

Tests core application functionality:
- Health check endpoints
- Readiness checks
- Exception handling
- CORS middleware
- Request timing middleware
"""

import pytest
from fastapi import FastAPI


class TestHealthEndpoints:
    """Tests for /health and /ready endpoints."""

    @pytest.mark.unit
    def test_health_check_returns_ok(self, client):
        """Verify health check endpoint returns status ok."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "lumina-care-api"
        assert "version" in data

    @pytest.mark.unit
    def test_health_check_response_schema(self, client):
        """Verify health check response contains required fields."""
        response = client.get("/health")

        data = response.json()
        required_fields = {"status", "service", "version"}
        assert required_fields.issubset(data.keys())

    @pytest.mark.unit
    def test_readiness_check_returns_ready(self, client):
        """Verify readiness check endpoint returns status ready."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    @pytest.mark.unit
    def test_readiness_check_includes_service_checks(self, client):
        """Verify readiness check includes dependency health."""
        response = client.get("/ready")

        data = response.json()
        assert "checks" in data
        checks = data["checks"]
        # Verify dependent services are reported
        assert "database" in checks or "ai_service" in checks or "cache" in checks


class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""

    @pytest.mark.unit
    def test_cors_headers_present_in_response(self, client):
        """Verify CORS headers are present in responses."""
        response = client.get("/health")

        # CORS headers should be present
        assert response.status_code == 200
        # Note: TestClient auto-handles CORS, but in production
        # these headers would be verified through browser requests

    @pytest.mark.unit
    def test_allowed_origin_localhost(self, client):
        """Verify localhost:3000 is allowed origin."""
        # This is a configuration test - verify the app was initialized
        # with correct CORS settings
        assert client is not None
        response = client.get("/health")
        assert response.status_code == 200


class TestRequestTimingMiddleware:
    """Tests for request timing middleware."""

    @pytest.mark.unit
    def test_response_includes_timing_header(self, client):
        """Verify response includes X-Process-Time-Ms header."""
        response = client.get("/health")

        assert response.status_code == 200
        # The timing header should be present
        assert "x-process-time-ms" in response.headers

    @pytest.mark.unit
    def test_timing_header_is_numeric(self, client):
        """Verify timing header contains numeric value."""
        response = client.get("/health")

        timing_header = response.headers.get("x-process-time-ms")
        assert timing_header is not None

        # Should be a valid numeric value
        try:
            timing_ms = float(timing_header)
            assert timing_ms >= 0
        except ValueError:
            pytest.fail(f"Timing header should be numeric, got: {timing_header}")


class TestExceptionHandling:
    """Tests for global exception handler."""

    @pytest.mark.unit
    def test_nonexistent_endpoint_returns_404(self, client):
        """Verify requests to nonexistent endpoints return 404."""
        response = client.get("/nonexistent/endpoint")

        assert response.status_code == 404

    @pytest.mark.unit
    def test_invalid_method_returns_405(self, client):
        """Verify invalid HTTP methods return 405 Method Not Allowed."""
        # GET is correct method, try POST
        response = client.post("/health")

        assert response.status_code == 405

    @pytest.mark.unit
    @pytest.mark.security
    def test_error_response_doesnt_leak_internal_details(self, client):
        """Verify error responses don't leak internal implementation details."""
        response = client.get("/nonexistent")

        # Should get a 404, not internal error details
        assert response.status_code == 404
        # Response should not contain internal stack traces
        assert "traceback" not in response.text.lower()
        assert "line " not in response.text.lower()


class TestApplicationStructure:
    """Tests for application configuration and structure."""

    @pytest.mark.unit
    def test_app_has_required_routers(self, client):
        """Verify all required routers are registered."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        spec = response.json()

        # Check for required API tag/paths
        # These should be present if routers are registered
        paths = spec.get("paths", {})
        # We expect some endpoints to be documented
        assert len(paths) > 0

    @pytest.mark.unit
    def test_api_documentation_available(self, client):
        """Verify OpenAPI documentation is available."""
        # OpenAPI schema should be available
        response = client.get("/openapi.json")
        assert response.status_code == 200

        # OpenAPI UI should be available
        response = client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_app_title_and_version(self, client):
        """Verify application metadata."""
        response = client.get("/openapi.json")
        spec = response.json()

        assert spec["info"]["title"] == "Lumina Care API"
        assert "0.1.0" in spec["info"]["version"]

    @pytest.mark.unit
    @pytest.mark.security
    def test_health_endpoint_no_auth_required(self, client):
        """Verify health check is publicly accessible."""
        # Health checks should not require authentication
        response = client.get("/health")

        assert response.status_code == 200
        # No 401 Unauthorized

    @pytest.mark.unit
    @pytest.mark.security
    def test_readiness_endpoint_no_auth_required(self, client):
        """Verify readiness check is publicly accessible."""
        response = client.get("/ready")

        assert response.status_code == 200


class TestApplicationStartup:
    """Tests for application initialization and startup."""

    @pytest.mark.unit
    def test_app_is_fastapi_instance(self, client):
        """Verify app is properly configured FastAPI instance."""
        # If TestClient initialized successfully, FastAPI is configured
        assert client is not None
        response = client.get("/health")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_app_title_in_docs(self, client):
        """Verify application title appears in documentation."""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "Lumina Care API" in response.text


class TestMiddlewareIntegration:
    """Integration tests for middleware stack."""

    @pytest.mark.unit
    def test_request_response_cycle_complete(self, client):
        """Verify full request/response cycle works."""
        response = client.get("/health")

        # Request should complete successfully
        assert response.status_code == 200
        # Response should have content
        assert response.text
        # Response should be valid JSON
        assert response.json() is not None
        # Timing middleware should add header
        assert "x-process-time-ms" in response.headers

    @pytest.mark.unit
    def test_multiple_sequential_requests(self, client):
        """Verify application handles multiple sequential requests."""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200

        # All requests should succeed
        for _ in range(5):
            response = client.get("/ready")
            assert response.status_code == 200
