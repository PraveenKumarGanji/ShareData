using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System;
using System.IO;
using System.Threading.Tasks;

namespace YourNamespace.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class UploadController : ControllerBase
    {
        private readonly string _uploadFolder;
        
        public UploadController(IConfiguration configuration)
        {
            _uploadFolder = configuration["UploadSettings:FolderPath"];
            Directory.CreateDirectory(_uploadFolder); // Ensure folder exists
        }
        
        [HttpPost]
        [RequestSizeLimit(100 * 1024 * 1024)] // 100MB limit for standard uploads
        public async Task<IActionResult> Upload()
        {
            try
            {
                var files = Request.Form.Files;
                if (files.Count == 0)
                    return BadRequest("No files received.");
                
                foreach (var file in files)
                {
                    if (file.Length > 0)
                    {
                        var filePath = Path.Combine(_uploadFolder, file.FileName);
                        using (var stream = new FileStream(filePath, FileMode.Create))
                        {
                            await file.CopyToAsync(stream);
                        }
                    }
                }
                
                return Ok(new { message = "Files uploaded successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
