(function () {
  "use strict";

  const I18N = window.LL_I18N;
  const STORAGE_KEY = "ll-lang";
  const CAT_ORDER = [
    "christian-inspiration",
    "mindfulness-peace",
    "gratitude-joy",
    "love-relationships",
    "art-watercolor",
    "encouragement"
  ];

  /* Diverse featured shelf: one standout per category mood */
  const FEATURED_ASINS = [
    "B0HG7DLLGH", /* Little Moments of Grace — christian */
    "B0FGTPGKJG", /* Gentle Deer Journal — mindfulness */
    "B0FDWKK89W", /* 5-Minute Gratitude — gratitude */
    "B0F7J2PHYF", /* We Choose Us — love */
    "B0DVSSN269", /* Mindful Colouring — art */
    "B0DPWHZSGN"  /* Rise & Shine — encouragement */
  ];

  let books = [];
  let categories = [];
  let lang = I18N.defaultLang;
  let activeCategory = "all";
  let modalAsin = null;

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  function t(key) {
    const pack = I18N.strings[lang] || I18N.strings.en;
    return pack[key] != null ? pack[key] : (I18N.strings.en[key] || key);
  }

  function catLabel(id) {
    const row = I18N.categories[id];
    if (!row) return id;
    return row[lang] || row.en || id;
  }

  function blurbFor(book) {
    if (!book.blurb) return "";
    return book.blurb[lang] || book.blurb.en || "";
  }

  function detectLang() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && I18N.strings[saved]) return saved;
    const nav = (navigator.language || "en").toLowerCase();
    if (nav.startsWith("zh-tw") || nav.startsWith("zh-hk") || nav.includes("hant")) return "zh-Hant";
    if (nav.startsWith("zh")) return "zh-Hans";
    if (nav.startsWith("ja")) return "ja";
    if (nav.startsWith("ko")) return "ko";
    return "en";
  }

  function setLang(next) {
    if (!I18N.strings[next]) next = "en";
    lang = next;
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang === "zh-Hant" ? "zh-Hant" : lang === "zh-Hans" ? "zh-Hans" : lang;
    applyChrome();
    renderFilters();
    renderFeatured();
    renderGrid();
    if (modalAsin) openModal(modalAsin, true);
    $$(".lang-btn").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.lang === lang ? "true" : "false");
    });
  }

  function applyChrome() {
    $$("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const val = t(key);
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") el.placeholder = val;
      else el.textContent = val;
    });
    $$("[data-i18n-aria]").forEach((el) => {
      el.setAttribute("aria-label", t(el.getAttribute("data-i18n-aria")));
    });
    const year = $("#year");
    if (year) year.textContent = String(new Date().getFullYear());
  }

  function renderLangSwitcher() {
    const host = $("#lang-switcher");
    if (!host) return;
    host.innerHTML = "";
    I18N.langs.forEach((L) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "lang-btn";
      btn.dataset.lang = L.code;
      btn.textContent = L.short;
      btn.title = L.label;
      btn.setAttribute("aria-label", L.label);
      btn.setAttribute("aria-pressed", L.code === lang ? "true" : "false");
      btn.addEventListener("click", () => setLang(L.code));
      host.appendChild(btn);
    });
  }

  function renderFilters() {
    const host = $("#filters");
    if (!host) return;
    const ids = ["all"].concat(
      CAT_ORDER.filter((id) => books.some((b) => b.category === id))
    );
    host.innerHTML = "";
    host.setAttribute("aria-label", t("filterLabel"));
    ids.forEach((id) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chip";
      btn.dataset.cat = id;
      btn.setAttribute("aria-pressed", id === activeCategory ? "true" : "false");
      if (id === "all") btn.textContent = t("filterAll");
      else {
        const count = books.filter((b) => b.category === id).length;
        btn.textContent = `${catLabel(id)} · ${count}`;
      }
      btn.addEventListener("click", () => {
        activeCategory = id;
        renderFilters();
        renderGrid();
      });
      host.appendChild(btn);
    });
  }

  function visibleBooks() {
    if (activeCategory === "all") return books.slice();
    return books.filter((b) => b.category === activeCategory);
  }

  function buildCard(book, opts) {
    const featured = opts && opts.featured;
    const card = document.createElement("article");
    card.className = featured ? "book-card book-card--featured" : "book-card";
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `${t("openBook")}: ${book.title}`);

    const coverWrap = document.createElement("div");
    coverWrap.className = "book-cover-wrap";
    const img = document.createElement("img");
    img.className = "book-cover";
    img.src = book.cover;
    img.alt = "";
    img.loading = "lazy";
    img.width = 1000;
    img.height = 1000;
    coverWrap.appendChild(img);

    const body = document.createElement("div");
    body.className = "book-body";
    const chip = document.createElement("span");
    chip.className = "cat-chip";
    chip.textContent = catLabel(book.category);
    const h3 = document.createElement("h3");
    h3.className = "book-title";
    h3.textContent = book.title;
    const blurb = document.createElement("p");
    blurb.className = "book-blurb";
    blurb.textContent = blurbFor(book);
    const actions = document.createElement("div");
    actions.className = "book-actions";
    const detailsBtn = document.createElement("button");
    detailsBtn.type = "button";
    detailsBtn.className = "btn btn-ghost";
    detailsBtn.textContent = t("openBook");
    const buy = document.createElement("a");
    buy.className = "btn btn-primary btn-sm";
    buy.href = book.amazon.uk;
    buy.target = "_blank";
    buy.rel = "noopener noreferrer";
    buy.textContent = t("buyAmazon");
    buy.addEventListener("click", (e) => e.stopPropagation());
    actions.append(detailsBtn, buy);
    body.append(chip, h3, blurb, actions);
    card.append(coverWrap, body);

    const open = () => openModal(book.asin);
    card.addEventListener("click", open);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        open();
      }
    });
    detailsBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      open();
    });
    return card;
  }

  function renderFeatured() {
    const grid = $("#featured-grid");
    if (!grid) return;
    grid.innerHTML = "";
    const byAsin = Object.create(null);
    books.forEach((b) => { byAsin[b.asin] = b; });
    FEATURED_ASINS.forEach((asin) => {
      const book = byAsin[asin];
      if (book) grid.appendChild(buildCard(book, { featured: true }));
    });
  }

  function renderGrid() {
    const grid = $("#book-grid");
    const countEl = $("#results-count");
    if (!grid) return;
    const list = visibleBooks();
    if (countEl) countEl.textContent = t("results").replace("{n}", String(list.length));
    grid.innerHTML = "";
    if (!list.length) {
      const p = document.createElement("p");
      p.className = "empty";
      p.textContent = t("empty");
      grid.appendChild(p);
      return;
    }
    list.forEach((book) => {
      grid.appendChild(buildCard(book));
    });
  }

  function openModal(asin, refreshOnly) {
    const book = books.find((b) => b.asin === asin);
    const modal = $("#book-modal");
    if (!book || !modal) return;
    modalAsin = asin;
    $("#modal-cover").src = book.cover;
    $("#modal-cover").alt = book.title;
    $("#modal-title").textContent = book.title;
    $("#modal-blurb").textContent = blurbFor(book);
    $("#modal-chip").textContent = catLabel(book.category);
    $("#modal-desc").textContent = book.description || "";
    $("#modal-desc-note").textContent = t("englishNote");

    const meta = $("#modal-meta");
    meta.innerHTML = "";
    const rows = [
      [t("category"), catLabel(book.category)],
      [t("format"), book.format],
      [t("pages"), book.pages ? String(book.pages) : null],
      [t("isbn"), book.isbn],
      [t("published"), book.publicationDate]
    ];
    rows.forEach(([k, v]) => {
      if (!v) return;
      const dt = document.createElement("dt");
      dt.textContent = k;
      const dd = document.createElement("dd");
      dd.textContent = v;
      meta.append(dt, dd);
    });

    const buyUk = $("#modal-buy-uk");
    const buyUs = $("#modal-buy-us");
    buyUk.href = book.amazon.uk;
    buyUs.href = book.amazon.us;
    buyUk.textContent = t("buyUk");
    buyUs.textContent = t("buyUs");
    $("#modal-close").setAttribute("aria-label", t("close"));

    if (!refreshOnly) {
      modal.hidden = false;
      document.body.classList.add("modal-open");
      $("#modal-close").focus();
    }
  }

  function closeModal() {
    const modal = $("#book-modal");
    if (!modal) return;
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    modalAsin = null;
  }

  async function loadData() {
    const [booksRes, catsRes] = await Promise.all([
      fetch("data/books.json"),
      fetch("data/categories.json")
    ]);
    books = await booksRes.json();
    categories = await catsRes.json();
  }

  function bindModal() {
    const modal = $("#book-modal");
    $("#modal-close").addEventListener("click", closeModal);
    $(".modal-backdrop", modal).addEventListener("click", closeModal);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modalAsin) closeModal();
    });
  }

  async function init() {
    lang = detectLang();
    renderLangSwitcher();
    applyChrome();
    bindModal();
    const loading = $("#loading");
    try {
      await loadData();
      if (loading) loading.hidden = true;
      renderFilters();
      renderFeatured();
      renderGrid();
      setLang(lang);
    } catch (err) {
      if (loading) {
        loading.textContent = "Could not load catalog.";
        loading.hidden = false;
      }
      console.error(err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
