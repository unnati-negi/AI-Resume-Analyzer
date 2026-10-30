/* =========================================================
   HIRELENS - Frontend JavaScript
   Minimal interface without decorative symbols.
========================================================= */

const $ = (id) => document.getElementById(id);

const fileInput = $("resumeFile");
const dropZone = $("dropZone");
const browseButton = $("browseButton");
const filePreview = $("filePreview");
const fileName = $("fileName");
const fileSize = $("fileSize");
const removeFileButton = $("removeFile");
const uploadStatus = $("uploadStatus");

const analyzeButton = $("analyzeButton");
const mainActionHint = $("mainActionHint");

const resultSection = $("results-section");
const extractedText = $("extractedText");
const skillsContainer = $("skillsContainer");
const skillCount = $("skillCount");
const resumeStatus = $("resumeStatus");
const copyButton = $("copyButton");
const downloadButton = $("downloadButton");

const jobDescription = $("jobDescription");
const charCount = $("charCount");
const jobAnalyzeButton = $("jobAnalyzeButton");
const jobResults = $("jobResults");
const jobSkillsContainer = $("jobSkillsContainer");
const jobSkillCount = $("jobSkillCount");
const requiredSkillsContainer = $("requiredSkillsContainer");
const preferredSkillsContainer = $("preferredSkillsContainer");

const matchResults = $("matchResults");
const toast = $("toast");
const toastMessage = $("toastMessage");

let selectedFile = null;
let extractedResumeText = "";
let resumeSkills = [];
let jobAnalyzed = false;

/* Create the matching button without requiring an HTML edit. */

let matchButton = $("matchButton");

if (!matchButton) {
    matchButton = document.createElement("button");
    matchButton.type = "button";
    matchButton.id = "matchButton";
    matchButton.className = "analyze-button";
    matchButton.textContent = "Match Resume to Job";
    matchButton.disabled = true;

    const mainAction = document.querySelector(".main-action");
    mainAction.appendChild(matchButton);
}

/* Notifications */

function showToast(message) {
    toastMessage.textContent = message;
    toast.classList.add("show");

    window.setTimeout(() => {
        toast.classList.remove("show");
    }, 2800);
}

/* File utilities */

function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

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

    if (file.size > 10 * 1024 * 1024) {
        showToast("File must be smaller than 10 MB.");
        return false;
    }

    return true;
}

/* Safe rendering helpers */

function renderTags(container, values, className, emptyMessage) {
    container.replaceChildren();

    if (!Array.isArray(values) || values.length === 0) {
        const message = document.createElement("p");
        message.className = "empty-message";
        message.textContent = emptyMessage;
        container.appendChild(message);
        return;
    }

    values.forEach((value) => {
        const tag = document.createElement("span");
        tag.className = className;
        tag.textContent = String(value);
        container.appendChild(tag);
    });
}

function renderList(list, values, emptyMessage) {
    list.replaceChildren();

    if (!Array.isArray(values) || values.length === 0) {
        const item = document.createElement("li");
        item.textContent = emptyMessage;
        list.appendChild(item);
        return;
    }

    values.forEach((value) => {
        const item = document.createElement("li");

        if (typeof value === "string") {
            item.textContent = value;
        } else if (value && typeof value === "object") {
            item.textContent =
                value.recommendation ||
                value.message ||
                value.skill ||
                JSON.stringify(value);
        } else {
            item.textContent = String(value);
        }

        list.appendChild(item);
    });
}

async function readJsonResponse(response) {
    const responseText = await response.text();
    let data;

    try {
        data = JSON.parse(responseText);
    } catch {
        throw new Error("The server returned an invalid response.");
    }

    if (!response.ok || data.error) {
        throw new Error(
            data.error || "The request could not be completed."
        );
    }

    return data;
}

/* Matching controls */

function resetMatchResults() {
    matchResults.classList.add("hidden");

    $("matchScoreValue").textContent = "--";
    $("matchInterpretation").textContent =
        "Run matching to view your results.";

    $("skillGapSummary").textContent = "";
    $("semanticStatus").textContent = "";

    renderList(
        $("matchedSkillsList"),
        [],
        "No matching skills identified."
    );

    renderList(
        $("missingSkillsList"),
        [],
        "No missing skills identified."
    );

    renderList(
        $("recommendationsList"),
        [],
        "No recommendations generated."
    );

    updateMatchButton();
}

function updateMatchButton() {
    matchButton.disabled = !(
        extractedResumeText.trim() &&
        jobDescription.value.trim() &&
        jobAnalyzed
    );
}

/* Resume selection */

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

    extractedResumeText = "";
    resumeSkills = [];

    extractedText.textContent = "";
    skillCount.textContent = "0";
    resumeStatus.textContent = "Not analyzed";

    renderTags(
        skillsContainer,
        [],
        "skill-tag",
        "No skills detected."
    );

    resetMatchResults();

    analyzeButton.disabled = false;
    mainActionHint.textContent =
        "Analyze the resume, then analyze the job description.";

    showToast("Resume selected.");
}

function removeSelectedFile() {
    selectedFile = null;
    fileInput.value = "";

    filePreview.classList.add("hidden");
    uploadStatus.classList.add("hidden");
    resultSection.classList.add("hidden");

    extractedResumeText = "";
    resumeSkills = [];

    extractedText.textContent = "";
    skillCount.textContent = "0";
    resumeStatus.textContent = "Not analyzed";

    renderTags(
        skillsContainer,
        [],
        "skill-tag",
        "No skills detected."
    );

    analyzeButton.disabled = true;

    resetMatchResults();

    mainActionHint.textContent =
        "Upload a resume to begin analysis.";

    showToast("Resume removed.");
}

/* File input and drag-and-drop */

browseButton.addEventListener("click", (event) => {
    event.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener("click", () => {
    fileInput.click();
});

dropZone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        fileInput.click();
    }
});

fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) {
        selectFile(fileInput.files[0]);
    }
});

dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");

    const file = event.dataTransfer.files[0];

    if (file) {
        selectFile(file);
    }
});

removeFileButton.addEventListener("click", removeSelectedFile);

/* Job description input */

jobDescription.addEventListener("input", () => {
    charCount.textContent =
        `${jobDescription.value.length} / 5000`;

    jobAnalyzed = false;

    jobResults.classList.add("hidden");

    renderTags(
        jobSkillsContainer,
        [],
        "job-skill-tag",
        "Analyze the job description to see detected skills."
    );

    renderTags(
        requiredSkillsContainer,
        [],
        "skill-tag",
        "Not classified yet."
    );

    renderTags(
        preferredSkillsContainer,
        [],
        "job-skill-tag",
        "Not classified yet."
    );

    jobSkillCount.textContent = "0";

    resetMatchResults();
});

/* Resume analysis */

analyzeButton.addEventListener("click", async () => {
    if (!selectedFile) {
        showToast("Please upload a resume first.");
        return;
    }

    const formData = new FormData();
    formData.append("resume", selectedFile);

    analyzeButton.disabled = true;
    uploadStatus.classList.remove("hidden");
    uploadStatus.textContent = "Analyzing your resume...";

    try {
        const response = await fetch("/upload-resume", {
            method: "POST",
            body: formData
        });

        const data = await readJsonResponse(response);

        extractedResumeText = data.text || "";

        if (!extractedResumeText.trim()) {
            throw new Error(
                "No readable text was found in this PDF."
            );
        }

        resumeSkills = Array.isArray(data.skills)
            ? data.skills
            : [];

        extractedText.textContent = extractedResumeText;
        skillCount.textContent = resumeSkills.length;
        resumeStatus.textContent = "Analyzed";

        renderTags(
            skillsContainer,
            resumeSkills,
            "skill-tag",
            "No known skills were detected."
        );

        resultSection.classList.remove("hidden");

        uploadStatus.textContent =
            "Resume analyzed successfully.";

        mainActionHint.textContent =
            "Now analyze the job description to enable matching.";

        resetMatchResults();

        showToast("Resume analyzed successfully.");

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        console.error("Resume analysis error:", error);

        uploadStatus.textContent = error.message;
        showToast(error.message);

    } finally {
        analyzeButton.disabled = false;
    }
});

/* Job description analysis */

jobAnalyzeButton.addEventListener("click", async () => {
    const description = jobDescription.value.trim();

    if (!description) {
        showToast("Please enter a job description first.");
        return;
    }

    jobAnalyzeButton.disabled = true;
    jobAnalyzeButton.textContent = "Analyzing...";

    try {
        const response = await fetch("/analyze-job", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                job_description: description
            })
        });

        const data = await readJsonResponse(response);

        const skills = Array.isArray(data.skills)
            ? data.skills
            : [];

        jobSkillCount.textContent = skills.length;

        renderTags(
            jobSkillsContainer,
            skills,
            "job-skill-tag",
            "No known technical skills were detected."
        );

        renderTags(
            requiredSkillsContainer,
            data.required_skills || [],
            "skill-tag",
            "No required skills were classified."
        );

        renderTags(
            preferredSkillsContainer,
            data.preferred_skills || [],
            "job-skill-tag",
            "No preferred skills were classified."
        );

        jobResults.classList.remove("hidden");
        jobAnalyzed = true;

        resetMatchResults();
        updateMatchButton();

        mainActionHint.textContent =
            "Resume and job analyzed. You can now match them.";

        showToast("Job description analyzed successfully.");

        jobResults.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        console.error("Job analysis error:", error);
        showToast(error.message);

    } finally {
        jobAnalyzeButton.disabled = false;
        jobAnalyzeButton.textContent = "Analyze Job Description";
    }
});

/* Resume-job matching */

matchButton.addEventListener("click", async () => {
    if (!extractedResumeText.trim()) {
        showToast("Analyze a resume before matching.");
        return;
    }

    const description = jobDescription.value.trim();

    if (!description || !jobAnalyzed) {
        showToast(
            "Analyze the job description before matching."
        );
        return;
    }

    matchButton.disabled = true;
    matchButton.textContent = "Matching...";

    resetMatchResults();

    try {
        const response = await fetch("/match-resume", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                resume_text: extractedResumeText,
                job_description: description
            })
        });

        const data = await readJsonResponse(response);

        const score = data.score || {};
        const matching = data.matching || {};

        const scoreValue =
            score.overall_score ??
            data.match_percentage ??
            matching.overall_match_percentage;

        if (
            scoreValue !== undefined &&
            scoreValue !== null &&
            Number.isFinite(Number(scoreValue))
        ) {
            $("matchScoreValue").textContent =
                `${Number(scoreValue).toFixed(1)}%`;
        } else {
            $("matchScoreValue").textContent = "Unavailable";
        }

        $("matchInterpretation").textContent =
            score.interpretation ||
            "Score calculated using the current matching rules.";

        const matchedSkills =
            matching.matched_skills ||
            data.matched_skills ||
            [];

        const missingSkills =
            matching.missing_skills ||
            data.missing_skills ||
            [];

        renderList(
            $("matchedSkillsList"),
            matchedSkills,
            "No matching skills identified."
        );

        renderList(
            $("missingSkillsList"),
            missingSkills,
            "No missing skills identified."
        );

        const recommendationData = data.recommendations;

        const recommendations = Array.isArray(recommendationData)
            ? recommendationData
            : (
                recommendationData &&
                Array.isArray(recommendationData.recommendations)
                    ? recommendationData.recommendations
                    : []
            );

        renderList(
            $("recommendationsList"),
            recommendations,
            "No recommendations were returned by the backend."
        );

        $("skillGapSummary").textContent =
            data.skill_gap_summary ||
            "A detailed skill-gap summary was not returned.";

        const semantic = data.semantic_matching || {};

        if (semantic.semantic_similarity !== undefined) {
            const similarity =
                Number(semantic.semantic_similarity);

            const percentage =
                similarity <= 1
                    ? similarity * 100
                    : similarity;

            $("semanticStatus").textContent =
                Number.isFinite(percentage)
                    ? `Semantic similarity: ${percentage.toFixed(1)}%`
                    : "Semantic similarity could not be formatted.";
        } else {
            $("semanticStatus").textContent =
                semantic.status === "unavailable"
                    ? "Semantic matching is unavailable. Keyword results are shown."
                    : "No semantic score was returned.";
        }

        matchResults.classList.remove("hidden");

        matchResults.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        showToast("Resume-job matching completed.");

    } catch (error) {
        console.error("Resume matching error:", error);
        showToast(error.message || "Could not match the resume.");

    } finally {
        matchButton.disabled = false;
        matchButton.textContent = "Match Resume to Job";
        updateMatchButton();
    }
});

/* Copy extracted resume text */

copyButton.addEventListener("click", async () => {
    if (!extractedResumeText) {
        showToast("No extracted text available.");
        return;
    }

    try {
        await navigator.clipboard.writeText(
            extractedResumeText
        );

        showToast("Resume text copied.");

    } catch (error) {
        console.error("Copy error:", error);
        showToast("Could not copy text.");
    }
});

/* Download extracted resume text */

downloadButton.addEventListener("click", () => {
    if (!extractedResumeText) {
        showToast("No extracted text available.");
        return;
    }

    const blob = new Blob(
        [extractedResumeText],
        { type: "text/plain;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "extracted_resume.txt";

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);

    showToast("Text file downloaded.");
});

/* Initial state */

updateMatchButton();