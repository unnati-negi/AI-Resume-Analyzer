/* =========================================================
   HIRELENS
   AI Resume Analyzer
   Frontend JavaScript
========================================================= */


/* =========================================================
   DOM ELEMENTS
========================================================= */

const fileInput =
    document.getElementById("resumeFile");


const dropZone =
    document.getElementById("dropZone");


const browseButton =
    document.getElementById("browseButton");


const filePreview =
    document.getElementById("filePreview");


const fileName =
    document.getElementById("fileName");


const fileSize =
    document.getElementById("fileSize");


const removeFileButton =
    document.getElementById("removeFile");


const uploadStatus =
    document.getElementById("uploadStatus");


const analyzeButton =
    document.getElementById("analyzeButton");


const resultSection =
    document.getElementById("results-section");


const extractedText =
    document.getElementById("extractedText");


const skillsContainer =
    document.getElementById("skillsContainer");


const skillCount =
    document.getElementById("skillCount");


const copyButton =
    document.getElementById("copyButton");


const downloadButton =
    document.getElementById("downloadButton");


const jobDescription =
    document.getElementById("jobDescription");


const charCount =
    document.getElementById("charCount");


const jobAnalyzeButton =
    document.getElementById("jobAnalyzeButton");


const jobResults =
    document.getElementById("jobResults");


const jobSkillsContainer =
    document.getElementById(
        "jobSkillsContainer"
    );


const jobSkillCount =
    document.getElementById(
        "jobSkillCount"
    );


const toast =
    document.getElementById("toast");


const toastMessage =
    document.getElementById(
        "toastMessage"
    );


/* =========================================================
   STATE
========================================================= */

let selectedFile = null;

let extractedResumeText = "";


/* =========================================================
   TOAST
========================================================= */

function showToast(message) {

    if (!toast || !toastMessage) {

        return;

    }


    toastMessage.textContent =
        message;


    toast.classList.add(
        "show"
    );


    setTimeout(
        () => {

            toast.classList.remove(
                "show"
            );

        },
        3000
    );

}


/* =========================================================
   FILE SIZE
========================================================= */

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return `${bytes} B`;

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return `${(
            bytes / 1024
        ).toFixed(1)} KB`;

    }


    return `${(
        bytes /
        (1024 * 1024)
    ).toFixed(1)} MB`;

}


/* =========================================================
   FILE VALIDATION
========================================================= */

function validateFile(file) {

    if (!file) {

        return false;

    }


    const isPDF =
        file.type ===
            "application/pdf" ||
        file.name
            .toLowerCase()
            .endsWith(".pdf");


    if (!isPDF) {

        showToast(
            "Please select a PDF file."
        );

        return false;

    }


    const maxSize =
        10 * 1024 * 1024;


    if (
        file.size >
        maxSize
    ) {

        showToast(
            "File must be smaller than 10 MB."
        );

        return false;

    }


    return true;

}


/* =========================================================
   SELECT FILE
========================================================= */

function selectFile(file) {

    if (
        !validateFile(file)
    ) {

        return;

    }


    selectedFile =
        file;


    fileName.textContent =
        file.name;


    fileSize.textContent =
        formatFileSize(
            file.size
        );


    filePreview.classList.remove(
        "hidden"
    );


    uploadStatus.classList.add(
        "hidden"
    );


    resultSection.classList.add(
        "hidden"
    );


    extractedResumeText =
        "";


    extractedText.textContent =
        "";


    skillsContainer.innerHTML =
        "";


    skillCount.textContent =
        "0";


    analyzeButton.disabled =
        false;


    showToast(
        "Resume selected."
    );

}


/* =========================================================
   BROWSE BUTTON
========================================================= */

browseButton.addEventListener(
    "click",
    (event) => {

        event.stopPropagation();

        fileInput.click();

    }
);


/* =========================================================
   DROP ZONE CLICK
========================================================= */

dropZone.addEventListener(
    "click",
    () => {

        fileInput.click();

    }
);


/* =========================================================
   FILE INPUT
========================================================= */

fileInput.addEventListener(
    "change",
    () => {

        const file =
            fileInput.files[0];


        if (file) {

            selectFile(file);

        }

    }
);


/* =========================================================
   DRAG OVER
========================================================= */

dropZone.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();


        dropZone.classList.add(
            "drag-over"
        );

    }
);


/* =========================================================
   DRAG LEAVE
========================================================= */

dropZone.addEventListener(
    "dragleave",
    () => {

        dropZone.classList.remove(
            "drag-over"
        );

    }
);


/* =========================================================
   DROP
========================================================= */

dropZone.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();


        dropZone.classList.remove(
            "drag-over"
        );


        const file =
            event.dataTransfer
                .files[0];


        if (file) {

            selectFile(file);

        }

    }
);


/* =========================================================
   REMOVE FILE
========================================================= */

removeFileButton.addEventListener(
    "click",
    (event) => {

        event.stopPropagation();


        selectedFile =
            null;


        fileInput.value =
            "";


        filePreview.classList.add(
            "hidden"
        );


        uploadStatus.classList.add(
            "hidden"
        );


        resultSection.classList.add(
            "hidden"
        );


        extractedResumeText =
            "";


        extractedText.textContent =
            "";


        skillsContainer.innerHTML =
            "";


        skillCount.textContent =
            "0";


        analyzeButton.disabled =
            true;


        showToast(
            "Resume removed."
        );

    }
);


/* =========================================================
   JOB DESCRIPTION COUNTER
========================================================= */

jobDescription.addEventListener(
    "input",
    () => {

        const length =
            jobDescription
                .value
                .length;


        charCount.textContent =
            `${length} / 5000`;

    }
);


/* =========================================================
   ANALYZE RESUME
========================================================= */

analyzeButton.addEventListener(
    "click",
    async () => {

        /* -------------------------------------------------
           Check file
        ------------------------------------------------- */

        if (!selectedFile) {

            showToast(
                "Please upload a resume first."
            );

            return;

        }


        /* -------------------------------------------------
           Form data
        ------------------------------------------------- */

        const formData =
            new FormData();


        formData.append(
            "resume",
            selectedFile
        );


        /* -------------------------------------------------
           Disable button
        ------------------------------------------------- */

        analyzeButton.disabled =
            true;


        /* -------------------------------------------------
           Loading
        ------------------------------------------------- */

        uploadStatus.classList.remove(
            "hidden"
        );


        uploadStatus.innerHTML = `

            <div class="status-loader"></div>

            <span>
                Analyzing your resume...
            </span>

        `;


        try {

            console.log(
                "Sending resume to Flask:",
                selectedFile.name
            );


            /* =============================================
               SEND TO FLASK
            ============================================= */

            const response =
                await fetch(
                    "/upload-resume",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            console.log(
                "Resume API status:",
                response.status
            );


            /* =============================================
               READ RESPONSE
            ============================================= */

            const responseText =
                await response.text();


            console.log(
                "Resume API response:",
                responseText
            );


            let data;


            try {

                data =
                    JSON.parse(
                        responseText
                    );

            }

            catch (error) {

                throw new Error(
                    "The server returned an invalid response."
                );

            }


            /* =============================================
               SERVER ERROR
            ============================================= */

            if (
                !response.ok ||
                data.error
            ) {

                throw new Error(
                    data.error ||
                    "Could not process the resume."
                );

            }


            /* =============================================
               GET RESUME TEXT
            ============================================= */

            extractedResumeText =
                data.text || "";


            /* =============================================
               CHECK TEXT
            ============================================= */

            if (
                !extractedResumeText
                    .trim()
            ) {

                throw new Error(
                    "No readable text was found in this PDF."
                );

            }


            /* =============================================
               DISPLAY TEXT
            ============================================= */

            extractedText.textContent =
                extractedResumeText;


            /* =============================================
               GET SKILLS
            ============================================= */

            const skills =
                Array.isArray(
                    data.skills
                )
                    ? data.skills
                    : [];


            /* =============================================
               SKILL COUNT
            ============================================= */

            skillCount.textContent =
                skills.length;


            /* =============================================
               CLEAR OLD SKILLS
            ============================================= */

            skillsContainer.innerHTML =
                "";


            /* =============================================
               DISPLAY SKILLS
            ============================================= */

            if (
                skills.length === 0
            ) {

                skillsContainer.innerHTML = `

                    <div class="no-skills">

                        No known skills were detected.

                    </div>

                `;

            }

            else {

                skills.forEach(
                    (skill) => {

                        const tag =
                            document.createElement(
                                "span"
                            );


                        tag.className =
                            "skill-tag";


                        tag.textContent =
                            skill;


                        skillsContainer.appendChild(
                            tag
                        );

                    }
                );

            }


            /* =============================================
               SHOW RESULTS
            ============================================= */

            resultSection.classList.remove(
                "hidden"
            );


            /* =============================================
               SUCCESS
            ============================================= */

            uploadStatus.innerHTML = `

                <span style="color: #16a77b;">
                    ✓
                </span>

                <span>
                    Resume analyzed successfully.
                </span>

            `;


            showToast(
                "Resume analyzed successfully."
            );


            /* =============================================
               SCROLL
            ============================================= */

            setTimeout(
                () => {

                    resultSection.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                },
                200
            );

        }


        catch (error) {

            console.error(
                "HIRELENS RESUME ERROR:",
                error
            );


            uploadStatus.innerHTML = `

                <span style="color: #e74c3c;">
                    !
                </span>

                <span>
                    ${error.message}
                </span>

            `;


            showToast(
                error.message
            );

        }


        finally {

            analyzeButton.disabled =
                false;

        }

    }
);


/* =========================================================
   ANALYZE JOB DESCRIPTION
========================================================= */

jobAnalyzeButton.addEventListener(
    "click",
    async () => {

        /* -------------------------------------------------
           Get description
        ------------------------------------------------- */

        const description =
            jobDescription
                .value
                .trim();


        /* -------------------------------------------------
           Validate
        ------------------------------------------------- */

        if (!description) {

            showToast(
                "Please enter a job description first."
            );

            return;

        }


        /* -------------------------------------------------
           Disable button
        ------------------------------------------------- */

        jobAnalyzeButton.disabled =
            true;


        jobAnalyzeButton.innerHTML =
            "Analyzing...";


        try {

            console.log(
                "Sending job description to Flask..."
            );


            /* =============================================
               SEND JOB DESCRIPTION
            ============================================= */

            const response =
                await fetch(
                    "/analyze-job",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                job_description:
                                    description
                            })

                    }
                );


            console.log(
                "Job API status:",
                response.status
            );


            /* =============================================
               READ RESPONSE
            ============================================= */

            const responseText =
                await response.text();


            console.log(
                "Job API response:",
                responseText
            );


            let data;


            try {

                data =
                    JSON.parse(
                        responseText
                    );

            }

            catch (error) {

                throw new Error(
                    "The server returned an invalid response."
                );

            }


            /* =============================================
               SERVER ERROR
            ============================================= */

            if (
                !response.ok ||
                data.error
            ) {

                throw new Error(
                    data.error ||
                    "Could not analyze job description."
                );

            }


            /* =============================================
               GET SKILLS
            ============================================= */

            const skills =
                Array.isArray(
                    data.skills
                )
                    ? data.skills
                    : [];


            /* =============================================
               UPDATE COUNT
            ============================================= */

            jobSkillCount.textContent =
                skills.length;


            /* =============================================
               CLEAR OLD SKILLS
            ============================================= */

            jobSkillsContainer.innerHTML =
                "";


            /* =============================================
               DISPLAY SKILLS
            ============================================= */

            if (
                skills.length === 0
            ) {

                jobSkillsContainer.innerHTML = `

                    <div class="no-job-skills">

                        No known technical skills
                        were detected.

                    </div>

                `;

            }

            else {

                skills.forEach(
                    (skill) => {

                        const tag =
                            document.createElement(
                                "span"
                            );


                        tag.className =
                            "job-skill-tag";


                        tag.textContent =
                            skill;


                        jobSkillsContainer.appendChild(
                            tag
                        );

                    }
                );

            }


            /* =============================================
               SHOW RESULTS
            ============================================= */

            jobResults.classList.remove(
                "hidden"
            );


            showToast(
                "Job description analyzed successfully."
            );


            /* =============================================
               SCROLL
            ============================================= */

            setTimeout(
                () => {

                    jobResults.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                },
                200
            );

        }


        catch (error) {

            console.error(
                "HIRELENS JOB ERROR:",
                error
            );


            showToast(
                error.message
            );

        }


        finally {

            jobAnalyzeButton.disabled =
                false;


            jobAnalyzeButton.innerHTML =
                "✦ Analyze Job Description <span>→</span>";

        }

    }
);


/* =========================================================
   COPY EXTRACTED TEXT
========================================================= */

copyButton.addEventListener(
    "click",
    async () => {

        if (
            !extractedResumeText
        ) {

            showToast(
                "No extracted text available."
            );

            return;

        }


        try {

            await navigator
                .clipboard
                .writeText(
                    extractedResumeText
                );


            showToast(
                "Resume text copied."
            );

        }


        catch (error) {

            console.error(
                "Copy error:",
                error
            );


            showToast(
                "Could not copy text."
            );

        }

    }
);


/* =========================================================
   DOWNLOAD EXTRACTED TEXT
========================================================= */

downloadButton.addEventListener(
    "click",
    () => {

        if (
            !extractedResumeText
        ) {

            showToast(
                "No extracted text available."
            );

            return;

        }


        const blob =
            new Blob(
                [
                    extractedResumeText
                ],
                {
                    type:
                        "text/plain"
                }
            );


        const url =
            URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href =
            url;


        link.download =
            "extracted_resume.txt";


        document.body.appendChild(
            link
        );


        link.click();


        document.body.removeChild(
            link
        );


        URL.revokeObjectURL(
            url
        );


        showToast(
            "Text file downloaded."
        );

    }
);