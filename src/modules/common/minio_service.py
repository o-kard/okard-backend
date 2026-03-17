import boto3
import os
import uuid
from fastapi import UploadFile

class MinioService:
    def __init__(self):
        # สร้างตัวเชื่อมต่อ (Client) ไปหา MinIO
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('MINIO_URL'),
            aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('MINIO_SECRET_KEY'),
            region_name='us-east-1' # Boto3 บังคับให้ใส่ แม้ MinIO จะไม่ได้ใช้ก็ตาม
        )
        self.bucket_name = "crowdfunding-bucket"

    def upload_file(self, file: UploadFile, folder: str = "general"):
        try:
            # 1. สร้างชื่อไฟล์ใหม่แบบสุ่ม (ป้องกันชื่อไฟล์ซ้ำกันแล้วทับของเก่า)
            file_extension = file.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # 2. ประกอบร่างเป็น Path จำลอง (เช่น campaigns/covers/xxxx.jpg)
            object_name = f"{folder}/{unique_filename}"

            # 3. อัปโหลดไฟล์ขึ้น MinIO
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                object_name,
                ExtraArgs={"ContentType": file.content_type} # ให้เว็บรู้ว่าเป็นไฟล์รูป
            )
            
            # 4. คืนค่า URL เต็มๆ เพื่อเอาไปเซฟลง Database
            public_url = f"{os.getenv('MINIO_PUBLIC_URL')}/{self.bucket_name}/{object_name}"
            return public_url
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการอัปโหลด: {e}")
            return None

    def delete_file(self, file_url: str):
        try:
            # 1. เช็คก่อนว่ามี URL ส่งมาจริงๆ
            if not file_url:
                return False

            # 2. ตัดส่วนหัวที่เป็น Domain และ ชื่อ Bucket ออก เพื่อให้เหลือแค่ Object Key
            # จาก https://.../crowdfunding-bucket/users/profiles/123.jpg 
            # ให้เหลือแค่ users/profiles/123.jpg
            prefix_to_remove = f"{os.getenv('MINIO_PUBLIC_URL')}/{self.bucket_name}/"
            object_key = file_url.replace(prefix_to_remove, "")
            
            # 3. สั่งยิงคำสั่งลบทิ้งเลย!
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการลบไฟล์: {e}")
            return False