/* ==========================================================================
   VERISTASOS — FRONTEND APPLICATION CONTROLLER
   ========================================================================== */

const API_BASE = (typeof window !== "undefined" && window.location.origin && window.location.origin.startsWith("http")) 
    ? window.location.origin 
    : "http://127.0.0.1:8000";

let selectedMediaFile = null;
let verificationHistory = [];

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    loadHistory();
    setupComposerEvents();
});

/* ==========================================================================
   1. THEME MANAGEMENT
   ========================================================================== */
function initTheme() {
    const saved = localStorage.getItem("veristas_theme") || "dark";
    document.documentElement.setAttribute("data-theme", saved);
    updateThemeUI(saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("veristas_theme", next);
    updateThemeUI(next);
}

function updateThemeUI(theme) {
    const label = document.getElementById("themeLabel");
    const icon = document.getElementById("themeIcon");
    if (label && icon) {
        if (theme === "dark") {
            label.textContent = "Dark Mode";
            icon.textContent = "☾";
        } else {
            label.textContent = "Light Mode";
            icon.textContent = "☀";
        }
    }
}

/* ==========================================================================
   2. SIDEBAR TOGGLES
   ========================================================================== */
function toggleSidebarCollapse() {
    const sidebar = document.getElementById("sidebar");
    const label = document.getElementById("collapseLabel");
    const icon = document.getElementById("collapseIcon");
    
    sidebar.classList.toggle("collapsed");
    const isCollapsed = sidebar.classList.contains("collapsed");
    
    if (label && icon) {
        label.textContent = isCollapsed ? "" : "Collapse Sidebar";
        icon.textContent = isCollapsed ? "▶" : "◀";
    }
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("mobile-open");
}

/* ==========================================================================
   3. COMPOSER & INPUT EVENTS
   ========================================================================== */
function setupComposerEvents() {
    const input = document.getElementById("composerInput");
    if (input) {
        input.addEventListener("input", () => {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 200) + "px";
        });

        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submitVerification();
            }
        });
    }
}

function usePrompt(text) {
    const input = document.getElementById("composerInput");
    if (input) {
        input.value = text;
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 200) + "px";
        input.focus();
    }
}

function toggleSourceDrawer() {
    const drawer = document.getElementById("sourceDrawer");
    if (drawer) {
        drawer.classList.toggle("open");
    }
}

function clearComposer() {
    const input = document.getElementById("composerInput");
    const url = document.getElementById("sourceUrlInput");
    const name = document.getElementById("sourceNameInput");
    const author = document.getElementById("authorInput");
    const mediaLabel = document.getElementById("attachmentLabel");

    if (input) { input.value = ""; input.style.height = "auto"; }
    if (url) url.value = "";
    if (name) name.value = "";
    if (author) author.value = "";
    if (mediaLabel) mediaLabel.textContent = "Attach Media";
    selectedMediaFile = null;
}

function triggerImageUpload() {
    const fileInput = document.getElementById("mediaFileInput");
    if (fileInput) fileInput.click();
}

function handleFileSelected(event) {
    const file = event.target.files[0];
    if (!file) return;
    selectedMediaFile = file;
    const mediaLabel = document.getElementById("attachmentLabel");
    if (mediaLabel) {
        mediaLabel.textContent = file.name.length > 15 ? file.name.substring(0, 12) + "..." : file.name;
    }
}

/* ==========================================================================
   4. VERIFICATION SUBMISSION & CHAT STREAM
   ========================================================================== */
async function submitVerification() {
    const input = document.getElementById("composerInput");
    const text = input ? input.value.trim() : "";
    const sendBtn = document.getElementById("sendBtn");
    const loadingTicker = document.getElementById("loadingTicker");
    const loadingStepText = document.getElementById("loadingStepText");

    if (!text && !selectedMediaFile) {
        alert("Please enter text content or select an image file to verify.");
        return;
    }

    // Lock UI & Show Loading Ticker
    if (sendBtn) sendBtn.disabled = true;
    if (loadingTicker) loadingTicker.style.display = "flex";
    
    // Hide empty state
    const emptyState = document.getElementById("emptyState");
    if (emptyState) emptyState.style.display = "none";

    // Append User Message to Chat Stream
    appendUserMessage(text || `[Media Attachment: ${selectedMediaFile.name}]`);

    // Ticker Animation Steps
    const steps = [
        "Analyzing content...",
        "Checking linguistic signals...",
        "Preparing explanation..."
    ];
    let stepIdx = 0;
    const tickerInterval = setInterval(() => {
        stepIdx = (stepIdx + 1) % steps.length;
        if (loadingStepText) loadingStepText.textContent = steps[stepIdx];
    }, 600);

    try {
        let responseData = null;

        if (selectedMediaFile) {
            // Media Forensics Endpoint
            const formData = new FormData();
            formData.append("file", selectedMediaFile);
            if (text) formData.append("article_text", text);

            const res = await fetch(`${API_BASE}/api/analyze-image`, {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Media analysis failed.");
            responseData = formatMediaResult(data, text);
        } else {
            // Text Analysis Endpoint
            const payload = {
                text: text,
                source_url: document.getElementById("sourceUrlInput")?.value || null,
                source_name: document.getElementById("sourceNameInput")?.value || null,
                author: document.getElementById("authorInput")?.value || null
            };

            const res = await fetch(`${API_BASE}/api/v1/text/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Text analysis failed.");
            responseData = formatTextResult(data.analysis, text);
        }

        clearInterval(tickerInterval);
        appendAssistantResponse(responseData);
        saveToHistory(text || selectedMediaFile.name, responseData.verdict, responseData);

        // Reset input
        clearComposer();

    } catch (err) {
        clearInterval(tickerInterval);
        appendAssistantError(err.message || "Unable to complete verification. Please check backend connection.");
    } finally {
        if (sendBtn) sendBtn.disabled = false;
        if (loadingTicker) loadingTicker.style.display = "none";
        scrollToBottom();
    }
}

/* ==========================================================================
   5. RESULT FORMATTERS & EXPLAINABILITY
   ========================================================================== */
function formatTextResult(analysis, rawText) {
    const score = Math.round(analysis.overall_risk_score || 0);
    let verdict = "NEEDS VERIFICATION";
    let verdictClass = "NEEDS_VERIFICATION";
    let summaryText = "Based on the available signals, this content contains mixed risk indicators and warrants further verification.";

    if (score < 30) {
        verdict = "LIKELY RELIABLE";
        verdictClass = "RELIABLE";
        summaryText = "Based on available linguistic and provenance signals, this content exhibits neutral tone and low sensationalism indicators.";
    } else if (score > 60) {
        verdict = "SUSPICIOUS";
        verdictClass = "SUSPICIOUS";
        summaryText = "Based on available signals, this content exhibits strong sensationalism, emotional language, or unverified claims.";
    }

    const ling = analysis.linguistic_analysis || {};
    const sensationalWords = ling.sensational_words || [];
    
    // Highlight Sensational Words inline in text
    let highlightedText = escapeHtml(rawText);
    if (sensationalWords.length > 0) {
        sensationalWords.forEach(word => {
            const regex = new RegExp(`\\b(${word})\\b`, "gi");
            highlightedText = highlightedText.replace(regex, `<mark class="sensational-highlight">$1</mark>`);
        });
    }

    const signals = [
        `Sensationalism Score: ${ling.sensationalism_score || 0}/100`,
        `Exclamation mark frequency: ${ling.exclamation_count || 0}`,
        `ALL-CAPS word frequency: ${ling.uppercase_word_count || 0}`,
        `Detected trigger terms: ${sensationalWords.length > 0 ? sensationalWords.join(", ") : "None detected"}`
    ];

    return {
        verdict: verdict,
        verdictClass: verdictClass,
        summary: summaryText,
        signals: signals,
        highlightedText: highlightedText,
        sensationalCount: sensationalWords.length,
        rawText: rawText
    };
}

function formatMediaResult(data, articleText) {
    const img = data.image_analysis || {};
    const auth = img.authenticity_screening || {};
    const verdict = auth.assessment === "LIKELY AUTHENTIC" ? "LIKELY RELIABLE" : "NEEDS VERIFICATION";
    const verdictClass = verdict === "LIKELY RELIABLE" ? "RELIABLE" : "NEEDS_VERIFICATION";

    const signals = [
        `File Name: ${img.filename || "Uploaded Image"} (${(img.size_bytes / 1024).toFixed(1)} KB)`,
        `MIME Type: ${img.mime_type || "image/png"}`,
        `Cryptographic SHA-256: ${(img.sha256 || "").substring(0, 16)}...`,
        `EXIF Metadata: ${img.exif_status || "NOT FOUND"}`
    ];

    return {
        verdict: verdict,
        verdictClass: verdictClass,
        summary: `Media analysis complete. Perceptual dHash: ${img.perceptual_hash || "N/A"}.`,
        signals: signals,
        highlightedText: articleText ? escapeHtml(articleText) : null,
        rawText: articleText || img.filename
    };
}

/* ==========================================================================
   6. DOM RENDERING HELPERS
   ========================================================================== */
function appendUserMessage(text) {
    const stream = document.getElementById("chatStream");
    const div = document.createElement("div");
    div.className = "chat-msg user";
    div.innerHTML = `
        <div class="msg-avatar">You</div>
        <div class="msg-content">
            <div class="msg-bubble">${escapeHtml(text)}</div>
        </div>
    `;
    stream.appendChild(div);
}

function appendAssistantResponse(data) {
    const stream = document.getElementById("chatStream");
    const div = document.createElement("div");
    div.className = "chat-msg assistant";

    let highlightSection = "";
    if (data.highlightedText) {
        highlightSection = `
            <div style="margin-top:8px;">
                <div style="font-size:11px; font-weight:700; color:var(--text-muted); margin-bottom:4px; text-transform:uppercase;">
                    Annotated Text (${data.sensationalCount || 0} trigger words highlighted):
                </div>
                <div class="highlight-text-container">${data.highlightedText}</div>
            </div>
        `;
    }

    div.innerHTML = `
        <div class="msg-avatar">V</div>
        <div class="msg-content">
            <div class="verification-card">
                <div class="verification-header">
                    <strong style="font-size:14px;">Verification Result</strong>
                    <span class="verdict-badge ${data.verdictClass}">${data.verdict}</span>
                </div>
                
                <div class="verification-summary-text">${data.summary}</div>

                <div class="explainability-box">
                    <div class="explainability-title">
                        <span>🔍</span>
                        <span>Signals Contributing to Result</span>
                    </div>
                    <ul class="signals-list">
                        ${data.signals.map(s => `<li class="signal-item">${escapeHtml(s)}</li>`).join("")}
                    </ul>
                    ${highlightSection}
                </div>

                <div class="msg-actions">
                    <button class="action-btn" onclick="copyResponseText(this, '${escapeHtml(data.summary)}')">
                        <span>📋</span>
                        <span>Copy Response</span>
                    </button>
                    <button class="action-btn" onclick="submitVerification()">
                        <span>🔄</span>
                        <span>Re-analyze</span>
                    </button>
                </div>
            </div>
        </div>
    `;
    stream.appendChild(div);
}

function appendAssistantError(errorMsg) {
    const stream = document.getElementById("chatStream");
    const div = document.createElement("div");
    div.className = "chat-msg assistant";
    div.innerHTML = `
        <div class="msg-avatar">V</div>
        <div class="msg-content">
            <div class="verification-card" style="border-color:var(--status-suspicious);">
                <div class="verification-header">
                    <strong style="font-size:14px; color:var(--status-suspicious);">Verification Notice</strong>
                </div>
                <div class="verification-summary-text">
                    ${escapeHtml(errorMsg)}
                </div>
            </div>
        </div>
    `;
    stream.appendChild(div);
}

/* ==========================================================================
   7. SESSION HISTORY MANAGER
   ========================================================================== */
function saveToHistory(text, verdict, fullData) {
    const record = {
        id: Date.now(),
        title: text.length > 30 ? text.substring(0, 28) + "..." : text,
        verdict: verdict,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        fullData: fullData
    };

    verificationHistory.unshift(record);
    if (verificationHistory.length > 20) verificationHistory.pop();

    try {
        localStorage.setItem("veristas_history", JSON.stringify(verificationHistory));
    } catch (e) {}

    renderHistory();
}

function loadHistory() {
    try {
        const saved = localStorage.getItem("veristas_history");
        if (saved) verificationHistory = JSON.parse(saved);
    } catch (e) {
        verificationHistory = [];
    }
    renderHistory();
}

function renderHistory() {
    const list = document.getElementById("historyList");
    if (!list) return;

    if (verificationHistory.length === 0) {
        list.innerHTML = `<div style="font-size:11px; color:var(--text-muted); padding:4px 8px;">No recent verifications</div>`;
        return;
    }

    list.innerHTML = "";
    verificationHistory.forEach(item => {
        const a = document.createElement("a");
        a.className = "history-item";
        let badgeClass = "NEEDS_VERIFICATION";
        if (item.verdict === "LIKELY RELIABLE") badgeClass = "RELIABLE";
        if (item.verdict === "SUSPICIOUS") badgeClass = "SUSPICIOUS";

        a.innerHTML = `
            <span class="history-item-text">${escapeHtml(item.title)}</span>
            <span class="history-item-badge ${badgeClass}">${item.verdict}</span>
        `;
        a.onclick = (e) => {
            e.preventDefault();
            loadHistoryItem(item);
        };
        list.appendChild(a);
    });
}

function loadHistoryItem(item) {
    const emptyState = document.getElementById("emptyState");
    if (emptyState) emptyState.style.display = "none";
    appendUserMessage(item.title);
    appendAssistantResponse(item.fullData);
    scrollToBottom();
}

/* ==========================================================================
   8. UTILITIES & MODAL CONTROLLERS
   ========================================================================== */
function startNewVerification(event) {
    if (event) event.preventDefault();
    clearComposer();
    const stream = document.getElementById("chatStream");
    if (stream) stream.innerHTML = "";
    const emptyState = document.getElementById("emptyState");
    if (emptyState) emptyState.style.display = "flex";
}

function showHistoryTab(event) {
    if (event) event.preventDefault();
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.remove("collapsed");
}

function openModal(modalId, event) {
    if (event) event.preventDefault();
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add("open");
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove("open");
}

function closeModalOnOverlay(event, modalId) {
    if (event.target.id === modalId) {
        closeModal(modalId);
    }
}

function copyResponseText(btn, text) {
    navigator.clipboard.writeText(text).then(() => {
        const orig = btn.innerHTML;
        btn.innerHTML = "<span>✓</span> <span>Copied!</span>";
        setTimeout(() => { btn.innerHTML = orig; }, 1500);
    });
}

function scrollToBottom() {
    const area = document.getElementById("contentArea");
    if (area) area.scrollTop = area.scrollHeight;
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}