/**
 * FormAI — Application Logic
 *
 * Architecture modulaire :
 *   - ToastManager      : notifications visuelles
 *   - SchemaBuilder     : gestion dynamique des champs via DOM
 *   - ExtractionAPI     : appels REST vers le backend FastAPI
 *   - ResultsRenderer   : rendu des résultats avec barres de confiance
 *   - App               : orchestrateur principal
 *
 * Pourquoi JS vanilla ?
 *   Simple, zéro dépendances, lisible et maintainable sans framework.
 *   Les interactions sont limitées : une SPA légère suffit.
 */

'use strict';

/* ================================================================
   ToastManager — Notifications non-bloquantes
   ================================================================ */

const ToastManager = (() => {
  const container = document.getElementById('toast-container');

  const ICONS = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️',
  };

  /**
   * Affiche un toast pendant `duration` ms.
   * @param {'success'|'warning'|'error'|'info'} type
   * @param {string} title
   * @param {string} [message]
   * @param {number} [duration=4000]
   */
  function show(type, title, message = '', duration = 4000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.setProperty('--toast-delay', `${duration}ms`);
    toast.innerHTML = `
      <span class="toast-icon">${ICONS[type] ?? 'ℹ️'}</span>
      <div class="toast-body">
        <div class="toast-title">${escapeHtml(title)}</div>
        ${message ? `<div class="toast-msg">${escapeHtml(message)}</div>` : ''}
      </div>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration + 300); // +300 for fade-out animation
  }

  return { show };
})();


/* ================================================================
   SchemaBuilder — Gestion des champs du schéma
   ================================================================ */

const SchemaBuilder = (() => {
  let fieldCounter = 0;

  const fieldsList = document.getElementById('fields-list');
  const countBadge = document.getElementById('field-count-badge');
  const schemaPreview = document.getElementById('schema-json-output');

  const TYPES = ['string', 'number', 'date', 'boolean'];

  /** Retourne le schéma courant sous forme d'objet. */
  function getSchema() {
    const name = document.getElementById('schema-name').value.trim();
    const description = document.getElementById('schema-desc').value.trim();

    const fields = Array.from(fieldsList.querySelectorAll('.field-item')).map(item => ({
      name: item.querySelector('.field-name').value.trim(),
      type: item.querySelector('.field-type').value,
      required: item.querySelector('.field-required').checked,
      description: item.querySelector('.field-desc').value.trim(),
    })).filter(f => f.name !== '');   // ignorer les champs sans nom

    return {
      schema_name: name || 'mon_schema',
      description,
      fields,
    };
  }

  /** Ajoute un champ au builder. */
  function addField(defaults = {}) {
    fieldCounter++;
    const id = `field-${fieldCounter}`;

    const li = document.createElement('li');
    li.className = 'field-item';
    li.dataset.fieldId = id;

    const typeOptions = TYPES.map(t =>
      `<option value="${t}" ${defaults.type === t ? 'selected' : ''}>${t}</option>`
    ).join('');

    li.innerHTML = `
      <div class="field-name-col">
        <div class="form-group">
          <label class="form-label" for="${id}-name">Nom du champ</label>
          <input id="${id}-name" class="form-input field-name" type="text"
                 placeholder="ex: numero_facture"
                 value="${escapeHtml(defaults.name ?? '')}" />
        </div>
        <div class="form-group">
          <label class="form-label" for="${id}-type">Type</label>
          <select id="${id}-type" class="form-select field-type">${typeOptions}</select>
        </div>
      </div>
      <div class="field-controls">
        <div class="form-group">
          <label class="form-label" for="${id}-desc">Description (optionnel)</label>
          <input id="${id}-desc" class="form-input field-desc" type="text"
                 placeholder="Contexte métier…"
                 value="${escapeHtml(defaults.description ?? '')}" />
        </div>
        <div class="checkbox-group">
          <input id="${id}-req" class="field-required" type="checkbox" ${defaults.required !== false ? 'checked' : ''} />
          <label for="${id}-req">Requis</label>
        </div>
        <button class="btn-remove-field" title="Supprimer ce champ" data-remove="${id}">
          <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
        </button>
      </div>`;

    // Suppression
    li.querySelector(`[data-remove="${id}"]`).addEventListener('click', () => {
      li.remove();
      updateMeta();
    });

    // Mise à jour en temps réel
    li.querySelectorAll('input, select').forEach(el =>
      el.addEventListener('input', updateMeta)
    );

    fieldsList.appendChild(li);
    updateMeta();
    // Focus sur le nom du champ ajouté
    li.querySelector('.field-name').focus();
  }

  /** Charge un schéma complet dans le builder. */
  function loadSchema(schemaObj) {
    // Réinitialiser les champs
    fieldsList.innerHTML = '';
    fieldCounter = 0;

    document.getElementById('schema-name').value = schemaObj.schema_name ?? '';
    document.getElementById('schema-desc').value = schemaObj.description ?? '';

    (schemaObj.fields ?? []).forEach(f => addField(f));
    updateMeta();
  }

  /** Vide le builder. */
  function clearSchema() {
    fieldsList.innerHTML = '';
    fieldCounter = 0;
    document.getElementById('schema-name').value = 'mon_schema';
    document.getElementById('schema-desc').value = '';
    updateMeta();
  }

  /** Met à jour le badge compteur et l'aperçu JSON. */
  function updateMeta() {
    const count = fieldsList.querySelectorAll('.field-item').length;
    countBadge.textContent = `${count} champ${count > 1 ? 's' : ''}`;

    const schema = getSchema();
    schemaPreview.textContent = JSON.stringify(schema, null, 2);

    // Activer / désactiver le bouton extract
    App.updateExtractButton();
  }

  return { addField, loadSchema, clearSchema, getSchema };
})();


/* ================================================================
   ExtractionAPI — Appels REST
   ================================================================ */

const ExtractionAPI = (() => {
  const BASE_URL = '';  // même origine que le serveur FastAPI

  /**
   * Vérifie l'état du backend.
   * @returns {Promise<boolean>}
   */
  async function checkHealth() {
    try {
      const res = await fetch(`${BASE_URL}/api/health`, { signal: AbortSignal.timeout(5000) });
      return res.ok;
    } catch {
      return false;
    }
  }

  /**
   * Récupère les schémas exemples depuis /api/schemas/examples.
   * @returns {Promise<Array>}
   */
  async function fetchExampleSchemas() {
    try {
      const res = await fetch(`${BASE_URL}/api/schemas/examples`);
      if (!res.ok) return [];
      return await res.json();
    } catch {
      return [];
    }
  }

  /**
   * Lance l'extraction via POST /api/extract.
   *
   * Cas d'erreur gérés :
   * - Réseau hors ligne → NetworkError
   * - Timeout → AbortError
   * - 422 → erreur de validation (document vide, schéma invalide)
   * - 503 → clé API manquante ou service indisponible
   * - 500 → erreur inattendue serveur
   *
   * @param {string} documentText
   * @param {object} schema
   * @returns {Promise<object>} ExtractionResult JSON
   */
  async function extract(documentText, schema) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60_000); // 60s max

    try {
      const res = await fetch(`${BASE_URL}/api/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_text: documentText, schema }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        let detail = `Erreur ${res.status}`;
        try {
          const errBody = await res.json();
          detail = errBody.detail ?? detail;
        } catch { /* corps non-JSON */ }
        throw new APIError(res.status, detail);
      }

      return await res.json();

    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new APIError(0, 'La requête a expiré (>60s). Vérifiez votre connexion.');
      }
      if (err instanceof APIError) throw err;
      throw new APIError(0, `Problème réseau : impossible de joindre le serveur.`);
    }
  }

  /**
   * Upload de multiples fichiers.
   * @param {File[]} fileArray
   * @returns {Promise<{files: Array}>}
   */
  async function uploadFiles(fileArray) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60_000); // 60s max

    try {
      const formData = new FormData();
      fileArray.forEach(f => formData.append('files', f));

      const res = await fetch(`${BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        let detail = `Erreur ${res.status}`;
        try {
          const errBody = await res.json();
          detail = errBody.detail ?? detail;
        } catch { /* corps non-JSON */ }
        throw new APIError(res.status, detail);
      }

      return await res.json();
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new APIError(0, 'Upload expiré (>30s). Fichier trop volumineux ?');
      }
      if (err instanceof APIError) throw err;
      throw new APIError(0, 'Problème réseau lors de l\'upload.');
    }
  }

  return { checkHealth, fetchExampleSchemas, extract, uploadFiles };
})();


/* Classe d'erreur personnalisée pour les erreurs API */
class APIError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}


/* ================================================================
   ResultsRenderer — Rendu des résultats
   ================================================================ */

const ResultsRenderer = (() => {
  const placeholder = document.getElementById('results-placeholder');
  const content = document.getElementById('results-content');
  const resultActions = document.getElementById('result-actions');

  /** Affiche un message d'erreur dans la zone résultats. */
  function showError(message) {
    placeholder.classList.add('hidden');
    resultActions.style.display = 'none';
    content.classList.remove('hidden');
    content.innerHTML = `
      <div class="result-summary status-error" role="alert">
        <span class="result-summary-icon">❌</span>
        <div class="result-summary-info">
          <strong>Extraction échouée</strong>
          <p>${escapeHtml(message)}</p>
        </div>
      </div>`;
  }

  /** Retourne la classe CSS de confiance selon le score. */
  function confClass(score) {
    if (score >= 0.75) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
  }

  /** Retourne la couleur CSS de la confiance. */
  function confColor(score) {
    if (score >= 0.75) return 'var(--success)';
    if (score >= 0.4) return 'var(--warning)';
    return 'var(--error)';
  }

  /** Rendu principal : prend ExtractionResult et injecte le HTML. */
  function render(result) {
    placeholder.classList.add('hidden');
    content.classList.remove('hidden');
    resultActions.style.display = 'flex';

    const status = result.status ?? 'warning';
    const globalConf = result.validation?.confidence_global ?? 0;
    const alerts = result.validation?.alerts ?? [];
    const data = result.data ?? {};

    // Emoji et label selon status
    const statusMap = {
      success: { icon: '✅', label: 'Extraction réussie', cssClass: 'status-success' },
      warning: { icon: '⚠️', label: 'Extraction partielle', cssClass: 'status-warning' },
      error: { icon: '❌', label: 'Extraction échouée', cssClass: 'status-error' },
    };
    const s = statusMap[status] ?? statusMap['warning'];

    // --- Summary header ---
    const summaryHtml = `
      <div class="result-summary ${s.cssClass}" role="status">
        <span class="result-summary-icon">${s.icon}</span>
        <div class="result-summary-info">
          <strong>${s.label}</strong>
          <p>${Object.keys(data).length} champ(s) traité(s) · Modèle : ${escapeHtml(result.metadata?.model ?? 'inconnu')}</p>
        </div>
        <div class="result-global-conf">
          <div class="conf-number" style="color: ${confColor(globalConf)}">${Math.round(globalConf * 100)}%</div>
          <div class="conf-label">Confiance</div>
        </div>
      </div>`;

    // --- Champs ---
    const fieldsHtml = Object.entries(data).map(([fieldName, fieldResult]) => {
      const pct = Math.round((fieldResult.confidence ?? 0) * 100);
      const fStatus = fieldResult.status ?? 'missing';
      const value = fieldResult.value;
      const hint = fieldResult.source_hint;

      const valueDisplay = value !== null && value !== undefined
        ? `<span>${escapeHtml(String(value))}</span>`
        : `<span class="is-null">null — champ non trouvé</span>`;

      return `
        <div class="field-result-card fr-${fStatus}">
          <div class="fr-top">
            <div>
              <div class="fr-name">${escapeHtml(fieldName)}</div>
            </div>
            <div class="fr-badges">
              <span class="status-chip ${fStatus}">${fStatus}</span>
            </div>
          </div>
          <div class="fr-value ${value === null || value === undefined ? 'is-null' : ''}">${valueDisplay}</div>
          <div class="conf-bar-wrapper">
            <div class="conf-bar-track">
              <div class="conf-bar-fill ${confClass(fieldResult.confidence ?? 0)}"
                   style="width: ${pct}%"></div>
            </div>
            <span class="conf-bar-pct">${pct}%</span>
          </div>
          ${hint ? `<div class="fr-hint">📍 ${escapeHtml(hint)}</div>` : ''}
        </div>`;
    }).join('');

    // --- Alertes ---
    let alertsHtml = '';
    if (alerts.length > 0) {
      const alertItems = alerts.map(a => `
        <div class="alert-item">
          <span>⚠</span>
          <span>${escapeHtml(a)}</span>
        </div>`).join('');
      alertsHtml = `
        <div class="result-alerts">
          <div class="alerts-title">Alertes de validation</div>
          ${alertItems}
        </div>`;
    }

    content.innerHTML = summaryHtml
      + (fieldsHtml ? `<div class="fields-result-list">${fieldsHtml}</div>` : '')
      + alertsHtml;
  }

  /** Réinitialise la zone résultats. */
  function reset() {
    placeholder.classList.remove('hidden');
    content.classList.add('hidden');
    content.innerHTML = '';
    resultActions.style.display = 'none';
  }

  /** Rendu pour un lot de fichiers (Batch Mode) */
  function renderBatch(batchResults, schema) {
    placeholder.classList.add('hidden');
    content.classList.remove('hidden');
    resultActions.style.display = 'flex';

    const fields = schema.fields;
    const tableHeaders = fields.map(f => `<th>${escapeHtml(f.name)}</th>`).join('');

    const rows = batchResults.map(b => {
      if (b.error) {
        return `<tr><td style="font-weight:600">${escapeHtml(b.filename)}</td><td colspan="${fields.length}" style="color:var(--error)">❌ ${escapeHtml(b.error)}</td></tr>`;
      }
      const data = b.result.data || {};
      const cells = fields.map(f => {
        const val = data[f.name]?.value;
        const display = val !== undefined && val !== null ? escapeHtml(String(val)) : '<span class="is-null">null</span>';
        return `<td>${display}</td>`;
      }).join('');
      return `<tr><td style="font-weight:600">${escapeHtml(b.filename)}</td>${cells}</tr>`;
    }).join('');

    content.innerHTML = `
      <div class="result-summary status-success" role="status">
        <span class="result-summary-icon">📦</span>
        <div class="result-summary-info">
          <strong>Traitement par lots terminé</strong>
          <p>${batchResults.length} document(s) traité(s).</p>
        </div>
      </div>
      <div style="overflow-x: auto; margin-top: 1rem; border: 1px solid var(--border); border-radius: 8px;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.875rem;">
          <thead style="background: var(--bg-surface); border-bottom: 1px solid var(--border);">
            <tr><th style="padding: 0.75rem;">Fichier</th>${tableHeaders.replace(/<th>/g, '<th style="padding: 0.75rem;">')}</tr>
          </thead>
          <tbody>
            ${rows.replace(/<td/g, '<td style="padding: 0.75rem; border-bottom: 1px solid var(--border);"')}
          </tbody>
        </table>
      </div>
    `;
  }

  return { render, renderBatch, showError, reset };
})();


/* ================================================================
   Utilitaires globaux
   ================================================================ */

/** Échappe les caractères HTML pour éviter les injections. */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/** Déclenche le téléchargement d'un blob JSON. */
function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}


/* ================================================================
   App — Orchestrateur principal
   ================================================================ */

const App = (() => {
  let lastResult = null;   // Garde le dernier ExtractionResult pour l'export
  let activeSampleDocument = null; // Sample document du preset courant
  let batchDocuments = []; // Liste des documents en mode batch

  const btnExtract = document.getElementById('btn-extract');
  const btnAddField = document.getElementById('btn-add-field');
  const btnClearSchema = document.getElementById('btn-clear-schema');
  const btnClearDoc = document.getElementById('btn-clear-doc');
  const btnLoadSample = document.getElementById('btn-load-sample');
  const btnExportJson = document.getElementById('btn-export-json');
  const docInput = document.getElementById('document-input');
  const charCount = document.getElementById('doc-char-count');
  const schemaPresets = document.getElementById('schema-presets');
  const previewToggle = document.getElementById('toggle-schema-preview');
  const previewJson = document.getElementById('schema-json-output');
  const apiStatusBadge = document.getElementById('api-status-badge');
  const uploadZone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('file-input');
  const uploadZoneContent = document.getElementById('upload-zone-content');
  const uploadFileInfo = document.getElementById('upload-file-info');
  const uploadFileName = document.getElementById('upload-file-name');
  const uploadFileSize = document.getElementById('upload-file-size');
  const btnRemoveFile = document.getElementById('btn-remove-file');
  const batchPreviewContainer = document.getElementById('batch-preview-container');
  const batchFileCount = document.getElementById('batch-file-count');
  const batchFileList = document.getElementById('batch-file-list');

  // Texte de facture exemple (embarqué, pas besoin de fetch)
  const SAMPLE_DOCUMENT = `FACTURE
Numéro: FAC-2026-0042
Date: 2026-03-03

Fournisseur: DataForm SAS
Adresse: 12 rue de la Paix, 75001 Paris
SIRET: 123 456 789 00012

Client: Atelier Delta
Adresse: 8 boulevard Haussmann, 75009 Paris

Prestations:
- Extraction automatisée de formulaires : 1200,00 EUR
- Support intégration : 300,00 EUR

Sous-total HT : 1500,00 EUR
TVA 20% : 300,00 EUR
Montant total TTC : 1800,00 EUR

Paiement sous 30 jours.
IBAN: FR76 3000 6000 0112 3456 7890 189`;

  /** Met à jour l'état du bouton Extract selon les saisies. */
  function updateExtractButton() {
    const hasDoc = docInput.value.trim().length > 0 || batchDocuments.length > 0;
    const hasFields = SchemaBuilder.getSchema().fields.length > 0;
    btnExtract.disabled = !(hasDoc && hasFields);
  }

  /** Met l'UI en état "chargement". */
  function setLoading(isLoading) {
    btnExtract.disabled = isLoading;
    btnExtract.querySelector('.btn-extract-content').classList.toggle('hidden', isLoading);
    btnExtract.querySelector('.btn-extract-loading').classList.toggle('hidden', !isLoading);
  }

  /** Lance l'extraction. */
  async function handleExtract() {
    const documentText = docInput.value.trim();
    const schema = SchemaBuilder.getSchema();

    if (!documentText && batchDocuments.length === 0) {
      ToastManager.show('warning', 'Document vide', 'Collez du texte ou importez des fichiers.');
      return;
    }
    if (schema.fields.length === 0) {
      ToastManager.show('warning', 'Schéma vide', 'Ajoutez au moins un champ au schéma.');
      return;
    }

    setLoading(true);
    ResultsRenderer.reset();
    lastResult = null;

    try {
      if (batchDocuments.length > 0) {
        // --- MODE BATCH ---
        let results = [];
        for (let i = 0; i < batchDocuments.length; i++) {
          const doc = batchDocuments[i];
          btnExtract.querySelector('.btn-extract-loading').innerHTML = `<span class="spinner"></span>Fichier ${i + 1}/${batchDocuments.length}…`;
          try {
            const res = await ExtractionAPI.extract(doc.text, schema);
            results.push({ filename: doc.filename, result: res });
          } catch (err) {
            results.push({ filename: doc.filename, error: err.detail || String(err) });
          }
        }
        lastResult = results; // Permet d'exporter l'array de résultats
        ResultsRenderer.renderBatch(results, schema);
        ToastManager.show('success', 'Batch terminé', `${results.length} fichiers traités.`);
      } else {
        // --- MODE NORMAL ---
        btnExtract.querySelector('.btn-extract-loading').innerHTML = `<span class="spinner"></span>Extraction en cours…`;
        const result = await ExtractionAPI.extract(documentText, schema);
        lastResult = result;
        ResultsRenderer.render(result);

        if (result.status === 'success') {
          ToastManager.show('success', 'Extraction réussie',
            `Confiance globale : ${Math.round((result.validation?.confidence_global ?? 0) * 100)}%`);
        } else if (result.status === 'warning') {
          ToastManager.show('warning', 'Extraction partielle', 'Certains champs sont incertains.');
        } else {
          ToastManager.show('error', 'Extraction échouée', result.validation?.alerts?.[0] ?? 'Voir les erreurs.');
        }
      }
    } catch (err) {
      const msg = err instanceof APIError ? err.detail : String(err);
      ResultsRenderer.showError(msg);
      ToastManager.show('error', 'Erreur', msg, 6000);
    } finally {
      btnExtract.querySelector('.btn-extract-loading').innerHTML = `<span class="spinner"></span>Extraction en cours…`;
      setLoading(false);
      updateExtractButton();
    }
  }

  /** Initialise le healthcheck et met à jour le badge de statut. */
  async function initHealthCheck() {
    const ok = await ExtractionAPI.checkHealth();
    apiStatusBadge.className = `status-badge ${ok ? 'status-ok' : 'status-error'}`;
    apiStatusBadge.innerHTML = `
      <span class="status-dot"></span>
      ${ok ? 'API connectée' : 'API hors ligne'}`;
    if (!ok) {
      ToastManager.show('error', 'Backend inaccessible',
        'Assurez-vous que le serveur FastAPI tourne sur le port 8000.', 7000);
    }
  }

  /** Charge les schémas exemples dans le select. */
  async function initExampleSchemas() {
    const examples = await ExtractionAPI.fetchExampleSchemas();
    examples.forEach(ex => {
      const opt = document.createElement('option');
      opt.value = JSON.stringify(ex.schema);
      opt.dataset.sample = ex.sample_document || '';
      opt.textContent = ex.name;
      schemaPresets.appendChild(opt);
    });
  }

  /** Bind de tous les event listeners. */
  function bindEvents() {
    // Ajout champ
    btnAddField.addEventListener('click', () => SchemaBuilder.addField());

    // Clear schéma
    btnClearSchema.addEventListener('click', () => {
      if (confirm('Effacer tous les champs du schéma ?')) SchemaBuilder.clearSchema();
    });

    // Clear document
    btnClearDoc.addEventListener('click', () => {
      docInput.value = '';
      charCount.textContent = '0 caractères';
      updateExtractButton();
    });

    // Charger document exemple — utilise le sample du preset actif si disponible
    btnLoadSample.addEventListener('click', () => {
      const doc = activeSampleDocument || SAMPLE_DOCUMENT;
      docInput.value = doc;
      charCount.textContent = `${doc.length.toLocaleString('fr-FR')} caractère${doc.length > 1 ? 's' : ''}`;
      updateExtractButton();
      const label = activeSampleDocument
        ? `Document exemple pour le schéma actif.`
        : 'Facture fictive DataForm SAS.';
      ToastManager.show('info', 'Document exemple chargé', label);
    });

    // Extraction
    btnExtract.addEventListener('click', handleExtract);

    // Compteur de caractères + validation en temps réel
    docInput.addEventListener('input', () => {
      const len = docInput.value.length;
      charCount.textContent = `${len.toLocaleString('fr-FR')} caractère${len > 1 ? 's' : ''}`;
      updateExtractButton();
    });

    // Raccourci clavier : Ctrl+Enter pour lancer l'extraction
    docInput.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!btnExtract.disabled) handleExtract();
      }
    });

    // Export JSON
    btnExportJson.addEventListener('click', () => {
      if (!lastResult) return;
      const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      downloadJson(lastResult, `extraction_${ts}.json`);
      ToastManager.show('success', 'Export réussi', 'Fichier JSON téléchargé.');
    });

    // Chargement d'un schéma preset
    schemaPresets.addEventListener('change', () => {
      const val = schemaPresets.value;
      if (!val) return;
      // Récupère le sample document stocké dans data-sample
      const selectedOpt = schemaPresets.options[schemaPresets.selectedIndex];
      const sampleDoc = selectedOpt?.dataset?.sample || '';
      try {
        const schemaObj = JSON.parse(val);
        SchemaBuilder.loadSchema(schemaObj);
        // Mémoriser le sample pour le bouton Exemple
        activeSampleDocument = sampleDoc || null;
        // Auto-charger le document exemple si un est disponible
        if (sampleDoc) {
          docInput.value = sampleDoc;
          charCount.textContent = `${sampleDoc.length.toLocaleString('fr-FR')} caractère${sampleDoc.length > 1 ? 's' : ''}`;
          updateExtractButton();
          ToastManager.show('info', 'Schéma + exemple chargés', schemaObj.schema_name);
        } else {
          ToastManager.show('info', 'Schéma chargé', schemaObj.schema_name);
        }
      } catch {
        ToastManager.show('error', 'Erreur', 'Impossible de charger ce schéma.');
      }
      schemaPresets.value = '';
    });

    // Toggle aperçu JSON schéma
    previewToggle.addEventListener('click', () => {
      const expanded = previewToggle.getAttribute('aria-expanded') === 'true';
      previewToggle.setAttribute('aria-expanded', String(!expanded));
      previewJson.classList.toggle('hidden', expanded);
    });
  }

  /** Initialise la zone drag-and-drop et l'input fichier. */
  function initUploadZone() {
    // Clic sur la zone → ouvre le sélecteur de fichier
    uploadZone.addEventListener('click', e => {
      if (e.target === btnRemoveFile) return; // Évite le re-trigger sur le bouton ✕
      fileInput.click();
    });

    // Sélection via l'input fichier
    fileInput.addEventListener('change', () => {
      if (fileInput.files?.length > 0) handleFileUpload(fileInput.files);
    });

    // Drag events
    uploadZone.addEventListener('dragover', e => {
      e.preventDefault();
      uploadZone.classList.add('drag-over');
    });
    uploadZone.addEventListener('dragleave', e => {
      if (!uploadZone.contains(e.relatedTarget)) uploadZone.classList.remove('drag-over');
    });
    uploadZone.addEventListener('drop', e => {
      e.preventDefault();
      uploadZone.classList.remove('drag-over');
      if (e.dataTransfer?.files?.length > 0) handleFileUpload(e.dataTransfer.files);
    });

    // Retirer le fichier
    btnRemoveFile.addEventListener('click', e => {
      e.stopPropagation();
      clearUploadedFile();
    });

    // Accessibilité clavier (Entrée / Espace)
    uploadZone.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInput.click();
      }
    });
  }

  /** Gère l'upload d'un array/nodeList de fichiers. */
  async function handleFileUpload(fileList) {
    const files = Array.from(fileList);
    const allowed = ['.pdf', '.txt', '.json'];

    // Filtrer les invalides côté UI
    const validFiles = files.filter(f => {
      const ext = f.name.slice(f.name.lastIndexOf('.')).toLowerCase();
      return allowed.includes(ext) && f.size <= 5 * 1024 * 1024;
    });

    if (validFiles.length === 0) {
      ToastManager.show('error', 'Format/Taille', 'Seuls PDF, TXT, JSON < 5Mo sont acceptés.');
      return;
    }
    if (validFiles.length < files.length) {
      ToastManager.show('warning', 'Fichiers ignorés', `${files.length - validFiles.length} fichier(s) refusé(s).`);
    }

    // UI : état chargement
    uploadZone.classList.add('upload-processing');
    uploadZoneContent.innerHTML = `
      <div class="upload-zone-content">
        <div class="spinner" style="border-top-color: var(--accent-1)"></div>
        <p class="upload-label">Lecture de ${validFiles.length} fichier(s)…</p>
      </div>`;

    try {
      const result = await ExtractionAPI.uploadFiles(validFiles);
      const successes = (result.files || []).filter(f => f.status === 'success');

      if (successes.length === 0) throw new Error("Erreur de traitement des fichiers.");

      if (successes.length === 1) {
        // --- SINGLE MODE ---
        batchDocuments = [];
        docInput.value = successes[0].text;
        const len = docInput.value.length;
        charCount.textContent = `${len.toLocaleString('fr-FR')} caractère${len > 1 ? 's' : ''}`;

        docInput.classList.remove('hidden');
        batchPreviewContainer.classList.add('hidden');

        uploadZoneContent.classList.add('hidden');
        uploadFileInfo.classList.remove('hidden');
        uploadFileName.textContent = successes[0].filename;
        uploadFileSize.textContent = `${successes[0].size_ko} Ko`;

        const existing = uploadFileInfo.querySelector('.upload-truncated-badge');
        if (existing) existing.remove();
        if (successes[0].truncated) {
          const badge = document.createElement('span');
          badge.className = 'upload-truncated-badge';
          badge.textContent = 'Tronqué';
          uploadFileSize.after(badge);
        }
        ToastManager.show('success', 'Fichier importé', `${successes[0].filename}`);
      } else {
        // --- BATCH MODE ---
        batchDocuments = successes;
        docInput.value = '';
        docInput.classList.add('hidden');
        batchPreviewContainer.classList.remove('hidden');

        batchFileCount.textContent = `${batchDocuments.length} fichiers`;
        batchFileList.innerHTML = batchDocuments.map(d =>
          `<li>• ${escapeHtml(d.filename)} <span style="opacity:0.6;font-size:0.85em">(${d.char_count} chars)${d.truncated ? ' ⚠️ Tronqué' : ''}</span></li>`
        ).join('');

        uploadZoneContent.classList.add('hidden');
        uploadFileInfo.classList.remove('hidden');
        uploadFileName.textContent = `${batchDocuments.length} fichiers préparés`;
        uploadFileSize.textContent = `Traitement par lots prêt`;
        ToastManager.show('success', 'Multiple import', `${batchDocuments.length} fichiers ajoutés.`);
      }

      updateExtractButton();

    } catch (err) {
      const msg = err instanceof APIError ? err.detail : String(err);
      ToastManager.show('error', 'Erreur d\'import', msg, 7000);
      clearUploadedFile();
    } finally {
      uploadZone.classList.remove('upload-processing');
    }
  }

  /** Remet la zone upload dans son état initial. */
  function clearUploadedFile() {
    fileInput.value = '';
    batchDocuments = [];
    docInput.classList.remove('hidden');
    batchPreviewContainer.classList.add('hidden');

    uploadZoneContent.innerHTML = `
      <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
      </svg>
      <p class="upload-label">Glissez un ou plusieurs fichiers ici</p>
      <p class="upload-hint">PDF océrisé, TXT, JSON &nbsp;·&nbsp; 5 Mo max par fichier</p>`;
    uploadZoneContent.classList.remove('hidden');
    uploadFileInfo.classList.add('hidden');
    const badge = uploadFileInfo.querySelector('.upload-truncated-badge');
    if (badge) badge.remove();
    updateExtractButton();
  }

  /** Point d'entrée. */
  async function init() {
    bindEvents();
    initUploadZone();

    // Schéma par défaut : 1 champ exemple pour guider l'utilisateur
    SchemaBuilder.addField({ name: 'numero_facture', type: 'string', required: true, description: 'Identifiant unique de la facture' });
    SchemaBuilder.addField({ name: 'date_facture', type: 'date', required: true, description: 'Date au format YYYY-MM-DD' });
    SchemaBuilder.addField({ name: 'montant_total', type: 'number', required: true, description: 'Montant TTC total' });

    updateExtractButton();

    // Initialisations async (non bloquantes)
    initHealthCheck();
    initExampleSchemas();
  }

  return { init, updateExtractButton };
})();


/* ================================================================
   Démarrage
   ================================================================ */
document.addEventListener('DOMContentLoaded', App.init);
