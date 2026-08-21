/* =========================================================
   HIRELENS
   AI Resume Analyzer
   Frontend JavaScript
   ========================================================= */


/* =========================================================
   DOM ELEMENTS
   ========================================================= */

const fileInput = document.getElementById("resumeFile");

const dropZone = document.getElementById("dropZone");

const browseButton = document.getElementById("browseButton");

const filePreview = document.getElementById("filePreview");

const fileName = document.getElementById("fileName");

const fileSize = document.getElementById("fileSize");

const removeFileButton = document.getElementById("removeFile");

const uploadStatus = document.getElementById("uploadStatus");

const analyzeButton = document.getElementById("analyzeButton");

const resultSection = document.getElementById("results-section");

const extractedText = document.getElementById("extractedText");

const copyButton = document.getElementById("copyButton");

const downloadButton = document.getElementById("downloadButton");

const jobDescription = document.getElementById("jobDescription");

const charCount = document.getElementById("charCount");

const toast = document.getElementById("toast");

const toastMessage = document.getElementById("toastMessage");


/* =========================================================
   STATE
   ========================================================= */

let selectedFile = null;

let extractedResumeText = "";


/* =========================================================
   TOAST
   ========================================================= */

function showToast(message) {

    toastMessage.textContent = message;

    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);
}


/* =========================================================
   FILE SIZE
   ========================================================= */

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return `${bytes} B`;

    }


    if (bytes < 1024 * 1024) {

        return `${(bytes / 1024).toFixed(1)} KB`;

    }


    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


/* =========================================================
   FILE VALIDATION
   ========================================================= */

function validateFile(file) {

    if (!file) {

        return false;

    }


    const isPDF =
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf");


    if (!isPDF) {

        showToast("Please select a PDF file.");

        return false;

    }


    const maxSize = 10 * 1024 * 1024;


    if (file.size > maxSize) {

        showToast("File must be smaller than 10 MB.");

        return false;

    }


    return true;
}


/* =========================================================
   SELECT FILE
   ========================================================= */

function selectFile(file) {

    if (!validateFile(file)) {

        return;

    }


    selectedFile = file;


    fileName.textContent = file.name;

    fileSize.textContent = formatFileSize(file.size);


    filePreview.classList.remove("hidden");

    uploadStatus.classList.add("hidden");

    resultSection.classList.add("hidden");


    analyzeButton.disabled = false;


    showToast("Resume selected.");
}


/* =========================================================
   BROWSE BUTTON
   ========================================================= */

browseButton.addEventListener("click", (event) => {

    event.stopPropagation();

    fileInput.click();

});


/* =========================================================
   DROP ZONE CLICK
   ========================================================= */

dropZone.addEventListener("click", () => {

    fileInput.click();

});


/* =========================================================
   FILE INPUT
   ========================================================= */

fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (file) {

        selectFile(file);

    }

});


/* =========================================================
   DRAG OVER
   ========================================================= */

dropZone.addEventListener("dragover", (event) => {

    event.preventDefault();

    dropZone.classList.add("drag-over");

});


/* =========================================================
   DRAG LEAVE
   ========================================================= */

dropZone.addEventListener("dragleave", () => {

    dropZone.classList.remove("drag-over");

});


/* =========================================================
   DROP
   ========================================================= */

dropZone.addEventListener("drop", (event) => {

    event.preventDefault();

    dropZone.classList.remove("drag-over");


    const file = event.dataTransfer.files[0];


    if (file) {

        selectFile(file);

    }

});


/* =========================================================
   REMOVE FILE
   ========================================================= */

removeFileButton.addEventListener("click", (event) => {

    event.stopPropagation();


    selectedFile = null;

    fileInput.value = "";


    filePreview.classList.add("hidden");

    uploadStatus.classList.add("hidden");

    resultSection.classList.add("hidden");


    extractedResumeText = "";


    extractedText.textContent = "";


    analyzeButton.disabled = true;


    showToast("Resume removed.");

});


/* =========================================================
   JOB DESCRIPTION COUNTER
   ========================================================= */

jobDescription.addEventListener("input", () => {

    const length = jobDescription.value.length;

    charCount.textContent = `${length} / 5000`;

});


/* =========================================================
   ANALYZE RESUME
   ========================================================= */

analyzeButton.addEventListener("click", async () => {


    /* Check file */

    if (!selectedFile) {

        showToast("Please upload a resume first.");

        return;

    }


    /* Create form data */

    const formData = new FormData();

    formData.append("resume", selectedFile);


    /* Disable button */

    analyzeButton.disabled = true;


    /* Show loading */

    uploadStatus.classList.remove("hidden");


    uploadStatus.innerHTML = `

        <div class="status-loader"></div>

        <span>
            Extracting resume text...
        </span>

    `;


    try {


        /* Send request to Flask */

        const response = await fetch(
            "/upload-resume",
            {
                method: "POST",
                body: formData
            }
        );


        /* Convert response to JSON */

        const data = await response.json();


        /* Handle errors */

        if (!response.ok || data.error) {

            throw new Error(
                data.error ||
                "Something went wrong."
            );

        }


        /* Get extracted text */

        extractedResumeText = data.text || "";


        /* Check empty text */

        if (!extractedResumeText.trim()) {

            throw new Error(
                "No readable text was found in this PDF."
            );

        }


        /* Display extracted text */

        extractedText.textContent =
            extractedResumeText;


        resultSection.classList.remove("hidden");


        /* Success status */

        uploadStatus.innerHTML = `

            <span style="color: #16a77b;">
                ✓
            </span>

            <span>
                Resume extracted successfully.
            </span>

        `;


        showToast(
            "Resume analyzed successfully."
        );


        /* Scroll to results */

        setTimeout(() => {

            resultSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 200);


    } catch (error) {


        /* Error status */

        uploadStatus.innerHTML = `

            <span style="color: #e74c3c;">
                !
            </span>

            <span>
                ${error.message}
            </span>

        `;


        showToast(
            "Could not process the resume."
        );

    } finally {


        /* Enable button again */

        analyzeButton.disabled = false;

    }

});


/* =========================================================
   COPY EXTRACTED TEXT
   ========================================================= */

copyButton.addEventListener("click", async () => {


    if (!extractedResumeText) {

        showToast(
            "No extracted text available."
        );

        return;

    }


    try {

        await navigator.clipboard.writeText(
            extractedResumeText
        );


        showToast(
            "Resume text copied."
        );


    } catch (error) {

        showToast(
            "Could not copy text."
        );

    }

});


/* =========================================================
   DOWNLOAD EXTRACTED TEXT
   ========================================================= */

downloadButton.addEventListener("click", () => {


    if (!extractedResumeText) {

        showToast(
            "No extracted text available."
        );

        return;

    }


    const blob = new Blob(
        [extractedResumeText],
        {
            type: "text/plain"
        }
    );


    const url =
        URL.createObjectURL(blob);


    const link =
        document.createElement("a");


    link.href = url;

    link.download =
        "extracted_resume.txt";


    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);


    URL.revokeObjectURL(url);


    showToast(
        "Text file downloaded."
    );

});