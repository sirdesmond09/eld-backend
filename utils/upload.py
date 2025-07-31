"""
Upload service for handling file uploads with django-storages.
"""

import os
import uuid
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone


class UploadService:
    """Service for handling file uploads with django-storages."""
    
    def upload_file(
        self, 
        file_obj, 
        folder: str = "uploads", 
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file using django-storages.
        
        Args:
            file_obj: File object to upload
            folder: Folder path in storage
            filename: Custom filename (optional)
            
        Returns:
            Dict containing upload information
        """
        if not filename:
            filename = self._generate_filename(file_obj.name)
        
        file_path = os.path.join(folder, filename)
        
        # Save using django-storages (will upload to S3 if configured)
        saved_path = default_storage.save(file_path, file_obj)
        
        # Get the URL
        file_url = default_storage.url(saved_path)
        
        return {
            "filename": filename,
            "file_path": saved_path,
            "file_url": file_url,
            "file_size": file_obj.size,
            "file_type": file_obj.content_type,
            "uploaded_at": timezone.now(),
        }
    
    def upload_file_async(
        self, 
        file_data: bytes, 
        filename: str, 
        folder: str = "uploads"
    ) -> Dict[str, Any]:
        """
        Upload a file asynchronously using django-storages.
        
        Args:
            file_data: File data as bytes
            filename: Name of the file
            folder: Folder path in storage
            
        Returns:
            Dict containing upload information
        """
        file_path = os.path.join(folder, filename)
        
        # Create ContentFile from bytes
        content_file = ContentFile(file_data, name=filename)
        
        # Save using django-storages
        saved_path = default_storage.save(file_path, content_file)
        
        # Get the URL
        file_url = default_storage.url(saved_path)
        
        return {
            "filename": filename,
            "file_path": saved_path,
            "file_url": file_url,
            "file_size": len(file_data),
            "uploaded_at": timezone.now(),
        }
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            default_storage.delete(file_path)
            return True
        except Exception:
            return False
    
    def get_file_url(self, file_path: str) -> Optional[str]:
        """
        Get the URL for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File URL or None if not found
        """
        try:
            return default_storage.url(file_path)
        except Exception:
            return None
    
    def _generate_filename(self, original_filename: str) -> str:
        """Generate a unique filename."""
        ext = os.path.splitext(original_filename)[1]
        return f"{uuid.uuid4().hex}{ext}"
    
    def validate_file(
        self, 
        file_obj, 
        allowed_types: Optional[list] = None, 
        max_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate a file.
        
        Args:
            file_obj: File object to validate
            allowed_types: List of allowed MIME types
            max_size: Maximum file size in bytes
            
        Returns:
            Dict containing validation result
        """
        errors = []
        
        # Check file type
        if allowed_types and file_obj.content_type not in allowed_types:
            errors.append(f"File type {file_obj.content_type} not allowed")
        
        # Check file size
        if max_size and file_obj.size > max_size:
            errors.append(f"File size {file_obj.size} exceeds maximum {max_size}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
        }


class ImageUploadService(UploadService):
    """Service for handling image uploads."""
    
    def __init__(self):
        super().__init__()
        self.allowed_types = [
            "image/jpeg",
            "image/jpg", 
            "image/png",
            "image/gif",
            "image/webp"
        ]
        self.max_size = 10 * 1024 * 1024  # 10MB
    
    def upload_image(
        self, 
        image_file, 
        folder: str = "images"
    ) -> Dict[str, Any]:
        """
        Upload an image with validation.
        
        Args:
            image_file: Image file object
            folder: Folder path in storage
            
        Returns:
            Dict containing upload information
        """
        # Validate image
        validation = self.validate_file(
            image_file, 
            self.allowed_types, 
            self.max_size
        )
        
        if not validation["is_valid"]:
            raise ValueError(f"Image validation failed: {validation['errors']}")
        
        return self.upload_file(image_file, folder)


class DocumentUploadService(UploadService):
    """Service for handling document uploads."""
    
    def __init__(self):
        super().__init__()
        self.allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "text/csv",
        ]
        self.max_size = 50 * 1024 * 1024  # 50MB
    
    def upload_document(
        self, 
        document_file, 
        folder: str = "documents"
    ) -> Dict[str, Any]:
        """
        Upload a document with validation.
        
        Args:
            document_file: Document file object
            folder: Folder path in storage
            
        Returns:
            Dict containing upload information
        """
        # Validate document
        validation = self.validate_file(
            document_file, 
            self.allowed_types, 
            self.max_size
        )
        
        if not validation["is_valid"]:
            raise ValueError(f"Document validation failed: {validation['errors']}")
        
        return self.upload_file(document_file, folder) 