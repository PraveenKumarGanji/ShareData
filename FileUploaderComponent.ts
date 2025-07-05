import { Component } from '@angular/core';
import { HttpClient, HttpRequest, HttpEventType, HttpResponse } from '@angular/common/http';

@Component({
  selector: 'app-file-uploader',
  templateUrl: './file-uploader.component.html',
  styleUrls: ['./file-uploader.component.scss']
})
export class FileUploaderComponent {
  public progress: number = 0;
  public message: string = '';
  public isUploading: boolean = false;
  
  constructor(private http: HttpClient) { }
  
  // Standard upload for smaller files
  uploadStandard(files: FileList) {
    if (files.length === 0) return;
    
    this.isUploading = true;
    this.progress = 0;
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append(files[i].name, files[i]);
    }
    
    const uploadReq = new HttpRequest('POST', 'api/upload', formData, {
      reportProgress: true,
    });
    
    this.http.request(uploadReq).subscribe(event => {
      if (event.type === HttpEventType.UploadProgress && event.total) {
        this.progress = Math.round(100 * event.loaded / event.total);
      } else if (event.type === HttpEventType.Response) {
        this.message = 'Upload complete!';
        this.isUploading = false;
      }
    }, error => {
      this.message = 'Upload failed: ' + error.message;
      this.isUploading = false;
    });
  }
  
  // Multipart upload for large files
  async uploadLargeFile(files: FileList) {
    if (files.length === 0) return;
    
    const file = files[0]; // Handle one file at a time for large uploads
    this.isUploading = true;
    this.progress = 0;
    this.message = 'Initializing upload...';
    
    try {
      // Step 1: Initialize multipart upload
      const initResponse = await this.http.post<{uploadId: string, presignedUrls: string[]}>
        (`api/upload/multipart/init?filename=${encodeURIComponent(file.name)}`, {}).toPromise();
      
      const uploadId = initResponse.uploadId;
      const presignedUrls = initResponse.presignedUrls;
      const chunkSize = 5 * 1024 * 1024; // 5MB chunks
      const totalChunks = Math.ceil(file.size / chunkSize);
      const uploadedETags: string[] = [];
      
      // Step 2: Upload each chunk
      for (let partNumber = 1; partNumber <= totalChunks; partNumber++) {
        const start = (partNumber - 1) * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);
        
        this.message = `Uploading part ${partNumber} of ${totalChunks}...`;
        
        // Upload the chunk
        const response = await fetch(presignedUrls[partNumber - 1], {
          method: 'PUT',
          body: chunk
        });
        
        if (!response.ok) {
          throw new Error(`Failed to upload part ${partNumber}: ${response.statusText}`);
        }
        
        // Get the ETag from the response headers
        const etag = response.headers.get('ETag');
        if (etag) {
          uploadedETags.push(etag.replace(/"/g, ''));
        }
        
        // Update progress
        this.progress = Math.round((partNumber / totalChunks) * 100);
      }
      
      // Step 3: Complete the multipart upload
      this.message = 'Finalizing upload...';
      const completeResponse = await this.http.post(
        `api/upload/multipart/complete?uploadId=${uploadId}`, 
        { parts: uploadedETags.map((etag, index) => ({ PartNumber: index + 1, ETag: etag })) }
      ).toPromise();
      
      this.message = 'Upload complete!';
      this.isUploading = false;
    } catch (error) {
      this.message = `Upload failed: ${error.message}`;
      this.isUploading = false;
    }
  }
}
