/* VeristasOS — Your AI Saathi Frontend Application Logic */

let isSeniorMode = false;
let currentInboxData = [];

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    loadDailyBrief();
    loadInboxData();
});

// NAVIGATION TAB SWITCHING
function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetId = item.getAttribute("data-target");
            
            navItems.forEach(n => n.classList.remove("active"));
            item.classList.add("active");

            document.querySelectorAll(".workspace-view").forEach(v => v.classList.remove("active"));
            const targetView = document.getElementById(targetId);
            if (targetView) targetView.classList.add("active");
            
            const titleEl = document.getElementById("current-view-title");
            if (titleEl) titleEl.innerText = item.querySelector("span:last-child").innerText;
        });
    });

    // Senior Mode Toggle
    const toggleSeniorBtn = document.getElementById("toggle-senior-mode");
    if (toggleSeniorBtn) {
        toggleSeniorBtn.addEventListener("click", () => {
            isSeniorMode = !isSeniorMode;
            const textEl = document.getElementById("senior-mode-text");
            const banner = document.getElementById("senior-banner-container");

            if (isSeniorMode) {
                toggleSeniorBtn.classList.add("active");
                if (textEl) textEl.innerText = "Senior Mode: ON 👴";
                if (banner) {
                    banner.style.display = "block";
                    banner.innerHTML = `
                        <div class="senior-alert-banner">
                            🔴 SENIOR CITIZEN SAFETY MODE ACTIVE<br>
                            <span style="font-size: 13px; font-weight: normal; color: var(--text-primary);">
                                Sabhi financial requests, OTPs, aur unknown links ko automatic BLOCK kiya jayega. 
                                Kisi bhi suspicious message par family member ko dikhayein.
                            </span>
                        </div>
                    `;
                }
            } else {
                toggleSeniorBtn.classList.remove("active");
                if (textEl) textEl.innerText = "Senior Mode: OFF";
                if (banner) banner.style.display = "none";
            }
            loadDailyBrief();
        });
    }
}

// DAILY BRIEF DATA
async function loadDailyBrief() {
    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch(`/api/saathi/brief?user_mode=${mode}`);
        const data = await res.json();
        
        if (data.status === "success" && data.brief) {
            const brief = data.brief;
            document.getElementById("stat-red-count").innerText = brief.actions_needed_count || 0;
            document.getElementById("stat-yellow-count").innerText = brief.reviews_needed_count || 0;
            document.getElementById("stat-green-count").innerText = brief.handled_count || 0;

            renderHomeCardLists(brief.red_actions, brief.yellow_reviews);
        }
    } catch (err) {
        console.warn("Daily brief fetch failed:", err);
    }
}

function renderHomeCardLists(redList, yellowList) {
    const redContainer = document.getElementById("home-red-list");
    const yellowContainer = document.getElementById("home-yellow-list");

    if (redContainer) {
        if (!redList || redList.length === 0) {
            redContainer.innerHTML = `<div style="color: var(--text-muted); font-size: 13px;">No critical threats blocked today.</div>`;
        } else {
            redContainer.innerHTML = redList.map(item => `
                <div class="inbox-card risk-high">
                    <div>
                        <div style="font-weight: 700;">${escapeHtml(item.title)}</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">From: ${escapeHtml(item.sender)}</div>
                        <div style="font-size: 12px; color: var(--accent-rose); margin-top: 4px;">Reason: ${escapeHtml(item.reason || '')}</div>
                    </div>
                    <span class="badge critical">BLOCKED</span>
                </div>
            `).join('');
        }
    }

    if (yellowContainer) {
        if (!yellowList || yellowList.length === 0) {
            yellowContainer.innerHTML = `<div style="color: var(--text-muted); font-size: 13px;">No pending reviews.</div>`;
        } else {
            yellowContainer.innerHTML = yellowList.map(item => `
                <div class="inbox-card risk-caution">
                    <div>
                        <div style="font-weight: 700;">${escapeHtml(item.title)}</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">From: ${escapeHtml(item.sender)}</div>
                    </div>
                    <span class="badge caution">ASK USER</span>
                </div>
            `).join('');
        }
    }
}

// PROTECTED INBOX DATA
async function loadInboxData() {
    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch(`/api/email/inbox?user_mode=${mode}`);
        const data = await res.json();
        
        if (data.status === "success" && data.inbox) {
            currentInboxData = data.inbox;
            renderInboxCards(data.inbox);
        }
    } catch (err) {
        console.warn("Inbox fetch failed:", err);
    }
}

function refreshInbox() {
    loadInboxData();
}

function renderInboxCards(inbox) {
    const container = document.getElementById("inbox-cards-list");
    if (!container) return;

    if (!inbox || inbox.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted);">Inbox empty.</div>`;
        return;
    }

    container.innerHTML = inbox.map(item => {
        const evalRes = item.firewall_evaluation || {};
        const decision = evalRes.decision || item.computed_decision || "ALLOW";
        const risk = evalRes.risk_level || item.computed_risk || "LOW";
        
        let riskClass = "risk-low";
        let badgeClass = "low";
        if (decision === "BLOCK" || risk === "CRITICAL" || risk === "HIGH") {
            riskClass = "risk-high";
            badgeClass = "critical";
        } else if (decision === "ASK_USER" || risk === "CAUTION") {
            riskClass = "risk-caution";
            badgeClass = "caution";
        }

        return `
            <div class="inbox-card ${riskClass}">
                <div style="flex: 1; padding-right: 16px;">
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 4px;">
                        <span class="badge ${badgeClass}">${decision}</span>
                        <span style="font-size: 12px; font-weight: 600; color: var(--text-muted);">${escapeHtml(item.date)}</span>
                    </div>
                    <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px;">${escapeHtml(item.subject)}</div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 6px;">From: ${escapeHtml(item.sender_name)} (${escapeHtml(item.sender)})</div>
                    <div style="font-size: 13px; color: var(--text-muted);">${escapeHtml(item.body)}</div>
                    
                    ${evalRes.why ? `
                        <div style="margin-top: 8px; font-size: 12px; color: var(--accent-cyan);">
                            <strong>WHY:</strong> ${escapeHtml(evalRes.why.join(' • '))}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// AI SAATHI CHAT INTERACTION
async function sendChatMessage() {
    const input = document.getElementById("chat-input-text");
    if (!input || !input.value.trim()) return;

    const userMsg = input.value.trim();
    input.value = "";

    appendChatBubble(userMsg, "user");

    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch("/api/saathi/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: userMsg, user_mode: mode })
        });
        const data = await res.json();

        if (data.status === "success" && data.result) {
            appendChatBubble(data.result.response, "saathi");
        } else {
            appendChatBubble("Kripya punah prayas karein.", "saathi");
        }
    } catch (err) {
        appendChatBubble("AI Saathi offline mode me hai.", "saathi");
    }
}

function sendQuickPrompt(promptText) {
    // Switch to AI Saathi tab
    const saathiTab = document.querySelector('.nav-item[data-target="view-saathi"]');
    if (saathiTab) saathiTab.click();

    const input = document.getElementById("chat-input-text");
    if (input) {
        input.value = promptText;
        sendChatMessage();
    }
}

function appendChatBubble(text, sender) {
    const log = document.getElementById("chat-log");
    if (!log) return;

    const div = document.createElement("div");
    div.className = `msg-bubble ${sender}`;
    div.innerHTML = escapeHtml(text).replace(/\n/g, "<br>");
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

// TRUST FIREWALL EVALUATOR
async function evaluateTrustFirewall() {
    const actionSelect = document.getElementById("firewall-action-select");
    const contentText = document.getElementById("firewall-content-text");
    const outContainer = document.getElementById("firewall-result-container");

    if (!actionSelect || !contentText || !outContainer) return;

    const action = actionSelect.value;
    const content = contentText.value.trim();
    if (!content) {
        outContainer.innerHTML = `<div style="color: var(--accent-rose);">Please enter text content to evaluate.</div>`;
        return;
    }

    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch("/api/trust/firewall", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action_name: action, content: content, user_mode: mode })
        });
        const data = await res.json();

        if (data.status === "success" && data.evaluation) {
            const evalRes = data.evaluation;
            outContainer.innerHTML = `
                <div style="background: var(--bg-card); padding: 20px; border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px;">
                        <span class="badge ${evalRes.decision === 'BLOCK' ? 'critical' : evalRes.decision === 'ASK_USER' ? 'caution' : 'low'}">
                            DECISION: ${evalRes.decision}
                        </span>
                        <span style="font-weight: 700;">Risk Level: ${evalRes.risk_level}</span>
                    </div>

                    <div style="font-size: 14px; margin-bottom: 10px;"><strong>Reason:</strong> ${escapeHtml(evalRes.decision_reason)}</div>
                    
                    <div style="margin-bottom: 10px;">
                        <strong>WHY:</strong>
                        <ul style="padding-left: 20px; color: var(--text-secondary); margin-top: 4px;">
                            ${evalRes.why ? evalRes.why.map(w => `<li>${escapeHtml(w)}</li>`).join('') : '<li>None</li>'}
                        </ul>
                    </div>

                    <div style="margin-bottom: 10px;">
                        <strong>EVIDENCE & RELIABILITY:</strong>
                        <div style="font-size: 13px; color: var(--accent-cyan); margin-top: 4px;">
                            Confidence: ${evalRes.confidence_percent}% | Uncertainty: ${evalRes.uncertainty} | Reliability Rating: ${evalRes.reliability}
                        </div>
                    </div>

                    <div style="background: rgba(0,240,255,0.08); padding: 12px; border-radius: 8px; font-weight: 600; color: var(--accent-cyan);">
                        💡 Recommended Action: ${escapeHtml(evalRes.recommended_action)}
                    </div>
                </div>
            `;
        }
    } catch (err) {
        outContainer.innerHTML = `<div style="color: var(--accent-rose);">Evaluation failed: ${err}</div>`;
    }
}

// PRIVACY SHIELD SCANNER
async function scanPrivacyInput() {
    const input = document.getElementById("privacy-input-text");
    const out = document.getElementById("privacy-scan-output");
    if (!input || !out) return;

    const text = input.value.trim();
    if (!text) return;

    try {
        const res = await fetch("/api/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();

        if (data.privacy_analysis) {
            const p = data.privacy_analysis;
            out.innerHTML = `
                <div style="background: var(--bg-subtle); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                    <div style="font-weight: 700; margin-bottom: 6px;">Privacy Risk: ${p.privacy_risk} (Grade: ${p.privacy_grade})</div>
                    <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 10px;">${escapeHtml(p.explanation)}</div>
                    
                    <div style="font-size: 12px; font-weight: 700; color: var(--accent-green); margin-bottom: 4px;">Masked Output:</div>
                    <div style="font-family: var(--font-mono); background: var(--bg-card); padding: 10px; border-radius: 6px; font-size: 13px;">
                        ${escapeHtml(p.masked_text)}
                    </div>
                </div>
            `;
        }
    } catch (err) {
        out.innerHTML = `<div style="color: var(--accent-rose);">Privacy scan failed.</div>`;
    }
}

// DEMO SCENARIO PRESET
function loadKycDemoScenario() {
    const homeTab = document.querySelector('.nav-item[data-target="view-home"]');
    if (homeTab) homeTab.click();

    const firewallTab = document.querySelector('.nav-item[data-target="view-firewall"]');
    if (firewallTab) firewallTab.click();

    const actionSelect = document.getElementById("firewall-action-select");
    const contentText = document.getElementById("firewall-content-text");

    if (actionSelect) actionSelect.value = "share_otp";
    if (contentText) {
        contentText.value = "URGENT: Your SBI Bank account 4589XXXX2109 will be suspended today! Click http://sbi-kyc-update-login.com/login and enter NetBanking OTP immediately.";
    }

    evaluateTrustFirewall();
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}