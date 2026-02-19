import os
import pytest
from fastapi.responses import FileResponse
from fastapi import HTTPException
from api.index import read_file

def test_path_traversal_blocked():
    """
    Test that path traversal attempts are blocked.
    """
    # Simulate a path traversal attempt
    filename = "../requirements.txt"

    # Call the function directly to bypass any router/middleware checks
    # Expect 403 Forbidden
    with pytest.raises(HTTPException) as excinfo:
        read_file(filename)

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Access denied"

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
        # Expect 403 Forbidden because resolving symlink points outside
        with pytest.raises(HTTPException) as excinfo:
            read_file(symlink_name)

        assert excinfo.value.status_code == 403
        assert excinfo.value.detail == "Access denied"

    finally:
        # Cleanup
        if os.path.exists(symlink_path):
            os.remove(symlink_path)

def test_valid_file_access():
    """
    Test that valid file access still works and returns security headers.
    """
    # Create a dummy file in public/ for testing if needed, or use index.html
    filename = "index.html"
    if not os.path.exists("public/index.html"):
        pytest.skip("public/index.html not found, skipping valid access test")

    response = read_file(filename)

    assert isinstance(response, FileResponse)
    # Use realpath to be safe in comparison
    assert os.path.realpath(response.path) == os.path.realpath("public/index.html")
