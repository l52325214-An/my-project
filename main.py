import os
import io
import boto3
from datetime import datetime
from botocore.exceptions import NoCredentialsError, ClientError
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-for-ckc-26")

BUCKET_NAME = "ckc-26"
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_s3_client():
    """Return a client using default credential provider chain (secure for local and EC2 IAM Roles)."""
    return boto3.client('s3')

def get_local_files():
    """List files in the local uploads directory."""
    files = []
    if os.path.exists(UPLOAD_FOLDER):
        for name in os.listdir(UPLOAD_FOLDER):
            path = os.path.join(UPLOAD_FOLDER, name)
            if os.path.isfile(path):
                stat = os.stat(path)
                files.append({
                    'key': name,
                    'size': stat.st_size,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'Local'
                })
    return files

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
    """Feature 3: S3 File Manager page with local fallback."""
    files = []
    error_msg = None
    s3_available = True

    try:
        s3 = get_s3_client()
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'S3'
                })
    except NoCredentialsError:
        s3_available = False
        error_msg = "未偵測到 AWS 認證憑證。系統已自動切換至「本機快取模式 (Local Mode)」。"
    except ClientError as e:
        s3_available = False
        error_msg = f"AWS S3 存取異常: {e.response['Error']['Message']}。系統已自動切換至「本機快取模式」。"
    except Exception as e:
        s3_available = False
        error_msg = f"發生非預期錯誤: {str(e)}。系統已自動切換至「本機快取模式」。"

    # Merge local fallback files
    local_files = get_local_files()
    files.extend(local_files)
    
    # Sort files by last modified date descending
    files.sort(key=lambda x: x['last_modified'], reverse=True)

    return render_template(
        "feature3.html",
        files=files,
        bucket_name=BUCKET_NAME,
        error_msg=error_msg,
        s3_available=s3_available
    )

@app.route("/feature3/upload", methods=["POST"])
def feature3_upload():
    """Upload a file to S3 (or fallback to local uploads directory)."""
    if 'file' not in request.files:
        flash("未選擇任何檔案", "error")
        return redirect(url_for('feature3'))
    
    file = request.files['file']
    if file.filename == '':
        flash("未選擇任何檔案", "error")
        return redirect(url_for('feature3'))
    
    filename = secure_filename(file.filename)
    
    try:
        s3 = get_s3_client()
        s3.upload_fileobj(file, BUCKET_NAME, filename)
        flash(f"檔案 {filename} 成功上傳至 AWS S3！", "success")
    except (NoCredentialsError, ClientError):
        # Fallback to local storage
        try:
            file.seek(0)  # Reset stream position
            local_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(local_path)
            flash(f"已成功將檔案 {filename} 上傳至本機快取目錄 (本機模式已啟用)", "success")
        except Exception as le:
            flash(f"上傳至本機失敗: {str(le)}", "error")
    except Exception as e:
        flash(f"上傳至 S3 失敗: {str(e)}", "error")
        
    return redirect(url_for('feature3'))

@app.route("/feature3/download/<path:filename>")
def feature3_download(filename):
    """Download a file (from local uploads or S3)."""
    # 1. Try local folder first
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(local_path) and os.path.isfile(local_path):
        return send_file(local_path, as_attachment=True)
        
    # 2. Try S3
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
        flash("未偵測到 AWS 憑證，且本機找不到該檔案。", "error")
    except ClientError as e:
        flash(f"下載失敗 (S3 錯誤): {e.response['Error']['Message']}", "error")
    except Exception as e:
        flash(f"下載失敗: {str(e)}", "error")
        
    return redirect(url_for('feature3'))

@app.route("/feature3/delete/<path:filename>", methods=["POST"])
def feature3_delete(filename):
    """Delete a file from S3 and/or local uploads directory."""
    deleted_local = False
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(local_path) and os.path.isfile(local_path):
        try:
            os.remove(local_path)
            deleted_local = True
        except Exception as e:
            flash(f"本機檔案刪除失敗: {str(e)}", "error")
            
    deleted_s3 = False
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
        deleted_s3 = True
    except (NoCredentialsError, ClientError):
        pass  # Ignore S3 credential errors if local was deleted
    except Exception as e:
        flash(f"S3 檔案刪除失敗: {str(e)}", "error")
        
    if deleted_local or deleted_s3:
        flash(f"檔案 {filename} 已成功刪除！", "success")
    else:
        flash(f"找不到檔案 {filename}，刪除失敗。", "error")
        
    return redirect(url_for('feature3'))

if __name__ == "__main__":
    # Start the Flask web application on port 19191
    app.run(host="0.0.0.0",port=5000, debug=True)