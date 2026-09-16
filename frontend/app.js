const API_URL = "http://127.0.0.1:8000";


async function sendQuery() {

    const input = document.getElementById("query");
    const chatBox = document.getElementById("chat-box");
    const status = document.getElementById("status");

    const query = input.value.trim();

    if (!query) {
        return;
    }

    chatBox.innerHTML += `
        <div class="message user">
            ${query}
        </div>
    `;

    input.value = "";

    status.innerText = "AI is processing your request...";

    try {

        const response = await fetch(
            `${API_URL}/chat?query=${encodeURIComponent(query)}`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        const jobId = data.job_id;

        status.innerText = "Agent is working...";

        await checkJob(jobId);

    } catch (error) {

        status.innerText = "Error connecting to server.";

        console.error(error);
    }
}


async function checkJob(jobId) {

    const chatBox = document.getElementById("chat-box");
    const status = document.getElementById("status");

    while (true) {

        const response = await fetch(
            `${API_URL}/job-status?job_id=${jobId}`
        );

        const data = await response.json();

        if (data.status === "finished") {

            chatBox.innerHTML += `
                <div class="message bot">
                    ${data.result}
                </div>
            `;

            status.innerText = "Completed";

            chatBox.scrollTop = chatBox.scrollHeight;

            break;
        }

        if (data.status === "failed") {

            chatBox.innerHTML += `
                <div class="message bot">
                    Sorry, something went wrong.
                </div>
            `;

            status.innerText = "Failed";

            break;
        }

        await new Promise(
            resolve => setTimeout(resolve, 1500)
        );
    }
}