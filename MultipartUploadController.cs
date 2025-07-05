using Microsoft.AspNetCore.Mvc;
using Amazon.S3;
using Amazon.S3.Model;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace YourNamespace.Controllers
{
    [Route("api/upload/multipart")]
    [ApiController]
    public class MultipartUploadController : ControllerBase
    {
        private readonly IAmazonS3 _s3Client;
        private readonly string _bucketName;
        
        public MultipartUploadController(IAmazonS3 s3Client, IConfiguration configuration)
        {
            _s3Client = s3Client;
            _bucketName = configuration["S3:BucketName"];
        }
        
        [HttpPost("init")]
        public async Task<IActionResult> InitiateMultipartUpload(string filename)
        {
            try
            {
                // Initialize multipart upload
                var initiateRequest = new InitiateMultipartUploadRequest
                {
                    BucketName = _bucketName,
                    Key = filename
                };
                
                var initiateResponse = await _s3Client.InitiateMultipartUploadAsync(initiateRequest);
                string uploadId = initiateResponse.UploadId;
                
                // Calculate number of parts (assuming 5MB chunks)
                int partSize = 5 * 1024 * 1024; // 5MB
                int maxParts = 10000; // S3 limit
                
                // Generate presigned URLs for each part
                var presignedUrls = new List<string>();
                for (int partNumber = 1; partNumber <= maxParts; partNumber++)
                {
                    var request = new GetPreSignedUrlRequest
                    {
                        BucketName = _bucketName,
                        Key = filename,
                        Verb = HttpVerb.PUT,
                        Expires = DateTime.UtcNow.AddHours(1),
                        UploadId = uploadId,
                        PartNumber = partNumber
                    };
                    
                    string url = _s3Client.GetPreSignedURL(request);
                    presignedUrls.Add(url);
                }
                
                return Ok(new { uploadId, presignedUrls });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Failed to initiate multipart upload: {ex.Message}");
            }
        }
        
        [HttpPost("complete")]
        public async Task<IActionResult> CompleteMultipartUpload(string uploadId, [FromBody] CompleteMultipartUploadRequest request)
        {
            try
            {
                var completeRequest = new Amazon.S3.Model.CompleteMultipartUploadRequest
                {
                    BucketName = _bucketName,
                    Key = request.FileName,
                    UploadId = uploadId,
                    PartETags = request.Parts.Select(p => new PartETag(p.PartNumber, p.ETag)).ToList()
                };
                
                var completeResponse = await _s3Client.CompleteMultipartUploadAsync(completeRequest);
                
                return Ok(new { location = completeResponse.Location });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Failed to complete multipart upload: {ex.Message}");
            }
        }
        
        [HttpPost("abort")]
        public async Task<IActionResult> AbortMultipartUpload(string uploadId, string filename)
        {
            try
            {
                var abortRequest = new AbortMultipartUploadRequest
                {
                    BucketName = _bucketName,
                    Key = filename,
                    UploadId = uploadId
                };
                
                await _s3Client.AbortMultipartUploadAsync(abortRequest);
                
                return Ok(new { message = "Upload aborted successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Failed to abort multipart upload: {ex.Message}");
            }
        }
    }
    
    public class CompleteMultipartUploadRequest
    {
        public string FileName { get; set; }
        public List<PartDetail> Parts { get; set; }
    }
    
    public class PartDetail
    {
        public int PartNumber { get; set; }
        public string ETag { get; set; }
    }
}
