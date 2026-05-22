
      const DEFAULT_PREVIEW = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";
    


    
      function togglePassword(inputId, iconContainer) {
        const input = document.getElementById(inputId);
        const img = iconContainer.querySelector("img");
        if (input.type === "password") {
            input.type = "text";
            img.src = "/static/res/eye-off.png";
        } else {
            input.type = "password";
            img.src = "/static/res/eye.png";
        }
    }
    

    
      function setupDropZone(dropAreaId, inputId, previewId) {
        const dropArea = document.getElementById(dropAreaId);
        const fileInput = document.getElementById(inputId);
        const preview = document.getElementById(previewId);

        // Click to browse
        dropArea.addEventListener("click", () => fileInput.click());

        // Browse handler
        fileInput.addEventListener("change", handleFiles);

        // Drag & Drop events
        dropArea.addEventListener("dragover", (e) => {
          e.preventDefault();
          dropArea.classList.add("dragover");
        });

        dropArea.addEventListener("dragleave", () => {
          dropArea.classList.remove("dragover");
        });

        dropArea.addEventListener("drop", (e) => {
          e.preventDefault();
          dropArea.classList.remove("dragover");
          const file = e.dataTransfer.files[0];
          if (file) showPreview(file);
        });

        function handleFiles() {
          const file = fileInput.files[0];
          if (file) showPreview(file);
        }

        function showPreview(file) {
          const url = URL.createObjectURL(file);

          // ✅ Only clear inside current drop area
          dropArea.parentElement.querySelectorAll(".preview-img, .preview-audio, .preview-video")
            .forEach(el => el.style.display = "none");

          if (file.type.startsWith("image")) {
            preview.src = url;
            preview.style.display = "block";
          }

          else if (file.type.startsWith("audio")) {
            preview.src = url;
            preview.style.display = "block";
          }

          else if (file.type.startsWith("video")) {
            preview.src = url;
            preview.style.display = "block";
          }
        }
      }

      // Initialize for both Encode & Decode areas
      setupDropZone("encode-drop-area", "encode-file", "encode-preview");
      setupDropZone("decode-drop-area", "decode-file", "decode-preview");
      setupDropZone("encode-audio-drop-area", "encode-audio-file", "encode-audio-preview");
      setupDropZone("encode-video-drop-area", "encode-video-file", "encode-video-preview");
      setupDropZone("decode-audio-drop-area", "decode-audio-file", "decode-audio-preview");
      setupDropZone("decode-video-drop-area", "decode-video-file", "decode-video-preview");
    

    
    
    function clearResults() {
      document.getElementById("encodeResult").innerHTML = "";
      document.getElementById("encodeAudioResult").innerHTML = "";
      document.getElementById("encodeVideoResult").innerHTML = "";
      document.getElementById("decodeResult").innerHTML = "";
      document.getElementById("decodeAudioResult").innerHTML = "";
      document.getElementById("decodeVideoResult").innerHTML = "";
    }

    function clearPreviews() {
      document.getElementById("encode-preview").src = DEFAULT_PREVIEW;
      document.getElementById("decode-preview").src = DEFAULT_PREVIEW;
      const audioPreviews = [
        "encode-audio-preview",
        "decode-audio-preview"
      ];
      const videoPreviews = [
        "encode-video-preview",
        "decode-video-preview"
      ];
      audioPreviews.forEach(id => {
        const audio = document.getElementById(id);
        audio.pause();
        audio.src = "";
        audio.load();
        audio.style.display = "none";
      });
      videoPreviews.forEach(id => {
        const video = document.getElementById(id);
        video.pause();
        video.src = "";
        video.load();
        video.style.display = "none";
      });
    }
    
    
    
    
    let selectedType = "image";
    let selectedMode = "encode";

    function showForm() {

      // hide ALL forms
      document.querySelectorAll(".workspace").forEach(f => f.classList.remove("active"));

      const formId = `${selectedMode}-${selectedType}`;
      const form = document.getElementById(formId);

      if (form) form.classList.add("active");
    }

    /* COVER SELECTOR */
    document.querySelectorAll(".cover-btn").forEach(btn => {
      btn.addEventListener("click", () => {

        document.querySelectorAll(".cover-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        selectedType = btn.dataset.type;
        clearResults();
        clearPreviews();
        showForm();
        updateHiddenInputs();
      });
    });

    /* MODE TOGGLE */
    document.getElementById("encode").addEventListener("change", () => {
      selectedMode = "encode";
      clearResults();
      clearPreviews();
      showForm();
    });

    document.getElementById("decode").addEventListener("change", () => {
      selectedMode = "decode";
      clearResults();
      clearPreviews();
      showForm();
    });

    /* HIDDEN INPUT */
    function updateHiddenInputs() {
      document.querySelectorAll("form").forEach(form => {
        let old = form.querySelector("input[name='stegMethod']");
        if (old) old.remove();

        let input = document.createElement("input");
        input.type = "hidden";
        input.name = "stegMethod";
        input.value = selectedType;

        form.appendChild(input);
      });
    }

    /* INITIAL LOAD */
    updateHiddenInputs();
    showForm();
    
    
    
    
    document.getElementById("encode-image").addEventListener("submit", async function (e) {
      e.preventDefault();

      const resultBox = document.getElementById("encodeResult");
      resultBox.className = "result-msg";
      resultBox.innerHTML = "<strong>Processing...</strong>";

      try {
        const response = await fetch("/encode", {
          method: "POST",
          body: new FormData(this)
        });

        const data = await response.json();

        if (data.status === "success") {
          resultBox.classList.add("success");
          resultBox.innerHTML = `
          <div class="result-card">
              <h3>✓ Stego Image Generated Successfully</h3>

              <div class="result-info">
                  <p><strong>Type:</strong> ${data.file_type}</p>
                  <p><strong>Size:</strong> ${data.file_size}</p>
              </div>
              <a href="/download/${data.output_file}"
                 class="download-btn">
                 Download Stego Image
              </a>
          </div>
          `;
          
          if (data.metrics) {
              displayMetrics("image", data.metrics);
          }
          
          this.reset();
          document.getElementById("encode-preview").src = DEFAULT_PREVIEW;

        } else {
          this.reset();
          resultBox.classList.add("error");
          resultBox.innerHTML = "<strong>Error:</strong> " + data.message;
        }

      } catch (err) {
        this.reset();
        resultBox.classList.add("error");
        resultBox.innerHTML = "<strong>Error:</strong> Server error.";
      }
    });
    
    
    
    
    
    document.getElementById("encode-audio").addEventListener("submit", async function (e) {
      e.preventDefault();

      const resultBox = document.getElementById("encodeAudioResult");
      resultBox.className = "result-msg";
      resultBox.innerHTML = "<strong>Processing...</strong>";

      try {
        const response = await fetch("/encode", {
          method: "POST",
          body: new FormData(this)
        });

        const data = await response.json();

        if (data.status === "success") {
          resultBox.classList.add("success");
          resultBox.innerHTML = `
          <div class="result-card">
              <h3>✓ Stego Audio Generated Successfully</h3>
              <div class="result-info">
                  <p><strong>Type:</strong> ${data.file_type}</p>
                  <p><strong>Size:</strong> ${data.file_size}</p>
              </div>
              <a href="/download/${data.output_file}"
                 class="download-btn">
                 Download Stego Audio
              </a>
          </div>
          `;
          
          if (data.metrics) {
              displayMetrics("audio", data.metrics);
          }
          
          this.reset();
          document.getElementById("encode-audio-preview").style.display = "none";
        } else {
          this.reset();
          resultBox.classList.add("error");
          resultBox.innerHTML = "<strong>Error:</strong> " + data.message;
        }

      } catch (err) {
        this.reset();
        resultBox.classList.add("error");
        resultBox.innerHTML = "<strong>Error:</strong> Server error.";
      }
    });
    
    
    
    document.getElementById("encode-video").addEventListener("submit", async function (e) {
      e.preventDefault();

      const resultBox = document.getElementById("encodeVideoResult");
      resultBox.className = "result-msg";
      resultBox.innerHTML = "<strong>Processing...</strong>";

      try {
        const response = await fetch("/encode", {
          method: "POST",
          body: new FormData(this)
        });

        const data = await response.json();

        if (data.status === "success") {
          resultBox.classList.add("success");
          resultBox.innerHTML = `
          <div class="result-card">
              <h3>✓ Stego Video Generated Successfully</h3>
              <div class="result-info">
                  <p><strong>Type:</strong> ${data.file_type}</p>
                  <p><strong>Size:</strong> ${data.file_size}</p>
              </div>
              <a href="/download/${data.output_file}"
                 class="download-btn">
                 Download Stego Video
              </a>
          </div>
          `;
          
          if (data.metrics) {
              displayMetrics("video", data.metrics);
          }
          
          this.reset();
          document.getElementById("encode-video-preview").style.display = "none";
        } else {
          this.reset();
          resultBox.classList.add("error");
          resultBox.innerHTML = "<strong>Error:</strong> " + data.message;
        }

      } catch (err) {
        this.reset();
        resultBox.classList.add("error");
        resultBox.innerHTML = "<strong>Error:</strong> Server error.";
      }
    });
    
    
    
    
    document.getElementById("decode-image").addEventListener("submit", async function (e) {
      e.preventDefault();

      const resultBox = document.getElementById("decodeResult");
      resultBox.className = "result-msg";
      resultBox.innerHTML = "<strong>Processing...</strong>";

      try {
        const response = await fetch("/decode", {
          method: "POST",
          body: new FormData(this)
        });

        const data = await response.json();

        if (data.status === "success") {
          resultBox.classList.add("success");
          resultBox.innerHTML = `<strong>Hidden Message:</strong> 
                                <span id="decodedTextImage">${data.message}</span>
                                <button type="button" class="copy-btn" onclick="copyToClipboard(this, 'decodedTextImage')">
                                <img src="/static/res/copy.png" class="copy-icon">
                                </button>`;
          autoClearMessage("decodeResult", 60000);
          this.reset();
          document.getElementById("decode-preview").src = DEFAULT_PREVIEW;

        } else {
          this.reset();
          document.getElementById("decode-preview").src = DEFAULT_PREVIEW;
          resultBox.classList.add("error");
          resultBox.innerHTML = "<strong>Error:</strong> " + data.message;
        }

      } catch (err) {
        resultBox.classList.add("error");
        resultBox.innerHTML = "<strong>Error:</strong> Server error.";
      }
    });
    
    
    
    
    document.getElementById("decode-audio").addEventListener("submit", async function (e) {
      e.preventDefault();

      const resultBox = document.getElementById("decodeAudioResult");
      resultBox.className = "result-msg";
      resultBox.innerHTML = "<strong>Processing...</strong>";

      try {
        const response = await fetch("/decode", {
          method: "POST",
          body: new FormData(this)
        });

        const data = await response.json();

        if (data.status === "success") {
          resultBox.classList.add("success");
          resultBox.innerHTML = `<strong>Hidden Message:</strong> 
                                <span id="decodedTextAudio">${data.message}</span>
                                <button type="button" class="copy-btn" onclick="copyToClipboard(this, 'decodedTextAudio')">
                                <img src="/static/res/copy.png" class="copy-icon">
                                </button>`;
          autoClearMessage("decodeAudioResult", 60000);
          this.reset();
          document.getElementById("decode-audio-preview").style.display = "none";
        } else {
          this.reset();
          document.getElementById("decode-audio-preview").style.display = "none";
          resultBox.classList.add("error");
          resultBox.innerHTML = "<strong>Error:</strong> " + data.message;
        }

      } catch (err) {
        resultBox.classList.add("error");
        resultBox.innerHTML = "<strong>Error:</strong> Server error during decoding.";
      }
    });
    
    
    
    document.getElementById("decode-video").addEventListener("submit", async function (e) {
      e.preventDefault();

      const resultBox = document.getElementById("decodeVideoResult");
      resultBox.className = "result-msg";
      resultBox.innerHTML = "<strong>Processing...</strong>";

      try {
        const response = await fetch("/decode", {
          method: "POST",
          body: new FormData(this)
        });

        const data = await response.json();

        if (data.status === "success") {
          resultBox.classList.add("success");
          resultBox.innerHTML = `<strong>Hidden Message:</strong> 
                                <span id="decodedTextVideo">${data.message}</span>
                                <button type="button" class="copy-btn" onclick="copyToClipboard(this, 'decodedTextVideo')">
                                <img src="/static/res/copy.png" class="copy-icon">
                                </button>`;
          autoClearMessage("decodeVideoResult", 60000);
          this.reset();
          document.getElementById("decode-video-preview").style.display = "none";
        } else {
          this.reset();
          document.getElementById("decode-video-preview").style.display = "none";
          resultBox.classList.add("error");
          resultBox.innerHTML = "<strong>Error:</strong> " + data.message;
        }

      } catch (err) {
        resultBox.classList.add("error");
        resultBox.innerHTML = "<strong>Error:</strong> Server error during decoding.";
      }
    });
    
    
    
    function autoClearMessage(elementId, delay = 60000) {
      setTimeout(() => {
        const el = document.getElementById(elementId);
        if (el) {
          el.innerHTML = "";
          el.className = ""; // remove success/error styling
        }
      }, delay);
    }
    
    
    
    function copyToClipboard(button, elementId) {
      const text = document.getElementById(elementId).innerText;

      navigator.clipboard.writeText(text).then(() => {

        const img = button.querySelector("img");

        // change to tick
        img.src = "/static/res/tick.png";

        // optional: slight scale effect
        img.style.transform = "scale(1.2)";

        // revert back after 1 second
        setTimeout(() => {
          img.src = "/static/res/copy.png";
          img.style.transform = "scale(1)";
        }, 1000);

      });
    }
    
    
    
    
    
    let qualityChartInstance = null;

    function displayMetrics(method, metrics) {
        const circleCard = document.querySelector(".circle-card");
        const metricsSection = document.getElementById("metricsSection");
        const metricsCards = document.getElementById("metricsCards");
        const ctx = document.getElementById("qualityChart").getContext("2d");

        metricsSection.style.display = "block";
        metricsCards.innerHTML = "";

        let labels = [];
        let values = [];

        function addCard(title, value) {
            metricsCards.innerHTML += `
                <div class="metric-card">
                    <h4>${title}</h4>
                    <p>${value}</p>
                </div>
            `;
        }

        if (method === "image") {
            circleCard.style.display = "flex";
            labels = ["PSNR", "SSIM"];
            values = [metrics.psnr, metrics.ssim];

            addCard("PSNR", metrics.psnr + " dB");
            addCard("SSIM", metrics.ssim);

            if (metrics.heatmap) {
                const heatmapContainer = document.getElementById("heatmapContainer");
                const heatmapImage = document.getElementById("heatmapImage");

                heatmapContainer.style.display = "block";

                heatmapImage.src =
                    "/outputs/" +
                    metrics.heatmap +
                    "?t=" +
                    new Date().getTime();
            } else {
                document.getElementById("heatmapContainer").style.display = "none";
            }
        }

        else if (method === "audio") {
            circleCard.style.display = "none";
            labels = ["SNR", "MSE"];
            values = [metrics.snr, metrics.mse];

            addCard("SNR", metrics.snr + " dB");
            addCard("MSE", metrics.mse);
            
            document.getElementById("heatmapContainer").style.display = "none";
        }

        else if (method === "video") {
            circleCard.style.display = "none";
            labels = ["Original Size", "Stego Size", "Increase", "% Increase"];
            values = [
                metrics.original_size_kb,
                metrics.stego_size_kb,
                metrics.size_increase_kb,
                metrics.percentage_increase
            ];

            addCard("Original Size", metrics.original_size_kb + " KB");
            addCard("Stego Size", metrics.stego_size_kb + " KB");
            addCard("Size Increase", metrics.size_increase_kb + " KB");
            addCard("% Increase", metrics.percentage_increase + "%");
            
            document.getElementById("heatmapContainer").style.display = "none";
        }

        if (qualityChartInstance) {
            qualityChartInstance.destroy();
        }

        // =========================
        // MODERN METRICS CHART
        // =========================

        let chartType = "bar";

        if (method === "image") {
            chartType = "bar";
        }

        else if (method === "audio") {
            chartType = "radar";
        }

        else if (method === "video") {
            chartType = "doughnut";
        }

        qualityChartInstance = new Chart(ctx, {
            type: chartType,

            data: {
                labels: labels,

                datasets: [{
                    label: "Quality Metrics",
                    data: values,

                    backgroundColor: [
                        "rgba(37, 99, 235, 0.75)",
                        "rgba(16, 185, 129, 0.75)",
                        "rgba(245, 158, 11, 0.75)",
                        "rgba(239, 68, 68, 0.75)"
                    ],

                    borderColor: [
                        "rgba(37, 99, 235, 1)",
                        "rgba(16, 185, 129, 1)",
                        "rgba(245, 158, 11, 1)",
                        "rgba(239, 68, 68, 1)"
                    ],

                    borderWidth: 2,
                    borderRadius: 12,
                    hoverOffset: 12,
                    tension: 0.4,
                    fill: true
                }]
            },

            options: {

                responsive: true,

                plugins: {

                    legend: {
                        display: true,
                        labels: {
                            color: "#e5e7eb",
                            font: {
                                size: 13,
                                weight: "600"
                            }
                        }
                    },

                    tooltip: {
                        enabled: true
                    }
                },

                scales: {

                    y: {
                        beginAtZero: true,

                        ticks: {
                            color: "#cbd5e1"
                        },

                        grid: {
                            color: "rgba(255,255,255,0.08)"
                        }
                    },

                    x: {

                        ticks: {
                            color: "#cbd5e1"
                        },

                        grid: {
                            display: false
                        }
                    }
                }
            }
        });


        // =========================
        // SSIM CIRCULAR RING
        // =========================

        if (metrics.ssim) {

            const ssimPercent =
                Math.round(metrics.ssim * 100);

            const ssimText =
                document.getElementById("ssimValue");

            const circle =
                document.getElementById("ssimCircle");

            if (ssimText && circle) {

                ssimText.innerText =
                    `${ssimPercent}%`;

                const radius = 90;

                const circumference =
                    2 * Math.PI * radius;

                const offset =
                    circumference -
                    (ssimPercent / 100) * circumference;

                circle.style.strokeDasharray =
                    circumference;

                circle.style.strokeDashoffset =
                    offset;
            }
        }
    }
    
    
    
    