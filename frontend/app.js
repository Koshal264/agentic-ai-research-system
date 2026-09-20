const API_URL = "http://127.0.0.1:8000";


// ========================================
// NORMAL CHAT
// ========================================

async function sendQuery() {

    const input =
        document.getElementById("query");

    const chatBox =
        document.getElementById("chat-box");

    const status =
        document.getElementById("status");


    const query =
        input.value.trim();


    if (!query) {
        return;
    }


    chatBox.innerHTML += `
        <div class="message user">
            ${query}
        </div>
    `;


    input.value = "";

    status.innerText =
        "AI is processing your request...";


    try {

        const response = await fetch(
            `${API_URL}/chat?query=${encodeURIComponent(query)}`,
            {
                method: "POST"
            }
        );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data =
            await response.json();


        const jobId =
            data.job_id;


        status.innerText =
            "Agent is working...";


        await checkJob(jobId);


    } catch (error) {

        console.error(error);

        status.innerText =
            "Error connecting to server.";

    }
}


// ========================================
// IMAGE ANALYSIS
// ========================================

async function analyzeImage() {

    const input =
        document.getElementById("query");

    const imageInput =
        document.getElementById("image");

    const chatBox =
        document.getElementById("chat-box");

    const status =
        document.getElementById("status");


    const query =
        input.value.trim();


    const image =
        imageInput.files[0];


    if (!image) {

        status.innerText =
            "Please select an image.";

        return;

    }


    if (!query) {

        status.innerText =
            "Please enter a question about the image.";

        return;

    }


    chatBox.innerHTML += `
        <div class="message user">
            🖼️ ${query}
        </div>
    `;


    input.value = "";


    status.innerText =
        "Uploading image...";


    try {

        const formData =
            new FormData();


        formData.append(
            "query",
            query
        );


        formData.append(
            "image",
            image
        );


        const response =
            await fetch(
                `${API_URL}/vision-chat`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data =
            await response.json();


        const jobId =
            data.job_id;


        status.innerText =
            "Vision Agent is analyzing the image...";


        await checkJob(jobId);


        imageInput.value = "";


    } catch (error) {

        console.error(error);

        status.innerText =
            "Error analyzing image.";

    }
}


// ========================================
// PDF UPLOAD
// ========================================

async function uploadPDF() {

    const pdfInput =
        document.getElementById("pdf");

    const status =
        document.getElementById("status");

    const chatBox =
        document.getElementById("chat-box");


    const pdf =
        pdfInput.files[0];


    if (!pdf) {

        status.innerText =
            "Please select a PDF.";

        return;

    }


    status.innerText =
        "Uploading and indexing PDF...";


    try {

        const formData =
            new FormData();


        formData.append(
            "pdf",
            pdf
        );


        const response =
            await fetch(
                `${API_URL}/upload-pdf`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "PDF response:",
            data
        );


        if (data.status === "success") {

            const result =
                data.result;


            chatBox.innerHTML += `
                <div class="message bot">
                    📄 PDF uploaded successfully!<br><br>
                    File: ${result.filename}<br>
                    Pages: ${result.pages}<br>
                    Chunks: ${result.chunks}<br><br>
                    You can now ask questions about this PDF.
                </div>
            `;


            status.innerText =
                "PDF indexed successfully.";

        } else {

            status.innerText =
                data.message || "PDF upload failed.";

        }


        pdfInput.value = "";


        chatBox.scrollTop =
            chatBox.scrollHeight;


    } catch (error) {

        console.error(error);

        status.innerText =
            "Error uploading PDF.";

    }
}


// ========================================
// CHECK JOB STATUS
// ========================================

async function checkJob(jobId) {

    const chatBox =
        document.getElementById("chat-box");

    const status =
        document.getElementById("status");


    while (true) {

        try {

            const response =
                await fetch(
                    `${API_URL}/job-status?job_id=${jobId}`
                );


            const data =
                await response.json();


            if (data.status === "finished") {

                chatBox.innerHTML += `
                    <div class="message bot">
                        ${data.result}
                    </div>
                `;


                status.innerText =
                    "Completed";


                chatBox.scrollTop =
                    chatBox.scrollHeight;


                break;

            }


            if (data.status === "failed") {

                chatBox.innerHTML += `
                    <div class="message bot">
                        Sorry, something went wrong while
                        processing your request.
                    </div>
                `;


                status.innerText =
                    "Failed";


                break;

            }


            status.innerText =
                "Agent is working...";


            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        1500
                    )
            );


        } catch (error) {

            console.error(error);


            status.innerText =
                "Error checking job status.";


            break;

        }

    }

}