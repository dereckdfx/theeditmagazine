/* The Edit Magazine — shared: privacy + GUARDAR ARTÍCULO */
(function () {
  var PRIVACY_KEY = 'privacyAccepted';
  var SAVED_KEY = 'editSavedArticles';

  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  /* ---------- Privacy ---------- */
  function privacyAccepted() {
    try { return localStorage.getItem(PRIVACY_KEY) === 'true'; } catch (e) { return false; }
  }
  /* Tailwind CDN: .flex and .hidden both set display; dynamically adding
     .hidden while .flex remains often leaves display:flex. Force hide/show. */
  function hidePrivacyOverlay(overlay) {
    if (!overlay) overlay = qs('#privacy-overlay');
    if (!overlay) return;
    overlay.classList.add('hidden');
    overlay.classList.remove('flex');
    overlay.style.display = 'none';
    overlay.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('overflow-hidden');
    ['main-header', 'main-content', 'main-footer', 'site-header', 'site-main', 'site-footer'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.classList.remove('opacity-50', 'pointer-events-none');
    });
  }
  function showPrivacyOverlay(overlay) {
    if (!overlay) overlay = qs('#privacy-overlay');
    if (!overlay) return;
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
    overlay.style.display = 'flex';
    overlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('overflow-hidden');
  }
  function acceptPrivacy(e) {
    if (e && e.preventDefault) e.preventDefault();
    try { localStorage.setItem(PRIVACY_KEY, 'true'); } catch (err) {}
    hidePrivacyOverlay();
  }
  window.closePrivacyPopup = acceptPrivacy;
  window.acceptPrivacy = acceptPrivacy;

  function initPrivacy() {
    var overlay = qs('#privacy-overlay');
    if (!overlay) return;
    if (privacyAccepted()) {
      hidePrivacyOverlay(overlay);
    } else {
      showPrivacyOverlay(overlay);
    }
    /* Accept / Reject / privacy-options that already use data-privacy-accept */
    qsa('[data-privacy-accept]').forEach(function (btn) {
      btn.addEventListener('click', acceptPrivacy);
    });
  }

  /* ---------- Save article ---------- */
  function loadSaved() {
    try { return JSON.parse(localStorage.getItem(SAVED_KEY) || '[]'); }
    catch (e) { return []; }
  }
  function persistSaved(arr) {
    try { localStorage.setItem(SAVED_KEY, JSON.stringify(arr)); } catch (e) {}
  }
  function isSaved(id) {
    return loadSaved().some(function (a) { return a.id === id; });
  }
  function toggleSave(meta, btn) {
    var list = loadSaved();
    var idx = list.findIndex(function (a) { return a.id === meta.id; });
    var saved;
    if (idx >= 0) {
      list.splice(idx, 1);
      saved = false;
    } else {
      list.unshift({
        id: meta.id,
        title: meta.title,
        url: meta.url,
        image: meta.image || '',
        category: meta.category || '',
        savedAt: new Date().toISOString()
      });
      saved = true;
    }
    persistSaved(list);
    updateSaveButton(btn, saved);
    return saved;
  }
  function updateSaveButton(btn, saved) {
    if (!btn) return;
    btn.setAttribute('aria-pressed', saved ? 'true' : 'false');
    btn.classList.toggle('is-saved', !!saved);
    var tip = btn.querySelector('[data-save-tip]');
    if (tip) {
      var lang = btn.getAttribute('data-lang') || document.documentElement.lang || 'es';
      if (lang.indexOf('en') === 0) {
        tip.textContent = saved ? 'ARTICLE SAVED' : 'SAVE ARTICLE';
      } else {
        tip.textContent = saved ? 'ARTÍCULO GUARDADO' : 'GUARDAR ARTÍCULO';
      }
    }
    var icon = btn.querySelector('[data-save-icon]');
    if (icon) {
      icon.innerHTML = saved
        ? '<i class="fa-solid fa-bookmark"></i>'
        : '<i class="fa-regular fa-bookmark"></i>';
    }
  }
  window.EditSave = {
    load: loadSaved,
    isSaved: isSaved,
    toggle: toggleSave,
    clear: function () { persistSaved([]); }
  };

  function initSaveButtons() {
    qsa('[data-save-article]').forEach(function (btn) {
      var meta = {
        id: btn.getAttribute('data-id') || '',
        title: btn.getAttribute('data-title') || '',
        url: btn.getAttribute('data-url') || btn.getAttribute('href') || window.location.pathname,
        image: btn.getAttribute('data-image') || '',
        category: btn.getAttribute('data-category') || ''
      };
      if (!meta.id) return;
      updateSaveButton(btn, isSaved(meta.id));
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        toggleSave(meta, btn);
      });
    });
  }

  function initSavedPage() {
    var root = qs('#saved-articles-list');
    if (!root) return;
    var list = loadSaved();
    var empty = qs('#saved-empty');
    if (!list.length) {
      if (empty) empty.classList.remove('hidden');
      root.innerHTML = '';
      return;
    }
    if (empty) empty.classList.add('hidden');
    root.innerHTML = list.map(function (a) {
      return (
        '<article class="group flex gap-4 border-b border-neutral-200 py-5">' +
          (a.image ? '<a href="' + a.url + '" class="w-24 h-32 flex-shrink-0 overflow-hidden bg-neutral-100"><img src="' + a.image + '" alt="" class="w-full h-full object-cover"/></a>' : '') +
          '<div class="flex-1">' +
            (a.category ? '<p class="text-[10px] tracking-[0.2em] uppercase text-neutral-500 mb-1">' + a.category + '</p>' : '') +
            '<h3 class="font-serif text-xl leading-snug"><a href="' + a.url + '" class="hover:underline">' + a.title + '</a></h3>' +
            '<button type="button" class="mt-3 text-[11px] tracking-widest uppercase text-neutral-500 hover:text-black" data-remove-saved="' + a.id + '">Quitar</button>' +
          '</div>' +
        '</article>'
      );
    }).join('');
    qsa('[data-remove-saved]', root).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = btn.getAttribute('data-remove-saved');
        persistSaved(loadSaved().filter(function (a) { return a.id !== id; }));
        initSavedPage();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initPrivacy();
    initSaveButtons();
    initSavedPage();
  });
})();
