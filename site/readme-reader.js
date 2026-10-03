/* Static README reader. The existing site picker changes ?lang=; this module
 * replaces the article in place. No server process or translation API is used. */
(function () {
  'use strict';

  var REPO = 'MaYangle/ai-engineering-from-scratch';
  var RAW = 'https://raw.githubusercontent.com/' + REPO + '/';
  var BLOB = 'https://github.com/' + REPO + '/blob/main/';
  var TREE = 'https://github.com/' + REPO + '/tree/main/';
  var LOCALES = { en: 1, es: 1, fr: 1, pt: 1, de: 1, it: 1, zh: 1, ja: 1, ko: 1, hi: 1, ar: 1, ru: 1, tr: 1 };
  var STATUS = {
    en: { loading: 'Loading the complete README…', full: 'Machine translation · English is the canonical source.', draft: 'Full translation is still being generated; some text may remain in English.', error: 'Could not load the README. Open it on GitHub instead.' },
    es: { loading: 'Cargando el README completo…', full: 'Traducción automática · El inglés es la versión canónica.', draft: 'La traducción completa está en curso; algunos textos pueden seguir en inglés.', error: 'No se pudo cargar el README. Ábrelo en GitHub.' },
    fr: { loading: 'Chargement du README complet…', full: 'Traduction automatique · La version anglaise fait foi.', draft: 'La traduction complète est en cours ; certains passages peuvent rester en anglais.', error: 'Impossible de charger le README. Ouvrez-le sur GitHub.' },
    pt: { loading: 'Carregando o README completo…', full: 'Tradução automática · O inglês é a versão canônica.', draft: 'A tradução completa está em andamento; alguns trechos podem permanecer em inglês.', error: 'Não foi possível carregar o README. Abra-o no GitHub.' },
    de: { loading: 'Vollständige README wird geladen…', full: 'Maschinelle Übersetzung · Die englische Fassung ist maßgeblich.', draft: 'Die vollständige Übersetzung läuft noch; einige Stellen können englisch sein.', error: 'README konnte nicht geladen werden. Öffne sie auf GitHub.' },
    it: { loading: 'Caricamento del README completo…', full: 'Traduzione automatica · La versione inglese è quella canonica.', draft: 'La traduzione completa è in corso; alcune parti potrebbero restare in inglese.', error: 'Impossibile caricare il README. Aprilo su GitHub.' },
    zh: { loading: '正在加载完整 README…', full: '机器翻译 · 以英文原文为准。', draft: '完整译文正在生成，部分内容暂时仍为英文。', error: '无法加载 README，请在 GitHub 查看。' },
    ja: { loading: 'README 全文を読み込み中…', full: '機械翻訳 · 英語版が正本です。', draft: '全文翻訳を生成中です。一部は英語のままです。', error: 'README を読み込めません。GitHub で開いてください。' },
    ko: { loading: '전체 README를 불러오는 중…', full: '기계 번역 · 영어 원문이 기준입니다.', draft: '전체 번역을 생성 중이며 일부는 영어로 표시될 수 있습니다.', error: 'README를 불러올 수 없습니다. GitHub에서 여세요.' },
    hi: { loading: 'पूरा README लोड हो रहा है…', full: 'मशीनी अनुवाद · अंग्रेज़ी मूल पाठ आधिकारिक है।', draft: 'पूरा अनुवाद तैयार हो रहा है; कुछ भाग अंग्रेज़ी में रह सकते हैं।', error: 'README लोड नहीं हो सका। इसे GitHub पर खोलें।' },
    ar: { loading: 'جارٍ تحميل README كاملًا…', full: 'ترجمة آلية · النص الإنجليزي هو المرجع.', draft: 'الترجمة الكاملة قيد الإنشاء؛ قد تبقى بعض الأجزاء بالإنجليزية.', error: 'تعذّر تحميل README. افتحه على GitHub.' },
    ru: { loading: 'Загружается полный README…', full: 'Машинный перевод · Английский оригинал является основным.', draft: 'Полный перевод ещё создаётся; часть текста может остаться на английском.', error: 'Не удалось загрузить README. Откройте его на GitHub.' },
    tr: { loading: 'Tam README yükleniyor…', full: 'Makine çevirisi · İngilizce metin esas alınır.', draft: 'Tam çeviri hazırlanıyor; bazı bölümler İngilizce kalabilir.', error: 'README yüklenemedi. GitHub üzerinde açın.' }
  };
  var content = document.getElementById('readmeContent');
  var status = document.getElementById('readmeStatus');
  var englishSource = null;
  var currentRequest = 0;

  function fetchText(path) {
    return fetch(RAW + path, { cache: 'no-cache' }).then(function (response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.text();
    });
  }

  function stripNavigation(md) {
    return md
      .replace(/^<p align="center"[^>]*><sub>[^\n]*<\/sub><\/p>\s*/i, '')
      .replace(/<!-- README-LANGUAGES:START -->[\s\S]*?<!-- README-LANGUAGES:END -->\s*/i, '')
      .replace(/^<p align="center">\s*<b>Read in your language:<\/b>[\s\S]*?<\/p>\s*/i, '');
  }

  function canonicalHeadings(md) {
    var inFence = false;
    var names = [];
    md.split(/\r?\n/).forEach(function (line) {
      if (/^\s*```/.test(line)) { inFence = !inFence; return; }
      if (inFence) return;
      var heading = line.match(/^#{1,6}\s+(.+)$/);
      if (heading) names.push(heading[1].replace(/<[^>]+>/g, '').replace(/\[[^\]]+\]\([^)]+\)/g, '').replace(/[`*_~]/g, ''));
    });
    var used = {};
    return names.map(function (name) {
      var base = name.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, '').trim().replace(/\s+/g, '-');
      if (!base) base = 'section';
      var count = used[base] || 0;
      used[base] = count + 1;
      return count ? base + '-' + count : base;
    });
  }

  function safeUrl(value) {
    var raw = String(value || '').trim();
    if (!raw || /[\u0000-\u001f]/.test(raw)) return '';
    if (raw.charAt(0) === '#') return raw;
    if (/^(https?:|mailto:)/i.test(raw)) return raw;
    if (/^[a-z][a-z0-9+.-]*:/i.test(raw) || raw.indexOf('//') === 0) return '';
    var clean = raw.replace(/^(?:\.\.\/)+/, '').replace(/^\.\//, '');
    if (/(^|\/)\.\.(\/|$)/.test(clean)) return '';
    return clean;
  }

  function sanitizeAndLink(markup, headings) {
    var template = document.createElement('template');
    template.innerHTML = markup;
    template.content.querySelectorAll('script,style,iframe,object,embed,form,input,button,meta,link,base,svg,math,video,audio,source,textarea,select').forEach(function (node) { node.remove(); });
    var attributes = { href: 1, src: 1, alt: 1, title: 1, width: 1, height: 1, align: 1, dir: 1, open: 1, name: 1, id: 1, colspan: 1, rowspan: 1 };
    template.content.querySelectorAll('*').forEach(function (node) {
      Array.prototype.slice.call(node.attributes).forEach(function (attribute) {
        var name = attribute.name.toLowerCase();
        if (!attributes[name] && name.indexOf('aria-') !== 0) node.removeAttribute(attribute.name);
      });
      if (node.hasAttribute('href')) {
        var href = safeUrl(node.getAttribute('href'));
        if (!href) node.removeAttribute('href');
        else if (href.charAt(0) !== '#' && !/^(https?:|mailto:)/i.test(href)) {
          node.setAttribute('href', (href.endsWith('/') ? TREE : BLOB) + href);
        } else node.setAttribute('href', href);
      }
      if (node.hasAttribute('src')) {
        var src = safeUrl(node.getAttribute('src'));
        if (!src || src.charAt(0) === '#') node.removeAttribute('src');
        else if (!/^https?:/i.test(src)) node.setAttribute('src', RAW + 'main/' + src);
        else node.setAttribute('src', src);
      }
      if (node.tagName === 'A' && /^https?:/i.test(node.getAttribute('href') || '')) {
        node.setAttribute('target', '_blank');
        node.setAttribute('rel', 'noopener noreferrer');
      }
    });
    var renderedHeadings = template.content.querySelectorAll('h1,h2,h3,h4,h5,h6');
    renderedHeadings.forEach(function (node, index) { if (headings[index]) node.id = headings[index]; });
    return template.content;
  }

  function paint(md, lang, kind) {
    if (!window.marked || typeof window.marked.parse !== 'function') throw new Error('Markdown renderer unavailable');
    var source = stripNavigation(md);
    var reference = stripNavigation(englishSource || md);
    var headings = canonicalHeadings(reference);
    var fragment = sanitizeAndLink(window.marked.parse(source, { gfm: true, breaks: false }), headings);
    content.replaceChildren(fragment);
    content.setAttribute('aria-busy', 'false');
    status.dataset.kind = kind;
    status.textContent = lang === 'en' ? '' : STATUS[lang][kind];
    document.title = (lang === 'en' ? 'README' : 'README · ' + (window.AIFS_LANGS.find(function (item) { return item.code === lang; }) || {}).native) + ' · AI Engineering from Scratch';
    if (location.hash) {
      var anchor = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (anchor) anchor.scrollIntoView();
    }
  }

  function show(requested) {
    var lang = LOCALES[requested] ? requested : 'en';
    var requestId = ++currentRequest;
    status.dataset.kind = 'loading';
    status.textContent = STATUS[lang].loading;
    content.setAttribute('aria-busy', 'true');
    var original = englishSource ? Promise.resolve(englishSource) : fetchText('main/README.md').then(function (md) { englishSource = md; return md; });
    original.then(function (english) {
      if (lang === 'en') return { text: english, kind: 'full' };
      return fetchText('translations/i18n/' + lang + '/README.full.md')
        .then(function (text) { return { text: text, kind: 'full' }; })
        .catch(function () {
          return fetchText('main/i18n/' + lang + '/README.md')
            .then(function (text) { return { text: text, kind: 'draft' }; });
        });
    }).then(function (result) {
      if (requestId !== currentRequest) return;
      paint(result.text, lang, result.kind);
    }).catch(function () {
      if (requestId !== currentRequest) return;
      content.setAttribute('aria-busy', 'false');
      status.dataset.kind = 'error';
      status.textContent = STATUS[lang].error;
      var link = document.createElement('a');
      link.href = 'https://github.com/' + REPO + '#readme';
      link.textContent = 'GitHub README';
      content.replaceChildren(link);
    });
  }

  window.AIFS_onLangChange = show;
  show(typeof window.AIFS_currentLang === 'function' ? window.AIFS_currentLang() : 'en');
})();
