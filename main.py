import os
import io
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-for-ckc-26")

BUCKET_NAME = "ckc-26"

def get_s3_client():
    """Return a client using default credential provider chain (secure for local and EC2 IAM Roles)."""
    return boto3.client('s3')

@app.route("/")
def hello():
    """Home route rendering the interactive UI."""
    return render_template("index.html")

@app.route("/feature1")
def feature1() -> str:
    """Feature 1 route."""
    return "早上要看股票"

@app.route("/feature2")
def feature2() -> str:
    """Feature 2 route."""
    return "要找下午上班的公司"

@app.route("/feature3")
def feature3():
    """Feature 3: S3 File Manager page."""
    files = []
    error_msg = None
    credential_error = False

    try:
        s3 = get_s3_client()
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                })
    except NoCredentialsError:
        error_msg = "未偵測到 AWS 認證憑證。請在本機設定 AWS 憑證，或在 EC2 上設定 IAM 角色。"
        credential_error = True
    except ClientError as e:
        error_msg = f"AWS S3 存取錯誤: {e.response['Error']['Message']}"
        if e.response['Error']['Code'] in ('InvalidAccessKeyId', 'SignatureDoesNotMatch'):
            credential_error = True
    except Exception as e:
        error_msg = f"發生非預期錯誤: {str(e)}"

    return render_template(
        "feature3.html",
        files=files,
        bucket_name=BUCKET_NAME,
        error_msg=error_msg,
        credential_error=credential_error
    )

@app.route("/feature3/upload", methods=["POST"])
def feature3_upload():
    """Upload a file to S3."""
    if 'file' not in request.files:
        flash("未選擇任何檔案", "error")
        return redirect(url_for('feature3'))
    
    file = request.files['file']
    if file.filename == '':
        flash("未選擇任何檔案", "error")
        return redirect(url_for('feature3'))
    
    try:
        filename = secure_filename(file.filename)
        s3 = get_s3_client()
        s3.upload_fileobj(file, BUCKET_NAME, filename)
        flash(f"檔案 {filename} 上傳成功！", "success")
    except NoCredentialsError:
        flash("未偵測到 AWS 憑證，無法上傳檔案。", "error")
    except ClientError as e:
        flash(f"上傳失敗 (S3 錯誤): {e.response['Error']['Message']}", "error")
    except Exception as e:
        flash(f"上傳失敗: {str(e)}", "error")
        
    return redirect(url_for('feature3'))

@app.route("/feature3/download/<path:filename>")
def feature3_download(filename):
    """Download a file from S3 directly via stream."""
    try:
        s3 = get_s3_client()
        file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
        file_data = file_obj['Body'].read()
        return send_file(
            io.BytesIO(file_data),
            download_name=filename,
            as_attachment=True
        )
    except NoCredentialsError:
        flash("未偵測到 AWS 憑證，無法下載檔案。", "error")
    except ClientError as e:
        flash(f"下載失敗 (S3 錯誤): {e.response['Error']['Message']}", "error")
    except Exception as e:
        flash(f"下載失敗: {str(e)}", "error")
        
    return redirect(url_for('feature3'))

@app.route("/feature3/delete/<path:filename>", methods=["POST"])
def feature3_delete(filename):
    """Delete a file from S3."""
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
        flash(f"檔案 {filename} 已成功刪除！", "success")
    except NoCredentialsError:
        flash("未偵測到 AWS 憑證，無法刪除檔案。", "error")
    except ClientError as e:
        flash(f"刪除失敗 (S3 錯誤): {e.response['Error']['Message']}", "error")
    except Exception as e:
        flash(f"刪除失敗: {str(e)}", "error")
        
    return redirect(url_for('feature3'))

if __name__ == "__main__":
    # Start the Flask web application on port 19191
    app.run(host="0.0.0.0",port=5000, debug=True)