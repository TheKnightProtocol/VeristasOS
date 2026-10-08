/* VeristasOS — Your AI Saathi Complete Application Logic */

let isSeniorMode = false;
let currentLanguage = "English";
let currentInboxData = [];
let activeInboxFilter = "ALL";
let userName = "User";

document.addEventListener("DOMContentLoaded", () => {
    initUserProfile();
    initNavigation();
    initThemeAndSidebar();
    loadDailyBrief();
    loadInboxData();

    const savedLang = localStorage.getItem("veristasos_language") || "English";
    changeLanguage(savedLang);

    window.addEventListener("click", (e) => {
        const emailModal = document.getElementById("email-modal");
        const onboardingModal = document.getElementById("onboarding-modal");
        if (e.target === emailModal) {
            closeEmailModal();
        }
        if (e.target === onboardingModal) {
            closeOnboardingModal();
        }
    });
});

// ONBOARDING & USER PROFILE MANAGEMENT
function initUserProfile() {
    const savedName = localStorage.getItem("veristasos_user_name");
    if (!savedName || !savedName.trim()) {
        const modal = document.getElementById("onboarding-modal");
        if (modal) modal.style.display = "flex";
    } else {
        userName = savedName.trim();
        updateUserNameUI(userName);
    }
}

function submitOnboardingName() {
    const input = document.getElementById("onboarding-name-input");
    if (!input || !input.value.trim()) {
        showToast("Please enter your name to continue");
        return;
    }

    userName = input.value.trim();
    localStorage.setItem("veristasos_user_name", userName);
    
    closeOnboardingModal();
    showToast(`Welcome, ${userName}! Your AI Saathi is ready.`);
}

function closeOnboardingModal() {
    const modal = document.getElementById("onboarding-modal");
    if (modal) modal.style.display = "none";
    if (!userName || !userName.trim()) {
        userName = "User";
        localStorage.setItem("veristasos_user_name", "User");
        updateUserNameUI("User");
    } else {
        updateUserNameUI(userName);
    }
}

function saveProfileNameChanges() {
    const input = document.getElementById("profile-name-input");
    if (!input || !input.value.trim()) {
        showToast("Please enter a valid name");
        return;
    }

    userName = input.value.trim();
    localStorage.setItem("veristasos_user_name", userName);
    updateUserNameUI(userName);
    showToast(`✓ Display name updated to "${userName}"`);
}

function updateUserNameUI(name) {
    const displayNameEl = document.getElementById("user-display-name");
    const topbarTitleEl = document.getElementById("current-view-title");
    const profileInputEl = document.getElementById("profile-name-input");

    if (displayNameEl) displayNameEl.innerText = name;
    if (profileInputEl) profileInputEl.value = name;
    if (topbarTitleEl) topbarTitleEl.innerText = `Good afternoon 👋`;
}

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
    const selectEl = document.getElementById("select-language");
    if (selectEl) selectEl.value = lang;
    if (typeof applyI18n === "function") {
        applyI18n(lang);
    }
    const dict = (typeof TRANSLATIONS !== "undefined" && typeof getLanguageCode === "function" && TRANSLATIONS[getLanguageCode(lang)]) || {};
    const prefix = dict.toast_lang_set || "Language set to";
    showToast(`${prefix} ${lang}`);
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
            const highlighted = data.highlighted_text || (data.verification && data.verification.highlighted_text);

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

                    ${highlighted ? `
                        <div style="font-size: 12px; font-weight: 700; margin-bottom: 4px;">Highlighted Sensational Words:</div>
                        <div style="background: var(--bg-subtle); padding: 12px; border-radius: 6px; font-size: 13px; line-height: 1.5;">
                            ${highlighted}
                        </div>
                    ` : ''}
                </div>
            `;
            showToast("✓ Trust Lens Analysis Complete");
        }
    } catch (err) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Evaluation failed. Please try again.</div>`;
    } finally {
        if (btn) { btn.innerText = "Analyze"; btn.disabled = false; }
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

    if (btn) { btn.innerText = "Analyzing..."; btn.disabled = true; }

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
        if (btn) { btn.innerText = "Analyze"; btn.disabled = false; }
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

// AI SAATHI CHAT ARCHITECTURE & CONVERSATION MEMORY
let currentConversationId = null;

function handleChatKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage();
    }
}

async function sendChatMessage() {
    const input = document.getElementById("chat-input-text");
    const btn = document.getElementById("btn-chat-send");
    const indicator = document.getElementById("typing-indicator");
    if (!input || !input.value.trim()) return;

    const userMsg = input.value.trim();
    input.value = "";

    appendChatBubble(userMsg, "user");
    if (btn) btn.disabled = true;
    if (indicator) indicator.style.display = "block";

    try {
        const mode = isSeniorMode ? "Senior" : "Adult";
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: userMsg,
                conversation_id: currentConversationId,
                user_name: userName,
                user_mode: mode
            })
        });
        const data = await res.json();

        if (data && data.message) {
            currentConversationId = data.conversation_id || currentConversationId;
            updateChatSessionBadge(currentConversationId);

            // Append main AI response bubble
            appendChatBubble(data.message, "saathi", data);

            // Handle ASK_CONFIRMATION card rendering
            if (data.action === "ASK_CONFIRMATION" && data.tool_requested) {
                renderActionConfirmationCard(data);
            }
        } else {
            appendChatBubble("⚠️ Service responded with an unexpected structure. Please try again.", "saathi");
        }
    } catch (err) {
        appendChatBubbleWithRetry("🔌 AI service is temporarily unavailable. Local safety tools remain active.", userMsg);
    } finally {
        if (btn) btn.disabled = false;
        if (indicator) indicator.style.display = "none";
    }
}

function updateChatSessionBadge(convId) {
    const badge = document.getElementById("chat-conv-badge");
    if (badge && convId) {
        badge.innerText = `Session: ${convId.slice(0, 10)}...`;
    }
}

function startNewConversation() {
    currentConversationId = null;
    const log = document.getElementById("chat-log");
    const badge = document.getElementById("chat-conv-badge");
    if (badge) badge.innerText = "Session: Active";

    if (log) {
        log.innerHTML = `
            <div class="msg-bubble saathi">
                <strong>Namaste ${escapeHtml(userName)}! I am your AI Saathi 🙏</strong><br>
                Started a new conversation session. How can I assist or verify digital safety for you now?
            </div>
        `;
    }
    showToast("✓ Started new conversation session");
}

async function clearCurrentConversation() {
    if (!currentConversationId) {
        startNewConversation();
        return;
    }

    try {
        await fetch(`/api/chat/history/${currentConversationId}`, { method: "DELETE" });
        startNewConversation();
        showToast("✓ Conversation memory cleared");
    } catch (err) {
        showToast("Failed to clear memory");
    }
}

function renderActionConfirmationCard(chatData) {
    const log = document.getElementById("chat-log");
    if (!log) return;

    const tool = chatData.tool_requested || {};
    const div = document.createElement("div");
    div.className = "card-panel";
    div.style.background = "var(--bg-subtle)";
    div.style.border = "1px solid var(--accent-amber)";
    div.style.margin = "8px 0";

    div.innerHTML = `
        <div style="font-weight: 700; color: var(--accent-amber); margin-bottom: 6px;">
            ⚠️ CONFIRMATION REQUIRED
        </div>
        <div style="font-size: 13.5px; margin-bottom: 10px;">
            AI Saathi requested to execute tool: <strong>${escapeHtml(tool.name || 'External Communication')}</strong>
        </div>
        <div style="display: flex; gap: 10px;">
            <button class="btn-send" style="background: var(--accent-green); color: #000;" onclick="confirmPendingAction(true, '${tool.name}', this)">✓ Approve & Execute</button>
            <button class="quick-btn" style="border-color: var(--accent-rose); color: var(--accent-rose);" onclick="confirmPendingAction(false, '${tool.name}', this)">✕ Decline</button>
        </div>
    `;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

async function confirmPendingAction(approved, toolName, btnEl) {
    const parentCard = btnEl ? btnEl.closest('.card-panel') : null;
    if (parentCard) {
        parentCard.innerHTML = `<div style="font-size: 13px; font-weight: 600; color: var(--text-secondary);">${approved ? '⏳ Processing approval...' : '🚫 Action cancelled by user.'}</div>`;
    }

    try {
        const res = await fetch("/api/chat/confirm_action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                user_approved: approved,
                action_type: toolName,
                action_details: {}
            })
        });
        const data = await res.json();
        if (data && data.result) {
            appendChatBubble(data.result.message, "saathi");
        }
    } catch (err) {
        showToast("Action execution update failed");
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

function appendChatBubble(text, sender, meta) {
    const log = document.getElementById("chat-log");
    if (!log) return;

    const div = document.createElement("div");
    div.className = `msg-bubble ${sender}`;
    if (meta && meta.action === "BLOCK") {
        div.style.border = "1px solid var(--accent-rose)";
    }
    
    if (sender === "saathi") {
        div.innerHTML = parseMarkdown(text);
    } else {
        div.innerHTML = escapeHtml(text).replace(/\n/g, "<br>");
    }
    
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

function parseMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);

    // Code blocks with Copy Code button
    html = html.replace(/```([a-zA-Z0-9_\-#\+]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const cleanLang = lang.trim() || "code";
        return `<div class="code-block-wrapper" style="background: #11131a; border: 1px solid var(--border-color); border-radius: 8px; margin: 10px 0; overflow: hidden;"><div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.05); padding: 6px 12px; font-size: 11px; font-weight: 600; color: var(--accent-cyan); text-transform: uppercase;"><span>${cleanLang}</span><button class="quick-btn" style="padding: 2px 8px; font-size: 10px;" onclick="copyCode(this)">Copy Code</button></div><pre style="margin:0; padding:12px; font-family: var(--font-mono); font-size: 13px; overflow-x: auto;"><code>${code.trim()}</code></pre></div>`;
    });

    // Inline Code
    html = html.replace(/`([^`]+)`/g, '<code style="background: rgba(0,240,255,0.1); color: var(--accent-cyan); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 12.5px;">$1</code>');

    // Headings
    html = html.replace(/^### (.*$)/gim, '<h3 style="font-size: 15px; font-weight: 700; margin: 10px 0 6px 0;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 style="font-size: 17px; font-weight: 800; margin: 12px 0 6px 0;">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 style="font-size: 19px; font-weight: 800; margin: 14px 0 8px 0;">$1</h1>');

    // Bold & Italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Bullet points
    html = html.replace(/^\s*[-•]\s+(.*$)/gim, '<li style="margin-left: 18px;">$1</li>');

    // New lines
    html = html.replace(/\n/g, '<br>');

    return html;
}

function copyCode(btnEl) {
    const codeWrapper = btnEl.closest('.code-block-wrapper');
    if (codeWrapper) {
        const codeBlock = codeWrapper.querySelector('code');
        if (codeBlock) {
            const text = codeBlock.innerText;
            navigator.clipboard.writeText(text).then(() => {
                const orig = btnEl.innerText;
                btnEl.innerText = "✓ Copied!";
                setTimeout(() => { btnEl.innerText = orig; }, 2000);
            }).catch(() => {
                showToast("Copied code to clipboard");
            });
        }
    }
}

function appendChatBubbleWithRetry(text, retryQuery) {
    const log = document.getElementById("chat-log");
    if (!log) return;

    const div = document.createElement("div");
    div.className = "msg-bubble saathi";
    div.style.border = "1px solid var(--accent-amber)";
    div.innerHTML = `
        ${escapeHtml(text)}<br><br>
        <button class="quick-btn" style="font-size: 11px; padding: 4px 10px;" onclick="retryChatQuery('${escapeHtml(retryQuery)}')">🔄 Retry Request</button>
    `;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

function retryChatQuery(query) {
    const input = document.getElementById("chat-input-text");
    if (input) {
        input.value = query;
        sendChatMessage();
    }
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