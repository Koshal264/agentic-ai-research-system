const API_URL = "http://127.0.0.1:8000";

// =====================================================
// AUTH
// =====================================================

function getToken() {
    return localStorage.getItem("access_token");
}

function getAuthHeaders() {
    const token = getToken();

    if (!token) {
        throw new Error("User is not logged in.");
    }

    return {
        "Authorization": `Bearer ${token}`
    };
}


// =====================================================
// SHOW LOGIN / APP
// =====================================================

function showApp() {
    document.getElementById("auth-screen").style.display = "none";
    document.getElementById("app-screen").style.display = "block";

    const username = localStorage.getItem("username");

    document.getElementById("logged-user").textContent =
        username || "User";
}

function showAuth() {
    document.getElementById("auth-screen").style.display = "flex";
    document.getElementById("app-screen").style.display = "none";
}


// =====================================================
// CHECK LOGIN
// =====================================================

if (getToken()) {
    showApp();
} else {
    showAuth();
}


// =====================================================
// LOGIN
// =====================================================

async function login() {

    const username =
        document
            .getElementById("login-username")
            .value
            .trim();

    const password =
        document
            .getElementById("login-password")
            .value;

    const status =
        document.getElementById("login-status");

    if (!username || !password) {

        status.textContent =
            "Please enter username and password.";

        return;
    }

    status.textContent = "Logging in...";

    try {

        const response =
            await fetch(
                `${API_URL}/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            status.textContent =
                data.detail ||
                "Login failed.";

            return;
        }

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        localStorage.setItem(
            "username",
            data.username
        );

        localStorage.setItem(
            "role",
            data.role
        );

        status.textContent =
            "Login successful!";

        showApp();

    } catch (error) {

        console.error(error);

        status.textContent =
            "Unable to connect to server.";
    }
}


// =====================================================
// SIGNUP
// =====================================================

async function signup() {

    const username =
        document
            .getElementById("signup-username")
            .value
            .trim();

    const password =
        document
            .getElementById("signup-password")
            .value;

    const status =
        document.getElementById("signup-status");

    if (!username || !password) {

        status.textContent =
            "Please enter username and password.";

        return;
    }

    if (password.length < 6) {

        status.textContent =
            "Password must be at least 6 characters.";

        return;
    }

    status.textContent =
        "Creating account...";

    try {

        const response =
            await fetch(
                `${API_URL}/auth/signup`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        username: username,
                        password: password,
                        role: "user"
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            status.textContent =
                data.detail ||
                "Signup failed.";

            return;
        }

        status.textContent =
            "Account created! You can now login.";

        document.getElementById(
            "login-username"
        ).value = username;

        showLogin();

    } catch (error) {

        console.error(error);

        status.textContent =
            "Unable to connect to server.";
    }
}


// =====================================================
// SWITCH LOGIN / SIGNUP
// =====================================================

function showSignup() {

    document.getElementById(
        "login-form"
    ).style.display = "none";

    document.getElementById(
        "signup-form"
    ).style.display = "block";
}

function showLogin() {

    document.getElementById(
        "signup-form"
    ).style.display = "none";

    document.getElementById(
        "login-form"
    ).style.display = "block";
}


// =====================================================
// LOGOUT
// =====================================================

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "username"
    );

    localStorage.removeItem(
        "role"
    );

    showAuth();
}


// =====================================================
// STATUS
// =====================================================

const statusBox =
    document.getElementById("status");

function showStatus(
    message,
    type = "loading"
) {

    statusBox.textContent =
        message;

    statusBox.className =
        `status show ${type}`;
}

function hideStatus() {

    statusBox.className =
        "status";
}


// =====================================================
// CHAT
// =====================================================

const chatBox =
    document.getElementById("chat-box");

const queryInput =
    document.getElementById("query");

const sendButton =
    document.getElementById("send-btn");


// =====================================================
// ADD MESSAGE
// =====================================================

function addMessage(
    message,
    type
) {

    const welcome =
        document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

    const messageDiv =
        document.createElement("div");

    messageDiv.className =
        `message ${type}`;

    const content =
        document.createElement("div");

    content.className =
        "message-content";

    content.textContent =
        message;

    messageDiv.appendChild(
        content
    );

    chatBox.appendChild(
        messageDiv
    );

    // =============================================
    // AUTO SCROLL TO NEW MESSAGE
    // =============================================

    requestAnimationFrame(() => {

        messageDiv.scrollIntoView({
            behavior: "smooth",
            block: "end"
        });

    });
}


// =====================================================
// SEND CHAT
// =====================================================

async function sendQuery() {

    const query =
        queryInput.value.trim();

    if (!query) {

        showStatus(
            "Please enter a question.",
            "error"
        );

        return;
    }

    // Show user message
    addMessage(
        query,
        "user"
    );

    queryInput.value = "";

    sendButton.disabled = true;

    showStatus(
        "AI is thinking...",
        "loading"
    );

    try {

        const response =
            await fetch(
                `${API_URL}/chat?query=${encodeURIComponent(query)}`,
                {
                    method: "POST",

                    headers:
                        getAuthHeaders()
                }
            );

        if (response.status === 401) {

            logout();

            throw new Error(
                "Session expired."
            );
        }

        if (!response.ok) {

            throw new Error(
                "Failed to send query."
            );
        }

        const data =
            await response.json();

        if (data.job_id) {

            await checkJob(
                data.job_id
            );
        }

    } catch (error) {

        console.error(error);

        addMessage(
            "Sorry, something went wrong.",
            "bot"
        );

        showStatus(
            "Request failed.",
            "error"
        );

    } finally {

        sendButton.disabled = false;

        setTimeout(
            hideStatus,
            2500
        );
    }
}


// =====================================================
// CHECK JOB
// =====================================================

async function checkJob(
    jobId
) {

    while (true) {

        try {

            const response =
                await fetch(
                    `${API_URL}/job-status?job_id=${jobId}`,
                    {
                        headers:
                            getAuthHeaders()
                    }
                );

            if (response.status === 401) {

                logout();

                return;
            }

            if (!response.ok) {

                throw new Error(
                    "Job status failed."
                );
            }

            const data =
                await response.json();

            // =====================================
            // FINISHED
            // =====================================

            if (
                data.status ===
                "finished"
            ) {

                addMessage(
                    data.result ||
                    "Task completed.",
                    "bot"
                );

                showStatus(
                    "Completed successfully.",
                    "success"
                );

                return;
            }

            // =====================================
            // FAILED
            // =====================================

            if (
                data.status ===
                "failed"
            ) {

                addMessage(
                    "The AI task failed. Check backend terminal.",
                    "bot"
                );

                showStatus(
                    "Task failed.",
                    "error"
                );

                return;
            }

            // =====================================
            // PROCESSING
            // =====================================

            showStatus(
                "AI is processing...",
                "loading"
            );

            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        1200
                    )
            );

        } catch (error) {

            console.error(error);

            showStatus(
                "Job status error.",
                "error"
            );

            return;
        }
    }
}


// =====================================================
// VISION AI
// =====================================================

async function analyzeImage() {

    const imageInput =
        document.getElementById("image");

    const imageQuery =
        document.getElementById(
            "image-query"
        );

    if (!imageInput.files.length) {

        showStatus(
            "Please select an image first.",
            "error"
        );

        return;
    }

    if (!imageQuery.value.trim()) {

        showStatus(
            "Please enter what you want to analyze.",
            "error"
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "image",
        imageInput.files[0]
    );

    showStatus(
        "Uploading image...",
        "loading"
    );

    try {

        const response =
            await fetch(
                `${API_URL}/vision-chat?query=${encodeURIComponent(
                    imageQuery.value.trim()
                )}`,
                {
                    method: "POST",

                    headers:
                        getAuthHeaders(),

                    body: formData
                }
            );

        if (response.status === 401) {

            logout();

            return;
        }

        if (!response.ok) {

            const errorData =
                await response
                    .json()
                    .catch(
                        () => null
                    );

            console.error(
                "Vision upload error:",
                errorData
            );

            throw new Error(
                errorData?.detail ||
                "Vision request failed."
            );
        }

        const data =
            await response.json();

        if (data.job_id) {

            await checkJob(
                data.job_id
            );
        }

    } catch (error) {

        console.error(
            "Vision error:",
            error
        );

        showStatus(
            error.message ||
            "Image analysis failed.",
            "error"
        );
    }
}


// =====================================================
// PDF UPLOAD / RAG
// =====================================================

async function uploadPDF() {

    const pdfInput =
        document.getElementById("pdf");

    if (!pdfInput.files.length) {

        showStatus(
            "Please select a PDF first.",
            "error"
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        pdfInput.files[0]
    );

    showStatus(
        "Uploading and indexing PDF...",
        "loading"
    );

    try {

        const response =
            await fetch(
                `${API_URL}/upload-pdf`,
                {
                    method: "POST",

                    headers:
                        getAuthHeaders(),

                    body: formData
                }
            );

        if (response.status === 401) {

            logout();

            return;
        }

        if (!response.ok) {

            const errorData =
                await response
                    .json()
                    .catch(
                        () => null
                    );

            console.error(
                "PDF upload error:",
                errorData
            );

            throw new Error(
                errorData?.detail ||
                "PDF upload failed."
            );
        }

        const data =
            await response.json();

        showStatus(
            data.message ||
            "PDF uploaded successfully.",
            "success"
        );

        const pdfName =
            document.getElementById(
                "pdf-name"
            );

        if (pdfName) {

            pdfName.textContent =
                pdfInput.files[0].name;
        }

    } catch (error) {

        console.error(
            "PDF upload failed:",
            error
        );

        showStatus(
            error.message ||
            "PDF upload failed.",
            "error"
        );
    }
}


// =====================================================
// PDF FILE NAME
// =====================================================

const pdfInput =
    document.getElementById("pdf");

if (pdfInput) {

    pdfInput.addEventListener(
        "change",
        function () {

            const fileName =
                document.getElementById(
                    "pdf-name"
                );

            if (!fileName) {
                return;
            }

            if (this.files.length) {

                fileName.textContent =
                    this.files[0].name;

            } else {

                fileName.textContent =
                    "No file selected";
            }
        }
    );
}


// =====================================================
// ENTER TO SEND
// =====================================================

if (queryInput) {

    queryInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendQuery();
            }
        }
    );
}


// =====================================================
// VOICE AI
// =====================================================

let mediaRecorder = null;

let audioChunks = [];

let isRecording = false;

let recordingMimeType = "";

let recordingExtension = "webm";


// =====================================================
// VOICE RECORDING
// =====================================================

async function toggleVoice() {

    const voiceButton =
        document.getElementById(
            "voice-btn"
        );

    const voiceStatus =
        document.getElementById(
            "voice-status"
        );

    if (isRecording) {

        mediaRecorder.stop();

        isRecording = false;

        voiceButton.innerHTML =
            "🎤 Start Recording <span>→</span>";

        voiceStatus.textContent =
            "Processing your voice...";

        return;
    }

    try {

        const stream =
            await navigator
                .mediaDevices
                .getUserMedia({
                    audio: true
                });

        // =========================================
        // SELECT RECORDING FORMAT
        // =========================================

        if (
            MediaRecorder.isTypeSupported(
                "audio/webm"
            )
        ) {

            recordingMimeType =
                "audio/webm";

            recordingExtension =
                "webm";

        } else if (
            MediaRecorder.isTypeSupported(
                "audio/mp4"
            )
        ) {

            recordingMimeType =
                "audio/mp4";

            recordingExtension =
                "m4a";

        } else {

            recordingMimeType = "";

            recordingExtension =
                "webm";
        }


        // =========================================
        // CREATE RECORDER
        // =========================================

        mediaRecorder =
            recordingMimeType
                ? new MediaRecorder(
                    stream,
                    {
                        mimeType:
                            recordingMimeType
                    }
                )
                : new MediaRecorder(
                    stream
                );

        audioChunks = [];


        // =========================================
        // AUDIO DATA
        // =========================================

        mediaRecorder.ondataavailable =
            function (event) {

                if (
                    event.data &&
                    event.data.size > 0
                ) {

                    audioChunks.push(
                        event.data
                    );
                }
            };


        // =========================================
        // RECORDING STOP
        // =========================================

        mediaRecorder.onstop =
            async function () {

                stream
                    .getTracks()
                    .forEach(
                        track =>
                            track.stop()
                    );

                const audioBlob =
                    new Blob(
                        audioChunks,
                        {
                            type:
                                recordingMimeType ||
                                "audio/webm"
                        }
                    );

                await sendVoice(
                    audioBlob
                );
            };


        // =========================================
        // START
        // =========================================

        mediaRecorder.start();

        isRecording = true;

        voiceButton.innerHTML =
            "⏹️ Stop Recording";

        voiceStatus.textContent =
            "🔴 Recording... Speak now";

        showStatus(
            "Listening...",
            "loading"
        );

    } catch (error) {

        console.error(
            "Microphone error:",
            error
        );

        voiceStatus.textContent =
            "Microphone access failed.";

        showStatus(
            "Please allow microphone access.",
            "error"
        );
    }
}


// =====================================================
// SEND VOICE
// =====================================================

async function sendVoice(
    audioBlob
) {

    const voiceStatus =
        document.getElementById(
            "voice-status"
        );

    const formData =
        new FormData();

    const audioFile =
        new File(
            [audioBlob],
            `voice_query.${recordingExtension}`,
            {
                type:
                    audioBlob.type ||
                    recordingMimeType ||
                    "audio/webm"
            }
        );

    formData.append(
        "audio",
        audioFile
    );

    try {

        showStatus(
            "Processing voice request...",
            "loading"
        );

        voiceStatus.textContent =
            "🤖 AI is processing...";


        // =========================================
        // SEND AUDIO
        // =========================================

        const response =
            await fetch(
                `${API_URL}/voice-chat`,
                {
                    method: "POST",

                    headers:
                        getAuthHeaders(),

                    body: formData
                }
            );


        if (response.status === 401) {

            logout();

            return;
        }


        if (!response.ok) {

            const errorData =
                await response
                    .json()
                    .catch(
                        () => null
                    );

            console.error(
                "Voice request error:",
                errorData
            );

            throw new Error(
                errorData?.detail ||
                "Voice request failed."
            );
        }


        const data =
            await response.json();


        // =========================================
        // SHOW TRANSCRIPT
        // =========================================

        if (data.transcript) {

            addMessage(
                data.transcript,
                "user"
            );

        } else if (data.query) {

            addMessage(
                data.query,
                "user"
            );
        }


        // =========================================
        // CHECK AI JOB
        // =========================================

        if (data.job_id) {

            await checkJob(
                data.job_id
            );
        }


        voiceStatus.textContent =
            "Click the button to speak again";

    } catch (error) {

        console.error(
            "Voice error:",
            error
        );

        voiceStatus.textContent =
            "Voice request failed.";

        showStatus(
            error.message ||
            "Voice processing failed.",
            "error"
        );
    }
}


// =====================================================
// FRONTEND LOADED
// =====================================================

console.log(
    "Sovereign AI frontend loaded"
);