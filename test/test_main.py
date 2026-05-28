import pytest
from main import app


@pytest.fixture
def client():
    """Create and configure a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_hello(client):
    """Test that home route renders index.html successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Flask" in response.data


def test_feature1(client):
    """Test that /feature1 returns 200 OK and correct message."""
    response = client.get("/feature1")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "早上要看股票"


def test_feature2(client):
    """Test that /feature2 returns 200 OK and correct message."""
    response = client.get("/feature2")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "要找下午上班的公司"


from unittest.mock import MagicMock, patch
from botocore.exceptions import NoCredentialsError, ClientError
import io

@patch("main.get_s3_client")
def test_feature3_list_success(mock_get_s3, client):
    """Test that /feature3 successfully lists S3 files."""
    mock_s3 = MagicMock()
    mock_get_s3.return_value = mock_s3
    
    import datetime
    # Mocking S3 response
    mock_s3.list_objects_v2.return_value = {
        'Contents': [
            {
                'Key': 'test-file-1.txt',
                'Size': 1024,
                'LastModified': datetime.datetime(2026, 5, 28, 12, 0, 0)
            }
        ]
    }
    
    response = client.get("/feature3")
    assert response.status_code == 200
    assert b"test-file-1.txt" in response.data
    assert b"1024" in response.data
    assert b"2026-05-28 12:00:00" in response.data


@patch("main.get_s3_client")
def test_feature3_list_no_credentials(mock_get_s3, client):
    """Test that /feature3 displays credential configuration guide when AWS credentials are missing."""
    mock_s3 = MagicMock()
    mock_get_s3.return_value = mock_s3
    mock_s3.list_objects_v2.side_effect = NoCredentialsError()
    
    response = client.get("/feature3")
    assert response.status_code == 200
    assert "未偵測到 AWS 認證憑證".encode("utf-8") in response.data
    assert "aws configure".encode("utf-8") in response.data


@patch("main.get_s3_client")
def test_feature3_upload(mock_get_s3, client):
    """Test uploading a file to /feature3/upload."""
    mock_s3 = MagicMock()
    mock_get_s3.return_value = mock_s3
    
    data = {
        'file': (io.BytesIO(b"dummy file contents"), 'test_upload.txt')
    }
    
    response = client.post("/feature3/upload", data=data, content_type='multipart/form-data')
    assert response.status_code == 302
    assert response.headers['Location'].endswith("/feature3")
    
    # Verify upload_fileobj was called
    mock_s3.upload_fileobj.assert_called_once()


@patch("main.get_s3_client")
def test_feature3_download(mock_get_s3, client):
    """Test downloading a file from /feature3/download/<filename>."""
    mock_s3 = MagicMock()
    mock_get_s3.return_value = mock_s3
    
    mock_body = MagicMock()
    mock_body.read.return_value = b"test s3 download contents"
    mock_s3.get_object.return_value = {
        'Body': mock_body
    }
    
    response = client.get("/feature3/download/test_download.txt")
    assert response.status_code == 200
    assert response.data == b"test s3 download contents"
    assert "attachment; filename=test_download.txt" in response.headers['Content-Disposition']


@patch("main.get_s3_client")
def test_feature3_delete(mock_get_s3, client):
    """Test deleting a file via /feature3/delete/<filename>."""
    mock_s3 = MagicMock()
    mock_get_s3.return_value = mock_s3
    
    response = client.post("/feature3/delete/test_delete.txt")
    assert response.status_code == 302
    assert response.headers['Location'].endswith("/feature3")
    
    mock_s3.delete_object.assert_called_once_with(Bucket="ckc-26", Key="test_delete.txt")

