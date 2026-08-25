const API_URL = "http://127.0.0.1:8000";

const textInput = document.getElementById("textInput");
const analyzeButton = document.getElementById("analyzeButton");
const results = document.getElementById("results");


analyzeButton.addEventListener("click", async () => {
    const text = textInput.value.trim();

    if (!text) {
        alert("Please enter some content to analyze.");
        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Analysis failed."
            );
        }

        displayResults(data);

    } catch (error) {
        console.error(error);

        results.innerHTML = `
            <div class="error">
                Unable to connect to the VeristasOS backend.
                <br>
                Make sure FastAPI is running.
            </div>
        `;

    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze Content →";
    }
});


function displayResults(data) {
    results.innerHTML = `
        <div class="result-card">

            <h2>Analysis Results</h2>

            <div class="metric">
                <span>Word Count</span>
                <strong>${data.word_count}</strong>
            </div>

            <div class="metric">
                <span>Sentence Count</span>
                <strong>${data.sentence_count}</strong>
            </div>

            <div class="metric">
                <span>Exclamation Count</span>
                <strong>${data.exclamation_count}</strong>
            </div>

            <div class="metric">
                <span>Question Count</span>
                <strong>${data.question_count}</strong>
            </div>

            <div class="metric">
                <span>Uppercase Words</span>
                <strong>${data.uppercase_word_count}</strong>
            </div>

            <div class="metric">
                <span>Sensationalism Score</span>
                <strong>${data.sensationalism_score}</strong>
            </div>

        </div>
    `;
}