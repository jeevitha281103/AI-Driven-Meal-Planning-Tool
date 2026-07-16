$(document).ready(function () {
  // Global elements and variables
  const uploadSection = $(".image-section");
  const uploadFileForm = $("#upload-file");
  const btnPredict = $("#btn-predict");
  const loaderWrapper = $(".loader-wrapper");
  const resultBox = $("#result-box");
  const resultDetails = $("#result-details");
  
  // Camera variables
  const videoElement = document.getElementById("webcam");
  const canvasElement = document.getElementById("webcam-canvas");
  const btnToggleCamera = $("#btn-toggle-camera");
  const btnCapturePredict = $("#btn-capture-predict");
  const cameraPlaceholder = $("#camera-placeholder");
  let localStream = null;

  // Initialize view
  uploadSection.hide();
  loaderWrapper.hide();
  resultBox.hide();

  // Helper to show prediction results
  function displayResult(data) {
    let result;
    try {
      result = typeof data === "string" ? JSON.parse(data) : data;
    } catch (e) {
      console.error("Failed to parse JSON response:", e);
      alert("Error: Invalid response from server");
      return;
    }

    if (result.error) {
      alert("Error: " + result.error);
      return;
    }

    loaderWrapper.hide();
    
    // Build beautiful result HTML grid
    const htmlContent = `
      <div class="col-md-4 mb-3">
        <div class="p-3 bg-light rounded-3 border border-dark border-opacity-10 text-center h-100">
          <p class="text-muted small mb-1">Detected Dish</p>
          <h5 class="text-dark text-capitalize mb-0">${result.product_name.replace(/_/g, ' ')}</h5>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="p-3 bg-light rounded-3 border border-dark border-opacity-10 text-center h-100">
          <p class="text-muted small mb-1">Serving Size</p>
          <h5 class="text-primary mb-0">${result.serving_size}</h5>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="p-3 bg-light rounded-3 border border-dark border-opacity-10 text-center h-100">
          <p class="text-muted small mb-1">Estimated Calories</p>
          <h5 class="text-success mb-0">${result.calories} kcal</h5>
        </div>
      </div>
    `;

    resultDetails.html(htmlContent);
    resultBox.fadeIn(400);
  }

  // --- Upload Flow ---
  function readURL(input) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $("#imagePreview").css("background-image", "url(" + e.target.result + ")");
        $("#imagePreview").hide().fadeIn(650);
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  $("#imageUpload").change(function () {
    uploadSection.show();
    btnPredict.show();
    resultBox.hide();
    readURL(this);
  });

  // Predict uploaded image
  btnPredict.click(function () {
    var form_data = new FormData(uploadFileForm[0]);
    btnPredict.hide();
    resultBox.hide();
    loaderWrapper.show();

    $.ajax({
      type: "POST",
      url: "/predict",
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,
      success: function (data) {
        displayResult(data);
      },
      error: function (xhr) {
        loaderWrapper.hide();
        btnPredict.show();
        let errMsg = "An error occurred during prediction.";
        if (xhr.responseJSON && xhr.responseJSON.error) {
          errMsg = xhr.responseJSON.error;
        }
        alert("Error: " + errMsg);
      }
    });
  });

  // --- Live Camera Flow ---
  
  // Start or Stop Camera stream
  btnToggleCamera.click(function () {
    if (localStream === null) {
      // Start Stream
      navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: "environment",
          width: { ideal: 640 },
          height: { ideal: 480 }
        } 
      })
      .then(function (stream) {
        localStream = stream;
        videoElement.srcObject = stream;
        cameraPlaceholder.hide();
        btnCapturePredict.show();
        btnToggleCamera.html('<i class="fa-solid fa-power-off me-2"></i> Stop Camera');
        btnToggleCamera.removeClass("btn-outline-dark").addClass("btn-danger");
      })
      .catch(function (err) {
        console.error("Camera access failed:", err);
        alert("Could not access camera. Please check permissions.");
      });
    } else {
      // Stop Stream
      stopCamera();
    }
  });

  function stopCamera() {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      localStream = null;
    }
    videoElement.srcObject = null;
    cameraPlaceholder.show();
    btnCapturePredict.hide();
    btnToggleCamera.html('<i class="fa-solid fa-power-off me-2 text-danger"></i> Start Camera');
    btnToggleCamera.removeClass("btn-danger").addClass("btn-outline-dark");
  }

  // Capture frame and predict
  btnCapturePredict.click(function () {
    if (!localStream) return;

    // Draw video frame onto canvas
    const ctx = canvasElement.getContext("2d");
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    
    // Draw mirrored image (or simple draw)
    ctx.save();
    // Since video is scaledX(-1) in CSS, let's keep the canvas matching or normal
    ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    ctx.restore();

    // Convert canvas to Blob
    canvasElement.toBlob(function (blob) {
      if (!blob) {
        alert("Failed to capture image from camera.");
        return;
      }

      // Create FormData containing the captured blob
      const formData = new FormData();
      formData.append("file", blob, "camera_capture.jpg");

      // Hide results & show loading
      resultBox.hide();
      loaderWrapper.show();

      $.ajax({
        type: "POST",
        url: "/predict",
        data: formData,
        contentType: false,
        cache: false,
        processData: false,
        success: function (data) {
          displayResult(data);
        },
        error: function (xhr) {
          loaderWrapper.hide();
          let errMsg = "An error occurred during prediction.";
          if (xhr.responseJSON && xhr.responseJSON.error) {
            errMsg = xhr.responseJSON.error;
          }
          alert("Error: " + errMsg);
        }
      });
    }, "image/jpeg", 0.9);
  });

  // Stop camera when switching tab to release resource
  $('button[data-bs-toggle="pill"]').on('shown.bs.tab', function (e) {
    if (e.target.id !== "camera-tab-btn") {
      stopCamera();
    }
    // Clean up results when switching views
    resultBox.hide();
  });
});
