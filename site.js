const grid = document.querySelector('.glyph-grid');
const replay = document.querySelector('.replay');
const motion = window.matchMedia('(prefers-reduced-motion: reduce)');

function revealLetters() {
  grid.classList.remove('running');
  if (motion.matches) return;
  void grid.offsetWidth;
  grid.classList.add('running');
}

function updateMotion() {
  replay.hidden = motion.matches;
  revealLetters();
}

replay.addEventListener('click', revealLetters);
motion.addEventListener('change', updateMotion);
updateMotion();

const filters = document.querySelector('.filters');
const search = document.querySelector('#search');
const kind = document.querySelector('#kind');
const count = document.querySelector('#count');
const empty = document.querySelector('.empty');

function normalize(text) {
  return text.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replaceAll('ı', 'i').trim();
}

const records = [...document.querySelectorAll('.record')].map(element => ({
  element,
  kind: element.dataset.kind,
  text: normalize(element.textContent).replace(/\s+/g, ' '),
}));

function filterRecords() {
  const words = normalize(search.value).split(/\s+/);
  let visible = 0;
  for (const record of records) {
    const matches = (!kind.value || kind.value === record.kind) && words.every(word => record.text.includes(word));
    record.element.hidden = !matches;
    if (matches) visible++;
  }
  empty.hidden = visible > 0;
  document.querySelector('.clear-search').hidden = !search.value && !kind.value;
  count.textContent = visible + ' ' + count.dataset.label;
}

search.addEventListener('input', filterRecords);
kind.addEventListener('change', filterRecords);
filters.hidden = false;
filterRecords();

for (const card of document.querySelectorAll('.book-card')) {
  card.addEventListener('click', () => {
    const record = document.getElementById(card.hash.slice(1));
    if (!record.hidden) return;
    search.value = '';
    kind.value = '';
    filterRecords();
  });
}

const haptics = document.querySelector('.haptics');
let vibrationEnabled = false;
haptics.hidden = !('vibrate' in navigator);
haptics.addEventListener('click', () => {
  vibrationEnabled = !vibrationEnabled;
  haptics.setAttribute('aria-pressed', String(vibrationEnabled));
});

document.addEventListener('click', event => {
  const target = event.target.closest('a, button');
  if (!target) return;
  if (vibrationEnabled && !motion.matches && 'vibrate' in navigator) navigator.vibrate(8);
  if (motion.matches) return;
  target.classList.remove('tap-feedback');
  void target.offsetWidth;
  target.classList.add('tap-feedback');
});
document.addEventListener('animationend', event => {
  if (event.animationName === 'tap') event.target.classList.remove('tap-feedback');
});

if ('IntersectionObserver' in window) {
  const revealTargets = document.querySelectorAll('.bio-head, .summary-strip, .bio-copy, .editorial-figure, .timeline li, .featured, .record');
  const revealObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  }, { rootMargin: '0px 0px 30px 0px', threshold: 0.04 });
  document.documentElement.classList.add('motion-ready');
  for (const target of revealTargets) {
    target.classList.add('reveal');
    revealObserver.observe(target);
  }

  const sectionObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      for (const link of document.querySelectorAll('.nav a')) {
        if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    }
  }, { rootMargin: '-15% 0px -55% 0px' });
  for (const section of document.querySelectorAll('main > section, .light-panel > section, .tint > section')) {
    sectionObserver.observe(section);
  }
}

const progress = document.querySelector('.reading-progress');
let scrollFrame = 0;
function updateProgress() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const fraction = scrollable > 0 ? Math.min(1, Math.max(0, window.scrollY / scrollable)) : 0;
  progress.style.transform = 'scaleX(' + fraction + ')';
  scrollFrame = 0;
}
function queueProgress() {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateProgress);
}
window.addEventListener('scroll', queueProgress, { passive: true });
window.addEventListener('resize', queueProgress);
search.addEventListener('input', queueProgress);
kind.addEventListener('change', queueProgress);
updateProgress();

const clearSearch = document.querySelector('.clear-search');
clearSearch.addEventListener('click', () => {
  search.value = ''; kind.value = ''; filterRecords(); queueProgress(); search.focus();
});
for (const link of document.querySelectorAll('[data-kind-link]')) {
  link.addEventListener('click', () => {
    search.value = ''; kind.value = link.dataset.kindLink; filterRecords(); queueProgress();
  });
}
