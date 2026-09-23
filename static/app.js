const state = {
  current: null,
  pollUntil: 0,
  taskClickTimer: null,
  lastTaskClick: { taskId: "", at: 0 },
  pendingModel: "",
  refreshing: false,
  study: null,
  studyPromptDismissed: false,
  interactionResolve: null,
};

const els = {
  messages: document.querySelector("#messages"),
  form: document.querySelector("#chatForm"),
  input: document.querySelector("#messageInput"),
  variables: document.querySelector("#variables"),
  csvInput: document.querySelector("#csvInput"),
  uploadLabel: document.querySelector("#uploadLabel"),
  dataList: document.querySelector("#dataList"),
  references: document.querySelector("#references"),
  progressBar: document.querySelector("#progressBar"),
  progressText: document.querySelector("#progressText"),
  aggregates: document.querySelector("#aggregates"),
  activeQuestion: document.querySelector("#activeQuestion"),
  runAnalysis: document.querySelector("#runAnalysis"),
  modelStatus: document.querySelector("#modelStatus"),
  newTask: document.querySelector("#newTask"),
  taskList: document.querySelector("#taskList"),
  addVariable: document.querySelector("#addVariable"),
  settingsButton: document.querySelector("#settingsButton"),
  taskDialog: document.querySelector("#taskDialog"),
  settingsDialog: document.querySelector("#settingsDialog"),
  modelSelect: document.querySelector("#modelSelect"),
  modelInput: document.querySelector("#modelInput"),
  saveSettings: document.querySelector("#saveSettings"),
  pullModel: document.querySelector("#pullModel"),
  modelList: document.querySelector("#modelList"),
  ollamaLibrary: document.querySelector("#ollamaLibrary"),
  pullProgress: document.querySelector("#pullProgress"),
  pullProgressBar: document.querySelector("#pullProgressBar"),
  pullProgressText: document.querySelector("#pullProgressText"),
  evidenceDialog: document.querySelector("#evidenceDialog"),
  evidenceTitle: document.querySelector("#evidenceTitle"),
  evidenceSummary: document.querySelector("#evidenceSummary"),
  evidenceRows: document.querySelector("#evidenceRows"),
  closeEvidence: document.querySelector("#closeEvidence"),
  appShell: document.querySelector("#appShell"),
  consentGate: document.querySelector("#consentGate"),
  consentForm: document.querySelector("#consentForm"),
  consentContent: document.querySelector("#consentContent"),
  consentReviewContent: document.querySelector("#consentReviewContent"),
  preStudyQuestions: document.querySelector("#preStudyQuestions"),
  ageConfirmed: document.querySelector("#ageConfirmed"),
  consentAccepted: document.querySelector("#consentAccepted"),
  declineConsent: document.querySelector("#declineConsent"),
  enterStudy: document.querySelector("#enterStudy"),
  consentError: document.querySelector("#consentError"),
  studyButton: document.querySelector("#studyButton"),
  consentDialog: document.querySelector("#consentDialog"),
  closeConsent: document.querySelector("#closeConsent"),
  studyRecordSummary: document.querySelector("#studyRecordSummary"),
  reviewStudyQuestions: document.querySelector("#reviewStudyQuestions"),
  updateStudyResponses: document.querySelector("#updateStudyResponses"),
  withdrawConsent: document.querySelector("#withdrawConsent"),
  studyPrompt: document.querySelector("#studyPrompt"),
  duringStudyQuestions: document.querySelector("#duringStudyQuestions"),
  saveStudyResponses: document.querySelector("#saveStudyResponses"),
  dismissStudyPrompt: document.querySelector("#dismissStudyPrompt"),
  selectedModelSummary: document.querySelector("#selectedModelSummary"),
  interactionDialog: document.querySelector("#interactionDialog"),
  interactionForm: document.querySelector("#interactionForm"),
  interactionEyebrow: document.querySelector("#interactionEyebrow"),
  interactionTitle: document.querySelector("#interactionTitle"),
  interactionMessage: document.querySelector("#interactionMessage"),
  interactionField: document.querySelector("#interactionField"),
  interactionLabel: document.querySelector("#interactionLabel"),
  interactionInput: document.querySelector("#interactionInput"),
  interactionTextarea: document.querySelector("#interactionTextarea"),
  closeInteraction: document.querySelector("#closeInteraction"),
  cancelInteraction: document.querySelector("#cancelInteraction"),
  confirmInteraction: document.querySelector("#confirmInteraction"),
};

const consentMarkup = `
  <section class="consent-section">
    <h2>Purpose of the study</h2>
    <p>You are invited to participate in a research study evaluating the usability and user experience of an AI-based interface developed using existing open-access models without fine-tuning. The study examines how people interact with the system and whether its outputs are useful for supporting data-informed decisions based on library survey data.</p>
  </section>
  <section class="consent-section">
    <h2>What you will do</h2>
    <p>You will load a CSV file containing library survey comments after removing personally identifiable information and data from anyone under age 18. You may enter your own prompts or use predefined prompts, rate AI-generated results, and complete a short optional questionnaire. The expected time is still to be finalized in the approved consent form.</p>
  </section>
  <section class="consent-section">
    <h2>Risks, privacy, and benefits</h2>
    <p>This study is expected to involve minimal risk, such as minor inconvenience or fatigue. Analysis runs locally through Ollama. Remove personally identifiable information before loading data. Responses are stored locally and reported in aggregate. There are no direct benefits, though your participation may help improve AI tools for academic libraries.</p>
  </section>
  <section class="consent-section">
    <h2>Voluntary participation</h2>
    <p>Participation is voluntary. You may refuse or stop at any time without penalty. No personally identifiable information will be included in publications or presentations unless explicitly authorized.</p>
  </section>
  <section class="consent-section contact-block">
    <h2>Questions</h2>
    <p>This is a development preview. Replace this text with the applicable study contacts and approved consent information before enabling it for participants.</p>
  </section>`;

function icon(name) {
  const paths = {
    up: '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/>',
    down: '<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/>',
    note: '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"/><path d="M8 8h8M8 12h5"/>',
    x: '<path d="m18 6-12 12M6 6l12 12"/>',
    plus: '<path d="M5 12h14M12 5v14"/>',
    trash: '<path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6M10 11v5M14 11v5"/>',
    play: '<path d="m6 3 14 9-14 9Z"/>',
    send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"/><path d="M17 21v-8H7v8M7 3v5h8"/>',
    download: '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
    file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    check: '<path d="m20 6-11 11-5-5"/>',
    folder: '<path d="M3 7h6l2 2h10v10H3Z"/>',
  };
  return `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[name] || ""}</svg>`;
}

function buttonMarkup(iconName, label) {
  return `${icon(iconName)}${label ? `<span>${escapeHtml(label)}</span>` : ""}`;
}

function decorateButton(element, iconName) {
  if (!element || element.querySelector("svg")) return;
  const label = element.textContent.trim();
  element.innerHTML = buttonMarkup(iconName, label);
}

function decorateIconOnly(element, iconName) {
  if (element) element.innerHTML = icon(iconName);
}

function decorateStaticButtons() {
  [
    [els.newTask, "plus"],
    [els.runAnalysis, "play"],
    [els.addVariable, "plus"],
    [els.saveStudyResponses, "save"],
    [els.saveSettings, "save"],
    [els.pullModel, "download"],
    [els.withdrawConsent, "logout"],
    [els.updateStudyResponses, "save"],
    [els.enterStudy, "check"],
    [els.declineConsent, "x"],
    [els.form?.querySelector('button[type="submit"]'), "send"],
    [els.cancelInteraction, "x"],
    [els.confirmInteraction, "save"],
  ].forEach(([element, iconName]) => decorateButton(element, iconName));
  [els.closeEvidence, els.closeConsent, els.dismissStudyPrompt, els.closeInteraction]
    .forEach((element) => decorateIconOnly(element, "x"));
  document.querySelectorAll('.modal button[value="cancel"]').forEach((element) => decorateIconOnly(element, "x"));
}

function finishInteraction(value) {
  const resolve = state.interactionResolve;
  state.interactionResolve = null;
  if (els.interactionDialog.open) els.interactionDialog.close();
  resolve?.(value);
}

function openInteraction({
  title,
  eyebrow = "Update",
  message = "",
  label = "Value",
  value = "",
  placeholder = "",
  confirmLabel = "Save",
  mode = "text",
  danger = false,
}) {
  if (state.interactionResolve) finishInteraction(null);
  els.interactionEyebrow.textContent = eyebrow;
  els.interactionTitle.textContent = title;
  els.interactionMessage.textContent = message;
  els.interactionMessage.hidden = !message;
  els.interactionField.hidden = mode === "confirm";
  els.interactionLabel.textContent = label;
  els.interactionInput.hidden = mode === "multiline";
  els.interactionTextarea.hidden = mode !== "multiline";
  const field = mode === "multiline" ? els.interactionTextarea : els.interactionInput;
  field.value = value;
  field.placeholder = placeholder;
  els.confirmInteraction.classList.toggle("danger-confirm", danger);
  els.confirmInteraction.innerHTML = buttonMarkup(danger ? "trash" : "save", confirmLabel);
  els.interactionDialog.showModal();
  if (mode !== "confirm") requestAnimationFrame(() => {
    field.focus();
    field.select();
  });
  return new Promise((resolve) => {
    state.interactionResolve = resolve;
  });
}

async function api(path, options = {}) {
  options.headers = {...options.headers, ...(state.current?.task_id ? {'X-Task-ID': state.current.task_id} : {})};
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.text();
    try {
      throw new Error(JSON.parse(body).error || response.statusText);
    } catch (error) {
      if (error instanceof SyntaxError) throw new Error(body || response.statusText);
      throw error;
    }
  }
  return response.json();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function answerValue(questionId) {
  return state.study?.responses?.[questionId]?.value || "";
}

function renderQuestion(question, context) {
  const name = `${context}-${question.id}`;
  const value = answerValue(question.id);
  const inferred = state.study?.responses?.[question.id]?.source === "model_inferred";
  if (question.type === "text" || question.type === "email") {
    return `
      <label class="question-field ${question.id.startsWith("contact_") ? "contact-question" : ""}">
        <span>${escapeHtml(question.label)} <small>optional</small></span>
        <input type="${question.type}" name="${escapeHtml(name)}" data-question-id="${escapeHtml(question.id)}" value="${escapeHtml(value)}" />
      </label>`;
  }
  return `
    <fieldset class="question-field">
      <legend>${escapeHtml(question.label)} ${question.optional ? "<small>optional</small>" : ""}</legend>
      <div class="choice-row ${question.type === "scale" ? "scale-row" : ""}">
        ${question.options.map((option) => `
          <label class="choice-chip">
            <input type="radio" name="${escapeHtml(name)}" data-question-id="${escapeHtml(question.id)}" value="${escapeHtml(option)}" ${option === value ? "checked" : ""} />
            <span>${escapeHtml(option)}</span>
          </label>`).join("")}
      </div>
      ${inferred ? '<small class="inferred-answer">Detected from chat; review if needed.</small>' : ""}
    </fieldset>`;
}

function renderStudyQuestions() {
  const questions = state.study?.questions || [];
  const before = questions.filter((item) => item.phase === "before");
  const after = questions.filter((item) => item.phase === "after");
  els.preStudyQuestions.innerHTML = before.map((item) => renderQuestion(item, "pre")).join("");
  els.duringStudyQuestions.innerHTML = after.map((item) => renderQuestion(item, "during")).join("");
  els.reviewStudyQuestions.innerHTML = questions.map((item) => renderQuestion(item, "review")).join("");
  const participant = state.study?.participant_id;
  els.studyRecordSummary.innerHTML = participant
    ? `<strong>Participant code</strong><code>${escapeHtml(participant.slice(0, 8))}</code><span>Stored locally on this computer</span>`
    : "";
}

function collectResponses(container) {
  const responses = {};
  container.querySelectorAll("[data-question-id]").forEach((input) => {
    if ((input.type === "radio" || input.type === "checkbox") && !input.checked) return;
    if (input.value.trim()) responses[input.dataset.questionId] = input.value.trim();
  });
  return responses;
}

async function refreshStudy() {
  state.study = await api("/api/study/status");
  renderStudyQuestions();
  return state.study;
}

function renderMessages(messages) {
  els.messages.innerHTML = messages
    .map(
      (message) => `
        <div class="message ${message.role}">
          <span class="message-avatar">${message.role === "user" ? "U" : "AI"}</span>
          <div class="message-body">${escapeHtml(message.content)}</div>
        </div>
      `,
    )
    .join("");
  els.messages.scrollTop = els.messages.scrollHeight;
}

function renderTasks(tasks, currentTaskId) {
  if (!tasks?.length) {
    els.taskList.innerHTML = "";
    return;
  }
  els.taskList.innerHTML = tasks
    .map((task) => {
      const active = task.task_id === currentTaskId ? "active" : "";
      const status = task.complete ? "complete" : `${task.messages || 0} turns`;
      return `
        <div class="task-item ${active}" data-task-id="${escapeHtml(task.task_id)}">
          <button class="task-open" type="button" data-task-id="${escapeHtml(task.task_id)}" data-title="${escapeHtml(task.title || "Untitled task")}">
            <strong class="task-title">${escapeHtml(task.title || "Untitled task")}</strong>
            <span>${escapeHtml(status)}</span>
          </button>
          <button class="task-delete" type="button" data-task-id="${escapeHtml(task.task_id)}" data-title="${escapeHtml(task.title || "Untitled task")}" aria-label="Remove ${escapeHtml(task.title || "Untitled task")}">${icon("x")}</button>
        </div>
      `;
    })
    .join("");
}

function startTaskRename(open) {
  clearTimeout(state.taskClickTimer);
  const item = open.closest(".task-item");
  if (!item) return;
  const title = open.dataset.title || "Untitled task";
  item.classList.add("editing");
  item.innerHTML = `
    <input class="task-edit-input" value="${escapeHtml(title)}" />
    <button class="task-delete" type="button" data-task-id="${escapeHtml(open.dataset.taskId)}" data-title="${escapeHtml(title)}" aria-label="Remove ${escapeHtml(title)}">${icon("x")}</button>
  `;
  const input = item.querySelector(".task-edit-input");
  input.focus();
  input.select();
}

function renderTemplates(templates = []) {
  const grid = els.taskDialog.querySelector(".template-grid");
  const cards = templates
    .map(
      (template) => `
        <button class="template-card" type="button" data-template-id="${escapeHtml(template.id)}">
          ${icon("file")}
          <strong>${escapeHtml(template.name)}</strong>
          <span>${escapeHtml(template.description)}</span>
        </button>
      `,
    )
    .join("");
  grid.innerHTML = `
    <button class="template-card" type="button" data-template-id="">
      ${icon("file")}<strong>Blank task</strong>
      <span>Start with no prompt, variables, labels, or data.</span>
    </button>
    ${cards}
  `;
}

function renderSettings(model) {
  if (!model) return;
  const preferred = ['qwen3.5:9b', 'qwen3:8b', 'mistral:latest', 'qwen3.5:4b', 'gemma4:31b'];
  const installed = (model.installed || []).filter(item => !item.name.toLowerCase().includes('cloud') && (!item.capabilities?.length || item.capabilities.includes('completion'))).sort((a,b) => (preferred.includes(a.name) ? preferred.indexOf(a.name) : 99) - (preferred.includes(b.name) ? preferred.indexOf(b.name) : 99));
  const recommendations = {'qwen3.5:9b': 'Recommended starting point. Check results against original comments.', 'qwen3:8b': 'Alternative local model; compare on your data.', 'gemma4:31b': 'Larger model; requires more memory and time.', 'qwen3.5:4b': 'Lower-memory candidate; validate accuracy on your data.', 'mistral:latest': 'Smaller comparison model; validate accuracy on your data.', 'qwen3.5:27b': 'Larger model for machines with more memory.'};
  const pull = model.pull || {};
  els.ollamaLibrary.href = model.library_url || "https://ollama.com/library";
  const selectedModel = state.pendingModel || model.selected;
  const fitLabel = (item) => {
    const gb = Number(item.size || 0) / 1024 / 1024 / 1024;
    if (!gb) return "Local";
    if (gb <= 5) return "Lightweight";
    if (gb <= 8) return "Good fit for 16 GB+";
    if (gb <= 14) return "Best with 24 GB+";
    return "Best with 32 GB+";
  };
  els.modelSelect.innerHTML = installed.length
    ? installed
        .map((item) => {
          const name = item.name || item.model;
          return `<option value="${escapeHtml(name)}" ${name === selectedModel ? "selected" : ""}>${escapeHtml(name)}</option>`;
        })
        .join("")
    : `<option value="${escapeHtml(model.selected || "mistral")}">${escapeHtml(model.selected || "mistral")}</option>`;
  const selectedItem = installed.find((item) => (item.name || item.model) === selectedModel);
  if (selectedItem) {
    const details = selectedItem.details || {};
    const size = selectedItem.size ? `${(selectedItem.size / 1024 / 1024 / 1024).toFixed(1)} GB on disk` : "Stored locally";
    els.selectedModelSummary.innerHTML = `<strong>${escapeHtml(selectedModel)}</strong><span>${escapeHtml([details.parameter_size, details.quantization_level, size].filter(Boolean).join(" · "))}</span>`;
  } else {
    els.selectedModelSummary.innerHTML = `<strong>${escapeHtml(selectedModel || "No model selected")}</strong><span>Start Ollama to inspect local model details.</span>`;
  }
  els.modelList.innerHTML = installed.length
    ? installed
        .map((item) => {
          const name = item.name || item.model;
          const details = item.details || {};
          const size = item.size ? `${Math.round(item.size / 1024 / 1024 / 1024)} GB` : "local";
          const tags = (item.tags || [details.family, details.parameter_size, details.quantization_level].filter(Boolean)).filter(Boolean);
          const tagMarkup = tags.map((tag) => `<span class="model-tag">${escapeHtml(tag)}</span>`).join("");
          const description = recommendations[name] || item.description || "Local model; evaluate before use.";
          return `
            <button class="model-item ${name === selectedModel ? "selected" : ""}" type="button" data-model-name="${escapeHtml(name)}">
              <span class="model-title"><strong>${escapeHtml(item.name || item.model)}</strong><em>${escapeHtml(fitLabel(item))}</em></span>
              <span>${escapeHtml(size)}${item.modified_at ? ` · Local update ${escapeHtml(item.modified_at.split("T")[0])}` : ""}</span>
              <p>${escapeHtml(description)}</p>
              <div class="model-tags">${tagMarkup}</div>
            </button>
          `;
        })
        .join("")
    : `<div class="model-item"><strong>No local models listed</strong><span>Start Ollama or pull a model.</span></div>`;
  const showProgress = pull.running || pull.status === "Pull complete" || pull.error;
  els.pullProgress.hidden = !showProgress;
  els.pullProgressBar.style.width = `${pull.percent || 0}%`;
  els.pullProgressText.textContent = pull.error
    ? `${pull.status}: ${pull.error}`
    : `${pull.model ? `${pull.model}: ` : ""}${pull.status || "Idle"}${pull.total ? ` (${pull.percent || 0}%)` : ""}`;
  els.pullModel.disabled = !!pull.running;
  els.pullModel.innerHTML = buttonMarkup("download", pull.running ? "Pulling..." : "Pull");
}

function renderVariables(variables) {
  if (!variables.length) {
    els.variables.innerHTML = `
      <article class="variable-card empty-state">
        <header>
          <strong>No topics yet</strong>
          <span class="clarity review">waiting</span>
        </header>
        <div class="labels">
          <span class="label">ask an analysis question</span>
        </div>
      </article>
    `;
    return;
  }
  els.variables.innerHTML = variables
    .map((variable) => {
      const clarityClass = variable.clarity === "ready" ? "ready" : variable.clarity.includes("review") ? "review" : "";
      const labels = variable.labels || [];
      const renderedLabels = labels.length
        ? labels
            .map(
              (label) => `
                <span class="label editable-label">
                  <button class="label-name" type="button" data-action="rename-label" data-variable="${escapeHtml(variable.name)}" data-label="${escapeHtml(label)}">${escapeHtml(label)}</button>
                  <button class="chip-remove" type="button" data-action="remove-label" data-variable="${escapeHtml(variable.name)}" data-label="${escapeHtml(label)}" aria-label="Remove ${escapeHtml(label)}">${icon("x")}</button>
                </span>
              `,
            )
            .join("")
        : `<span class="label">labels pending</span>`;
      return `
        <article class="variable-card">
          <header>
            <button class="variable-name" type="button" data-action="rename-variable" data-variable="${escapeHtml(variable.name)}">${escapeHtml(variable.name)}</button>
            <span class="clarity ${clarityClass}">${escapeHtml(variable.clarity)}</span>
          </header>
          <div class="labels">${renderedLabels}</div>
          <div class="variable-actions">
            ${labels.length && variable.clarity !== 'ready' ? `<button class="mini-button" type="button" data-action="approve-labels" data-variable="${escapeHtml(variable.name)}" title="Use only this label list">${buttonMarkup('check', 'Confirm')}</button>` : ''}
            <button class="mini-button" type="button" data-action="add-label" data-variable="${escapeHtml(variable.name)}">${buttonMarkup("plus", "Label")}</button>
            <button class="mini-button danger" type="button" data-action="remove-variable" data-variable="${escapeHtml(variable.name)}">${buttonMarkup("trash", "Remove")}</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderDataSources(sources) {
  els.uploadLabel.innerHTML = buttonMarkup("folder", "Load CSV Data");
  els.uploadLabel.title = sources.length ? "Replace the active dataset and clear its prior results" : "Select a CSV dataset";
  els.dataList.innerHTML = sources
    .map(
      (source) => `
        <div class="data-item">
          <strong>${escapeHtml(source.filename)}</strong>
          <span>${source.rows} rows</span>
          <select data-source="${escapeHtml(source.id)}">
            ${source.columns
              .map(
                (column) =>
                  `<option value="${escapeHtml(column)}" ${column === source.text_column ? "selected" : ""}>${escapeHtml(column)}</option>`,
              )
              .join("")}
          </select>
        </div>
      `,
    )
    .join("");

  els.dataList.querySelectorAll("select").forEach((select) => {
    select.addEventListener("change", async () => {
      const payload = {
        source_id: select.dataset.source,
        text_column: select.value,
      };
      const next = await api("/api/text-column", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      await refresh(next.state);
    });
  });
}

function renderReferences(sources) {
  if (!sources.length) {
    els.references.innerHTML = `<span class="ref-chip">No data loaded</span>`;
    return;
  }
  els.references.innerHTML = sources
    .map((source) => `<span class="ref-chip">${escapeHtml(source.filename)} · ${source.rows} rows · ${escapeHtml(source.text_column)}</span>`)
    .join("");
}

function renderProgress(job) {
  const total = job.total || 0;
  const processed = job.processed || 0;
  const pct = total ? Math.round((processed / total) * 100) : 0;
  els.progressBar.style.width = `${pct}%`;
  const fallback = job.fallback_count ? ` · ${job.fallback_count} unclassified during analysis` : "";
  const issue = job.issues?.length ? ` · ${job.issues.at(-1)}` : "";
  els.progressText.textContent = total ? `${job.message}: ${processed}/${total}${fallback}${issue}` : job.message || "Idle";
  if (state.current?.results_stale) els.progressText.textContent += " · Topics changed: rerun to refresh results";
  document.querySelector('#cancelAnalysis').hidden = !job.running;
  document.querySelector('#reviewRows').disabled = !processed || !!job.running || !!state.current?.results_stale;
  document.querySelector('#exportReview').disabled = !processed || !!job.running;
  els.runAnalysis.disabled = !!job.running;
  els.runAnalysis.innerHTML = buttonMarkup("play", job.running ? "Analyzing..." : "Run analysis");
  els.csvInput.disabled = !!job.running;
  els.variables.querySelectorAll('button').forEach(button => { button.disabled = !!job.running; });
  els.addVariable.disabled = !!job.running;
  els.uploadLabel.classList.toggle("disabled", !!job.running);
  const shouldShowStudyPrompt = state.study?.enabled && !!job.complete && !state.studyPromptDismissed;
  els.studyPrompt.hidden = !shouldShowStudyPrompt;
}

function feedbackRating(variable, label) {
  return (state.current?.feedback || []).find((item) => item.variable === variable && item.label === label)?.rating;
}

function renderAggregates(results) {
  const keys = Object.keys(results || {});
  if (!keys.length) {
    els.aggregates.innerHTML = `<p class="muted">No aggregate results yet.</p>`;
    return;
  }
  els.aggregates.innerHTML = keys
    .map((key) => {
      const counts = results[key].counts || {};
      const quotes = results[key].sample_quotes || {};
      const rows = Object.entries(counts)
        .map(([label, count]) => {
          const evidence = (quotes[label] || [])[0];
          const quote = typeof evidence === "string" ? evidence : evidence?.text;
          const rating = feedbackRating(key, label);
          const notes = (state.current.feedback_events || []).filter(item => item.job_id === state.current.analysis_job.job_id && item.variable === key && item.label === label && item.comment);
          return `
            <div class="count-row">
              <button class="result-label" type="button" data-action="show-evidence" data-variable="${escapeHtml(key)}" data-label="${escapeHtml(label)}">${escapeHtml(label)}</button>
              <strong>${count}</strong>
              <span class="result-feedback" aria-label="Rate this result">
                <button class="feedback-button ${rating === "up" ? "selected" : ""}" type="button" data-action="feedback" data-rating="up" data-variable="${escapeHtml(key)}" data-label="${escapeHtml(label)}" title="Useful" aria-label="Useful" aria-pressed="${rating === "up"}">${icon("up")}</button>
                <button class="feedback-button ${rating === "down" ? "selected" : ""}" type="button" data-action="feedback" data-rating="down" data-variable="${escapeHtml(key)}" data-label="${escapeHtml(label)}" title="Not useful" aria-label="Not useful" aria-pressed="${rating === "down"}">${icon("down")}</button>
                <button class="feedback-button" type="button" data-action="feedback-note" data-variable="${escapeHtml(key)}" data-label="${escapeHtml(label)}" title="Add optional feedback note" aria-label="Add optional feedback note">${icon("note")}</button>
              </span>
            </div>
            ${quote ? `<p class="quote">${escapeHtml(quote)}</p>` : ""}
            ${notes.length ? `<details><summary>${notes.length} feedback note${notes.length === 1 ? '' : 's'}</summary>${notes.map(note => `<p>${escapeHtml(note.comment)}</p>`).join('')}</details>` : ''}
          `;
        })
        .join("");
      return `
        <article class="aggregate-card">
          <h3>${escapeHtml(key)}</h3>
          ${rows}
        </article>
      `;
    })
    .join("");
}

async function refresh(nextState) {
  if (state.refreshing && !nextState) return;
  state.refreshing = true;
  try {
    state.current = nextState || (await api("/api/state"));
  renderTasks(state.current.tasks || [], state.current.task_id);
  renderTemplates(state.current.templates || []);
  renderMessages(state.current.messages || []);
  renderVariables(state.current.variables || []);
  renderDataSources(state.current.data_sources || []);
  renderReferences(state.current.data_sources || []);
  renderProgress(state.current.analysis_job || {});
  renderAggregates(state.current.aggregate_results || {});
  els.activeQuestion.textContent = "Discover insights from text through human-AI conversations.";
  const model = state.current.model;
  els.modelStatus.textContent = model ? `${model.provider}: ${model.model}` : "Ollama if available, keyword fallback otherwise";
    renderSettings(model);
  } finally {
    state.refreshing = false;
  }
}

function reportError(error) {
  els.progressText.textContent = error?.message || "Something went wrong.";
}

window.addEventListener('unhandledrejection', event => {
  reportError(event.reason);
  event.preventDefault();
});

async function variableAction(payload) {
  const next = await api("/api/variables", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await refresh(next);
}

async function saveResponses(container) {
  const next = await api("/api/study/responses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses: collectResponses(container) }),
  });
  state.study = next;
  renderStudyQuestions();
}

els.interactionForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (els.interactionField.hidden) {
    finishInteraction(true);
    return;
  }
  const field = els.interactionTextarea.hidden ? els.interactionInput : els.interactionTextarea;
  finishInteraction(field.value.trim());
});

els.cancelInteraction.addEventListener("click", () => finishInteraction(null));
els.closeInteraction.addEventListener("click", () => finishInteraction(null));
els.interactionDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  finishInteraction(null);
});
els.interactionDialog.addEventListener("close", () => {
  if (state.interactionResolve) finishInteraction(null);
});

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = els.input.value.trim();
  if (!message) return;
  els.input.value = "";
  const next = await api("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (/run analysis|analy[sz]e|analyse|start/i.test(message)) {
    state.pollUntil = Date.now() + 30000;
  }
  await refreshStudy();
  await refresh(next.state);
});

els.runAnalysis.addEventListener("click", async () => {
  const next = await api("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "run analysis" }),
  });
  state.pollUntil = Date.now() + 30000;
  await refresh(next.state);
});

els.csvInput.addEventListener("change", async () => {
  const file = els.csvInput.files[0];
  if (!file) return;
  const body = new FormData();
  body.append("file", file);
  try {
    const next = await fetch("/api/upload", { method: "POST", body, headers: {'X-Task-ID': state.current.task_id} });
    const payload = await next.json();
    if (!next.ok) throw new Error(payload.error || next.statusText);
    await refresh(payload.state);
  } catch (error) {
    reportError(error);
  } finally {
    els.csvInput.value = "";
  }
});

els.newTask.addEventListener("click", async () => {
  els.taskDialog.showModal();
});

els.taskDialog.addEventListener("click", async (event) => {
  const card = event.target.closest(".template-card");
  if (!card) return;
  const next = await api("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "new", template_id: card.dataset.templateId || null }),
  });
  els.taskDialog.close();
  await refresh(next);
});

els.taskList.addEventListener("click", async (event) => {
  const remove = event.target.closest(".task-delete");
  if (remove) {
    const title = remove.dataset.title || "this task";
    const confirmed = await openInteraction({
      title: "Remove task?",
      eyebrow: "Confirm removal",
      message: `“${title}” and its saved conversation, data reference, and results will be removed.`,
      confirmLabel: "Remove task",
      mode: "confirm",
      danger: true,
    });
    if (!confirmed) return;
    const next = await api("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "delete", task_id: remove.dataset.taskId }),
    });
    await refresh(next);
    return;
  }
  const button = event.target.closest(".task-open[data-task-id]");
  if (!button) return;
  const now = Date.now();
  const isRapidSecondClick =
    state.lastTaskClick.taskId === button.dataset.taskId && now - state.lastTaskClick.at < 500;
  state.lastTaskClick = { taskId: button.dataset.taskId, at: now };
  if (event.detail >= 2 || isRapidSecondClick) {
    event.preventDefault();
    startTaskRename(button);
    return;
  }
  if (button.closest(".task-item")?.classList.contains("active")) return;
  clearTimeout(state.taskClickTimer);
  state.taskClickTimer = setTimeout(async () => {
    const next = await api("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "switch", task_id: button.dataset.taskId }),
    });
    await refresh(next);
  }, 220);
});

els.taskList.addEventListener("dblclick", (event) => {
  const open = event.target.closest(".task-open[data-task-id]");
  if (!open) return;
  event.preventDefault();
  startTaskRename(open);
});

els.taskList.addEventListener("keydown", async (event) => {
  const input = event.target.closest(".task-edit-input");
  if (!input) return;
  const item = input.closest(".task-item");
  if (event.key === "Escape") {
    await refresh();
  }
  if (event.key === "Enter") {
    const title = input.value.trim();
    if (!title) return;
    const next = await api("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "rename", task_id: item.dataset.taskId, title }),
    });
    await refresh(next);
  }
});

els.settingsButton.addEventListener("click", async () => {
  await refresh();
  document.querySelector('#batchSize').value = state.current.model.batch_size;
  document.querySelector('#contextLength').value = state.current.model.context_length;
  els.settingsDialog.showModal();
});

els.consentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  els.consentError.textContent = "";
  try {
    const next = await api("/api/study/consent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        accepted: els.consentAccepted.checked,
        age_confirmed: els.ageConfirmed.checked,
        responses: collectResponses(els.preStudyQuestions),
      }),
    });
    if (!next.consented) throw new Error("Consent is required to enter the study application.");
    state.study = next;
    renderStudyQuestions();
    els.consentGate.hidden = true;
    await refresh();
    els.appShell.hidden = false;
  } catch (error) {
    els.consentError.textContent = error.message;
  }
});

els.declineConsent.addEventListener("click", async () => {
  try {
    await api("/api/study/consent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ accepted: false, age_confirmed: false }),
    });
  } finally {
    els.consentForm.innerHTML = '<div class="decline-message"><h2>Thank you for considering the study.</h2><p>You chose not to participate. You may close this page.</p></div>';
  }
});

els.studyButton.addEventListener("click", async () => {
  await refreshStudy();
  els.consentDialog.showModal();
});

els.closeConsent.addEventListener("click", () => els.consentDialog.close());
els.updateStudyResponses.addEventListener("click", async () => {
  await saveResponses(els.reviewStudyQuestions);
  els.consentDialog.close();
});
els.withdrawConsent.addEventListener("click", async () => {
  const confirmed = await openInteraction({
    title: "Withdraw consent?",
    eyebrow: "Research participation",
    message: "You will leave the study application. The research team’s approved withdrawal and data-retention procedures still apply to information already collected.",
    confirmLabel: "Withdraw consent",
    mode: "confirm",
    danger: true,
  });
  if (!confirmed) return;
  state.study = await api("/api/study/consent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accepted: false, age_confirmed: false }),
  });
  els.consentDialog.close();
  els.appShell.hidden = true;
  els.consentGate.hidden = false;
  els.ageConfirmed.checked = false;
  els.consentAccepted.checked = false;
  els.consentError.textContent = "Consent was withdrawn. The analysis workspace is no longer available.";
});
els.saveStudyResponses.addEventListener("click", async () => {
  await saveResponses(els.duringStudyQuestions);
  state.studyPromptDismissed = true;
  els.studyPrompt.hidden = true;
});
els.dismissStudyPrompt.addEventListener("click", () => {
  state.studyPromptDismissed = true;
  els.studyPrompt.hidden = true;
});

els.modelSelect.addEventListener("change", async () => {
  state.pendingModel = els.modelSelect.value;
  renderSettings(state.current.model);
});

els.modelList.addEventListener("click", (event) => {
  const item = event.target.closest("[data-model-name]");
  if (!item) return;
  state.pendingModel = item.dataset.modelName;
  els.modelSelect.value = state.pendingModel;
  renderSettings(state.current.model);
});

els.saveSettings.addEventListener("click", async () => {
  const selected = els.modelSelect.value;
  if (!selected) return;
  const next = await api("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "select_model", model: selected, batch_size: Number(document.querySelector('#batchSize').value), context_length: Number(document.querySelector('#contextLength').value) }),
  });
  state.pendingModel = "";
  await refresh(next);
  els.settingsDialog.close();
});

els.pullModel.addEventListener("click", async () => {
  const selected = els.modelInput.value.trim();
  if (!selected) return;
  const next = await api("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "pull_model", model: selected }),
  });
  els.modelInput.value = "";
  await refresh(next);
});

els.aggregates.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const variable = button.dataset.variable;
  const label = button.dataset.label;
  try {
    if (button.dataset.action === "show-evidence") {
      const payload = await api(`/api/evidence?variable=${encodeURIComponent(variable)}&label=${encodeURIComponent(label)}`);
      els.evidenceTitle.textContent = label;
      els.evidenceSummary.textContent = `${payload.rows.length} source comment${payload.rows.length === 1 ? "" : "s"} · ${variable}`;
      els.evidenceRows.innerHTML = payload.rows.length
        ? payload.rows.map((row) => `
            <article class="evidence-row">
              <strong>Row ${Number(row.row_index) + 1}</strong>
              <p>${escapeHtml(row.text)}</p>
              ${row.rationale ? `<small>${escapeHtml(row.rationale)}</small>` : ""}
            </article>
          `).join("")
        : `<p class="muted">No matching source comments were found.</p>`;
      els.evidenceDialog.showModal();
    }
    if (button.dataset.action === "feedback") {
      const next = await api("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variable, label, rating: button.dataset.rating }),
      });
      await refresh(next);
    }
    if (button.dataset.action === "feedback-note") {
      const comment = await openInteraction({
        title: "Add a feedback note",
        eyebrow: "Optional result feedback",
        message: `Share what seems accurate, unclear, or worth correcting for “${label}”.`,
        label: "Comment",
        placeholder: "Type an optional comment about this result",
        confirmLabel: "Save note",
        mode: "multiline",
      });
      if (!comment?.trim()) return;
      const next = await api("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variable, label, comment: comment.trim() }),
      });
      await refresh(next);
    }
  } catch (error) {
    reportError(error);
  }
});

els.closeEvidence.addEventListener("click", () => els.evidenceDialog.close());

els.addVariable.addEventListener("click", async () => {
  const name = await openInteraction({
    title: "Add a topic",
    message: "Add a concept that should be identified in each comment.",
    label: "Topic name",
    placeholder: "Example: service area",
    confirmLabel: "Add topic",
  });
  if (!name) return;
  await variableAction({ action: "add_variable", name });
});

els.variables.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  const variable = button.dataset.variable;

  if (action === 'approve-labels') await variableAction({action: 'approve_labels', name: variable});
  if (action === "rename-variable") {
    const newName = await openInteraction({
      title: "Rename topic",
      label: "Topic name",
      value: variable,
      confirmLabel: "Rename topic",
    });
    if (!newName || newName === variable) return;
    await variableAction({ action: "rename_variable", name: variable, new_name: newName });
  }

  if (action === "remove-variable") {
    const confirmed = await openInteraction({
      title: "Remove topic?",
      eyebrow: "Confirm removal",
      message: `“${variable}” and its labels will be removed from this task.`,
      confirmLabel: "Remove topic",
      mode: "confirm",
      danger: true,
    });
    if (!confirmed) return;
    await variableAction({ action: "remove_variable", name: variable });
  }

  if (action === "add-label") {
    const label = await openInteraction({
      title: "Add a label",
      message: `Add a possible value for “${variable}”.`,
      label: "Label",
      placeholder: "Enter a label",
      confirmLabel: "Add label",
    });
    if (!label) return;
    await variableAction({ action: "add_label", name: variable, label });
  }

  if (action === "rename-label") {
    const oldLabel = button.dataset.label;
    const newLabel = await openInteraction({
      title: "Edit label",
      label: "Label",
      value: oldLabel,
      confirmLabel: "Save label",
    });
    if (!newLabel || newLabel === oldLabel) return;
    await variableAction({ action: "rename_label", name: variable, old_label: oldLabel, new_label: newLabel });
  }

  if (action === "remove-label") {
    const label = button.dataset.label;
    await variableAction({ action: "remove_label", name: variable, label });
  }
});

setInterval(async () => {
  try {
    if (state.current?.analysis_job?.running || Date.now() < state.pollUntil || state.current?.model?.pull?.running) {
      await refresh();
    }
  } catch (error) {
    reportError(error);
  }
}, 1500);

async function bootstrap() {
  decorateStaticButtons();
  els.consentContent.innerHTML = consentMarkup;
  els.consentReviewContent.innerHTML = consentMarkup;
  const study = await refreshStudy();
  els.studyButton.hidden = !study.enabled;
  if (study.enabled && !study.consented) {
    els.consentGate.hidden = false;
    els.appShell.hidden = true;
    return;
  }
  els.consentGate.hidden = true;
  await refresh();
  els.appShell.hidden = false;
}

document.querySelector('#cancelAnalysis').innerHTML = buttonMarkup('x', 'Stop');
document.querySelector('#reviewRows').innerHTML = buttonMarkup('file', 'Review comments');
document.querySelector('#exportReview').innerHTML = icon('download');
document.querySelector('#cancelAnalysis').addEventListener('click', async () => {
  try { await refresh(await api('/api/cancel', {method: 'POST'})); } catch (error) { reportError(error); }
});
document.querySelector('#exportReview').addEventListener('click', async () => {
  const proceed = await openInteraction({title: 'Export analysis and feedback', message: 'This local file includes original comments, your question, model settings, results, and feedback history. Store it with your protected research data.', confirmLabel: 'Download', mode: 'confirm'});
  if (proceed) window.location.href = '/api/review.json';
});
document.querySelector('#reviewRows').addEventListener('click', async () => {
  try {
    const payload = await api('/api/rows');
    els.evidenceTitle.textContent = 'Review and correct comments';
    els.evidenceSummary.textContent = 'Corrections update counts immediately. Ratings record usefulness and do not retrain the model.';
    els.evidenceRows.innerHTML = payload.rows.map(row => `<article class="evidence-row">
      <strong>Comment ${row.row_index + 1}${row.review_required ? ' · Needs review' : ''}</strong>
      <p>${escapeHtml(row.text)}</p>
      ${payload.variables.map(variable => `<fieldset class="correction-group" data-single="${['sentiment','success_story','quote_worthy'].includes(variable.name)}" data-row="${row.row_index}" data-variable="${escapeHtml(variable.name)}">
        <legend>${escapeHtml(variable.name)}</legend>
        ${variable.labels.map(label => `<label><input type="checkbox" value="${escapeHtml(label)}" ${(row.analysis[variable.name] || []).includes(label) ? 'checked' : ''}> ${escapeHtml(label)}</label>`).join('')}
        <button type="button" data-correct>${buttonMarkup('save', 'Save correction')}</button>
        <span role="status"></span>
      </fieldset>`).join('')}</article>`).join('');
    els.evidenceDialog.showModal();
  } catch (error) { reportError(error); }
});
els.evidenceRows.addEventListener('change', event => {
  const group = event.target.closest('[data-single="true"]');
  if (group && event.target.checked) group.querySelectorAll('input').forEach(input => { if (input !== event.target) input.checked = false; });
});
els.evidenceRows.addEventListener('click', async event => {
  const button = event.target.closest('[data-correct]');
  if (!button) return;
  const group = button.closest('fieldset');
  button.disabled = true;
  try {
    await refresh(await api('/api/correction', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({row_index: Number(group.dataset.row), variable: group.dataset.variable, labels: [...group.querySelectorAll('input:checked')].map(input => input.value)})}));
    group.querySelector('[role="status"]').textContent = 'Saved; counts updated';
  } catch (error) { group.querySelector('[role="status"]').textContent = error.message; }
  finally { button.disabled = false; }
});

bootstrap().catch((error) => {
  els.consentGate.hidden = false;
  els.consentError.textContent = error.message;
});
