const API_BASE = `${window.location.origin}/hr/engagement`;

let projectMetadata = null;

// --- INITIALIZATION ---
async function initDashboard() {
    await fetchMetadata();
    populateCandidateSelector();

    const selector = document.getElementById('candidate-selector');
    if (selector && selector.value) loadDashboardData(selector.value);
}

function refreshCurrent() {
    const selector = document.getElementById('candidate-selector');
    if (selector) loadDashboardData(selector.value);
}

async function fetchMetadata() {
    try {
        const res = await fetch(`${API_BASE}/metadata`);
        projectMetadata = await res.json();
        console.log("Metadata loaded:", projectMetadata);
    } catch (err) {
        console.error("Failed to fetch metadata:", err);
    }
}

function populateCandidateSelector() {
    const selector = document.getElementById('candidate-selector');
    if (!selector || !projectMetadata) return;

    selector.innerHTML = projectMetadata.candidates.map(c =>
        `<option value="${c.candidate_id}">${c.full_name} (${c.candidate_id})</option>`
    ).join('');
}

async function initVisualizer() {
    await fetchMetadata();
    populateVisualizerFields();
}

function populateVisualizerFields() {
    if (!projectMetadata) return;

    // 1. Stages
    const stageSelector = document.getElementById('s1-stage');
    if (stageSelector) {
        stageSelector.innerHTML = projectMetadata.stages.map(s =>
            `<option value="${s}">${s}</option>`
        ).join('');
    }

    // 2. Message Types
    const msgTypeSelector = document.getElementById('s2-type');
    if (msgTypeSelector) {
        msgTypeSelector.innerHTML = projectMetadata.message_types.map(m =>
            `<option value="${m}">${m.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>`
        ).join('');
    }

    // 2. Default IDs for visualizer (convenience)
    if (projectMetadata.candidates.length > 0) {
        const cId = projectMetadata.candidates[0].candidate_id;
        ['s1-id', 's2-id', 's6-id', 's7-id'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = cId;
        });
    }

    if (projectMetadata.jobs.length > 0) {
        const jId = projectMetadata.jobs[0].job_id;
        ['s1-job'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = jId;
        });
    }
}

async function loadDashboardData(candidateId) {
    if (!candidateId) return;
    // Check if we are actually on the dashboard page
    if (!document.getElementById('activity-body')) return;

    try {
        const candidate = projectMetadata ? projectMetadata.candidates.find(c => c.candidate_id === candidateId) : null;
        const name = candidate ? candidate.full_name : candidateId;

        document.getElementById('dashboard-title').innerText = `Overview: ${name}`;
        document.getElementById('last-updated').innerText = `Last updated: ${new Date().toLocaleTimeString()}`;

        const jobId = getActiveJobId(candidateId);

        // 1. Fetch Pipeline Info (Direct from DB-backed API)
        const resPipeline = await fetch(`${API_BASE}/candidate/${candidateId}/job/${jobId}/pipeline`);
        const pipeline = await resPipeline.json();

        const stageEl = document.getElementById('stat-stage');
        const channelEl = document.getElementById('stat-channel');
        const tableBody = document.getElementById('activity-body');

        if (pipeline && !pipeline.detail) {
            stageEl.innerText = pipeline.stage || "ACTIVE";
            channelEl.innerText = pipeline.preferred_channel || "--";
        } else {
            stageEl.innerText = "NO DATA";
            channelEl.innerText = "--";
        }

        // 2. Fetch Timeline (ONLY for interaction count)
        const resTimeline = await fetch(`${API_BASE}/candidate/${candidateId}/job/${jobId}/timeline`);
        const timelineData = await resTimeline.json();
        const events = timelineData.events || [];
        document.getElementById('stat-int').innerText = events.length;

        // 3. Disable timeline rendering as requested
        tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 40px; color: var(--text-muted);">
            Live timeline rendering is disabled. Use "API Visualizer" for full history.
        </td></tr>`;

        // 4. Fetch Risk Evaluate
        const resRisk = await fetch(`${API_BASE}/risk/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidateId, jobId })
        });
        const riskData = await resRisk.json();
        const score = riskData.riskScore || 0;

        const riskP = document.getElementById('stat-risk');
        const riskCard = document.getElementById('risk-card');
        if (riskP && riskCard) {
            riskP.innerText = score;
            if (score >= 70) { riskCard.style.borderLeftColor = "#ef4444"; riskP.style.color = "#ef4444"; }
            else if (score >= 40) { riskCard.style.borderLeftColor = "#f59e0b"; riskP.style.color = "#f59e0b"; }
            else { riskCard.style.borderLeftColor = "#10b981"; riskP.style.color = "#10b981"; }
        }
    } catch (err) { console.error("Dashboard Load Error:", err); }
}

// --- VISUALIZER LOGIC (Runs on visualizer.html) ---
function showRes(id, data) {
    const el = document.getElementById(`res-${id}`);
    if (!el) return;
    el.innerText = JSON.stringify(data, null, 2);
    el.style.borderColor = data.detail ? '#ef4444' : '#38bdf8';
}

// Helper to get common IDs from the first API section
function getCommonIds() {
    const s1Id = document.getElementById('s1-id');
    const s1Job = document.getElementById('s1-job');

    if (s1Id && s1Job) {
        return { candidateId: s1Id.value, jobId: s1Job.value };
    }

    const dashboardSelector = document.getElementById('candidate-selector');
    if (dashboardSelector) {
        const cId = dashboardSelector.value;
        return { candidateId: cId, jobId: getActiveJobId(cId) };
    }

    return { candidateId: "CAND-001", jobId: "JOB-101" };
}

function getActiveJobId(candidateId) {
    if (!projectMetadata || !projectMetadata.candidates) return "JOB-101";
    // Search for candidate in metadata to get their associated job_id
    // But since our candidate_pipeline might not be in metadata yet, 
    // let's assume JOB-101 as default but keep it open for future expansion
    return "JOB-101";
}

async function runUpdateStage() {
    const ids = getCommonIds();
    const res = await fetch(`${API_BASE}/stage/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            candidateId: ids.candidateId,
            jobId: ids.jobId,
            newStage: document.getElementById('s1-stage').value
        })
    });
    showRes(1, await res.json());
}

async function runSendMessage() {
    const ids = getCommonIds();
    const res = await fetch(`${API_BASE}/status/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            candidateId: document.getElementById('s2-id').value,
            jobId: ids.jobId,
            messageType: document.getElementById('s2-type').value
        })
    });
    showRes(2, await res.json());
}

async function runProposeSlots() {
    const ids = getCommonIds();
    const date = document.getElementById('s3-date').value;
    const res = await fetch(`${API_BASE}/interview/propose-slots`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            candidateId: ids.candidateId,
            jobId: ids.jobId,
            date: date
        })
    });
    showRes(3, await res.json());
}

async function runConfirmSlot() {
    const ids = getCommonIds();
    const res = await fetch(`${API_BASE}/interview/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            candidateId: ids.candidateId,
            jobId: ids.jobId,
            chosenSlot: document.getElementById('s4-slot').value
        })
    });
    showRes(4, await res.json());
}

async function runGenerateOffer() {
    const ids = getCommonIds();
    const res = await fetch(`${API_BASE}/offer/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            candidateId: ids.candidateId,
            jobId: ids.jobId,
            joiningDate: document.getElementById('s5-join').value
        })
    });
    showRes(5, await res.json());
}

async function runEvaluateRisk() {
    const ids = getCommonIds();
    const res = await fetch(`${API_BASE}/risk/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            candidateId: document.getElementById('s6-id').value,
            jobId: ids.jobId
        })
    });
    showRes(6, await res.json());
}

async function runGetTimeline() {
    const ids = getCommonIds();
    const id = document.getElementById('s7-id').value;
    const res = await fetch(`${API_BASE}/candidate/${id}/job/${ids.jobId}/timeline`);
    showRes(7, await res.json());
}