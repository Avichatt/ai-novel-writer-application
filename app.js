/**
 * Whispers of Starlight and Shadow - eBook Reader App Logic
 */

const CHAPTER_DATA = [
    {
        id: 1,
        title: "Chapter 1: The Spark in the Observatory",
        file: "manuscript/chapter_01.md"
    },
    {
        id: 2,
        title: "Chapter 2: Bound by Midnight",
        file: "manuscript/chapter_02.md"
    },
    {
        id: 3,
        title: "Chapter 3: Into the Shadow Citadel",
        file: "manuscript/chapter_03.md"
    },
    {
        id: 4,
        title: "Chapter 4: The Sanctuary of Ravenstone",
        file: "manuscript/chapter_04.md"
    },
    {
        id: 5,
        title: "Chapter 5: Shadows at the Court",
        file: "manuscript/chapter_05.md"
    },
    {
        id: 6,
        title: "Chapter 6 & 7: Secrets of the Void & Trial of Whispers",
        file: "manuscript/chapter_06_07.md"
    },
    {
        id: 7,
        title: "Chapter 8, 9 & 10: The Eclipse & A Court of Stars",
        file: "manuscript/chapter_08_09_10.md"
    }
];

const OUTLINE_SUMMARY = [
    { num: 1, title: "The Spark in the Observatory", desc: "Lyra's astral flare collides with Kaelen's void blade, forging the Soulbound Tether." },
    { num: 2, title: "Bound by Midnight", desc: "The realization of the proximity constraint and their escape from the Citadel." },
    { num: 3, title: "Into the Shadow Citadel", desc: "Travel to Ravenstone Keep and battling shadow hounds in the snowstorm." },
    { num: 4, title: "The Sanctuary of Ravenstone", desc: "Forced proximity in Kaelen's private chambers and learning magic equilibrium." },
    { num: 5, title: "Shadows at the Court", desc: "The Midnight Court Ball, waltzing under chandeliers, and standing up to Vespera." },
    { num: 6, title: "Secrets of the Void Well", desc: "Discovering how to seal the Void Well using Astral-Umbral Fusion." },
    { num: 7, title: "The Trial of Whispers", desc: "Overcoming fear phantoms in the Obsidian Forest and cementing their bond." },
    { num: 8, title: "The Grand Masquerade & Betrayal", desc: "Vespera's trap during the Eclipse and Kaelen's void rage." },
    { num: 9, title: "The Celestial Eclipse", desc: "Lyra and Kaelen combine starlight and shadow to seal the Void Well forever." },
    { num: 10, title: "A Court of Stars and Shadow", desc: "Peace restored and an eternal promise under a sky of starlight aurora." }
];

let currentChapterIndex = 0;
let currentFontSize = 18;
let audioContext = null;
let isAudioPlaying = false;
let ambientOscillators = [];

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // Init Starfield
    initStarfieldCanvas();

    // Populate Navigation
    renderChapterList();
    renderOutlineTab();

    // Event Listeners
    setupEventListeners();

    // Load initial chapter
    loadChapter(0);
});

/* ── Starfield Canvas Animation ────────────────────────────────────────────── */
function initStarfieldCanvas() {
    const canvas = document.getElementById("starfield");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener("resize", () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const stars = [];
    const count = 120;

    for (let i = 0; i < count; i++) {
        stars.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 1.8,
            alpha: Math.random(),
            speed: 0.005 + Math.random() * 0.015,
            color: Math.random() > 0.5 ? "#F3C669" : "#9D64FE"
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let star of stars) {
            star.alpha += star.speed;
            if (star.alpha > 1 || star.alpha < 0.1) {
                star.speed = -star.speed;
            }

            ctx.beginPath();
            ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            ctx.fillStyle = star.color;
            ctx.globalAlpha = Math.abs(star.alpha);
            ctx.fill();
        }

        requestAnimationFrame(animate);
    }

    animate();
}

/* ── Chapter Management ─────────────────────────────────────────────────────── */
function renderChapterList() {
    const listContainer = document.getElementById("chapter-list");
    if (!listContainer) return;

    listContainer.innerHTML = CHAPTER_DATA.map((ch, idx) => `
        <li>
            <button class="chapter-item-btn ${idx === 0 ? 'active' : ''}" data-index="${idx}">
                <span>${ch.title}</span>
                <i data-lucide="chevron-right" style="width: 14px; height: 14px;"></i>
            </button>
        </li>
    `).join("");

    if (window.lucide) lucide.createIcons();

    document.querySelectorAll(".chapter-item-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const idx = parseInt(btn.getAttribute("data-index"));
            loadChapter(idx);
        });
    });
}

function renderOutlineTab() {
    const outlineContainer = document.getElementById("outline-summary-list");
    if (!outlineContainer) return;

    outlineContainer.innerHTML = OUTLINE_SUMMARY.map(item => `
        <div style="margin-bottom: 16px; padding: 14px; background: rgba(255,255,255,0.03); border-radius: 10px; border-left: 3px solid var(--accent-gold);">
            <strong style="color: var(--accent-gold);">Chapter ${item.num}: ${item.title}</strong>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin-top: 4px;">${item.desc}</p>
        </div>
    `).join("");
}

async function loadChapter(index) {
    if (index < 0 || index >= CHAPTER_DATA.length) return;

    currentChapterIndex = index;
    const ch = CHAPTER_DATA[index];

    // Update Nav Active State
    document.querySelectorAll(".chapter-item-btn").forEach((btn, i) => {
        btn.classList.toggle("active", i === index);
    });

    // Update Indicator
    const indicator = document.getElementById("chapter-indicator");
    if (indicator) {
        indicator.textContent = `Chapter ${index + 1} of ${CHAPTER_DATA.length}`;
    }

    // Disable/Enable Nav Buttons
    document.getElementById("prev-chapter-btn").disabled = (index === 0);
    document.getElementById("next-chapter-btn").disabled = (index === CHAPTER_DATA.length - 1);

    // Fetch and render Markdown
    const article = document.getElementById("chapter-content");
    try {
        const response = await fetch(ch.file);
        if (!response.ok) throw new Error("Chapter file not found");
        const mdText = await response.text();
        article.innerHTML = parseSimpleMarkdown(mdText);
    } catch (err) {
        article.innerHTML = `
            <h2>${ch.title}</h2>
            <p>Welcome to <em>Whispers of Starlight and Shadow</em>. Click 'Start Reading Chapter 1' or choose a chapter from the sidebar.</p>
        `;
    }

    // Scroll to top of article
    window.scrollTo({ top: 0, behavior: "smooth" });
    updateReadingProgress();
}

function parseSimpleMarkdown(md) {
    let html = md
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        .replace(/^---$/gim, '<hr style="border: 0; height: 1px; background: var(--border-glass); margin: 30px 0;">');

    // Paragraph wrapping
    const paragraphs = html.split(/\n\s*\n/);
    return paragraphs.map(p => {
        p = p.trim();
        if (p.startsWith('<h') || p.startsWith('<hr')) return p;
        return `<p>${p}</p>`;
    }).join('\n');
}

/* ── Reading Controls & Progress ────────────────────────────────────────────── */
function setupEventListeners() {
    // Sidebar toggle
    const toggleBtn = document.getElementById("toggle-sidebar-btn");
    const sidebar = document.getElementById("sidebar");
    toggleBtn?.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });

    // Start reading hero button
    document.getElementById("start-reading-btn")?.addEventListener("click", () => {
        loadChapter(0);
    });

    // Next/Prev Buttons
    document.getElementById("prev-chapter-btn")?.addEventListener("click", () => {
        if (currentChapterIndex > 0) loadChapter(currentChapterIndex - 1);
    });

    document.getElementById("next-chapter-btn")?.addEventListener("click", () => {
        if (currentChapterIndex < CHAPTER_DATA.length - 1) loadChapter(currentChapterIndex + 1);
    });

    // Font size controls
    document.getElementById("font-increase")?.addEventListener("click", () => {
        if (currentFontSize < 28) {
            currentFontSize += 2;
            updateFontSize();
        }
    });

    document.getElementById("font-decrease")?.addEventListener("click", () => {
        if (currentFontSize > 14) {
            currentFontSize -= 2;
            updateFontSize();
        }
    });

    // Theme selector
    document.querySelectorAll(".theme-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".theme-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const theme = btn.getAttribute("data-theme");
            document.body.className = theme;
        });
    });

    // Story Bible Modal
    const modal = document.getElementById("bible-modal");
    document.getElementById("bible-modal-btn")?.addEventListener("click", () => {
        modal.classList.remove("hidden");
    });
    document.getElementById("close-modal-btn")?.addEventListener("click", () => {
        modal.classList.add("hidden");
    });

    // Modal Tabs
    document.querySelectorAll(".modal-tab-btn").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".modal-tab-btn").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            
            tab.classList.add("active");
            const targetId = tab.getAttribute("data-tab");
            document.getElementById(targetId)?.classList.add("active");
        });
    });

    // Ambiance Soundscape Toggle
    document.getElementById("ambiance-btn")?.addEventListener("click", toggleAmbientSoundscape);

    // Window scroll for progress
    window.addEventListener("scroll", updateReadingProgress);
}

function updateFontSize() {
    document.documentElement.style.setProperty("--reader-font-size", `${currentFontSize}px`);
    document.getElementById("font-size-val").textContent = `${currentFontSize}px`;
}

function updateReadingProgress() {
    const article = document.getElementById("chapter-content");
    if (!article) return;

    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    
    document.getElementById("reading-progress").style.width = `${Math.min(100, Math.max(0, progress))}%`;
}

/* ── Web Audio Synth for Dark Fantasy Ambiance ─────────────────────────────── */
function toggleAmbientSoundscape() {
    const btn = document.getElementById("ambiance-btn");
    
    if (isAudioPlaying) {
        stopAmbientSoundscape();
        btn.classList.remove("pill-accent");
        btn.querySelector("span").textContent = "Ambiance";
    } else {
        startAmbientSoundscape();
        btn.classList.add("pill-accent");
        btn.querySelector("span").textContent = "Playing ♪";
    }
}

function startAmbientSoundscape() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    if (audioContext.state === "suspended") {
        audioContext.resume();
    }

    // Ambient Drone (Deep Indigo Frequencies: 110Hz & 164.81Hz)
    const freqs = [110.00, 164.81, 220.00];
    ambientOscillators = freqs.map(freq => {
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, audioContext.currentTime);
        gain.gain.setValueAtTime(0.04, audioContext.currentTime);

        osc.connect(gain);
        gain.connect(audioContext.destination);
        osc.start();
        return { osc, gain };
    });

    isAudioPlaying = true;
}

function stopAmbientSoundscape() {
    ambientOscillators.forEach(({ osc, gain }) => {
        gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.5);
        setTimeout(() => osc.stop(), 500);
    });
    ambientOscillators = [];
    isAudioPlaying = false;
}
