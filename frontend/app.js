/* VeristasOS — Your AI Saathi Complete Application Logic */

let isSeniorMode = false;
let currentLanguage = "English";
let currentInboxData = [];
let activeInboxFilter = "ALL";

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initThemeAndSidebar();
    loadDailyBrief();
    loadInboxData();
});

// NAVIGATION TAB SWITCHING
function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetId = item.getAttribute("data-target");
            switchView(targetId);
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
                showToast("👴 Senior Citizen Mode Enabled");
            } else {
                toggleSeniorBtn.classList.remove("active");
                if (textEl) textEl.innerText = "Senior Mode: OFF";
                if (banner) banner.style.display = "none";
                showToast("Senior Mode Disabled");
            }
            loadDailyBrief();
        });
    }
}

function switchView(targetId) {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(n => {
        if (n.getAttribute("data-target") === targetId) {
            n.classList.add("active");
        } else {
            n.classList.remove("active");
        }
    });

    document.querySelectorAll(".workspace-view").forEach(v => v.classList.remove("active"));
    const targetView = document.getElementById(targetId);
    if (targetView) targetView.classList.add("active");
    
    const activeNav = document.querySelector(`.nav-item[data-target="${targetId}"]`);
    const titleEl = document.getElementById("current-view-title");
    if (titleEl && activeNav) {
        const textSpan = activeNav.querySelector(".nav-text") || activeNav.querySelector("span:last-child");
        if (textSpan) titleEl.innerText = textSpan.innerText;
    }
}

// THEME & SIDEBAR COLLAPSE
function initThemeAndSidebar() {
    const savedTheme = localStorage.getItem("veristasos_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeUI(savedTheme);

    const toggleSidebarBtn = document.getElementById("toggle-sidebar");
    const sidebar = document.getElementById("sidebar-container");
    if (toggleSidebarBtn && sidebar) {
        toggleSidebarBtn.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
            const isCollapsed = sidebar.classList.contains("collapsed");
            localStorage.setItem("veristasos_sidebar_collapsed", isCollapsed ? "true" : "false");
        });

        if (localStorage.getItem("veristasos_sidebar_collapsed") === "true") {
            sidebar.classList.add("collapsed");
        }
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("veristasos_theme", newTheme);
    updateThemeUI(newTheme);
    showToast(`Switched to ${newTheme.toUpperCase()} Mode`);
}

function updateThemeUI(theme) {
    const iconEl = document.getElementById("theme-icon");
    const textEl = document.getElementById("theme-text");
    if (iconEl) iconEl.innerText = theme === "dark" ? "🌙" : "☀️";
    if (textEl) textEl.innerText = theme === "dark" ? "Dark" : "Light";
}

function changeLanguage(lang) {
    currentLanguage = lang;
    showToast(`Language set to ${lang}`);
}

// DAILY BRIEF DATA
async function loadDailyBrief() {
    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch(`/api/saathi/brief?user_mode=${mode}`);
        const data = await res.json();
        
        if (data.status === "success" && data.brief) {
            const brief = data.brief;
            const redEl = document.getElementById("stat-red-count");
            const yellowEl = document.getElementById("stat-yellow-count");
            const greenEl = document.getElementById("stat-green-count");

            if (redEl) redEl.innerText = brief.actions_needed_count || 0;
            if (yellowEl) yellowEl.innerText = brief.reviews_needed_count || 0;
            if (greenEl) greenEl.innerText = brief.handled_count || 0;

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
                <div class="inbox-card risk-high" onclick="switchView('view-mail-shield')">
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
                <div class="inbox-card risk-caution" onclick="switchView('view-mail-shield')">
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

// MAIL SHIELD & INBOX
async function loadInboxData() {
    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch(`/api/email/inbox?user_mode=${mode}`);
        const data = await res.json();
        
        if (data.status === "success" && data.inbox) {
            currentInboxData = data.inbox;
            renderInboxCards(filterInboxItems(data.inbox, activeInboxFilter));
        }
    } catch (err) {
        console.warn("Inbox fetch failed:", err);
    }
}

function refreshInbox() {
    loadInboxData();
    showToast("Inbox refreshed");
}

function filterInboxCategory(cat) {
    activeInboxFilter = cat;
    renderInboxCards(filterInboxItems(currentInboxData, cat));
}

function filterInboxItems(inbox, cat) {
    if (cat === "ALL") return inbox;
    return inbox.filter(item => {
        const decision = item.computed_decision || "ALLOW";
        const risk = item.computed_risk || "LOW";
        if (cat === "HIGH") return decision === "BLOCK" || risk === "CRITICAL" || risk === "HIGH";
        if (cat === "CAUTION") return decision === "ASK_USER" || risk === "CAUTION";
        if (cat === "LOW") return decision === "ALLOW" && risk === "LOW";
        return true;
    });
}

function renderInboxCards(inbox) {
    const container = document.getElementById("inbox-cards-list");
    if (!container) return;

    if (!inbox || inbox.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); padding: 20px;">No messages found in this category.</div>`;
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
            <div class="inbox-card ${riskClass}" onclick="openEmailModal('${item.id}')">
                <div style="flex: 1; padding-right: 16px;">
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 4px;">
                        <span class="badge ${badgeClass}">${decision}</span>
                        <span style="font-size: 12px; font-weight: 600; color: var(--text-muted);">${escapeHtml(item.date)}</span>
                    </div>
                    <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px;">${escapeHtml(item.subject)}</div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 6px;">From: ${escapeHtml(item.sender_name)} (${escapeHtml(item.sender)})</div>
                    <div style="font-size: 13px; color: var(--text-muted); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${escapeHtml(item.body)}</div>
                </div>
                <div style="font-size: 12px; color: var(--accent-cyan); font-weight: 600;">View Details →</div>
            </div>
        `;
    }).join('');
}

function openEmailModal(emailId) {
    const item = currentInboxData.find(e => e.id === emailId);
    if (!item) return;

    const modal = document.getElementById("email-modal");
    const subjectEl = document.getElementById("modal-email-subject");
    const bodyEl = document.getElementById("modal-email-body");
    const evalEl = document.getElementById("modal-email-firewall");

    if (subjectEl) subjectEl.innerText = item.subject;
    if (bodyEl) {
        bodyEl.innerHTML = `
            <strong>From:</strong> ${escapeHtml(item.sender_name)} &lt;${escapeHtml(item.sender)}&gt;<br>
            <strong>Date:</strong> ${escapeHtml(item.date)}<br><br>
            ${escapeHtml(item.body).replace(/\n/g, '<br>')}
        `;
    }

    const evalRes = item.firewall_evaluation || {};
    if (evalEl) {
        evalEl.innerHTML = `
            <div style="background: var(--bg-subtle); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 8px;">
                    <span class="badge ${evalRes.decision === 'BLOCK' ? 'critical' : evalRes.decision === 'ASK_USER' ? 'caution' : 'low'}">
                        FIREWALL DECISION: ${evalRes.decision || 'ALLOW'}
                    </span>
                    <span style="font-weight: 600; font-size: 13px;">Risk: ${evalRes.risk_level || 'LOW'}</span>
                </div>
                ${evalRes.why ? `<div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 6px;"><strong>WHY:</strong> ${escapeHtml(evalRes.why.join(' • '))}</div>` : ''}
                <div style="font-size: 12px; color: var(--accent-cyan);">Recommended Action: ${escapeHtml(evalRes.recommended_action || 'Safe to proceed')}</div>
            </div>
        `;
    }

    if (modal) modal.style.display = "flex";
}

function closeEmailModal() {
    const modal = document.getElementById("email-modal");
    if (modal) modal.style.display = "none";
}

// TRUST LENS ANALYZER
async function runTrustLensAnalysis() {
    const input = document.getElementById("trust-lens-input");
    const container = document.getElementById("trust-lens-output-container");
    const btn = document.getElementById("btn-analyze-lens");

    if (!input || !container) return;
    const text = input.value.trim();
    if (!text) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Please enter text content to evaluate.</div>`;
        return;
    }

    if (btn) { btn.innerText = "Analyzing..."; btn.disabled = true; }

    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch("/api/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();

        if (data.trust_lens) {
            const tl = data.trust_lens;
            container.innerHTML = `
                <div class="card-panel">
                    <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 14px;">
                        <span class="badge ${tl.verdict_badge === 'CRITICAL WARNING' || tl.verdict_badge === 'SUSPICIOUS' ? 'critical' : 'low'}">
                            ${escapeHtml(tl.verdict_badge)}
                        </span>
                        <span style="font-size: 14px; font-weight: 700;">Score: ${tl.risk_score} / 100</span>
                    </div>

                    <div style="margin-bottom: 14px; line-height: 1.6;">
                        <strong>WHY?</strong>
                        <ul style="padding-left: 20px; color: var(--text-secondary); margin-top: 4px;">
                            ${tl.why_reasons ? tl.why_reasons.map(w => `<li>${escapeHtml(w)}</li>`).join('') : '<li>Clean evaluation</li>'}
                        </ul>
                    </div>

                    <div style="margin-bottom: 14px; background: rgba(0,240,255,0.08); padding: 12px; border-radius: 8px; font-weight: 600; color: var(--accent-cyan);">
                        💡 Recommended Action: ${escapeHtml(tl.actionable_recommendation)}
                    </div>

                    ${data.highlighted_text ? `
                        <div style="font-size: 12px; font-weight: 700; margin-bottom: 4px;">Highlighted Sensational Words:</div>
                        <div style="background: var(--bg-subtle); padding: 12px; border-radius: 6px; font-size: 13px; line-height: 1.5;">
                            ${data.highlighted_text}
                        </div>
                    ` : ''}
                </div>
            `;
            showToast("✓ Trust Lens Analysis Complete");
        }
    } catch (err) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Evaluation failed. Please verify backend connection.</div>`;
    } finally {
        if (btn) { btn.innerText = "Analyze Trust Lens"; btn.disabled = false; }
    }
}

// BHARAT SCAM SHIELD SCANNER
async function runScamShieldScan() {
    const input = document.getElementById("scam-shield-input");
    const container = document.getElementById("scam-shield-output");
    const btn = document.getElementById("btn-scan-scam");

    if (!input || !container) return;
    const text = input.value.trim();
    if (!text) return;

    if (btn) { btn.innerText = "Scanning..."; btn.disabled = true; }

    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch("/api/trust/firewall", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action_name: "check_message", content: text, user_mode: mode })
        });
        const data = await res.json();

        if (data.status === "success" && data.evaluation) {
            const evalRes = data.evaluation;
            const dna = evalRes.scam_dna || {};
            const scores = dna.scam_dna_scores || {};

            container.innerHTML = `
                <div class="card-panel">
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px;">
                        <span class="badge ${evalRes.decision === 'BLOCK' ? 'critical' : 'low'}">${evalRes.decision}</span>
                        <span style="font-weight: 700;">Pattern: ${escapeHtml(dna.top_attack_vector || 'General Message')}</span>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <div style="font-size: 13px; font-weight: 700; margin-bottom: 8px;">SCAM DNA PROFILE:</div>
                        ${Object.entries(scores).map(([k, v]) => `
                            <div style="margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                                    <span>${escapeHtml(k)}</span>
                                    <span>${v}%</span>
                                </div>
                                <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: ${v}%;"></div></div>
                            </div>
                        `).join('')}
                    </div>

                    ${evalRes.hinglish_advice ? `
                        <div style="background: rgba(16,185,129,0.1); border: 1px solid var(--accent-green); padding: 12px; border-radius: 8px; color: var(--accent-green); font-size: 13.5px; font-weight: 600;">
                            Saathi Advice (Hinglish): ${escapeHtml(evalRes.hinglish_advice)}
                        </div>
                    ` : ''}
                </div>
            `;
        }
    } catch (err) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Scam scan failed.</div>`;
    } finally {
        if (btn) { btn.innerText = "Analyze Scam DNA"; btn.disabled = false; }
    }
}

function filterScamCategory(cat) {
    const input = document.getElementById("scam-shield-input");
    if (!input) return;

    const samples = {
        KYC: "URGENT: Your bank account 4589XXXX2109 will be suspended today! Click http://sbi-kyc-update-login.com to verify KYC.",
        UPI: "Congratulations! You won Rs 50,000. Enter your UPI PIN to claim money instantly.",
        OTP: "SBI Alert: Share OTP 4589 with customer executive to unblock your account.",
        INVESTMENT: "Guaranteed Rs 50,000 daily passive income! Pay Rs 999 registration fee via UPI.",
        JOB: "Part time WFH job: Earn Rs 5000 daily by liking YouTube videos. Telegram us now.",
        COURIER: "Your India Post parcel is held due to wrong address. Click link and pay Rs 25 redelivery fee."
    };

    input.value = samples[cat] || "";
    runScamShieldScan();
}

// PRIVACY SCANNER
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
            showToast("✓ Privacy Scan & Masking Complete");
        }
    } catch (err) {
        out.innerHTML = `<div style="color: var(--accent-rose);">Privacy scan failed.</div>`;
    }
}

// POLICY PERMISSIONS UPDATER
async function updatePolicySetting(cat, val) {
    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch("/api/policy/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_mode: mode, allow_medium_risk: (val === "ALWAYS_ALLOW") })
        });
        const data = await res.json();

        if (data.status === "success") {
            showToast(`✓ Permission updated for ${cat.toUpperCase()}: ${val}`);
        }
    } catch (err) {
        showToast("⚠ Policy update failed");
    }
}

// AI SAATHI CHAT INTERACTION
async function sendChatMessage() {
    const input = document.getElementById("chat-input-text");
    const btn = document.getElementById("btn-chat-send");
    if (!input || !input.value.trim()) return;

    const userMsg = input.value.trim();
    input.value = "";

    appendChatBubble(userMsg, "user");
    if (btn) btn.disabled = true;

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
        appendChatBubble("🔌 Saathi is offline. Basic local safety checks available.", "saathi");
    } finally {
        if (btn) btn.disabled = false;
    }
}

function sendQuickPrompt(promptText) {
    switchView("view-saathi");
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

// DEMO SCENARIO PRESET
function loadKycDemoScenario() {
    switchView("view-trust-lens");
    const input = document.getElementById("trust-lens-input");
    if (input) {
        input.value = "URGENT: Your SBI Bank account 4589XXXX2109 will be suspended today! Click http://sbi-kyc-update-login.com/login and enter NetBanking OTP immediately.";
    }
    runTrustLensAnalysis();
}

// TOAST NOTIFICATIONS
function showToast(msg) {
    const toast = document.getElementById("toast-banner");
    if (!toast) return;

    toast.innerText = msg;
    toast.style.display = "block";
    setTimeout(() => { toast.style.display = "none"; }, 3000);
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}