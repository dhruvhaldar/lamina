import os
import pytest
from fastapi.responses import FileResponse
from api.index import read_file

def test_path_traversal_blocked():
    """
    Test that path traversal attempts are blocked.
    """
    # Simulate a path traversal attempt
    filename = "../requirements.txt"

    # Call the function directly to bypass any router/middleware checks
    response = read_file(filename)

    # Check if the response is a FileResponse
    if isinstance(response, FileResponse):
        # Resolve the path and check if it escaped public/
        resolved_path = os.path.abspath(response.path)
        public_dir = os.path.abspath("public")

        # If it escaped public/, fail the test
        if not resolved_path.startswith(public_dir):
            pytest.fail(f"Path traversal vulnerability detected! Accessed: {resolved_path}")

    # If it's not a FileResponse, it likely returned an error dict, which is safe(r)
    assert isinstance(response, dict)
    assert "error" in response
    assert response["error"] == "Access denied"

def test_symlink_traversal_blocked():
    """
    Test that symlink traversal attempts are blocked.
    """
    # Create a symlink in public/ pointing to requirements.txt (outside public/)
    symlink_name = "test_symlink.txt"
    symlink_path = os.path.join("public", symlink_name)
    target_path = "../requirements.txt"

    # Ensure public dir exists
    if not os.path.exists("public"):
        os.makedirs("public")

    # Remove existing symlink if any
    if os.path.exists(symlink_path):
        os.remove(symlink_path)

    try:
        os.symlink(target_path, symlink_path)

        # Try to access the symlink
        response = read_file(symlink_name)

        # Verify it is blocked
        if isinstance(response, FileResponse):
             # Check if the response path resolves to outside public
             resolved_path = os.path.realpath(response.path)
             public_dir = os.path.realpath("public")

             if not resolved_path.startswith(public_dir):
                 pytest.fail(f"Symlink traversal vulnerability detected! Accessed: {resolved_path}")

        assert isinstance(response, dict)
        assert "error" in response
        assert response["error"] == "Access denied"

    finally:
        # Cleanup
        if os.path.exists(symlink_path):
            os.remove(symlink_path)

def test_valid_file_access():
    """
    Test that valid file access still works.
    """
    # Create a dummy file in public/ for testing if needed, or use index.html
    filename = "index.html"
    if not os.path.exists("public/index.html"):
        pytest.skip("public/index.html not found, skipping valid access test")

    response = read_file(filename)

    assert isinstance(response, FileResponse)
    # Use realpath to be safe in comparison
    assert os.path.realpath(response.path) == os.path.realpath("public/index.html")
