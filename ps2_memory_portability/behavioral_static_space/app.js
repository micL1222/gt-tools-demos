"use strict";

const FLOW = Object.freeze({
  INITIAL: "INITIAL",
  REFLECTION_COMPLETE: "REFLECTION_COMPLETE",
  BENCHMARK_REVEALED: "BENCHMARK_REVEALED",
  FINAL_DECISION: "FINAL_DECISION",
  SUBMITTED: "SUBMITTED"
});

const CHOICES = Object.freeze(["Stay", "Switch"]);
const CONDITIONS = Object.freeze({ Full: 0.20, Partial: 0.35, None: 0.50 });
const BENEFITS = Object.freeze([0.15, 0.30, 0.45, 0.60]);
const RATING_NAMES = Object.freeze(["difficulty", "personalization", "privacy", "trust"]);

const state = {
  scenarios: [],
  currentScenario: null,
  currentPlay: null,
  stage: FLOW.INITIAL
};

// This array exists only for the life of the currently open page. It contains
// structured records only and is never serialized or sent anywhere.
const priorPlays = [];

const elements = {
  main: document.getElementById("main-content"),
  configurationError: document.getElementById("configuration-error"),
  configurationErrorMessage: document.getElementById("configuration-error-message"),
  benefit: document.getElementById("benefit-value"),
  condition: document.getElementById("condition-value"),
  conditionDescription: document.getElementById("condition-description"),
  initialFieldset: document.getElementById("initial-decision-fieldset"),
  initialReflection: document.getElementById("initial-reflection"),
  revealButton: document.getElementById("reveal-button"),
  initialError: document.getElementById("initial-error"),
  benchmarkPanel: document.getElementById("benchmark-panel"),
  benchmarkBenefit: document.getElementById("benchmark-benefit"),
  benchmarkHurdle: document.getElementById("benchmark-hurdle"),
  benchmarkNet: document.getElementById("benchmark-net"),
  benchmarkPrediction: document.getElementById("benchmark-prediction"),
  initialAgreement: document.getElementById("initial-agreement"),
  finalSection: document.getElementById("final-section"),
  finalFieldset: document.getElementById("final-decision-fieldset"),
  postReflection: document.getElementById("post-reflection"),
  submitButton: document.getElementById("submit-button"),
  finalError: document.getElementById("final-error"),
  peerPanel: document.getElementById("peer-panel"),
  peerIntro: document.getElementById("peer-intro"),
  peerSummaries: document.getElementById("peer-summaries"),
  nextActions: document.getElementById("next-actions"),
  newScenario: document.getElementById("new-scenario-button"),
  clearHistory: document.getElementById("clear-history-button"),
  historyStatus: document.getElementById("history-status")
};

function benchmarkFor(benefit, hurdle) {
  if (benefit === hurdle) {
    throw new Error("Scenario catalog contains a prohibited equality case.");
  }
  return benefit > hurdle ? "Switch" : "Stay";
}

function validateScenarios(scenarios) {
  if (!Array.isArray(scenarios) || scenarios.length !== 12) {
    throw new Error("The scenario catalog must contain exactly 12 scenarios.");
  }
  const ids = new Set();
  const conditions = new Set();
  const benefits = new Set();
  const predictions = [];
  scenarios.forEach((scenario) => {
    const fields = ["scenario_id", "condition", "benefit", "hurdle", "benchmark_prediction", "condition_description"];
    if (!fields.every((field) => Object.hasOwn(scenario, field))) {
      throw new Error("A scenario is missing a required field.");
    }
    if (ids.has(scenario.scenario_id) || !Object.hasOwn(CONDITIONS, scenario.condition)) {
      throw new Error("Scenario IDs and conditions must be valid and unique.");
    }
    if (!BENEFITS.includes(scenario.benefit) || scenario.hurdle !== CONDITIONS[scenario.condition]) {
      throw new Error("Scenario benefits or hurdles do not match the fixed catalog.");
    }
    const recomputed = benchmarkFor(scenario.benefit, scenario.hurdle);
    if (!CHOICES.includes(scenario.benchmark_prediction) || recomputed !== scenario.benchmark_prediction) {
      throw new Error("A scenario benchmark prediction does not match g and r.");
    }
    ids.add(scenario.scenario_id);
    conditions.add(scenario.condition);
    benefits.add(scenario.benefit);
    predictions.push(scenario.benchmark_prediction);
  });
  if (ids.size !== 12 || conditions.size !== 3 || benefits.size !== 4 || predictions.filter((item) => item === "Stay").length !== 6 || predictions.filter((item) => item === "Switch").length !== 6) {
    throw new Error("The scenario catalog is not balanced as required.");
  }
}

function randomIndex(length) {
  if (window.crypto && window.crypto.getRandomValues) {
    const maximum = Math.floor(0x100000000 / length) * length;
    const value = new Uint32Array(1);
    do { window.crypto.getRandomValues(value); } while (value[0] >= maximum);
    return value[0] % length;
  }
  return Math.floor(Math.random() * length);
}

function newPlayId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `play-${Date.now()}-${randomIndex(1000000)}`;
}

function selectedChoice(name) {
  const checked = document.querySelector(`input[name="${name}"]:checked`);
  return checked ? checked.value : null;
}

function selectedRating(name) {
  const checked = document.querySelector(`input[name="${name}"]:checked`);
  return checked ? Number(checked.value) : null;
}

function setDisabled(container, disabled) {
  container.querySelectorAll("input, textarea, button").forEach((control) => { control.disabled = disabled; });
}

function clearNode(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function createRatingInputs() {
  document.querySelectorAll(".rating-options").forEach((container) => {
    const name = container.dataset.rating;
    clearNode(container);
    for (let value = 1; value <= 7; value += 1) {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = name;
      input.value = String(value);
      label.append(input, document.createTextNode(String(value)));
      container.appendChild(label);
    }
  });
}

function chooseScenario(allowQueryParameter) {
  const requestedId = allowQueryParameter ? new URLSearchParams(window.location.search).get("scenario") : null;
  const requested = state.scenarios.find((scenario) => scenario.scenario_id === requestedId);
  return requested || state.scenarios[randomIndex(state.scenarios.length)];
}

function renderScenario(scenario) {
  state.currentScenario = scenario;
  state.currentPlay = { playId: newPlayId(), scenario };
  state.stage = FLOW.INITIAL;
  elements.benefit.textContent = `g = ${scenario.benefit.toFixed(2)}`;
  elements.condition.textContent = scenario.condition;
  elements.conditionDescription.textContent = scenario.condition_description;
  document.querySelectorAll("input[name='initial-choice'], input[name='final-choice'], input[data-rating]").forEach((input) => { input.checked = false; });
  RATING_NAMES.forEach((name) => document.querySelectorAll(`input[name='${name}']`).forEach((input) => { input.checked = false; }));
  elements.initialReflection.value = "";
  elements.postReflection.value = "";
  setDisabled(elements.initialFieldset, false);
  document.querySelectorAll(".rating-grid fieldset").forEach((fieldset) => setDisabled(fieldset, false));
  elements.initialReflection.disabled = false;
  elements.revealButton.disabled = false;
  setDisabled(elements.finalFieldset, false);
  elements.postReflection.disabled = false;
  elements.submitButton.disabled = false;
  elements.initialError.textContent = "";
  elements.finalError.textContent = "";
  elements.initialAgreement.textContent = "";
  elements.benchmarkPanel.hidden = true;
  elements.finalSection.hidden = true;
  elements.peerPanel.hidden = true;
  elements.nextActions.hidden = true;
  elements.historyStatus.textContent = "";
}

function revealBenchmark() {
  if (state.stage !== FLOW.INITIAL) return;
  const initialChoice = selectedChoice("initial-choice");
  const ratings = Object.fromEntries(RATING_NAMES.map((name) => [name, selectedRating(name)]));
  if (!initialChoice || Object.values(ratings).some((value) => !Number.isInteger(value) || value < 1 || value > 7)) {
    elements.initialError.textContent = "Choose an initial decision and all four ratings from 1 to 7 before revealing the benchmark.";
    return;
  }
  state.stage = FLOW.REFLECTION_COMPLETE;
  const scenario = state.currentScenario;
  const prediction = benchmarkFor(scenario.benefit, scenario.hurdle);
  state.currentPlay.initialChoice = initialChoice;
  state.currentPlay.initialAgreesWithBenchmark = initialChoice === prediction;
  state.currentPlay.ratings = ratings;
  state.stage = FLOW.BENCHMARK_REVEALED;
  setDisabled(elements.initialFieldset, true);
  document.querySelectorAll(".rating-grid fieldset").forEach((fieldset) => setDisabled(fieldset, true));
  elements.initialReflection.disabled = true;
  elements.revealButton.disabled = true;
  elements.benchmarkBenefit.textContent = `g = ${scenario.benefit.toFixed(2)}`;
  elements.benchmarkHurdle.textContent = `r = ${scenario.hurdle.toFixed(2)}`;
  elements.benchmarkNet.textContent = `g - r = ${(scenario.benefit - scenario.hurdle).toFixed(2)}`;
  elements.benchmarkPrediction.textContent = prediction.toUpperCase();
  elements.initialAgreement.textContent = `Your recorded initial decision ${state.currentPlay.initialAgreesWithBenchmark ? "matches" : "differs from"} the benchmark.`;
  elements.benchmarkPanel.hidden = false;
  elements.finalSection.hidden = false;
  elements.initialError.textContent = "Initial decision and reflection are recorded for this play.";
}

function makeAggregateRecord(finalChoice) {
  const scenario = state.currentScenario;
  const prediction = benchmarkFor(scenario.benefit, scenario.hurdle);
  return {
    scenarioId: scenario.scenario_id,
    portabilityCondition: scenario.condition,
    benefit: scenario.benefit,
    hurdle: scenario.hurdle,
    benchmarkPrediction: prediction,
    initialChoice: state.currentPlay.initialChoice,
    finalChoice,
    changedChoice: finalChoice !== state.currentPlay.initialChoice,
    initialBenchmarkAgreement: state.currentPlay.initialAgreesWithBenchmark,
    finalBenchmarkAgreement: finalChoice === prediction,
    switchingDifficulty: state.currentPlay.ratings.difficulty,
    personalizationConcern: state.currentPlay.ratings.personalization,
    privacyConcern: state.currentPlay.ratings.privacy,
    trust: state.currentPlay.ratings.trust
  };
}

function summarize(records) {
  const count = records.length;
  if (count === 0) return null;
  const total = (field) => records.reduce((sum, record) => sum + record[field], 0);
  const countChoice = (choice) => records.filter((record) => record.finalChoice === choice).length;
  return {
    count,
    stay: countChoice("Stay"),
    switch: countChoice("Switch"),
    agreementRate: records.filter((record) => record.finalBenchmarkAgreement).length / count,
    difficulty: total("switchingDifficulty") / count,
    personalization: total("personalizationConcern") / count,
    privacy: total("privacyConcern") / count,
    trust: total("trust") / count
  };
}

function appendSummary(title, summary) {
  const block = document.createElement("section");
  block.className = "summary-block";
  const heading = document.createElement("h3");
  heading.textContent = title;
  block.appendChild(heading);
  if (!summary) {
    const empty = document.createElement("p");
    empty.textContent = "No earlier anonymous plays are available.";
    block.appendChild(empty);
  } else {
    const list = document.createElement("ul");
    list.className = "summary-list";
    [
      `Prior anonymous plays: ${summary.count}`,
      `Stay: ${summary.stay} (${Math.round((summary.stay / summary.count) * 100)}%)`,
      `Switch: ${summary.switch} (${Math.round((summary.switch / summary.count) * 100)}%)`,
      `Benchmark agreement: ${Math.round(summary.agreementRate * 100)}%`,
      `Mean switching difficulty: ${summary.difficulty.toFixed(2)} / 7`,
      `Mean personalization concern: ${summary.personalization.toFixed(2)} / 7`,
      `Mean privacy concern: ${summary.privacy.toFixed(2)} / 7`,
      `Mean trust in Assistant B: ${summary.trust.toFixed(2)} / 7`
    ].forEach((text) => { const item = document.createElement("li"); item.textContent = text; list.appendChild(item); });
    block.appendChild(list);
  }
  elements.peerSummaries.appendChild(block);
}

function renderPeerSnapshot(snapshot, record) {
  clearNode(elements.peerSummaries);
  elements.peerIntro.textContent = snapshot.overall ? "The summaries below include only plays submitted before yours in this browser session." : "No earlier anonymous plays are available in this browser session yet. No seed or fake peer data are shown.";
  const finalRelation = record.finalBenchmarkAgreement ? "matches" : "differs from";
  const current = document.createElement("p");
  current.textContent = `Your final decision: ${record.finalChoice}. Simplified benchmark: ${record.benchmarkPrediction}. Your final decision ${finalRelation} the benchmark.`;
  elements.peerSummaries.appendChild(current);
  appendSummary(`Same portability condition (${record.portabilityCondition})`, snapshot.sameCondition);
  appendSummary("Overall prior plays", snapshot.overall);
  elements.peerPanel.hidden = false;
}

function submitDecision() {
  if (state.stage !== FLOW.BENCHMARK_REVEALED) return;
  const finalChoice = selectedChoice("final-choice");
  if (!finalChoice) {
    elements.finalError.textContent = "Choose a final Stay or Switch decision before submitting.";
    return;
  }
  state.stage = FLOW.FINAL_DECISION;
  const record = makeAggregateRecord(finalChoice);
  const snapshot = {
    sameCondition: summarize(priorPlays.filter((play) => play.portabilityCondition === record.portabilityCondition)),
    overall: summarize(priorPlays)
  };
  priorPlays.push(record);
  state.stage = FLOW.SUBMITTED;
  setDisabled(elements.finalFieldset, true);
  elements.postReflection.disabled = true;
  elements.submitButton.disabled = true;
  elements.finalError.textContent = `Decision submitted once. You ${record.changedChoice ? "changed" : "kept"} your decision after the benchmark.`;
  renderPeerSnapshot(snapshot, record);
  elements.nextActions.hidden = false;
}

function clearPeerHistory() {
  if (!window.confirm("Clear only peer history from this current page session?")) return;
  priorPlays.splice(0, priorPlays.length);
  elements.historyStatus.textContent = "Browser-session peer history cleared. No information was sent anywhere.";
  if (state.stage === FLOW.SUBMITTED) {
    clearNode(elements.peerSummaries);
    elements.peerIntro.textContent = "No earlier anonymous plays are available in this browser session yet.";
  }
}

function showConfigurationError(error) {
  elements.main.hidden = true;
  elements.configurationError.hidden = false;
  elements.configurationErrorMessage.textContent = error instanceof Error ? error.message : "The scenario configuration could not be loaded.";
}

async function initialize() {
  try {
    const response = await fetch("./scenarios.json");
    if (!response.ok) throw new Error("The scenario configuration could not be loaded.");
    const scenarios = await response.json();
    validateScenarios(scenarios);
    state.scenarios = scenarios;
    createRatingInputs();
    renderScenario(chooseScenario(true));
    elements.revealButton.addEventListener("click", revealBenchmark);
    elements.submitButton.addEventListener("click", submitDecision);
    elements.newScenario.addEventListener("click", () => renderScenario(chooseScenario(false)));
    elements.clearHistory.addEventListener("click", clearPeerHistory);
  } catch (error) {
    showConfigurationError(error);
  }
}

initialize();
