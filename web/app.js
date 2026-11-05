/**
 * GRE Torture Alarm - Modern Dark Mode Application Logic
 * 
 * Features:
 * 1. RTG Real-Time Audio Synthesis for Models 1-7 (Default: Model 6 Apex Felid V2).
 * 2. Big vibrating "SHUT UP :(((((" button cycling across 500 tasteful desperate messages.
 * 3. 5-Minute Timer (300s) on upper UI with smooth progress bar.
 * 4. Target: 100 Points within 5 minutes. Correct = +P, Incorrect = -P/2.
 * 5. Inactivity Watchdog: 5 minutes of zero interaction reverts to full terror alarm.
 * 6. "100 Ways to Love a Cat" punishment audio ramping to full volume over 30s.
 */

// Global State
const STATE = {
  current: "IDLE", // IDLE, ALARM_RINGING, QUIZ_ACTIVE, CAT_PUNISHMENT, VICTORY
  alarmTime: "07:00",
  alarmPeriod: "AM",
  isArmed: false,
  selectedModel: "model6",

  // Quiz & Timer
  currentPoints: 0,
  targetPoints: 100,
  quizDurationSeconds: 300, // 5 minutes
  quizSecondsRemaining: 300,
  quizInterval: null,

  // Inactivity Watchdog
  inactivityLimitSeconds: 300, // 5 minutes
  lastInteractionTime: Date.now(),
  watchdogInterval: null,

  // Questions
  currentQuestion: null,
  answeredQuestions: [],
  scoreHistory: [],

  // Audio Engines
  audioCtx: null,
  activeAlarmNodes: [],
  alarmAudioElement: null,
  catAudio: null,
  catRampInterval: null,
  catAudioNodes: [],
  catRampStartTime: null,
  catCurrentWayIndex: 0,
  catSpeechUtterance: null,
  catKaraokeLyrics: [],
  passageFontSize: 17,
  manifestedCatCount: 0,
  manifestedCats: [],
  bouncingCats: [],
  hiddenCatFeatures: [],

  // Ambient 5-Minute Focus Soundtrack & Ambient Audio Slider
  selectedProceduralTrack: "ambient_clean_soul",
  proceduralAudio: null,
  ambientVolume: 0.65, // Ambient volume slider (0.0 to 1.0)
  isAmbientMuted: false, // Ambient mute state
  isAudioPrimed: false,
  lastTriggeredMinuteKey: null,

  // Max Study Duration & Analytics
  maxStudyDurationMinutes: 20,
  studySessionStartTime: null,
  catBlendStartTime: null
};

// 500 Tasteful Shut-Up Messages
let SHUT_UP_MESSAGES = [
  "SHUT UP :(((((",
  "PLEASE SHUT UP :(((((",
  "MAKE IT STOP :(((((",
  "MY AMYGDALA IS ON FIRE",
  "I BEG OF THEE, SILENCE",
  "OKAY OKAY I WILL PREP FOR GRE",
  "UNSUBSCRIBE FROM CONSCIOUSNESS",
  "THE APEX PREDATOR IS IN MY ROOM",
  "MY COCHLEA IS WEEPING",
  "CEASE AND DESIST :(((((",
  "I SURRENDER! GIVE ME QUESTIONS",
  "MY HEART RATE IS 190 BPM",
  "I REPENT OF MY SNOOZE HABITS",
  "STOP THE 22 HZ LION RUMBLE",
  "I WILL MEMORIZE BARRONS 333",
  "PLEASE SPARE MY NEURONS",
  "WHO AUTHORIZED THIS TORTURE",
  "I AM SITTING UP IN BED LOOK",
  "WHY DO YOU HATE ME :(((((",
  "I CHOOSE VOCAB OVER DEAFNESS"
];

// 100 Ways to Love a Cat
let CAT_WAYS = [
  "Keep a tidy house for them",
  "Be sure to clip their claws",
  "Provide a sunny windowsill",
  "Give them an empty cardboard box",
  "Don't squeeze their paws too hard",
  "Whisper 'I love you' in their ear",
  "Play them acoustic folk music",
  "Give them a collar with a tiny bell",
  "Brush their teeth with salmon paste",
  "Hold them upside down like a baby"
];

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener("DOMContentLoaded", async () => {
  initClock();
  setupWatchdog();
  await loadData();
  bindUIEvents();
  initCatPhysics();
  setAlarmPeriod(STATE.alarmPeriod || "AM");
  renderState();
  renderLaTeX(document.body);
  setTimeout(() => renderLaTeX(document.body), 300);
});

// Load external JSON data if available
async function loadData() {
  if (window.BUNDLED_SHUT_UP_MESSAGES && window.BUNDLED_SHUT_UP_MESSAGES.length > 0) {
    SHUT_UP_MESSAGES = window.BUNDLED_SHUT_UP_MESSAGES;
  }
  if (window.BUNDLED_CAT_WAYS && window.BUNDLED_CAT_WAYS.length > 0) {
    CAT_WAYS = window.BUNDLED_CAT_WAYS;
  }
  if (window.BUNDLED_CAT_KARAOKE && window.BUNDLED_CAT_KARAOKE.length > 0) {
    STATE.catKaraokeLyrics = window.BUNDLED_CAT_KARAOKE;
  }
  if (window.BUNDLED_HIDDEN_CATS && window.BUNDLED_HIDDEN_CATS.length > 0) {
    STATE.hiddenCatFeatures = window.BUNDLED_HIDDEN_CATS;
  }

  try {
    const resMsg = await fetch("/api/shut_up_messages");
    if (resMsg.ok) {
      const data = await resMsg.json();
      if (Array.isArray(data) && data.length >= 100) {
        SHUT_UP_MESSAGES = data;
      }
    }
  } catch (e) {
    console.warn("Using bundled shut up messages");
  }

  try {
    const resCat = await fetch("/api/cat_ways");
    if (resCat.ok) {
      const data = await resCat.json();
      if (Array.isArray(data) && data.length >= 50) {
        CAT_WAYS = data;
      }
    }
  } catch (e) {
    console.warn("Using bundled cat ways");
  }

  try {
    const resKaraoke = await fetch("/api/cat_karaoke");
    if (resKaraoke.ok) {
      const data = await resKaraoke.json();
      if (Array.isArray(data) && data.length > 0) {
        STATE.catKaraokeLyrics = data;
      }
    }
  } catch (e) {
    console.warn("Using fallback cat ways for karaoke");
  }

  try {
    const resHidden = await fetch("/api/hidden_cats");
    if (resHidden.ok) {
      const data = await resHidden.json();
      if (Array.isArray(data) && data.length > 0) {
        STATE.hiddenCatFeatures = data;
      }
    }
  } catch (e) {
    console.warn("Using fallback hidden cats");
  }
}

// Live Digital Clock (Immune to Leading-Zero Mismatch and Background Tab Second-Zero Throttling)
function initClock() {
  function updateTime() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    const period = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    const hoursStr = String(hours).padStart(2, "0");

    const clockElem = document.getElementById("digital-clock");
    if (clockElem) {
      clockElem.textContent = `${hoursStr}:${minutes}:${seconds} ${period}`;
    }

    // Robust Alarm Trigger Check (Normalized numerical comparison)
    if (STATE.isArmed && STATE.current === "IDLE") {
      const parts = (STATE.alarmTime || "07:00").split(":");
      const targetH = parseInt(parts[0], 10);
      const targetM = parseInt(parts[1], 10);
      const targetP = (STATE.alarmPeriod || "AM").trim().toUpperCase();

      const curH = hours;
      const curM = now.getMinutes();
      const curP = period.toUpperCase();

      const minuteKey = `${now.getFullYear()}-${now.getMonth()+1}-${now.getDate()} ${curH}:${curM} ${curP}`;

      if (curH === targetH && curM === targetM && curP === targetP) {
        if (STATE.lastTriggeredMinuteKey !== minuteKey) {
          STATE.lastTriggeredMinuteKey = minuteKey;
          triggerAlarm("SCHEDULED_CLOCK_MATCH");
        }
      }
    }
  }
  updateTime();
  setInterval(updateTime, 1000);
}

// Inactivity Watchdog
function setupWatchdog() {
  const events = ["mousemove", "mousedown", "keydown", "touchstart", "scroll"];
  let lastReportedTime = 0;
  const REPORT_THROTTLE_MS = 15000; // Zero-Trust: Deterministic throttle: ping backend at most once every 15s

  events.forEach(evt => {
    window.addEventListener(evt, () => {
      const now = Date.now();
      STATE.lastInteractionTime = now;
      // Deterministically notify backend of user activity if throttle window has elapsed
      if (now - lastReportedTime >= REPORT_THROTTLE_MS) {
        lastReportedTime = now;
        fetch("/api/interaction", { method: "POST" }).catch(() => {});
      }
    }, { passive: true });
  });

  // Check inactivity every second
  STATE.watchdogInterval = setInterval(() => {
    if (STATE.current === "QUIZ_ACTIVE" || STATE.current === "CAT_PUNISHMENT") {
      const inactiveSec = (Date.now() - STATE.lastInteractionTime) / 1000;
      const remainingSec = Math.max(0, STATE.inactivityLimitSeconds - inactiveSec);

      const watchElem = document.getElementById("watchdog-timer-display");
      if (watchElem) {
        const m = Math.floor(remainingSec / 60);
        const s = Math.floor(remainingSec % 60);
        watchElem.textContent = `Inactivity Watchdog: ${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
        if (remainingSec < 60) {
          watchElem.classList.add("text-rose-400", "animate-pulse");
        } else {
          watchElem.classList.remove("text-rose-400", "animate-pulse");
        }
      }

      // Check Max Study Duration timeout (resets to initial state and presents statistics)
      if (STATE.studySessionStartTime) {
        const totalStudySec = (Date.now() - STATE.studySessionStartTime) / 1000;
        const maxSec = (STATE.maxStudyDurationMinutes || 20) * 60;
        if (totalStudySec >= maxSec) {
          console.warn("Max Study Duration reached! Terminating session and displaying statistics.");
          endStudySessionMaxDuration();
          return;
        }
      }

      // Revert if zero interaction for 5 minutes!
      if (inactiveSec >= STATE.inactivityLimitSeconds && STATE.currentPoints < STATE.targetPoints) {
        console.warn("USER ASSUMED ASLEEP! Reverting to ALARM_RINGING!");
        triggerAlarm("INACTIVITY_WATCHDOG_TRIGGERED");
      }
    }
  }, 1000);
}

// Audio Autoplay Policy Priming
function primeAudioEngine() {
  if (!STATE.audioCtx) {
    STATE.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (STATE.audioCtx && STATE.audioCtx.state === "suspended") {
    STATE.audioCtx.resume();
  }
  try {
    const buffer = STATE.audioCtx.createBuffer(1, 1, 22050);
    const source = STATE.audioCtx.createBufferSource();
    source.buffer = buffer;
    source.connect(STATE.audioCtx.destination);
    source.start(0);
  } catch (e) {}

  STATE.isAudioPrimed = true;
  const ind = document.getElementById("audio-primed-indicator");
  if (ind) {
    ind.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Audio Engine: Primed & Armed`;
    ind.className = "text-[11px] font-mono text-emerald-400 flex items-center gap-1.5 pt-1";
  }
}

// Bind UI Interactions
function bindUIEvents() {
  // Interaction listeners for audio priming
  document.addEventListener("click", primeAudioEngine, { passive: true });
  document.addEventListener("touchstart", primeAudioEngine, { passive: true });
  document.addEventListener("keydown", primeAudioEngine, { passive: true });

  // Preset buttons
  document.getElementById("btn-test-alarm")?.addEventListener("click", () => {
    primeAudioEngine();
    triggerAlarm("MANUAL_TEST");
  });
  document.getElementById("btn-preset-5s")?.addEventListener("click", () => {
    primeAudioEngine();
    scheduleQuickTest(5);
  });
  document.getElementById("btn-preset-1m")?.addEventListener("click", () => {
    primeAudioEngine();
    scheduleQuickTest(60);
  });

  // Arm toggle
  document.getElementById("btn-arm-toggle")?.addEventListener("click", toggleArmAlarm);

  // Big Shut Up Button
  const shutUpBtn = document.getElementById("btn-shut-up-main");
  if (shutUpBtn) {
    shutUpBtn.addEventListener("click", handleShutUpClicked);
    shutUpBtn.addEventListener("mouseenter", cycleShutUpMessage);
  }

  // Question submission & selection
  document.getElementById("btn-submit-answer")?.addEventListener("click", submitUserAnswer);
  document.getElementById("btn-clear-answer")?.addEventListener("click", () => {
    document.querySelectorAll('#question-card-container input').forEach(input => {
      input.checked = false;
    });
    hideValidationError();
    // Reset Sentence Equivalence live counter
    const seBadge = document.getElementById("se-count-badge");
    if (seBadge) {
      seBadge.className = "font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30";
      seBadge.textContent = "0 of 2 selected";
    }
    // Reset multi-blank indicators
    document.querySelectorAll(".blank-status").forEach(bs => {
      bs.textContent = "Unselected";
      bs.className = "blank-status text-[10px] text-slate-500 font-normal";
    });
    document.querySelectorAll(".blank-choice-box").forEach(b => {
      b.classList.remove("border-cyan-500/60", "bg-cyan-950/20");
    });
  });
  document.getElementById("btn-next-question")?.addEventListener("click", fetchNextQuestion);

  // Disarm / Reset
  document.getElementById("btn-victory-disarm")?.addEventListener("click", resetToIdle);
  document.getElementById("btn-force-disarm")?.addEventListener("click", resetToIdle);

  // Testing Button: Immediately progress to "100 Ways to Love a Cat" Punishment Phase
  document.querySelectorAll(".btn-test-cat, #btn-test-cat-punishment, #btn-banner-trigger-cat, #btn-ringing-test-cat").forEach(btn => {
    btn.addEventListener("click", () => {
      testImmediateCatPunishment();
    });
  });

  // Hidden Cats Menagerie Modal
  document.getElementById("hidden-cats-counter-pill")?.addEventListener("click", openMenagerieModal);
  document.getElementById("btn-close-menagerie")?.addEventListener("click", closeMenagerieModal);
  document.getElementById("modal-cat-menagerie")?.addEventListener("click", (e) => {
    if (e.target.id === "modal-cat-menagerie") closeMenagerieModal();
  });

  // Dedicated AM / PM Buttons
  document.getElementById("btn-period-am")?.addEventListener("click", () => setAlarmPeriod("AM"));
  document.getElementById("btn-period-pm")?.addEventListener("click", () => setAlarmPeriod("PM"));
  document.getElementById("select-alarm-period")?.addEventListener("change", (e) => setAlarmPeriod(e.target.value));

  // Model select
  document.getElementById("select-sound-model")?.addEventListener("change", (e) => {
    STATE.selectedModel = e.target.value;
  });

  // Max Study Duration select
  document.getElementById("select-max-study-duration")?.addEventListener("change", (e) => {
    STATE.maxStudyDurationMinutes = parseInt(e.target.value, 10) || 20;
    showToast(`Max study duration set to ${STATE.maxStudyDurationMinutes} minutes`, "cyan");
  });

  // Session Statistics Modal Buttons
  document.getElementById("btn-close-session-stats")?.addEventListener("click", closeSessionStatisticsModal);
  document.getElementById("btn-stats-dismiss")?.addEventListener("click", closeSessionStatisticsModal);
  document.getElementById("btn-stats-arm-next")?.addEventListener("click", () => {
    closeSessionStatisticsModal();
    STATE.isArmed = true;
    renderState();
    showToast("Alarm armed for next wake-up!", "emerald");
  });
  document.getElementById("modal-session-statistics")?.addEventListener("click", (e) => {
    if (e.target.id === "modal-session-statistics") closeSessionStatisticsModal();
  });

  // Ambient Focus Generator Selection Dropdowns (Synced between Setup and Quiz)
  document.querySelectorAll(".select-ambient-generator-sync").forEach(sel => {
    sel.addEventListener("change", (e) => {
      setAmbientGenerator(e.target.value);
    });
  });

  // Ambient Audio Volume Sliders (Synced between Setup and Quiz)
  document.querySelectorAll(".slider-ambient-volume-sync").forEach(slider => {
    slider.addEventListener("input", (e) => {
      setAmbientVolume(Number(e.target.value) / 100.0);
    });
    slider.addEventListener("change", (e) => {
      setAmbientVolume(Number(e.target.value) / 100.0);
    });
  });

  // Ambient Audio Mute Toggle Button
  document.getElementById("btn-quiz-ambient-mute")?.addEventListener("click", () => {
    toggleAmbientMute();
  });

  let previewAudio = null;
  document.getElementById("btn-preview-procedural")?.addEventListener("click", () => {
    primeAudioEngine();
    const btn = document.getElementById("btn-preview-procedural");
    if (previewAudio) {
      previewAudio.pause();
      previewAudio = null;
      if (btn) btn.textContent = "Preview 30s";
      return;
    }
    const trackKey = STATE.selectedProceduralTrack || "ambient_clean_soul";
    if (trackKey === "none") {
      showToast("Selected track is Muted", "slate");
      return;
    }
    const src = (typeof PROCEDURAL_AUDIO_MAP !== "undefined" && PROCEDURAL_AUDIO_MAP[trackKey]) ? PROCEDURAL_AUDIO_MAP[trackKey] : "/ambient_tracks/08_clean_soul.mp3";
    previewAudio = new Audio(src);
    const effVol = STATE.isAmbientMuted ? 0.0 : (STATE.ambientVolume ?? 0.65);
    previewAudio.volume = effVol;
    previewAudio.play().then(() => {
      if (btn) btn.textContent = "Stop Preview";
    }).catch(err => {
      showToast("Audio playback blocked, click to enable", "amber");
    });
    previewAudio.onended = () => {
      previewAudio = null;
      if (btn) btn.textContent = "Preview 30s";
    };
  });
}

function setAlarmPeriod(period) {
  STATE.alarmPeriod = period;
  const amBtn = document.getElementById("btn-period-am");
  const pmBtn = document.getElementById("btn-period-pm");
  const selectElem = document.getElementById("select-alarm-period");

  if (selectElem) selectElem.value = period;

  if (period === "AM") {
    amBtn?.classList.add("bg-cyan-500", "text-white", "shadow-md", "shadow-cyan-500/30");
    amBtn?.classList.remove("text-slate-400");
    pmBtn?.classList.remove("bg-cyan-500", "text-white", "shadow-md", "shadow-cyan-500/30");
    pmBtn?.classList.add("text-slate-400");
  } else {
    pmBtn?.classList.add("bg-cyan-500", "text-white", "shadow-md", "shadow-cyan-500/30");
    pmBtn?.classList.remove("text-slate-400");
    amBtn?.classList.remove("bg-cyan-500", "text-white", "shadow-md", "shadow-cyan-500/30");
    amBtn?.classList.add("text-slate-400");
  }
}
window.setAlarmPeriod = setAlarmPeriod;

function scheduleQuickTest(seconds) {
  const targetDate = new Date(Date.now() + seconds * 1000);
  let h = targetDate.getHours();
  const m = String(targetDate.getMinutes()).padStart(2, "0");
  const p = h >= 12 ? "PM" : "AM";
  h = h % 12 || 12;
  const hStr = String(h).padStart(2, "0");

  STATE.alarmTime = `${hStr}:${m}`;
  setAlarmPeriod(p);
  STATE.isArmed = true;

  document.getElementById("input-alarm-time").value = `${hStr}:${m}`;

  renderState();
  showToast(`Alarm set for ${STATE.alarmTime} ${STATE.alarmPeriod} (${seconds}s from now)!`, "emerald");

  // Exact fallback timer
  setTimeout(() => {
    if (STATE.isArmed && STATE.current === "IDLE") {
      triggerAlarm();
    }
  }, seconds * 1000);
}

function toggleArmAlarm() {
  primeAudioEngine();
  STATE.isArmed = !STATE.isArmed;
  const timeInput = document.getElementById("input-alarm-time");
  const periodInput = document.getElementById("select-alarm-period");
  if (timeInput) STATE.alarmTime = timeInput.value;
  if (periodInput) STATE.alarmPeriod = periodInput.value;

  renderState();
  showToast(STATE.isArmed ? `Alarm Armed for ${STATE.alarmTime} ${STATE.alarmPeriod}` : "Alarm Disarmed", STATE.isArmed ? "emerald" : "slate");

  // Sync state to backend
  if (STATE.isArmed) {
    fetch("/api/arm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        time: STATE.alarmTime,
        period: STATE.alarmPeriod,
        is_armed: true,
        model: STATE.selectedModel,
        volume: 1.0 // Alarm assault siren fixed at 100% volume
      })
    }).catch(() => {});
  } else {
    fetch("/api/disarm", { method: "POST" }).catch(() => {});
  }
}

function cycleShutUpMessage() {
  const btn = document.getElementById("btn-shut-up-main");
  if (btn && SHUT_UP_MESSAGES.length > 0) {
    const idx = Math.floor(Math.random() * SHUT_UP_MESSAGES.length);
    btn.innerHTML = `<span class="text-xs uppercase tracking-widest text-red-200 block mb-1">Click to Silence</span> ${SHUT_UP_MESSAGES[idx]}`;
  }
}

// ==========================================
// STATE TRANSITIONS
// ==========================================

function triggerAlarm(reason = "ALARM_RINGING") {
  primeAudioEngine();
  STATE.current = "ALARM_RINGING";
  STATE.lastInteractionTime = Date.now();
  stopCatPunishment();
  stopProceduralBackgroundTrack();
  clearInterval(STATE.quizInterval);

  cycleShutUpMessage();
  renderState();

  // Play RTG Sound Tone via Web Audio / authentic WAV streaming
  playRTGAlarmTone(STATE.selectedModel);

  // Notify backend of alarm ringing state
  fetch("/api/trigger", { method: "POST" }).catch(() => {});

  if (reason === "INACTIVITY_WATCHDOG_TRIGGERED") {
    showToast("SLEEP DETECTED! 5 minutes of inactivity elapsed. Alarm reactivated!", "crimson");
  }
}

function handleShutUpClicked() {
  // Stop RTG Alarm
  stopRTGAlarmTone();
  document.body.classList.remove("punishment-cat-mode");

  // Enter Quiz Mode
  STATE.current = "QUIZ_ACTIVE";
  STATE.currentPoints = 0;
  STATE.quizSecondsRemaining = STATE.quizDurationSeconds;
  STATE.quizStartTime = Date.now();
  STATE.lastInteractionTime = Date.now();
  STATE.studySessionStartTime = Date.now();
  STATE.answeredQuestions = [];

  renderState();
  startQuizTimer();
  fetchNextQuestion();

  // Start Evidence-Based Procedural Focus Track!
  playProceduralBackgroundTrack();

  // Notify backend to initialize quiz_start_time and transition server state
  fetch("/api/shut_up", { method: "POST" }).catch(() => {});

  showToast("Alarm muted! 5-Minute Timer Started. Accumulate 100 Points!", "cyan");
}

function startQuizTimer() {
  clearInterval(STATE.quizInterval);
  if (!STATE.quizStartTime) {
    STATE.quizStartTime = Date.now();
  }
  STATE.quizInterval = setInterval(() => {
    if (STATE.current !== "QUIZ_ACTIVE") {
      clearInterval(STATE.quizInterval);
      return;
    }

    // Wall-clock calculation prevents drift when browser background tabs are throttled
    const elapsed = Math.floor((Date.now() - STATE.quizStartTime) / 1000);
    STATE.quizSecondsRemaining = Math.max(0, STATE.quizDurationSeconds - elapsed);
    updateTimerDisplay();

    // Check expiration
    if (STATE.quizSecondsRemaining <= 0) {
      clearInterval(STATE.quizInterval);
      if (STATE.currentPoints >= STATE.targetPoints) {
        triggerVictory();
      } else {
        triggerCatPunishment();
      }
    }
  }, 1000);
}

function updateTimerDisplay() {
  const rem = Math.max(0, STATE.quizSecondsRemaining);
  const m = Math.floor(rem / 60);
  const s = Math.floor(rem % 60);
  const timerText = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;

  const elem = document.getElementById("timer-countdown-text");
  const bar = document.getElementById("timer-progress-bar");

  if (elem) elem.textContent = timerText;
  if (bar) {
    const pct = (rem / STATE.quizDurationSeconds) * 100;
    bar.style.width = `${pct}%`;
    if (rem <= 60) {
      bar.className = "progress-bar-fill bg-rose-500 animate-pulse";
      if (elem) elem.className = "text-2xl font-black font-mono text-rose-400 animate-pulse";
    } else if (rem <= 150) {
      bar.className = "progress-bar-fill bg-amber-500";
      if (elem) elem.className = "text-2xl font-black font-mono text-amber-300";
    } else {
      bar.className = "progress-bar-fill progress-timer";
      if (elem) elem.className = "text-2xl font-black font-mono text-cyan-400";
    }
  }
}

function updateScoreDisplay(delta = 0) {
  const scoreElem = document.getElementById("score-points-text");
  const scoreBar = document.getElementById("score-progress-bar");
  const deltaContainer = document.getElementById("score-delta-container");

  if (scoreElem) {
    scoreElem.textContent = `${STATE.currentPoints} / ${STATE.targetPoints} PTS`;
  }

  if (scoreBar) {
    const pct = Math.max(0, Math.min(100, (STATE.currentPoints / STATE.targetPoints) * 100));
    scoreBar.style.width = `${pct}%`;
  }

  // Floating score delta badge
  if (deltaContainer && delta !== 0) {
    const badge = document.createElement("div");
    badge.className = delta > 0 ? "score-badge-positive" : "score-badge-negative";
    badge.textContent = delta > 0 ? `+${delta} PTS` : `${delta} PTS`;
    deltaContainer.innerHTML = "";
    deltaContainer.appendChild(badge);
    setTimeout(() => { if (badge.parentNode) badge.remove(); }, 1500);
  }

  // Check victory
  if (STATE.currentPoints >= STATE.targetPoints) {
    triggerVictory();
  }
}

// ==========================================
// "100 WAYS TO LOVE A CAT" PUNISHMENT & MENAGERIE ENGINE
// ==========================================

async function testImmediateCatPunishment() {
  primeAudioEngine();
  stopRTGAlarmTone();
  if (!STATE.studySessionStartTime) {
    STATE.studySessionStartTime = Date.now();
  }

  // If ambient track is not currently playing, start it so audio blending can be observed
  if (!STATE.proceduralAudio && STATE.selectedProceduralTrack !== "none") {
    playProceduralBackgroundTrack();
  }

  // Zero out the 5-minute countdown clock
  clearInterval(STATE.quizInterval);
  STATE.quizSecondsRemaining = 0;
  updateTimerDisplay();

  // Ensure server is synchronized
  fetch("/api/shut_up", { method: "POST" }).catch(() => {});

  // If question is not yet loaded, load one before triggering cat mode
  if (!STATE.currentQuestion) {
    await fetchNextQuestion();
  }

  // Trigger the full 100 Ways to Love a Cat phase with audio blending
  triggerCatPunishment();
  showToast("🐾 TEST BUTTON: Immediate jump to '100 Ways to Love a Cat' phase with audio blending!", "amber");
}

function triggerCatPunishment() {
  STATE.current = "CAT_PUNISHMENT";
  STATE.catRampStartTime = Date.now();
  STATE.catBlendStartTime = Date.now();
  document.body.classList.add("punishment-cat-mode");
  // Procedural background audio is NOT stopped immediately; it cross-fades into 100WTLAC over 30s
  renderState();

  // Change top app icon & status to animated crying cat
  setCryingCatIcon(true);

  // Show floating Menagerie HUD
  const pill = document.getElementById("hidden-cats-counter-pill");
  if (pill) pill.classList.remove("hidden");

  // Transform question card in-place without re-rendering DOM:
  // Preserves 100% of user selections, radio/checkbox checks, KaTeX formulas, and scroll position!
  if (STATE.currentQuestion) {
    applyCatModeToQuestionCard();
  }

  showToast("5 MINUTES ELAPSED! Audio blending active: Ambient track fading out while '100 Ways to Love a Cat' blends in (100% Penalty Active)!", "amber");

  // Play authentic MP3 audio with 30s cross-fade volume blend & matched karaoke
  playCatPunishmentMusic();
}

function applyCatModeToQuestionCard() {
  const q = STATE.currentQuestion;
  if (!q) return;

  // 1. In-place update of penalty badge without rebuilding or flashing card DOM
  const penaltyBadge = document.getElementById("question-penalty-badge");
  if (penaltyBadge) {
    penaltyBadge.className = "px-2.5 py-0.5 rounded bg-rose-600/30 text-rose-300 font-bold border border-rose-500/60 animate-pulse font-mono text-xs";
    penaltyBadge.textContent = `-${q.point_value} PTS (100% PUNISHMENT ACTIVE!)`;
  }

  // 2. Transform the submit button text and styling in-place
  const submitBtn = document.getElementById("btn-submit-answer");
  if (submitBtn) {
    submitBtn.innerHTML = `<span>🐾 SUBMIT CLAW STRIKE (+${q.point_value} PTS · ${STATE.currentPoints}/100 PTS) 🐾</span>`;
    submitBtn.classList.remove("bg-cyan-600", "hover:bg-cyan-500", "shadow-cyan-600/30");
    submitBtn.classList.add("bg-gradient-to-r", "from-rose-600", "to-amber-600", "hover:from-rose-500", "hover:to-amber-500", "shadow-rose-600/40");
  }

  // 3. Transform the clear button in-place
  const clearBtn = document.getElementById("btn-clear-answer");
  if (clearBtn) {
    clearBtn.innerHTML = '<span>🐾 LICK CLEAN 🐾</span>';
  }

  // 4. Highlight question container with glowing feline border without altering contents
  const cardContainer = document.getElementById("question-card-container");
  if (cardContainer) {
    cardContainer.classList.add("border-rose-500/70", "shadow-[0_0_30px_rgba(244,63,94,0.35)]");
  }
}

function grantCatAudioReprieve(seconds = 15) {
  STATE.reprieveEndTime = Date.now() + (seconds * 1000);
  if (STATE.catAudio && !STATE.catAudio.paused) {
    // Drop volume immediately to 12% so user gets instant auditory relief
    STATE.catAudio.volume = Math.max(0.02, STATE.catAudio.volume * 0.12);
  }
  showToast(`🐾 15s AUDIO REPRIEVE! Felines repelled by correct ETS answer!`, "emerald");
}

function setCryingCatIcon(isCrying) {
  const iconInner = document.getElementById("app-main-icon-inner");
  const mainIcon = document.getElementById("app-main-icon");
  const statusBadge = document.getElementById("app-status-badge");

  if (isCrying) {
    document.body.classList.add("punishment-cat-mode");
    if (iconInner) {
      iconInner.innerHTML = `
        <div class="crying-cat-container" title="100 Ways to Love a Cat Punishment Active">
          <span class="crying-cat-face">😿</span>
          <span class="crying-tear left-tear">💧</span>
          <span class="crying-tear right-tear">💧</span>
        </div>
      `;
    }
    if (mainIcon) {
      mainIcon.classList.remove("from-cyan-600", "via-emerald-500", "to-amber-500", "from-rose-600", "via-amber-500", "to-cyan-500");
      mainIcon.classList.add("from-amber-600", "to-rose-600", "border-amber-400/50");
    }
    if (statusBadge) {
      statusBadge.className = "status-pill status-cat";
      statusBadge.innerHTML = `<span class="animate-bounce">😿</span> PUNISHMENT: 100 WAYS (100% PENALTY ACTIVE)`;
    }
  } else {
    document.body.classList.remove("punishment-cat-mode");
    if (iconInner) {
      iconInner.innerHTML = `
        <div class="dancing-cat-container" title="GRE Torture Alarm - Dancing Cat Ready">
          <span class="dancing-cat-note left-note">♪</span>
          <span class="dancing-cat-face">😸</span>
          <span class="dancing-cat-note right-note">♫</span>
        </div>
      `;
    }
    if (mainIcon) {
      mainIcon.className = "w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-emerald-500 to-amber-500 flex items-center justify-center shadow-lg shadow-cyan-600/30 font-black text-white text-lg transition-all duration-300";
    }
  }
}

function playCatPunishmentMusic() {
  stopCatPunishment();

  STATE.catRampStartTime = Date.now();
  STATE.catBlendStartTime = Date.now();

  try {
    // Play authentic "100 Ways To Love A Cat Ways 1-100.mp3"
    const audioUrl = "/audio/100%20Ways%20To%20Love%20A%20Cat%20Ways%201-100.mp3";
    STATE.catAudio = new Audio(audioUrl);
    STATE.catAudio.volume = 0.0; // Start at 0 volume for cross-fade blending
    STATE.catAudio.currentTime = 0.0;
    
    const playPromise = STATE.catAudio.play();
    if (playPromise !== undefined) {
      playPromise.catch(err => {
        console.warn("Autoplay blocked or audio load error, using synth fallback:", err);
        playFallbackCatSynth();
      });
    }
  } catch (e) {
    console.warn("Could not initialize MP3 audio, using synth fallback:", e);
    playFallbackCatSynth();
  }

  // 30-Second Audio Cross-Fade Blending and Karaoke Tracker:
  // Procedural ambient track fades down from ambientVolume to 0 while 100WTLAC blends up to 100% (1.0)
  clearInterval(STATE.catRampInterval);
  STATE.catRampInterval = setInterval(() => {
    if (STATE.current !== "CAT_PUNISHMENT") {
      stopCatPunishment();
      return;
    }

    const elapsed = (Date.now() - STATE.catRampStartTime) / 1000;
    const blendFrac = Math.min(1.0, elapsed / 30.0);

    // 100 Ways to Love a Cat: fades UP to 1.0 (100% fixed volume)
    let catTargetVolume = Math.max(0.001, blendFrac * 1.0);

    const isReprieveActive = Date.now() < (STATE.reprieveEndTime || 0);
    if (isReprieveActive) {
      catTargetVolume = Math.max(0.02, catTargetVolume * 0.12); // 88% sensory attenuation
    }

    if (STATE.catAudio && !STATE.catAudio.paused) {
      STATE.catAudio.volume = Math.max(0.0, Math.min(1.0, catTargetVolume));
    }

    // Procedural Ambient Track: cross-fades DOWN from ambientVolume to 0.0 over 30s
    if (STATE.proceduralAudio && !STATE.proceduralAudio.paused) {
      const baseAmbient = STATE.isAmbientMuted ? 0.0 : (STATE.ambientVolume ?? 0.65);
      const blendedAmbientVol = Math.max(0.0, (1.0 - blendFrac) * baseAmbient);
      STATE.proceduralAudio.volume = blendedAmbientVol;
      if (blendFrac >= 1.0) {
        stopProceduralBackgroundTrack();
      }
    }

    // Update Blend/Ramp Progress Bar & Label
    const rampElem = document.getElementById("cat-ramp-progress-bar");
    const rampText = document.getElementById("cat-ramp-text");
    if (rampElem) rampElem.style.width = `${blendFrac * 100}%`;
    if (rampText) {
      if (isReprieveActive) {
        const reprieveSecLeft = Math.ceil(((STATE.reprieveEndTime || 0) - Date.now()) / 1000);
        rampText.innerHTML = `<span class="text-emerald-300 font-bold animate-pulse">🐾 15s AUDIO REPRIEVE ACTIVE (${reprieveSecLeft}s)</span>`;
      } else {
        const remainingSec = Math.max(0, 30 - Math.round(elapsed));
        if (remainingSec > 0) {
          rampText.textContent = `Audio Blending: ${Math.round(blendFrac * 100)}% 100WTLAC / ${Math.round((1 - blendFrac) * 100)}% Ambient (${remainingSec}s)`;
        } else {
          rampText.textContent = `100% Volume (Max Felid Terror Mode)`;
        }
      }
    }

    // Synchronize Karaoke Lyrics to Audio Time
    updateKaraokeFromAudio();
  }, 100);
}

function updateKaraokeFromAudio() {
  const lyricElem = document.getElementById("cat-current-lyric");
  if (!lyricElem) return;

  const currentSeconds = (STATE.catAudio && STATE.catAudio.currentTime > 0)
    ? STATE.catAudio.currentTime
    : ((Date.now() - STATE.catRampStartTime) / 1000);

  const lyrics = STATE.catKaraokeLyrics || [];
  if (lyrics.length === 0) {
    const wayNum = Math.floor(currentSeconds / 15.36) + 1;
    lyricElem.innerHTML = `
      <div class="text-amber-400 font-bold block text-sm">100 WAYS TO LOVE A CAT · WAY #${wayNum}</div>
      <div class="text-xl font-extrabold text-white">"There are one hundred ways to love a cat..."</div>
    `;
    return;
  }

  // Find active way based on start and end timestamps
  let activeWay = lyrics.find(item => currentSeconds >= item.start_seconds && currentSeconds < item.end_seconds);
  if (!activeWay) {
    if (currentSeconds < lyrics[0].start_seconds) {
      activeWay = lyrics[0];
    } else {
      activeWay = lyrics[lyrics.length - 1];
    }
  }

  // Manifest new hidden cats (accumulating once per way up to 100)
  if (activeWay && activeWay.way_number > STATE.manifestedCatCount && STATE.hiddenCatFeatures && STATE.hiddenCatFeatures.length > 0) {
    while (STATE.manifestedCatCount < activeWay.way_number && STATE.manifestedCatCount < STATE.hiddenCatFeatures.length) {
      manifestNextCat();
    }
  }

  const mins = Math.floor(currentSeconds / 60);
  const secs = Math.floor(currentSeconds % 60);
  const timeFormatted = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

  const startT = activeWay.start_seconds;
  const actStart = activeWay.action_start_seconds;
  const actEnd = activeWay.action_end_seconds;
  const isVerseEndWay = (activeWay.way_number % 4 === 0);
  const postRefrainEnd = startT + 15.36;

  let wordsDisplayHtml = "";

  // Check 4 Phasic States:
  if (currentSeconds < actStart) {
    // -------------------------------------------------------------
    // PHASE 1: PRE-REFRAIN (4 bars / 7.68s)
    // Line 1 (bars 1-2, 0.0 - 3.84s): "There are one hundred ways to love a cat"
    // Line 2 (bars 3-4, 3.84 - 7.68s): "One hundred loving ways"
    // -------------------------------------------------------------
    const midPreRefrain = startT + 3.84;
    const isLine1Active = currentSeconds < midPreRefrain;
    const isLine2Active = !isLine1Active;

    wordsDisplayHtml = `
      <div class="my-3 text-center">
        <span class="karaoke-refrain-badge bg-amber-500/20 text-amber-300 border border-amber-500/30">
          ♪ PRE-REFRAIN · WAY #${activeWay.way_number} ♪
        </span>
        <div class="space-y-1.5 mt-1">
          <div class="text-lg md:text-xl font-bold transition-all duration-200 ${isLine1Active ? 'text-amber-300 font-extrabold scale-105' : 'text-amber-500/70'}">
            ${isLine1Active ? '<span class="inline-block animate-bounce mr-1">🐱</span>' : ''}"There are one hundred ways to love a cat"
          </div>
          <div class="text-lg md:text-xl font-bold transition-all duration-200 ${isLine2Active ? 'text-amber-300 font-extrabold scale-105' : 'text-slate-400'}">
            ${isLine2Active ? '<span class="inline-block animate-bounce mr-1">🐱</span>' : ''}"One hundred loving ways"
          </div>
        </div>
        <div class="mt-2 text-xs text-cyan-300 font-mono flex items-center justify-center gap-1.5">
          <span>Up Next:</span>
          <span class="font-bold text-white bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">${activeWay.display_lyric}</span>
        </div>
      </div>
    `;
  } else if (currentSeconds >= actStart && currentSeconds < actEnd) {
    // -------------------------------------------------------------
    // PHASE 2: ACTIVE SUNG ADVICE (Word-by-word tracking with Cat Head)
    // -------------------------------------------------------------
    const words = activeWay.words || [];
    wordsDisplayHtml = `
      <div class="my-3">
        <div class="text-center mb-1">
          <span class="karaoke-refrain-badge bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse">
            🐾 ACTIVE SUNG ADVICE (WAY #${activeWay.way_number}) 🐾
          </span>
        </div>
        <div class="karaoke-words-wrapper">
          ${words.map(w => {
            let stateClass = "future";
            let isCurrent = false;
            if (currentSeconds >= w.end) {
              stateClass = "sung";
            } else if (currentSeconds >= w.start && currentSeconds < w.end) {
              stateClass = "active";
              isCurrent = true;
            }
            return `
              <div class="karaoke-word-container ${stateClass}">
                <span class="karaoke-word">${w.word}</span>
                ${isCurrent ? '<div class="karaoke-word-cat-head">🐱</div>' : ''}
              </div>
            `;
          }).join("")}
        </div>
      </div>
    `;
  } else if (!isVerseEndWay || (isVerseEndWay && currentSeconds < postRefrainEnd)) {
    // -------------------------------------------------------------
    // PHASE 3: POST-ADVICE REFRAIN ("One hundred loving ways")
    // -------------------------------------------------------------
    wordsDisplayHtml = `
      <div class="my-3 text-center">
        <span class="karaoke-refrain-badge bg-amber-500/20 text-amber-300 border border-amber-500/30">
          ♪ POST-ADVICE REFRAIN ♪
        </span>
        <div class="text-xl md:text-2xl font-black text-amber-300 my-1 animate-pulse flex items-center justify-center gap-2">
          <span>🐱</span>
          <span>"One hundred loving ways"</span>
          <span>🐱</span>
        </div>
        <div class="text-xs text-slate-400 font-mono mt-1">
          ✓ Advice delivered: <span class="text-slate-200 font-bold">${activeWay.display_lyric}</span>
        </div>
      </div>
    `;
  } else {
    // -------------------------------------------------------------
    // PHASE 4: VERSE CHORUS REFRAIN (8 bars / 16 beats: 4 lines)
    // Occurs after Way 4, 8, 12, 16, 20, etc.
    // -------------------------------------------------------------
    const chorusStart = postRefrainEnd;
    const chorusElapsed = Math.max(0, currentSeconds - chorusStart);
    const lineSlot = Math.min(3, Math.floor(chorusElapsed / 3.84));

    const chorusLines = [
      "One hundred loving ways",
      "One hundred loving ways",
      "One hundred loving ways",
      "One hundred loving ways"
    ];

    wordsDisplayHtml = `
      <div class="my-2 text-center">
        <span class="karaoke-refrain-badge bg-amber-400/20 text-amber-300 border border-amber-400/40">
          ♪ VERSE ${activeWay.verse_index} CHORUS REFRAIN ♪
        </span>
        <div class="karaoke-chorus-grid">
          ${chorusLines.map((line, idx) => {
            let lineState = "future";
            if (idx < lineSlot) lineState = "sung";
            else if (idx === lineSlot) lineState = "active";
            return `
              <div class="karaoke-chorus-line ${lineState}">
                ${idx === lineSlot ? '<span class="animate-bounce">🐱</span>' : '<span class="text-xs opacity-50">#' + (idx + 1) + '</span>'}
                <span>"${line}"</span>
              </div>
            `;
          }).join("")}
        </div>
        <div class="text-xs text-slate-400 font-mono mt-2">
          Next Verse: <strong class="text-amber-300">Way ${activeWay.way_number + 1}</strong> starting shortly...
        </div>
      </div>
    `;
  }

  lyricElem.innerHTML = `
    <div class="flex items-center justify-between text-xs text-amber-400 font-mono mb-2 pb-1 border-b border-amber-500/20">
      <span class="font-bold tracking-wider">WAY #${activeWay.way_number} OF 100 (VERSE ${activeWay.verse_index}/25)</span>
      <span class="bg-amber-500/10 px-2.5 py-0.5 rounded text-amber-300 border border-amber-500/30">AUDIO: ${timeFormatted} / 35:21</span>
    </div>

    ${wordsDisplayHtml}

    <div class="text-[11px] text-slate-400 font-mono mt-2 pt-1 border-t border-slate-800 flex items-center justify-between">
      <span class="text-amber-300 font-bold">🐱 Bouncing Cat Head below each active word</span>
      <span class="text-slate-400">Up Next: Way ${Math.min(100, activeWay.way_number + 1)}</span>
    </div>
  `;
}

// ==============================================================
// 100 HIDDEN CATS PHYSICS ENGINE (PAGE-TIED 2D MOTION)
// Bouncing off page walls, panels, and each other in document space
// ==============================================================
let physicsLoopRunning = false;
let physicsLastTime = 0;
let cachedObstacleBoxes = [];
let cachedDocW = 1200;
let cachedDocH = 900;
let lastDocBoundsTime = 0;

function computeContentDimensions() {
  const footer = document.querySelector("footer");
  const main = document.querySelector("main");
  let contentBottom = window.innerHeight;
  if (footer) {
    contentBottom = Math.max(contentBottom, footer.offsetTop + footer.offsetHeight);
  } else if (main) {
    contentBottom = Math.max(contentBottom, main.offsetTop + main.offsetHeight + 40);
  } else {
    contentBottom = Math.max(document.documentElement.clientHeight || window.innerHeight, window.innerHeight);
  }
  const contentWidth = Math.max(document.documentElement.clientWidth || window.innerWidth, window.innerWidth);
  return { width: contentWidth, height: contentBottom };
}

function smoothlyRepositionCatsOnResize(oldW, oldH, newW, newH) {
  if (!STATE.bouncingCats || STATE.bouncingCats.length === 0) return;
  if (!oldW || !oldH || !newW || !newH) return;

  const scaleX = newW / oldW;
  const scaleY = newH / oldH;

  for (let i = 0; i < STATE.bouncingCats.length; i++) {
    const c = STATE.bouncingCats[i];
    if (!c) continue;

    // Scale coordinates proportionally to preserve layout distribution
    c.x = c.x * scaleX;
    c.y = c.y * scaleY;

    // Keep within safe document margins
    const minX = c.radius + 10;
    const maxX = Math.max(minX, newW - c.radius - 10);
    const minY = c.radius + 50; // Below header
    const maxY = Math.max(minY, newH - c.radius - 15);

    // If caught near rising floor, impart an upward bounce impulse
    if (c.y >= maxY - 20) {
      c.y = maxY;
      c.vy = -Math.max(0.8, Math.abs(c.vy) * 1.15); // Smooth upward bounce
    } else if (c.y <= minY + 10) {
      c.y = minY;
      c.vy = Math.max(0.8, Math.abs(c.vy) * 1.15); // Smooth downward bounce
    }

    if (c.x >= maxX - 15) {
      c.x = maxX;
      c.vx = -Math.max(0.8, Math.abs(c.vx) * 1.15);
    } else if (c.x <= minX + 15) {
      c.x = minX;
      c.vx = Math.max(0.8, Math.abs(c.vx) * 1.15);
    }

    // Apply immediate transform to prevent visual hitching or teleportation
    if (c.el) {
      c.el.style.transform = `translate3d(${(c.x - c.radius).toFixed(1)}px, ${(c.y - c.radius).toFixed(1)}px, 0)`;
    }
  }
}

function updateDocBounds() {
  const { width: newW, height: newH } = computeContentDimensions();
  const oldW = cachedDocW || newW;
  const oldH = cachedDocH || newH;

  cachedDocW = newW;
  cachedDocH = newH;

  const layer = document.getElementById("hidden-cats-manifest-layer");
  if (layer) {
    layer.style.width = `${newW}px`;
    layer.style.height = `${newH}px`;
  }

  // Smoothly reposition all bouncing cat particles when document dimensions shift
  if (oldH > 0 && oldW > 0 && (Math.abs(newH - oldH) > 4 || Math.abs(newW - oldW) > 4)) {
    smoothlyRepositionCatsOnResize(oldW, oldH, newW, newH);
  }
}

function setupDynamicResizeObservers() {
  if (typeof ResizeObserver === "undefined") return;

  const observer = new ResizeObserver(() => {
    updateDocBounds();
    cachedObstacleBoxes = getPanelDocumentBoxes();
  });

  const main = document.querySelector("main");
  if (main) observer.observe(main);

  const questionCard = document.getElementById("question-card-container");
  if (questionCard) observer.observe(questionCard);

  const quizPanel = document.getElementById("panel-quiz-solving");
  if (quizPanel) observer.observe(quizPanel);
}

function initCatPhysics() {
  updateDocBounds();
  setupDynamicResizeObservers();
  cachedObstacleBoxes = getPanelDocumentBoxes();

  // Only run the animation frame loop when cat particles actually exist
  if (STATE.bouncingCats.length > 0 && !physicsLoopRunning) {
    physicsLoopRunning = true;
    physicsLastTime = performance.now();
    requestAnimationFrame(physicsStep);
  }

  window.addEventListener("resize", () => {
    updateDocBounds();
    cachedObstacleBoxes = getPanelDocumentBoxes();
  });
}

function getPanelDocumentBoxes() {
  const panels = document.querySelectorAll("header, #top-tracker-banner, .glass-panel, #alarm-ringing-card, #alarm-trigger-section");
  const boxes = [];
  const scrollX = window.scrollX || window.pageXOffset || 0;
  const scrollY = window.scrollY || window.pageYOffset || 0;

  panels.forEach(p => {
    if (p.id === "modal-cat-menagerie") return;
    if (p.offsetParent === null) return;
    if (p.classList.contains("hidden")) return;

    const r = p.getBoundingClientRect();
    if (r.width > 20 && r.height > 20) {
      boxes.push({
        left: r.left + scrollX,
        top: r.top + scrollY,
        right: r.right + scrollX,
        bottom: r.bottom + scrollY
      });
    }
  });
  return boxes;
}

function physicsStep(now) {
  if (!physicsLoopRunning) return;

  // Sleep the animation frame loop when particle count is 0 (avoids waking idle GPU/CPU)
  if (STATE.bouncingCats.length === 0) {
    physicsLoopRunning = false;
    return;
  }

  const dt = Math.min(32, Math.max(8, now - physicsLastTime)) / 16.666;
  physicsLastTime = now;

  // Throttled document and obstacle bounds query (once every 1000ms) to eliminate DOM layout thrashing
  if (now - lastDocBoundsTime > 1000) {
    updateDocBounds();
    cachedObstacleBoxes = getPanelDocumentBoxes();
    lastDocBoundsTime = now;
  }

  const docW = cachedDocW;
  const docH = cachedDocH;

  const cats = STATE.bouncingCats;
  const n = cats.length;

  // 1. Move and Wall Collisions (Document Boundaries)
  for (let i = 0; i < n; i++) {
    const c = cats[i];
    c.x += c.vx * dt;
    c.y += c.vy * dt;

    // Document Left / Right Walls
    if (c.x - c.radius < 5) {
      c.x = c.radius + 5;
      c.vx = Math.abs(c.vx);
    } else if (c.x + c.radius > docW - 5) {
      c.x = docW - c.radius - 5;
      c.vx = -Math.abs(c.vx);
    }

    // Document Top / Bottom Walls
    if (c.y - c.radius < 5) {
      c.y = c.radius + 5;
      c.vy = Math.abs(c.vy);
    } else if (c.y + c.radius > docH - 5) {
      c.y = docH - c.radius - 5;
      c.vy = -Math.abs(c.vy);
    }

    // 2. Obstacle Panels Collisions
    for (let p = 0; p < cachedObstacleBoxes.length; p++) {
      const box = cachedObstacleBoxes[p];
      const cx = Math.max(box.left, Math.min(c.x, box.right));
      const cy = Math.max(box.top, Math.min(c.y, box.bottom));
      const dx = c.x - cx;
      const dy = c.y - cy;
      const d2 = dx * dx + dy * dy;

      if (d2 < c.radius * c.radius) {
        const d = Math.sqrt(d2);
        if (d > 0.001) {
          const nx = dx / d;
          const ny = dy / d;
          c.x = cx + nx * c.radius;
          c.y = cy + ny * c.radius;
          const dot = c.vx * nx + c.vy * ny;
          if (dot < 0) {
            c.vx = c.vx - 2 * dot * nx;
            c.vy = c.vy - 2 * dot * ny;
          }
        } else {
          // Centered inside box: eject to nearest edge
          const dLeft = Math.abs(c.x - box.left);
          const dRight = Math.abs(box.right - c.x);
          const dTop = Math.abs(c.y - box.top);
          const dBottom = Math.abs(box.bottom - c.y);
          const minD = Math.min(dLeft, dRight, dTop, dBottom);
          if (minD === dLeft) { c.x = box.left - c.radius; c.vx = -Math.abs(c.vx); }
          else if (minD === dRight) { c.x = box.right + c.radius; c.vx = Math.abs(c.vx); }
          else if (minD === dTop) { c.y = box.top - c.radius; c.vy = -Math.abs(c.vy); }
          else { c.y = box.bottom + c.radius; c.vy = Math.abs(c.vy); }
        }
      }
    }
  }

  // 3. Inter-Cat Elastic Collisions (O(N^2))
  for (let i = 0; i < n; i++) {
    const ci = cats[i];
    for (let j = i + 1; j < n; j++) {
      const cj = cats[j];
      const dx = cj.x - ci.x;
      const dy = cj.y - ci.y;
      const minDist = ci.radius + cj.radius;
      const d2 = dx * dx + dy * dy;

      if (d2 < minDist * minDist && d2 > 0.0001) {
        const d = Math.sqrt(d2);
        const nx = dx / d;
        const ny = dy / d;

        // Separate overlapping particles
        const overlap = 0.5 * (minDist - d);
        ci.x -= nx * overlap;
        ci.y -= ny * overlap;
        cj.x += nx * overlap;
        cj.y += ny * overlap;

        // Normal relative velocity
        const kx = ci.vx - cj.vx;
        const ky = ci.vy - cj.vy;
        const p = (nx * kx + ny * ky);

        if (p > 0) {
          ci.vx -= p * nx;
          ci.vy -= p * ny;
          cj.vx += p * nx;
          cj.vy += p * ny;
        }
      }
    }
  }

  // 4. Speed Clamping & Apply Page Coordinates to DOM
  for (let i = 0; i < n; i++) {
    const c = cats[i];
    const spd = Math.sqrt(c.vx * c.vx + c.vy * c.vy);
    if (spd < 0.7) {
      c.vx = (c.vx / (spd || 1)) * 0.9;
      c.vy = (c.vy / (spd || 1)) * 0.9;
    } else if (spd > 3.0) {
      c.vx = (c.vx / spd) * 3.0;
      c.vy = (c.vy / spd) * 3.0;
    }

    // Tied to page position via translate3d
    c.el.style.transform = `translate3d(${(c.x - c.radius).toFixed(1)}px, ${(c.y - c.radius).toFixed(1)}px, 0)`;
  }

  requestAnimationFrame(physicsStep);
}

// Manifest 100 Hidden Cats (Accumulating 1 per way; 100% feline icons, cutesy first 15, spooky unlocked after 15)
function manifestNextCat() {
  if (!STATE.hiddenCatFeatures || STATE.manifestedCatCount >= STATE.hiddenCatFeatures.length) return;
  const cat = STATE.hiddenCatFeatures[STATE.manifestedCatCount];
  STATE.manifestedCatCount++;
  STATE.manifestedCats.push(cat);

  // Update Floating HUD Pill
  const pill = document.getElementById("hidden-cats-counter-pill");
  const countText = document.getElementById("manifested-count-text");
  const typeBadge = document.getElementById("manifested-type-badge");
  const latestName = document.getElementById("manifested-latest-name");
  
  if (pill) pill.classList.remove("hidden");
  if (countText) countText.textContent = `${STATE.manifestedCatCount} / 100 Felines`;
  if (typeBadge) {
    if (cat.type === "spooky") {
      typeBadge.className = "px-1.5 py-0.2 rounded text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse font-bold";
      typeBadge.textContent = "SPOOKY";
    } else {
      typeBadge.className = "px-1.5 py-0.2 rounded text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold";
      typeBadge.textContent = "CUTESY";
    }
  }
  if (latestName) latestName.textContent = `#${cat.way_unlock}: ${cat.name}`;

  // Add visual element to manifestation overlay layer
  const layer = document.getElementById("hidden-cats-manifest-layer");
  if (!layer) return;

  const el = document.createElement("div");
  el.className = `manifested-cat-item ${cat.type === 'spooky' ? 'manifested-spooky' : 'manifested-cutesy'}`;
  el.setAttribute("title", `[${cat.type.toUpperCase()}] Way #${cat.way_unlock}: ${cat.name}\n${cat.description}`);
  el.innerHTML = cat.icon;

  el.addEventListener("click", (e) => {
    e.stopPropagation();
    showToast(`${cat.type === 'spooky' ? '⚠️ SPOOKY' : '🐾 CUTESY'} #${cat.way_unlock} [${cat.name}]: ${cat.description}`, cat.type === 'spooky' ? 'crimson' : 'amber');
  });

  // Calculate spawn position in page coordinates
  const scrollY = window.scrollY || window.pageYOffset || 0;
  const viewH = window.innerHeight;
  const viewW = window.innerWidth;
  const docW = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth, viewW);
  const docH = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, viewH);

  let spawnX, spawnY;
  const side = STATE.manifestedCatCount % 4;
  if (side === 0) { // top margin
    spawnX = Math.random() * (docW - 80) + 40;
    spawnY = Math.max(30, scrollY + 40 + Math.random() * 50);
  } else if (side === 1) { // right margin
    spawnX = docW - 50 - Math.random() * 40;
    spawnY = Math.max(40, Math.min(docH - 60, scrollY + Math.random() * (viewH - 120) + 50));
  } else if (side === 2) { // bottom margin
    spawnX = Math.random() * (docW - 80) + 40;
    spawnY = Math.min(docH - 50, scrollY + viewH - 80 - Math.random() * 40);
  } else { // left margin
    spawnX = 30 + Math.random() * 40;
    spawnY = Math.max(40, Math.min(docH - 60, scrollY + Math.random() * (viewH - 120) + 50));
  }

  const angle = Math.random() * Math.PI * 2;
  const speed = 1.0 + Math.random() * 1.4;
  let vx = Math.cos(angle) * speed;
  let vy = Math.sin(angle) * speed;
  if (Math.abs(vx) < 0.5) vx = vx >= 0 ? 0.8 : -0.8;
  if (Math.abs(vy) < 0.5) vy = vy >= 0 ? 0.8 : -0.8;

  const radius = cat.type === "spooky" ? 22 : 18;

  const catParticle = {
    id: cat.way_unlock,
    catData: cat,
    el: el,
    x: spawnX,
    y: spawnY,
    vx: vx,
    vy: vy,
    radius: radius,
    mass: radius
  };

  STATE.bouncingCats.push(catParticle);
  layer.appendChild(el);

  // Awaken physics loop if it was asleep
  if (!physicsLoopRunning) {
    physicsLoopRunning = true;
    physicsLastTime = performance.now();
    requestAnimationFrame(physicsStep);
  }
}

function openMenagerieModal() {
  const modal = document.getElementById("modal-cat-menagerie");
  const listContainer = document.getElementById("menagerie-list-container");
  const badge = document.getElementById("modal-manifest-badge");
  if (!modal || !listContainer) return;

  badge.textContent = `${STATE.manifestedCatCount} / 100`;

  if (STATE.manifestedCats.length === 0) {
    listContainer.innerHTML = `
      <div class="py-12 text-center text-slate-500">
        <span class="text-3xl block mb-2">🐾</span>
        No felines have manifested yet. They emerge once per way as "100 Ways to Love a Cat" plays!
      </div>
    `;
  } else {
    listContainer.innerHTML = STATE.manifestedCats.map(cat => `
      <div class="p-3 rounded-xl border flex items-center justify-between gap-3 ${cat.type === 'spooky' ? 'bg-rose-950/20 border-rose-500/40 text-rose-200' : 'bg-slate-900/60 border-slate-800 text-slate-200'}">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 flex-shrink-0 flex items-center justify-center">${cat.icon}</div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-bold text-white">#${cat.way_unlock} ${cat.name}</span>
              <span class="px-1.5 py-0.2 rounded text-[10px] uppercase font-bold ${cat.type === 'spooky' ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'}">${cat.type}</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-0.5">${cat.description}</p>
          </div>
        </div>
        <span class="text-[10px] text-slate-500 font-mono">Way ${cat.way_unlock}</span>
      </div>
    `).reverse().join("");
  }

  modal.classList.remove("hidden");
  // Render KaTeX for top bar subtitle and any mathematical notations in the modal
  renderLaTeX(modal);
}

function closeMenagerieModal() {
  document.getElementById("modal-cat-menagerie")?.classList.add("hidden");
}

function clearHiddenCats() {
  physicsLoopRunning = false;
  STATE.manifestedCatCount = 0;
  STATE.manifestedCats = [];
  STATE.bouncingCats = [];
  const layer = document.getElementById("hidden-cats-manifest-layer");
  if (layer) layer.innerHTML = "";
  const pill = document.getElementById("hidden-cats-counter-pill");
  if (pill) pill.classList.add("hidden");
  closeMenagerieModal();
}

function playFallbackCatSynth() {
  if (!STATE.audioCtx) {
    STATE.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  const ctx = STATE.audioCtx;
  if (ctx.state === "suspended") ctx.resume();

  const masterGain = ctx.createGain();
  masterGain.gain.setValueAtTime(0.001, ctx.currentTime);
  masterGain.gain.exponentialRampToValueAtTime(1.0, ctx.currentTime + 30.0); // Fixed 100% volume
  masterGain.connect(ctx.destination);
  STATE.catAudioNodes.push(masterGain);

  const chords = [
    [261.63, 329.63, 392.00], // C
    [196.00, 246.94, 293.66], // G
    [220.00, 261.63, 329.63], // Am
    [174.61, 220.00, 261.63]  // F
  ];
  let chordStep = 0;
  const catInterval = setInterval(() => {
    if (STATE.current !== "CAT_PUNISHMENT") {
      clearInterval(catInterval);
      return;
    }
    const t = ctx.currentTime;
    const currentChord = chords[chordStep % chords.length];
    chordStep++;
    currentChord.forEach(freq => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq * 2, t);
      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.45);
      osc.connect(gain);
      gain.connect(masterGain);
      osc.start(t);
      osc.stop(t + 0.45);
    });
  }, 480);
  STATE.catAudioNodes.push({ stop: () => clearInterval(catInterval) });
}

function stopCatPunishment() {
  clearInterval(STATE.catRampInterval);

  if (STATE.catAudio) {
    try {
      STATE.catAudio.pause();
      STATE.catAudio.currentTime = 0;
    } catch (e) {}
    STATE.catAudio = null;
  }

  STATE.catAudioNodes.forEach(n => {
    try {
      if (typeof n.stop === "function") n.stop();
      if (typeof n.disconnect === "function") n.disconnect();
    } catch (e) {}
  });
  STATE.catAudioNodes = [];
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
}

// ==========================================
// VICTORY ENGINE
// ==========================================
function triggerVictory() {
  STATE.current = "VICTORY";
  stopRTGAlarmTone();
  stopCatPunishment();
  stopProceduralBackgroundTrack();
  clearInterval(STATE.quizInterval);

  setCryingCatIcon(false);

  renderState();
  showToast("VICTORY! 100 Points Accumulated. You are awake and GRE-ready!", "emerald");

  // Fill victory summary
  const summaryElem = document.getElementById("victory-summary");
  if (summaryElem) {
    const elapsed = Math.round((Date.now() - STATE.lastInteractionTime) / 1000);
    summaryElem.innerHTML = `
      <div class="text-emerald-400 text-3xl font-black mb-1">100+ POINTS REACHED!</div>
      <p class="text-sm text-slate-300">All alarms and punishments neutralized. Your mind is fully conscious.</p>
      <div class="grid grid-cols-2 gap-3 mt-4 text-xs font-mono">
        <div class="bg-slate-900/80 p-3 rounded-lg border border-emerald-500/30">
          <span class="text-slate-400 block">Final Score</span>
          <span class="text-xl font-bold text-emerald-400">${STATE.currentPoints} PTS</span>
        </div>
        <div class="bg-slate-900/80 p-3 rounded-lg border border-slate-700">
          <span class="text-slate-400 block">Questions Solved</span>
          <span class="text-xl font-bold text-white">${STATE.answeredQuestions.length}</span>
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <button id="btn-victory-view-stats" type="button" class="py-2 px-4 rounded-xl font-bold bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono shadow-md shadow-cyan-600/30 transition">
          📊 View Complete Session Statistics
        </button>
      </div>
    `;
    document.getElementById("btn-victory-view-stats")?.addEventListener("click", () => openSessionStatisticsModal("VICTORY"));
  }
}

function resetToIdle() {
  stopRTGAlarmTone();
  stopCatPunishment();
  stopProceduralBackgroundTrack();
  clearInterval(STATE.quizInterval);

  setCryingCatIcon(false);
  clearHiddenCats();

  STATE.current = "IDLE";
  STATE.isArmed = false;
  STATE.currentPoints = 0;
  STATE.quizStartTime = null;
  STATE.answeredQuestions = [];
  renderState();
  showToast("Alarm System Reset to Idle.", "slate");

  // Reset server state & points to prevent bleeding across sessions
  fetch("/api/disarm", { method: "POST" }).catch(() => {});
}

function endStudySessionMaxDuration() {
  stopRTGAlarmTone();
  stopCatPunishment();
  stopProceduralBackgroundTrack();
  clearInterval(STATE.quizInterval);

  setCryingCatIcon(false);
  clearHiddenCats();

  // Reset to initial state
  STATE.current = "IDLE";
  STATE.isArmed = false;
  renderState();

  // Reset server state & points
  fetch("/api/disarm", { method: "POST" }).catch(() => {});

  // Display comprehensive session statistics modal
  openSessionStatisticsModal("MAX_DURATION");
  showToast("⏰ Max study duration reached! Alarm disarmed & session statistics rendered.", "cyan");
}

function openSessionStatisticsModal(reason = "MAX_DURATION") {
  const modal = document.getElementById("modal-session-statistics");
  if (!modal) return;

  // Header reason badge
  const reasonPill = document.getElementById("stats-session-reason-pill");
  const subtitle = document.getElementById("stats-session-subtitle");
  if (reasonPill) {
    if (reason === "MAX_DURATION") {
      reasonPill.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40";
      reasonPill.textContent = "MAX DURATION ELAPSED";
      if (subtitle) subtitle.textContent = `Completed ${STATE.maxStudyDurationMinutes || 20}-minute study session limit. Initial state restored.`;
    } else if (reason === "VICTORY") {
      reasonPill.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40";
      reasonPill.textContent = "VICTORY 100+ PTS REACHED";
      if (subtitle) subtitle.textContent = "All alarms and punishments neutralized. Your mind is fully conscious.";
    } else {
      reasonPill.className = "text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40";
      reasonPill.textContent = "SESSION COMPLETED";
      if (subtitle) subtitle.textContent = "Comprehensive performance breakdown & cognitive arousal metrics";
    }
  }

  // Calculate elapsed session time
  let elapsedSec = 0;
  if (STATE.studySessionStartTime) {
    elapsedSec = Math.max(0, Math.round((Date.now() - STATE.studySessionStartTime) / 1000));
  }
  const mins = Math.floor(elapsedSec / 60);
  const secs = elapsedSec % 60;
  const timeStr = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

  const timeEl = document.getElementById("stats-total-time");
  if (timeEl) timeEl.textContent = timeStr;

  // Questions and Accuracy
  const questions = STATE.answeredQuestions || [];
  const totalCount = questions.length;
  const correctCount = questions.filter(q => q.is_correct).length;
  const accuracyPct = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;

  const countEl = document.getElementById("stats-questions-count");
  if (countEl) countEl.textContent = String(totalCount);

  const accEl = document.getElementById("stats-accuracy-pct");
  if (accEl) {
    accEl.textContent = `${accuracyPct}%`;
    accEl.className = `text-xl font-black mt-1 block ${accuracyPct >= 70 ? 'text-emerald-400' : (accuracyPct >= 40 ? 'text-amber-400' : 'text-rose-400')}`;
  }

  const scoreEl = document.getElementById("stats-final-score");
  if (scoreEl) {
    scoreEl.textContent = `${STATE.currentPoints} PTS`;
    scoreEl.className = `text-xl font-black mt-1 block ${STATE.currentPoints >= 100 ? 'text-emerald-400' : 'text-amber-300'}`;
  }

  // Subtypes Breakdown
  const breakdownContainer = document.getElementById("stats-subtypes-breakdown");
  if (breakdownContainer) {
    if (questions.length === 0) {
      breakdownContainer.innerHTML = `<div class="text-slate-500 italic py-2">No question submissions recorded in this study session.</div>`;
    } else {
      const groups = {};
      questions.forEach(q => {
        const key = q.subtype || q.type || "General Question";
        if (!groups[key]) groups[key] = { attempted: 0, correct: 0 };
        groups[key].attempted++;
        if (q.is_correct) groups[key].correct++;
      });

      breakdownContainer.innerHTML = Object.entries(groups).map(([name, data]) => {
        const pct = Math.round((data.correct / data.attempted) * 100);
        const barColor = pct >= 80 ? "bg-emerald-400" : (pct >= 50 ? "bg-cyan-400" : "bg-rose-400");
        return `
          <div class="flex items-center justify-between py-1.5 border-b border-slate-800/40">
            <div class="flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full ${barColor}"></span>
              <span class="font-bold text-slate-200">${name}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-slate-400 font-mono">${data.correct}/${data.attempted} (${pct}%)</span>
              <div class="w-20 bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                <div class="${barColor} h-full transition-all duration-300" style="width: ${pct}%"></div>
              </div>
            </div>
          </div>
        `;
      }).join("");
    }
  }

  // Cognitive Readiness
  const readinessLvl = document.getElementById("stats-readiness-level");
  const readinessDesc = document.getElementById("stats-readiness-desc");
  if (readinessLvl && readinessDesc) {
    if (STATE.currentPoints >= 100) {
      readinessLvl.textContent = "Optimal ETS Alertness (Disarmed)";
      readinessDesc.textContent = "Prefrontal cortex fully stimulated and active. Verbal and quantitative reasoning neural circuits are primed for test day.";
      readinessLvl.className = "text-sm font-bold text-emerald-400 mb-1";
    } else if (totalCount >= 4 && accuracyPct >= 65) {
      readinessLvl.textContent = "High Sensory Arousal (Calibrated)";
      readinessDesc.textContent = "Auditory aversion stimuli and rapid problem-solving successfully neutralized morning sleep inertia.";
      readinessLvl.className = "text-sm font-bold text-cyan-300 mb-1";
    } else if (totalCount > 0) {
      readinessLvl.textContent = "Moderate Arousal (Warming Up)";
      readinessDesc.textContent = "Awake and responsive, cognitive faculties continuing to ramp. Additional practice recommended.";
      readinessLvl.className = "text-sm font-bold text-amber-300 mb-1";
    } else {
      readinessLvl.textContent = "Sensory Activation Initialized";
      readinessDesc.textContent = "Alarm sounded; session concluded before question completions were registered.";
      readinessLvl.className = "text-sm font-bold text-slate-300 mb-1";
    }
  }

  // Feline Menagerie Status
  const menagerieLvl = document.getElementById("stats-menagerie-level");
  const menagerieDesc = document.getElementById("stats-menagerie-desc");
  if (menagerieLvl && menagerieDesc) {
    menagerieLvl.textContent = `${STATE.manifestedCatCount} / 100 Felines Encountered`;
    if (STATE.manifestedCatCount === 0) {
      menagerieDesc.textContent = "Pristine run! You answered questions swiftly enough to prevent feline manifestation assault.";
    } else {
      const spooky = (STATE.manifestedCats || []).filter(c => c.type === "spooky").length;
      const cutesy = (STATE.manifestedCats || []).filter(c => c.type !== "spooky").length;
      menagerieDesc.textContent = `${STATE.manifestedCatCount} bouncy felines escaped into the menagerie (${spooky} Spooky, ${cutesy} Cutesy).`;
    }
  }

  modal.classList.remove("hidden");
}

function closeSessionStatisticsModal() {
  const modal = document.getElementById("modal-session-statistics");
  if (modal) modal.classList.add("hidden");
}

// ==========================================
// GRE QUESTIONS & SCORING
// ==========================================
async function fetchNextQuestion() {
  const container = document.getElementById("question-card-container");
  if (container) {
    container.innerHTML = `
      <div class="py-12 flex flex-col items-center justify-center text-slate-400">
        <div class="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-3"></div>
        <span class="text-xs font-mono uppercase tracking-wider">Fetching Calibrated GRE Question...</span>
      </div>
    `;
  }

  try {
    const res = await fetch("/api/question/next");
    if (!res.ok) throw new Error("API call failed");
    const q = await res.json();
    STATE.currentQuestion = q;
    renderQuestion(q);
  } catch (e) {
    // Fallback bundled question
    const fallbackQ = {
      id: "gre_local_01",
      section: "Verbal Reasoning",
      subtype: "Text Completion (1 Blank)",
      difficulty: "medium",
      point_value: 21,
      penalty_value: 11,
      question: "Though the volume of radioactive waste produced by nuclear power plants is _____, the problem of how to dispose of that waste safely remains critical.",
      options: [
        { label: "A", text: "miniscule" },
        { label: "B", text: "hazardous" },
        { label: "C", text: "unmanageable" },
        { label: "D", text: "prolific" },
        { label: "E", text: "exorbitant" }
      ],
      correct_answer: ["A"],
      explanation: "The word 'Though' establishes contrast between the small volume and the critical disposal problem. 'Miniscule' fits."
    };
    STATE.currentQuestion = fallbackQ;
    renderQuestion(fallbackQ);
  }
}

function formatPassageParagraphs(text) {
  if (!text) return "";
  // Split on double newlines or single newlines
  const paragraphs = text.split(/\n\s*\n|\r\n\s*\r\n/);
  if (paragraphs.length > 1) {
    return paragraphs.map(p => `<p class="mb-4">${p.trim()}</p>`).join("");
  }
  const lines = text.split(/\n|\r\n/);
  if (lines.length > 2) {
    return lines.map(line => `<p class="mb-3">${line.trim()}</p>`).join("");
  }
  return `<p>${text.trim()}</p>`;
}

function adjustPassageFontSize(delta) {
  STATE.passageFontSize = Math.min(26, Math.max(13, (STATE.passageFontSize || 17) + delta));
  const box = document.getElementById("passage-content-box");
  const indicator = document.getElementById("font-size-indicator");
  if (box) {
    box.style.fontSize = `${STATE.passageFontSize}px`;
    box.style.lineHeight = `${Math.min(2.1, 1.85 + (STATE.passageFontSize - 17) * 0.02)}`;
  }
  if (indicator) {
    indicator.textContent = `${STATE.passageFontSize}px`;
  }
}
window.adjustPassageFontSize = adjustPassageFontSize;

function renderQuestion(q) {
  const container = document.getElementById("question-card-container");
  if (!container) return;

  const hasPassage = Boolean(q.passage);
  const is3Blanks = q.subtype.includes("3 Blanks");
  const is2Blanks = q.subtype.includes("2 Blanks");
  const isSE = q.subtype.includes("Sentence Equivalence");

  let optionsHtml = "";

  if (is3Blanks || is2Blanks) {
    // Group options by blank
    const blank1 = q.options.filter(o => o.blank === 1);
    const blank2 = q.options.filter(o => o.blank === 2);
    const blank3 = q.options.filter(o => o.blank === 3);

    optionsHtml = `
      <div id="question-options-container" class="grid grid-cols-1 md:grid-cols-${is3Blanks ? 3 : 2} gap-4 mt-4">
        <div id="blank-box-1" class="blank-choice-box bg-slate-900/60 p-3 rounded-xl border border-slate-800 transition-all">
          <div class="text-xs font-mono font-bold text-cyan-400 mb-2 uppercase flex items-center justify-between">
            <span>Blank (i)</span>
            <span class="blank-status text-[10px] text-slate-500 font-normal">Unselected</span>
          </div>
          <div class="space-y-2">
            ${blank1.map(o => `
              <label class="quiz-option flex items-center gap-2 p-2 rounded-lg bg-slate-800/40 hover:bg-slate-800 border border-slate-700/50 cursor-pointer text-xs transition-all">
                <input type="radio" name="blank_1" value="${o.label}" class="text-cyan-500">
                <span class="quiz-option-badge w-5 h-5 rounded flex items-center justify-center font-bold text-cyan-300 font-mono text-[11px]">${o.label}</span>
                <span class="text-slate-200">${o.text}</span>
              </label>
            `).join("")}
          </div>
        </div>

        <div id="blank-box-2" class="blank-choice-box bg-slate-900/60 p-3 rounded-xl border border-slate-800 transition-all">
          <div class="text-xs font-mono font-bold text-cyan-400 mb-2 uppercase flex items-center justify-between">
            <span>Blank (ii)</span>
            <span class="blank-status text-[10px] text-slate-500 font-normal">Unselected</span>
          </div>
          <div class="space-y-2">
            ${blank2.map(o => `
              <label class="quiz-option flex items-center gap-2 p-2 rounded-lg bg-slate-800/40 hover:bg-slate-800 border border-slate-700/50 cursor-pointer text-xs transition-all">
                <input type="radio" name="blank_2" value="${o.label}" class="text-cyan-500">
                <span class="quiz-option-badge w-5 h-5 rounded flex items-center justify-center font-bold text-cyan-300 font-mono text-[11px]">${o.label}</span>
                <span class="text-slate-200">${o.text}</span>
              </label>
            `).join("")}
          </div>
        </div>

        ${is3Blanks ? `
        <div id="blank-box-3" class="blank-choice-box bg-slate-900/60 p-3 rounded-xl border border-slate-800 transition-all">
          <div class="text-xs font-mono font-bold text-cyan-400 mb-2 uppercase flex items-center justify-between">
            <span>Blank (iii)</span>
            <span class="blank-status text-[10px] text-slate-500 font-normal">Unselected</span>
          </div>
          <div class="space-y-2">
            ${blank3.map(o => `
              <label class="quiz-option flex items-center gap-2 p-2 rounded-lg bg-slate-800/40 hover:bg-slate-800 border border-slate-700/50 cursor-pointer text-xs transition-all">
                <input type="radio" name="blank_3" value="${o.label}" class="text-cyan-500">
                <span class="quiz-option-badge w-5 h-5 rounded flex items-center justify-center font-bold text-cyan-300 font-mono text-[11px]">${o.label}</span>
                <span class="text-slate-200">${o.text}</span>
              </label>
            `).join("")}
          </div>
        </div>
        ` : ""}
      </div>
    `;
  } else {
    // Single Choice OR Multi-Select (Sentence Equivalence, Reading Comp multi-select, Quant multi-select)
    const isMultiSelect = Boolean(q.is_multi_select) || isSE || (Array.isArray(q.correct_answer) && q.correct_answer.length > 1) || (q.question && (q.question.toLowerCase().includes("select all") || q.question.toLowerCase().includes("indicate all")));
    const inputType = isMultiSelect ? "checkbox" : "radio";

    let helperHeader = "";
    if (isSE) {
      helperHeader = `
        <div id="se-counter-container" class="text-xs font-mono text-amber-300 mb-2 flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
            <span>Sentence Equivalence: Select EXACTLY TWO choices:</span>
          </div>
          <span id="se-count-badge" class="font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">0 of 2 selected</span>
        </div>
      `;
    } else if (isMultiSelect) {
      helperHeader = `<div class="text-xs font-mono text-cyan-300 mb-2 flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span> Select ALL choices that apply (one or more choices may be correct):</div>`;
    } else {
      helperHeader = `<div class="text-xs font-mono text-slate-400 mb-2">Select ONE answer choice:</div>`;
    }

    optionsHtml = `
      <div id="question-options-container" class="grid grid-cols-1 gap-2 mt-4">
        ${helperHeader}
        ${q.options.map(o => `
          <label class="quiz-option flex items-center gap-3 p-3 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-600 cursor-pointer transition-all">
            <input type="${inputType}" name="choice" value="${o.label}" class="w-4 h-4 text-cyan-500 focus:ring-cyan-500 ${isMultiSelect ? 'rounded' : 'rounded-full'}">
            <span class="quiz-option-badge w-6 h-6 rounded-md bg-slate-800 flex items-center justify-center text-xs font-bold text-cyan-400 font-mono">${o.label}</span>
            <span class="text-sm text-slate-200">${o.text}</span>
          </label>
        `).join("")}
      </div>
    `;
  }

  const wordCount = q.passage ? q.passage.trim().split(/\s+/).length : 0;
  const isPunishment = STATE.current === "CAT_PUNISHMENT" || STATE.quizSecondsRemaining <= 0;
  const penaltyVal = isPunishment ? q.point_value : q.penalty_value;
  const penaltyBadgeHtml = isPunishment
    ? `<span id="question-penalty-badge" class="px-2.5 py-0.5 rounded bg-rose-600/30 text-rose-300 font-bold border border-rose-500/60 animate-pulse font-mono text-xs">-${penaltyVal} PTS (100% PUNISHMENT ACTIVE!)</span>`
    : `<span id="question-penalty-badge" class="px-2 py-0.5 rounded bg-rose-500/15 text-rose-300 font-bold border border-rose-500/30 font-mono text-xs">-${penaltyVal} PTS PENALTY</span>`;

  container.innerHTML = `
    <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800 text-xs font-mono">
      <div class="flex items-center gap-2">
        <span class="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-bold">${q.section}</span>
        <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">${q.subtype}</span>
        <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-400">${q.difficulty.toUpperCase()}</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="px-2.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 font-bold border border-emerald-500/30">
          +${q.point_value} PTS
        </span>
        ${penaltyBadgeHtml}
      </div>
    </div>

    ${hasPassage ? `
      <div class="passage-reader-card p-4 md:p-5 my-4">
        <div class="flex items-center justify-between pb-2 mb-3 border-b border-cyan-500/20 text-xs font-mono text-cyan-400">
          <div class="flex items-center gap-2">
            <span class="font-bold uppercase tracking-wider">📖 Reading Passage</span>
            <span class="text-slate-400 text-[11px]">• ${wordCount} words</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-slate-400 text-[11px]">Passage Font:</span>
            <button type="button" onclick="adjustPassageFontSize(-1)" class="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center border border-slate-700 transition" title="Decrease font size">A-</button>
            <span id="font-size-indicator" class="w-8 text-center font-bold text-cyan-300 text-xs font-mono">${STATE.passageFontSize || 17}px</span>
            <button type="button" onclick="adjustPassageFontSize(1)" class="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs flex items-center justify-center border border-slate-700 transition" title="Increase font size">A+</button>
          </div>
        </div>
        <div id="passage-content-box" class="passage-reader max-h-[460px] overflow-y-auto pr-3 leading-relaxed" style="font-size: ${STATE.passageFontSize || 17}px; line-height: 1.85;">
          ${formatPassageParagraphs(q.passage)}
        </div>
      </div>
    ` : ""}

    <div class="my-4 text-base md:text-lg font-medium text-slate-100 leading-relaxed">
      ${q.question}
    </div>

    ${optionsHtml}

    <!-- Inline Dedicated Validation Alert Box (front-and-center, impossible to miss) -->
    <div id="question-validation-alert" class="hidden my-4 p-3.5 rounded-xl border border-rose-500/80 bg-rose-950/90 text-rose-200 text-xs font-mono shadow-xl transition-all"></div>

    <div id="answer-feedback-container" class="mt-4"></div>
  `;

  // Attach change listeners to update UI and dismiss validation alert when user makes a choice
  const allInputs = container.querySelectorAll("input");
  allInputs.forEach(inp => {
    inp.addEventListener("change", () => {
      hideValidationError();

      // Update blank statuses if multi-blank
      if (is3Blanks || is2Blanks) {
        for (let b = 1; b <= (is3Blanks ? 3 : 2); b++) {
          const checked = container.querySelector(`input[name="blank_${b}"]:checked`);
          const box = document.getElementById(`blank-box-${b}`);
          if (box) {
            const statusSpan = box.querySelector(".blank-status");
            if (checked) {
              box.classList.add("border-cyan-500/60", "bg-cyan-950/20");
              if (statusSpan) {
                statusSpan.textContent = `Selected: [${checked.value}]`;
                statusSpan.className = "blank-status text-[10px] text-cyan-300 font-bold";
              }
            } else {
              box.classList.remove("border-cyan-500/60", "bg-cyan-950/20");
              if (statusSpan) {
                statusSpan.textContent = "Unselected";
                statusSpan.className = "blank-status text-[10px] text-slate-500 font-normal";
              }
            }
          }
        }
      }

      // Update Sentence Equivalence live counter
      if (isSE) {
        const checkedCount = container.querySelectorAll('input[name="choice"]:checked').length;
        const badge = document.getElementById("se-count-badge");
        if (badge) {
          if (checkedCount === 2) {
            badge.className = "font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 animate-pulse";
            badge.textContent = "✓ 2 of 2 selected (Ready!)";
          } else {
            badge.className = "font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30";
            badge.textContent = `${checkedCount} of 2 selected`;
          }
        }
      }
    });
  });

  // Trigger KaTeX math typesetting on questions, passages, and options
  renderLaTeX(container);

  // Reset submit & clear button state and feline styling
  const submitBtn = document.getElementById("btn-submit-answer");
  const nextBtn = document.getElementById("btn-next-question");
  const clearBtn = document.getElementById("btn-clear-answer");

  if (submitBtn) {
    submitBtn.classList.remove("hidden");
    submitBtn.disabled = false;
    if (isPunishment) {
      submitBtn.innerHTML = `<span>🐾 SUBMIT CLAW STRIKE (+${q.point_value} PTS · ${STATE.currentPoints}/100 PTS) 🐾</span>`;
      submitBtn.classList.remove("bg-cyan-600", "hover:bg-cyan-500", "shadow-cyan-600/30");
      submitBtn.classList.add("bg-gradient-to-r", "from-rose-600", "to-amber-600", "hover:from-rose-500", "hover:to-amber-500", "shadow-rose-600/40");
    } else {
      submitBtn.innerHTML = '<span>Submit Answer</span>';
      submitBtn.classList.remove("bg-gradient-to-r", "from-rose-600", "to-amber-600", "hover:from-rose-500", "hover:to-amber-500", "shadow-rose-600/40");
      submitBtn.classList.add("bg-cyan-600", "hover:bg-cyan-500", "shadow-cyan-600/30");
    }
  }

  if (clearBtn) {
    clearBtn.classList.remove("hidden");
    if (isPunishment) {
      clearBtn.innerHTML = '<span>🐾 LICK CLEAN 🐾</span>';
    } else {
      clearBtn.innerHTML = '<span>Clear Selection</span>';
    }
  }

  if (nextBtn) nextBtn.classList.add("hidden");
}

function showValidationError(message, targetElem = null) {
  const alertBox = document.getElementById("question-validation-alert");
  const submitBtn = document.getElementById("btn-submit-answer");

  if (alertBox) {
    alertBox.innerHTML = `
      <div class="flex items-center gap-2.5">
        <span class="text-base text-rose-400 shrink-0">⚠️</span>
        <div class="flex-1">
          <strong class="text-white block font-bold uppercase tracking-wider text-[11px] mb-0.5">Answer Incomplete</strong>
          <span class="text-rose-200">${message}</span>
        </div>
      </div>
    `;
    alertBox.classList.remove("hidden");
    alertBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Button shake error animation
  if (submitBtn) {
    submitBtn.classList.remove("shake-error");
    void submitBtn.offsetWidth; // trigger reflow
    submitBtn.classList.add("shake-error");
    setTimeout(() => submitBtn.classList.remove("shake-error"), 600);
  }

  // Clear previous validation highlights
  document.querySelectorAll(".validation-ring-error").forEach(el => {
    el.classList.remove("validation-ring-error", "ring-2", "ring-rose-500", "bg-rose-950/30");
  });

  if (targetElem) {
    targetElem.classList.add("validation-ring-error", "ring-2", "ring-rose-500", "bg-rose-950/30");
  }
}

function hideValidationError() {
  const alertBox = document.getElementById("question-validation-alert");
  if (alertBox) alertBox.classList.add("hidden");
  document.querySelectorAll(".validation-ring-error").forEach(el => {
    el.classList.remove("validation-ring-error", "ring-2", "ring-rose-500", "bg-rose-950/30");
  });
}

async function submitUserAnswer() {
  const q = STATE.currentQuestion;
  if (!q) return;

  let userSelection = null;
  const is3Blanks = q.subtype.includes("3 Blanks");
  const is2Blanks = q.subtype.includes("2 Blanks");
  const isSE = q.subtype.includes("Sentence Equivalence");
  const isMultiSelect = Boolean(q.is_multi_select) || isSE || (Array.isArray(q.correct_answer) && q.correct_answer.length > 1) || (q.question && (q.question.toLowerCase().includes("select all") || q.question.toLowerCase().includes("indicate all")));

  if (is3Blanks) {
    const b1 = document.querySelector('input[name="blank_1"]:checked')?.value;
    const b2 = document.querySelector('input[name="blank_2"]:checked')?.value;
    const b3 = document.querySelector('input[name="blank_3"]:checked')?.value;
    const missing = [];
    if (!b1) missing.push({ label: "Blank (i)", id: "blank-box-1" });
    if (!b2) missing.push({ label: "Blank (ii)", id: "blank-box-2" });
    if (!b3) missing.push({ label: "Blank (iii)", id: "blank-box-3" });
    if (missing.length > 0) {
      const names = missing.map(m => m.label).join(" and ");
      const firstEl = document.getElementById(missing[0].id);
      showValidationError(`Please select an answer choice for ${names}!`, firstEl);
      return;
    }
    userSelection = [b1, b2, b3];
  } else if (is2Blanks) {
    const b1 = document.querySelector('input[name="blank_1"]:checked')?.value;
    const b2 = document.querySelector('input[name="blank_2"]:checked')?.value;
    const missing = [];
    if (!b1) missing.push({ label: "Blank (i)", id: "blank-box-1" });
    if (!b2) missing.push({ label: "Blank (ii)", id: "blank-box-2" });
    if (missing.length > 0) {
      const names = missing.map(m => m.label).join(" and ");
      const firstEl = document.getElementById(missing[0].id);
      showValidationError(`Please select an answer choice for ${names}!`, firstEl);
      return;
    }
    userSelection = [b1, b2];
  } else if (isSE) {
    const checked = Array.from(document.querySelectorAll('input[name="choice"]:checked')).map(el => el.value);
    if (checked.length !== 2) {
      const countMsg = checked.length === 0
        ? "No choices are currently selected."
        : `You currently have ${checked.length} of 2 required choices selected.`;
      showValidationError(`Sentence Equivalence requires selecting EXACTLY TWO choices! ${countMsg}`, document.getElementById("question-options-container"));
      return;
    }
    userSelection = checked.sort();
  } else if (isMultiSelect) {
    const checked = Array.from(document.querySelectorAll('input[name="choice"]:checked')).map(el => el.value);
    if (checked.length === 0) {
      showValidationError("Please select at least one answer choice!", document.getElementById("question-options-container"));
      return;
    }
    userSelection = checked.sort();
  } else {
    const selected = document.querySelector('input[name="choice"]:checked')?.value;
    if (!selected) {
      showValidationError("Please select an answer choice before submitting!", document.getElementById("question-options-container"));
      return;
    }
    userSelection = [selected];
  }

  // Clear validation alert upon valid submission attempt
  hideValidationError();

  // Submit to backend or evaluate locally
  let evalResult = null;
  try {
    const res = await fetch("/api/question/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: q.id, user_answer: userSelection })
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.evaluation && Array.isArray(data.evaluation.correct_answer)) {
        evalResult = data.evaluation;
        STATE.currentPoints = data.current_points ?? STATE.currentPoints;
      } else {
        console.warn("Backend submit error payload:", data);
      }
    }
  } catch (e) {
    console.warn("Backend submit error, falling back to client evaluation:", e);
  }

  // Guarantees non-null evaluation whether online, offline, or fallback
  if (!evalResult) {
    const expected = (q.correct_answer || []).map(x => String(x).toUpperCase()).sort();
    const userSorted = (userSelection || []).map(x => String(x).toUpperCase()).sort();
    const isCorrect = JSON.stringify(expected) === JSON.stringify(userSorted);
    const isPunishment = STATE.current === "CAT_PUNISHMENT" || STATE.quizSecondsRemaining <= 0;
    const penalty = isPunishment ? q.point_value : q.penalty_value;
    const delta = isCorrect ? q.point_value : -penalty;
    STATE.currentPoints = Math.max(0, STATE.currentPoints + delta);
    evalResult = {
      is_correct: isCorrect,
      points_delta: delta,
      penalty_percentage: isPunishment ? 100 : 50,
      correct_answer: expected,
      explanation: q.explanation || "Standard ETS derivation."
    };
  }

  // Update Score Display
  updateScoreDisplay(evalResult.points_delta);

  // Record answered question into history for session statistics
  STATE.answeredQuestions.push({
    question_id: q.id,
    type: q.type,
    subtype: q.subtype,
    point_value: q.point_value,
    user_answer: userSelection,
    correct_answer: evalResult.correct_answer,
    is_correct: evalResult.is_correct,
    points_delta: evalResult.points_delta,
    is_punishment_mode: isPunishmentNow,
    timestamp: Date.now()
  });

  // Sensory Reprieve & Visual Impact during Cat Mode
  const isPunishmentNow = STATE.current === "CAT_PUNISHMENT" || STATE.quizSecondsRemaining <= 0;
  if (isPunishmentNow && evalResult.is_correct) {
    grantCatAudioReprieve(15);
  }

  // Show Rich Inline Feedback
  const formattedAns = Array.isArray(evalResult?.correct_answer)
    ? evalResult.correct_answer.join(", ")
    : (evalResult?.correct_answer ? String(evalResult.correct_answer) : (q.correct_answer ? [].concat(q.correct_answer).join(", ") : "N/A"));

  const fbContainer = document.getElementById("answer-feedback-container");
  if (fbContainer) {
    if (isPunishmentNow) {
      if (evalResult.is_correct) {
        fbContainer.innerHTML = `
          <div class="p-4 rounded-xl border bg-emerald-500/20 border-emerald-500/50 shadow-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-black text-emerald-300 flex items-center gap-2">
                🐾 DIRECT CLAW STRIKE! CORRECT ANSWER!
              </span>
              <span class="px-2.5 py-1 rounded bg-emerald-400/20 text-emerald-200 font-mono text-xs font-bold border border-emerald-400/40 animate-pulse">
                +${evalResult.points_delta} PTS · 15s REPRIEVE ACTIVE
              </span>
            </div>
            <div class="text-xs text-slate-300 leading-relaxed font-mono">
              <span class="text-slate-400">Correct Answer:</span> <strong class="text-white">${formattedAns}</strong>
            </div>
            <div class="text-xs text-slate-400 leading-relaxed mt-1">
              ${evalResult.explanation || "Standard derivation."}
            </div>
            <div class="mt-3 pt-2.5 border-t border-emerald-500/30 flex items-center justify-between text-xs font-mono text-emerald-200">
              <span>Score: <strong class="text-white font-bold">${STATE.currentPoints} / 100 PTS</strong></span>
              <span class="text-amber-300">${Math.max(0, STATE.targetPoints - STATE.currentPoints)} PTS needed to permanently disarm</span>
            </div>
          </div>
        `;
      } else {
        fbContainer.innerHTML = `
          <div class="p-4 rounded-xl border bg-rose-600/20 border-rose-500/60 shadow-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-black text-rose-300 flex items-center gap-2">
                🐾 CLAW STRIKE MISSED! 100% PENALTY INCURRED
              </span>
              <span class="px-2.5 py-1 rounded bg-rose-500/30 text-rose-200 font-mono text-xs font-bold border border-rose-500/50">
                ${evalResult.points_delta} PTS (100% AT STAKE)
              </span>
            </div>
            <div class="text-xs text-slate-300 leading-relaxed font-mono">
              <span class="text-slate-400">Correct Answer:</span> <strong class="text-white">${formattedAns}</strong>
            </div>
            <div class="text-xs text-slate-400 leading-relaxed mt-1">
              ${evalResult.explanation || "Standard derivation."}
            </div>
            <div class="mt-3 pt-2.5 border-t border-rose-500/30 flex items-center justify-between text-xs font-mono text-rose-200">
              <span>Score: <strong class="text-white font-bold">${STATE.currentPoints} / 100 PTS</strong></span>
              <span class="text-amber-300">${Math.max(0, STATE.targetPoints - STATE.currentPoints)} PTS needed to permanently disarm</span>
            </div>
          </div>
        `;
      }
    } else {
      fbContainer.innerHTML = `
        <div class="p-4 rounded-xl border ${evalResult.is_correct ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-rose-500/10 border-rose-500/30'}">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-bold ${evalResult.is_correct ? 'text-emerald-400' : 'text-rose-400'} flex items-center gap-1.5">
              ${evalResult.is_correct ? '✓ CORRECT ANSWER!' : '✗ INCORRECT ANSWER'}
            </span>
            <span class="text-xs font-mono font-bold ${evalResult.is_correct ? 'text-emerald-300' : 'text-rose-300'}">
              ${evalResult.points_delta > 0 ? `+${evalResult.points_delta}` : `${evalResult.points_delta}`} PTS
            </span>
          </div>
          <div class="text-xs text-slate-300 leading-relaxed font-mono">
            <span class="text-slate-400">Correct Answer:</span> <strong class="text-white">${formattedAns}</strong>
          </div>
          <div class="text-xs text-slate-400 leading-relaxed mt-1">
            ${evalResult.explanation || "Standard derivation."}
          </div>
        </div>
      `;
    }
    renderLaTeX(fbContainer);
  }

  // Toggle and style next button
  document.getElementById("btn-submit-answer")?.classList.add("hidden");
  document.getElementById("btn-clear-answer")?.classList.add("hidden");
  const nextBtn = document.getElementById("btn-next-question");
  if (nextBtn) {
    nextBtn.classList.remove("hidden");
    if (isPunishmentNow) {
      const remaining = Math.max(0, STATE.targetPoints - STATE.currentPoints);
      nextBtn.innerHTML = `<span>🐾 NEXT QUESTION (${remaining} PTS REMAINING TO DISARM) &rarr;</span>`;
    } else {
      nextBtn.innerHTML = `<span>Next Question &rarr;</span>`;
    }
  }

  // Check victory condition immediately
  if (STATE.currentPoints >= STATE.targetPoints) {
    triggerVictory();
  }
}

function renderLaTeX(element, retries = 0) {
  if (!element) return;
  if (typeof renderMathInElement === "function") {
    try {
      renderMathInElement(element, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\[", right: "\\]", display: true },
          { left: "\\(", right: "\\)", display: false }
        ],
        throwOnError: false
      });
    } catch (e) {
      console.warn("KaTeX rendering warning:", e);
    }
  } else if (retries < 10) {
    // Retry when KaTeX scripts finish loading asynchronously (up to 10 attempts = 2.5s)
    setTimeout(() => renderLaTeX(element, retries + 1), 250);
  } else {
    console.warn("KaTeX unavailable; proceeding with standard plaintext rendering.");
  }
}

// ==========================================
// REAL-TIME PROCEDURAL & WAV AUDIO ENGINES
// ==========================================

const MODEL_AUDIO_MAP = {
  model1: "/audio/model1_amygdala_roughness.wav",
  model2: "/audio/model2_stick_slip_friction.wav",
  model3: "/audio/model3_plomp_levelt_dissonance.wav",
  model4: "/audio/model4_stochastic_mmn_disruption.wav",
  model5: "/audio/model5_hyperbolic_looming.wav",
  model6: "/audio/model6_apex_felid_roar.wav",
  model7: "/audio/model7_serpentine_stridulation.wav"
};

const PROCEDURAL_AUDIO_MAP = {
  ambient_clean_soul: "/ambient_tracks/08_clean_soul.mp3",
  ambient_promises: "/ambient_tracks/09_promises_to_keep.mp3",
  ambient_fresh_air: "/ambient_tracks/10_fresh_air.mp3",
  ambient_meditation_01: "/ambient_tracks/04_meditation_impromptu_01.mp3",
  ambient_meditation_02: "/ambient_tracks/05_meditation_impromptu_02.mp3",
  ambient_calmant: "/ambient_tracks/07_calmant.mp3",
  ambient_space_1990: "/ambient_tracks/01_space_1990.mp3",
  ambient_mirage: "/ambient_tracks/02_mirage.mp3",
  ambient_immersed: "/ambient_tracks/03_immersed.mp3",
  ambient_frozen_star: "/ambient_tracks/06_frozen_star.mp3",
  ambient_airship: "/ambient_tracks/11_airship_serenity.mp3",
  ambient_earth_on_wind: "/ambient_tracks/12_earth_on_wind.mp3"
};

const PROCEDURAL_TRACK_NAMES = {
  ambient_clean_soul: "Clean Soul — Kevin MacLeod (5:07 · Chill Lo-Fi Focus)",
  ambient_promises: "Promises to Keep — Kevin MacLeod (5:04 · Solo Grand Piano)",
  ambient_fresh_air: "Fresh Air — Kevin MacLeod (4:54 · Refreshing Piano)",
  ambient_meditation_01: "Meditation Impromptu 01 — Kevin MacLeod (3:33 · Contemplative Piano)",
  ambient_meditation_02: "Meditation Impromptu 02 — Kevin MacLeod (4:09 · Flowing Piano)",
  ambient_calmant: "Calmant — Kevin MacLeod (3:24 · Gentle Piano)",
  ambient_space_1990: "Space 1990 — Kevin MacLeod (4:26 · Ambient Synth)",
  ambient_mirage: "Mirage — Kevin MacLeod (4:00 · Atmospheric Drone)",
  ambient_immersed: "Immersed — Kevin MacLeod (4:09 · Minimal Soundscape)",
  ambient_frozen_star: "Frozen Star — Kevin MacLeod (3:41 · Ethereal Harp & Choir)",
  ambient_airship: "Airship Serenity — Kevin MacLeod (4:00 · 8-Bit Ambient)",
  ambient_earth_on_wind: "Earth On Wind — Noisesurfer (4:12 · CC0 Organic Drone)",
  none: "Muted (Silent Study)"
};

function updateAmbientTrackDescription() {
  const desc = PROCEDURAL_TRACK_NAMES[STATE.selectedProceduralTrack] || STATE.selectedProceduralTrack;
  const descElem = document.getElementById("quiz-ambient-track-title");
  if (descElem) descElem.textContent = desc;
}

function updateAmbientStatusBadge(text, variant = "cyan") {
  const badge = document.getElementById("quiz-ambient-badge");
  if (!badge) return;
  if (variant === "cyan") {
    badge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1.5";
    badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span><span>${text}</span>`;
  } else if (variant === "amber") {
    badge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1.5";
    badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span><span>${text}</span>`;
  } else {
    badge.className = "px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1.5";
    badge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-slate-500"></span><span>${text}</span>`;
  }
}

function setAmbientVolume(volFraction) {
  STATE.ambientVolume = Math.max(0.0, Math.min(1.0, volFraction));
  STATE.isAmbientMuted = STATE.ambientVolume === 0;
  applyAmbientAudioVolume();
}

function toggleAmbientMute() {
  STATE.isAmbientMuted = !STATE.isAmbientMuted;
  applyAmbientAudioVolume();
  if (STATE.isAmbientMuted) {
    showToast("Ambient focus audio muted", "slate");
  } else {
    showToast(`Ambient audio unmuted (${Math.round((STATE.ambientVolume ?? 0.65) * 100)}%)`, "cyan");
  }
}

function applyAmbientAudioVolume() {
  const effectiveVol = STATE.isAmbientMuted ? 0.0 : (STATE.ambientVolume ?? 0.65);
  if (STATE.proceduralAudio) {
    STATE.proceduralAudio.volume = effectiveVol;
  }

  const pct = Math.round((STATE.ambientVolume ?? 0.65) * 100);
  document.querySelectorAll(".slider-ambient-volume-sync").forEach(sl => {
    sl.value = pct;
  });
  document.querySelectorAll(".label-ambient-volume-sync").forEach(lbl => {
    lbl.textContent = STATE.isAmbientMuted ? "0%" : `${pct}%`;
  });

  const icon = document.getElementById("icon-quiz-ambient-volume");
  if (icon) {
    if (STATE.isAmbientMuted || effectiveVol === 0) {
      icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />`;
      icon.classList.remove("text-cyan-400");
      icon.classList.add("text-slate-500");
      updateAmbientStatusBadge("MUTED", "slate");
    } else {
      icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />`;
      icon.classList.add("text-cyan-400");
      icon.classList.remove("text-slate-500");
      if (STATE.current === "QUIZ_ACTIVE" && STATE.selectedProceduralTrack !== "none") {
        updateAmbientStatusBadge("PLAYING", "cyan");
      }
    }
  }
}

function setAmbientGenerator(generatorKey) {
  STATE.selectedProceduralTrack = generatorKey;
  document.querySelectorAll(".select-ambient-generator-sync").forEach(sel => {
    sel.value = generatorKey;
  });
  updateAmbientTrackDescription();

  if (STATE.current === "QUIZ_ACTIVE") {
    if (generatorKey === "none") {
      stopProceduralBackgroundTrack();
      updateAmbientStatusBadge("MUTED", "slate");
      showToast("Ambient focus audio muted", "slate");
    } else {
      playProceduralBackgroundTrack();
      updateAmbientStatusBadge("PLAYING", "cyan");
      showToast(`Ambient Track: ${PROCEDURAL_TRACK_NAMES[generatorKey] || generatorKey}`, "cyan");
    }
  }
}

function playProceduralBackgroundTrack() {
  stopProceduralBackgroundTrack();
  if (STATE.selectedProceduralTrack === "none") {
    updateAmbientStatusBadge("MUTED", "slate");
    return;
  }

  const wavPath = PROCEDURAL_AUDIO_MAP[STATE.selectedProceduralTrack];
  if (!wavPath) return;

  try {
    STATE.proceduralAudio = new Audio(wavPath);
    STATE.proceduralAudio.loop = true;
    const effectiveVol = STATE.isAmbientMuted ? 0.0 : (STATE.ambientVolume ?? 0.65);
    STATE.proceduralAudio.volume = effectiveVol;
    updateAmbientTrackDescription();
    const playPromise = STATE.proceduralAudio.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        if (!STATE.isAmbientMuted && effectiveVol > 0) {
          updateAmbientStatusBadge("PLAYING", "cyan");
        } else {
          updateAmbientStatusBadge("MUTED", "slate");
        }
      }).catch(e => {
        console.warn("Procedural background audio playback blocked:", e);
      });
    }
  } catch (e) {
    console.warn("Could not start procedural audio:", e);
  }
}

function stopProceduralBackgroundTrack() {
  if (STATE.proceduralAudio) {
    try {
      STATE.proceduralAudio.pause();
      STATE.proceduralAudio.currentTime = 0;
    } catch (e) {}
    STATE.proceduralAudio = null;
  }
  if (STATE.current === "CAT_PUNISHMENT") {
    updateAmbientStatusBadge("CEASED (CAT MODE)", "amber");
  } else if (STATE.current === "IDLE" || STATE.current === "VICTORY") {
    updateAmbientStatusBadge("STANDBY", "slate");
  }
}

function playRTGAlarmTone(modelKey) {
  stopRTGAlarmTone();

  // 1. Try playing authentic WAV file from audio_samples/
  const wavPath = MODEL_AUDIO_MAP[modelKey] || MODEL_AUDIO_MAP.model6;
  let playedWav = false;
  try {
    STATE.alarmAudioElement = new Audio(wavPath);
    STATE.alarmAudioElement.loop = true;
    STATE.alarmAudioElement.volume = 1.0; // Fixed 100% volume for alarm assault siren
    STATE.alarmAudioElement.play().then(() => {
      playedWav = true;
    }).catch(err => {
      console.warn("WAV playback blocked or offline, using Web Audio DSP fallback:", err);
      synthesizeAlarmDSP(modelKey);
    });
  } catch (e) {
    synthesizeAlarmDSP(modelKey);
  }
}

function stopRTGAlarmTone() {
  if (STATE.alarmAudioElement) {
    try {
      STATE.alarmAudioElement.pause();
      STATE.alarmAudioElement.currentTime = 0;
    } catch (e) {}
    STATE.alarmAudioElement = null;
  }
  STATE.activeAlarmNodes.forEach(node => {
    try {
      if (typeof node.stop === "function") node.stop();
      if (typeof node.disconnect === "function") node.disconnect();
    } catch (e) {}
  });
  STATE.activeAlarmNodes = [];
}

function synthesizeAlarmDSP(modelKey) {
  if (!STATE.audioCtx) {
    STATE.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  const ctx = STATE.audioCtx;
  if (ctx.state === "suspended") ctx.resume();

  const masterGain = ctx.createGain();
  masterGain.gain.setValueAtTime(1.0, ctx.currentTime); // Fixed 100% volume
  masterGain.connect(ctx.destination);
  STATE.activeAlarmNodes.push(masterGain);

  if (modelKey === "model6") {
    // Model 6: Apex Felid Assault V2 (22-35 Hz Sub-rumble + 750-1150 Hz Laryngeal tear)
    const oscLarynx = ctx.createOscillator();
    const oscSub = ctx.createOscillator();
    const lfoMod = ctx.createOscillator();
    const modGain = ctx.createGain();
    const distNode = ctx.createWaveShaper();

    const curve = new Float32Array(256);
    for (let i = 0; i < 256; i++) {
      const x = (i * 2) / 256 - 1;
      curve[i] = Math.tanh(x * 3.5);
    }
    distNode.curve = curve;

    oscLarynx.type = "sawtooth";
    oscLarynx.frequency.setValueAtTime(840, ctx.currentTime);

    lfoMod.type = "sine";
    lfoMod.frequency.setValueAtTime(32, ctx.currentTime);
    modGain.gain.setValueAtTime(140, ctx.currentTime);
    lfoMod.connect(modGain);
    modGain.connect(oscLarynx.frequency);

    oscSub.type = "sine";
    oscSub.frequency.setValueAtTime(28, ctx.currentTime);

    const subGain = ctx.createGain();
    subGain.gain.setValueAtTime(0.7, ctx.currentTime);

    oscLarynx.connect(distNode);
    distNode.connect(masterGain);
    oscSub.connect(subGain);
    subGain.connect(masterGain);

    oscLarynx.start();
    oscSub.start();
    lfoMod.start();

    STATE.activeAlarmNodes.push(oscLarynx, oscSub, lfoMod);

  } else if (modelKey === "model4") {
    // Model 4: Stochastic MMN Disruption (Poisson pulse train)
    const mmnInterval = setInterval(() => {
      if (STATE.current !== "ALARM_RINGING") {
        clearInterval(mmnInterval);
        return;
      }
      const t = ctx.currentTime;
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      const freqs = [320, 480, 720, 1100, 1650, 2400, 3600, 5200];
      osc.frequency.setValueAtTime(freqs[Math.floor(Math.random() * freqs.length)], t);
      osc.type = Math.random() < 0.5 ? "square" : "sawtooth";

      const dur = 0.02 + Math.random() * 0.08;
      g.gain.setValueAtTime(0.4, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);

      osc.connect(g);
      g.connect(masterGain);
      osc.start(t);
      osc.stop(t + dur);
    }, 90);
    STATE.activeAlarmNodes.push({ stop: () => clearInterval(mmnInterval) });

  } else if (modelKey === "model1") {
    // Model 1: Amygdala Roughness Harvester (2500 Hz carrier, 70 Hz roughness)
    const osc = ctx.createOscillator();
    const lfo = ctx.createOscillator();
    const lfoG = ctx.createGain();

    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(2500, ctx.currentTime);

    lfo.type = "sine";
    lfo.frequency.setValueAtTime(70, ctx.currentTime);
    lfoG.gain.setValueAtTime(800, ctx.currentTime);

    lfo.connect(lfoG);
    lfoG.connect(osc.frequency);
    osc.connect(masterGain);

    osc.start();
    lfo.start();
    STATE.activeAlarmNodes.push(osc, lfo);

  } else if (modelKey === "model2") {
    // Model 2: Frictional Stick-Slip Screech (Chalkboard friction)
    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    osc1.type = "sawtooth";
    osc1.frequency.setValueAtTime(3800, ctx.currentTime);
    osc2.type = "square";
    osc2.frequency.setValueAtTime(4150, ctx.currentTime);

    osc1.connect(masterGain);
    osc2.connect(masterGain);
    osc1.start();
    osc2.start();
    STATE.activeAlarmNodes.push(osc1, osc2);

  } else if (modelKey === "model7") {
    // Model 7: Serpentine Venom Stridulation (Hiss + rattle bursts)
    const rattleInterval = setInterval(() => {
      if (STATE.current !== "ALARM_RINGING") {
        clearInterval(rattleInterval);
        return;
      }
      const t = ctx.currentTime;
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(5400 + Math.random() * 1200, t);
      g.gain.setValueAtTime(0.3, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
      osc.connect(g);
      g.connect(masterGain);
      osc.start(t);
      osc.stop(t + 0.05);
    }, 45);
    STATE.activeAlarmNodes.push({ stop: () => clearInterval(rattleInterval) });

  } else {
    // Generic Roughness fallback (30-130 Hz roughness)
    const osc = ctx.createOscillator();
    const lfo = ctx.createOscillator();
    const lfoG = ctx.createGain();

    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(3200, ctx.currentTime);

    lfo.type = "sine";
    lfo.frequency.setValueAtTime(65, ctx.currentTime);
    lfoG.gain.setValueAtTime(450, ctx.currentTime);

    lfo.connect(lfoG);
    lfoG.connect(osc.frequency);
    osc.connect(masterGain);

    osc.start();
    lfo.start();
    STATE.activeAlarmNodes.push(osc, lfo);
  }
}

// ==========================================
// UI RENDERING & STATE SWITCHING
// ==========================================
function renderState() {
  const panelSetup = document.getElementById("panel-alarm-setup");
  const panelRinging = document.getElementById("panel-alarm-ringing");
  const panelQuiz = document.getElementById("panel-quiz-solving");
  const panelCat = document.getElementById("panel-cat-punishment");
  const panelVictory = document.getElementById("panel-victory");

  // Determine active panels smoothly without momentary flicker or layout shifts
  const shouldShowSetup = STATE.current === "IDLE";
  const shouldShowRinging = STATE.current === "ALARM_RINGING";
  const shouldShowQuiz = STATE.current === "QUIZ_ACTIVE" || STATE.current === "CAT_PUNISHMENT";
  const shouldShowCat = STATE.current === "CAT_PUNISHMENT";
  const shouldShowVictory = STATE.current === "VICTORY";

  if (panelSetup) panelSetup.classList.toggle("hidden", !shouldShowSetup);
  if (panelRinging) panelRinging.classList.toggle("hidden", !shouldShowRinging);
  if (panelQuiz) panelQuiz.classList.toggle("hidden", !shouldShowQuiz);
  if (panelCat) panelCat.classList.toggle("hidden", !shouldShowCat);
  if (panelVictory) panelVictory.classList.toggle("hidden", !shouldShowVictory);

  const statusBadge = document.getElementById("app-status-badge");

  if (STATE.current === "IDLE") {
    if (statusBadge) {
      statusBadge.className = STATE.isArmed ? "status-pill status-armed" : "status-pill bg-slate-800 text-slate-400 border border-slate-700";
      statusBadge.textContent = STATE.isArmed ? "ARMED & WATCHING" : "STANDBY (DISARMED)";
    }
    const armBtn = document.getElementById("btn-arm-toggle");
    if (armBtn) {
      armBtn.textContent = STATE.isArmed ? "Disarm Alarm" : "Arm Alarm System";
      armBtn.className = STATE.isArmed 
        ? "w-full py-3 px-4 rounded-xl font-bold bg-slate-800 hover:bg-slate-700 text-rose-400 border border-rose-500/30 transition-all text-sm"
        : "w-full py-3 px-4 rounded-xl font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 transition-all text-sm";
    }

  } else if (STATE.current === "ALARM_RINGING") {
    if (statusBadge) {
      statusBadge.className = "status-pill status-ringing";
      statusBadge.textContent = "ALARM RINGING · PSYCHOACOUSTIC ASSAULT";
    }

  } else if (STATE.current === "QUIZ_ACTIVE") {
    if (statusBadge) {
      statusBadge.className = "status-pill status-solving";
      statusBadge.textContent = "5-MIN QUIZ ACTIVE · ACCUMULATE 100 PTS";
    }
    updateTimerDisplay();
    updateScoreDisplay();

  } else if (STATE.current === "CAT_PUNISHMENT") {
    if (statusBadge) {
      statusBadge.className = "status-pill status-cat";
      statusBadge.textContent = "PUNISHMENT: 100 WAYS TO LOVE A CAT (RAMPING)";
    }
    updateScoreDisplay();

  } else if (STATE.current === "VICTORY") {
    if (statusBadge) {
      statusBadge.className = "status-pill status-armed";
      statusBadge.textContent = "CONSCIOUS & ETS READY · VICTORY";
    }
  }
}

// Toast notification helper
function showToast(message, color = "cyan") {
  const toast = document.createElement("div");
  const colorMap = {
    emerald: "bg-emerald-950/90 border-emerald-500/50 text-emerald-300",
    crimson: "bg-rose-950/90 border-rose-500/50 text-rose-300",
    cyan: "bg-cyan-950/90 border-cyan-500/50 text-cyan-300",
    amber: "bg-amber-950/90 border-amber-500/50 text-amber-300",
    slate: "bg-slate-900/90 border-slate-700 text-slate-300"
  };
  toast.className = `fixed bottom-6 right-6 px-4 py-3 rounded-xl border text-xs font-mono shadow-2xl backdrop-blur-md z-50 transition-all ${colorMap[color] || colorMap.cyan}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}
