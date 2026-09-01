const app = document.getElementById('app');
let currentUser = null;

// Bootstrap Icons SVG sprite (vendored into the image at build time — see
// Dockerfile — so this stays a local reference with no runtime CDN call).
function icon(name, size) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 16 16" fill="currentColor"><use href="/static/icons/bootstrap-icons.svg#${name}"></use></svg>`;
}
const PLAY_ICON = icon('play-fill', 12);
const PAUSE_ICON = icon('pause-fill', 12);
const ICON_PREV = icon('skip-start-fill', 14);
const ICON_NEXT = icon('skip-end-fill', 14);
const ICON_HOME = icon('house', 16);
const ICON_PLAYLISTS = icon('vinyl', 16);
const ICON_ARTISTS = icon('people-fill', 16);
const ICON_ADMIN = icon('shield-lock', 16);
const ICON_NOTE = icon('music-note-beamed', 15);
const ICON_NOTE_LG = icon('music-note-beamed', 28);
const ICON_SEARCH = icon('search', 14);
const ICON_HEART = icon('heart', 13);
const ICON_HEART_FILLED = icon('heart-fill', 13);
const ICON_REMOVE = icon('x-lg', 11);
const ICON_ADD = icon('plus-lg', 13);
const ICON_LOCK = icon('lock-fill', 10);
const ICON_LIBRARY = icon('collection-play', 34);
const ICON_PERSON_CIRCLE = icon('person-circle', 22);

// 50 deterministic cover-art gradients, spread evenly around the color
// wheel via the golden-angle (137.508°) so adjacent ids don't land on
// similar hues. Same id always gets the same color across reloads.
const CARD_PALETTE = Array.from({ length: 50 }, (_, i) => {
  const h1 = Math.round((i * 137.508) % 360);
  const h2 = Math.round((h1 + 35) % 360);
  return `linear-gradient(135deg, hsl(${h1} 62% 46%), hsl(${h2} 58% 34%))`;
});
function cardArtBg(id) {
  return CARD_PALETTE[Math.abs(Number(id) || 0) % CARD_PALETTE.length];
}

// Fake playback state — no audio, just UI feedback (now-playing bar +
// equalizer + per-row play/pause icons).
let nowPlaying = null; // { id, title, artist }
let isPlaying = false;

// Self-flagging hooks: the flag only appears in the DOM once attacker-
// controlled markup you injected actually executes as script.
window.wfXssFlag = () => {
  app.insertAdjacentHTML('beforeend', '<p id="wf-xss-flag" style="color:#ff6f59">FLAG{wf_dom_xss_confirmed}</p>');
};
window.wfXssFlag2 = () => {
  app.insertAdjacentHTML('beforeend', '<p id="wf-xss-flag2" style="color:#ff6f59">FLAG{wf_stored_xss_confirmed}</p>');
};

async function api(path, opts) {
  const res = await fetch(path, Object.assign({ headers: { 'Content-Type': 'application/json' } }, opts));
  return res.json();
}

function nav(path) {
  history.pushState({}, '', path);
  render();
}

async function refreshCurrentUser() {
  const me = await api('/api/auth/me');
  currentUser = me.user || null;
}

// Sidebar "Your Library" data — real Following/Recently-played/Playlists, not fake.
let sidebarLibrary = { recent: [], following: [], playlists: [] };

async function refreshSidebarLibrary() {
  if (!currentUser) {
    sidebarLibrary = { recent: [], following: [], playlists: [] };
    return;
  }
  const [recent, following, playlists] = await Promise.all([
    api(`/api/users/${currentUser.id}/recent`),
    api(`/api/users/${currentUser.id}/following`),
    api('/api/playlists/mine'),
  ]);
  sidebarLibrary = {
    recent: Array.isArray(recent) ? recent : [],
    following: Array.isArray(following) ? following : [],
    playlists: Array.isArray(playlists) ? playlists : [],
  };
}

async function refreshSession() {
  await refreshCurrentUser();
  await refreshSidebarLibrary();
}

function sidebarLibraryHtml() {
  if (!currentUser) {
    return `
      <div class="wf-sidebar-guest">
        <div class="wf-sidebar-guest-icon">${ICON_LIBRARY}</div>
        <p>Log in to build your library — save playlists, follow artists, and keep a play history.</p>
        <a href="/account" data-link class="wf-btn wf-btn-ghost wf-sidebar-login-btn">Log in</a>
      </div>`;
  }
  return `
    <div class="wf-sidebar-library">
      <div class="wf-sidebar-heading">Your Library</div>

      <div class="wf-sidebar-subheading">Playlists</div>
      <form id="wf-sidebar-create-playlist-form" class="wf-sidebar-create-form">
        <input type="text" name="title" placeholder="New playlist name" maxlength="60">
        <button type="submit" title="Create playlist">${ICON_ADD}</button>
      </form>
      ${sidebarLibrary.playlists.length
        ? sidebarLibrary.playlists.map(p => `
          <div class="wf-sidebar-lib-row">
            <a href="/playlist/${p.id}" data-link class="wf-sidebar-lib-item wf-sidebar-lib-item-art">
              <span class="wf-sidebar-swatch" style="background:${cardArtBg(p.id)}"></span>
              <span class="wf-sidebar-lib-text">${escapeHtml(p.title)}</span>
              ${p.is_private ? `<span class="wf-sidebar-lock">${ICON_LOCK}</span>` : ''}
            </a>
            <button class="wf-sidebar-delete-btn" data-delete-playlist data-playlist-id="${p.id}" title="Delete playlist">${ICON_REMOVE}</button>
          </div>`).join('')
        : '<div class="wf-sidebar-lib-empty">No playlists yet</div>'}

      <div class="wf-sidebar-subheading">Following</div>
      ${sidebarLibrary.following.length
        ? sidebarLibrary.following.map(f => `
          <a href="/artist/${f.artist_id}" data-link class="wf-sidebar-lib-item wf-sidebar-lib-item-art">
            <span class="wf-sidebar-swatch wf-sidebar-swatch-round" style="background:${cardArtBg(f.artist_id)}"></span>
            <span class="wf-sidebar-lib-text">${escapeHtml(f.artist_name)}</span>
          </a>`).join('')
        : '<div class="wf-sidebar-lib-empty">Nothing followed yet</div>'}

      <div class="wf-sidebar-subheading">Recently played</div>
      ${sidebarLibrary.recent.length
        ? sidebarLibrary.recent.slice(0, 5).map(r => `
          <div class="wf-sidebar-lib-item wf-sidebar-lib-item-art wf-sidebar-lib-static">
            <span class="wf-sidebar-swatch" style="background:${cardArtBg(r.id)}"></span>
            <span class="wf-sidebar-lib-text">${escapeHtml(r.title)}</span>
          </div>`).join('')
        : '<div class="wf-sidebar-lib-empty">Nothing played yet</div>'}
    </div>`;
}

// Patches just the sidebar's library slot in place (e.g. after a follow
// toggle), without a full layout() re-render.
async function syncSidebarLibrary() {
  await refreshSidebarLibrary();
  const el = document.querySelector('.wf-sidebar-lib-slot');
  if (el) el.innerHTML = sidebarLibraryHtml();
}

function isActive(href) {
  if (href === '/') return location.pathname === '/';
  return location.pathname.startsWith(href);
}

function followBtnHtml(following) {
  return `${following ? ICON_HEART_FILLED : ICON_HEART}<span>${following ? 'Following' : 'Follow'}</span>`;
}

let playProgress = 0; // fake elapsed seconds
let playTimerHandle = null;

function formatTime(sec) {
  sec = Math.max(0, Math.floor(sec));
  return `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;
}

function stopPlayTimer() {
  if (playTimerHandle) { clearInterval(playTimerHandle); playTimerHandle = null; }
}

function startPlayTimer() {
  stopPlayTimer();
  playTimerHandle = setInterval(() => {
    if (!nowPlaying) return stopPlayTimer();
    playProgress += 1;
    if (playProgress >= nowPlaying.duration) {
      // Track "ends" — same as a real player, drop back to paused at 0.
      playProgress = 0;
      isPlaying = false;
      stopPlayTimer();
    }
    updateProgressUI();
  }, 1000);
}

function playTrack(id, title, artist, duration, artistId) {
  nowPlaying = { id: Number(id), title, artist, duration: duration || 180, artistId: artistId ? Number(artistId) : null };
  isPlaying = true;
  playProgress = 0;
  startPlayTimer();
  syncPlayerState();
}

function togglePlay() {
  if (!nowPlaying) return;
  isPlaying = !isPlaying;
  if (isPlaying) startPlayTimer(); else stopPlayTimer();
  syncPlayerState();
}

// Cheap per-second DOM patch (progress fill, time label, play/pause icon)
// without rebuilding the whole player bar every tick.
function updateProgressUI() {
  if (!nowPlaying) return;
  const pct = Math.min(100, (playProgress / nowPlaying.duration) * 100);
  const fill = document.querySelector('.wf-player-progress-fill');
  if (fill) fill.style.width = pct + '%';
  const elapsed = document.querySelector('.wf-player-elapsed');
  if (elapsed) elapsed.textContent = `${formatTime(playProgress)} / ${formatTime(nowPlaying.duration)}`;
  const footer = document.querySelector('.wf-player');
  if (footer) footer.classList.toggle('wf-player-playing', isPlaying);
  const tpIcon = document.getElementById('wf-tp-play-btn');
  if (tpIcon) tpIcon.innerHTML = isPlaying ? PAUSE_ICON : PLAY_ICON;
  document.querySelectorAll('[data-play]').forEach((btn) => {
    const active = nowPlaying.id === Number(btn.dataset.id);
    btn.closest('.wf-track')?.classList.toggle('wf-track-active', !!active);
    btn.innerHTML = active && isPlaying ? PAUSE_ICON : PLAY_ICON;
  });
}

function playerBarHtml() {
  const title = nowPlaying ? escapeHtml(nowPlaying.title) : 'Nothing playing';
  const artist = nowPlaying ? escapeHtml(nowPlaying.artist) : '&mdash;';
  const artistHtml = nowPlaying && nowPlaying.artistId
    ? `<a href="/artist/${nowPlaying.artistId}" data-link class="wf-player-artist">${artist}</a>`
    : `<span class="wf-player-artist">${artist}</span>`;
  const icon = isPlaying ? PAUSE_ICON : PLAY_ICON;
  const pct = nowPlaying ? Math.min(100, (playProgress / nowPlaying.duration) * 100) : 0;
  const timeLabel = nowPlaying ? `${formatTime(playProgress)} / ${formatTime(nowPlaying.duration)}` : '';
  return `
    <div class="wf-player-progress-line"><div class="wf-player-progress-fill" style="width:${pct}%"></div></div>
    <div class="wf-player-track">
      <div class="wf-player-art"></div>
      <div class="wf-player-meta">
        <span class="wf-player-title">${title}</span>
        ${artistHtml}
      </div>
      ${nowPlaying ? `<button class="wf-add-btn wf-player-add" data-open-add-sheet data-track-id="${nowPlaying.id}" data-track-title="${escapeAttr(nowPlaying.title)}" title="Add to playlist">${ICON_ADD}</button>` : ''}
    </div>
    <div class="wf-player-transport">
      <span class="wf-tp-btn">${ICON_PREV}</span>
      <span class="wf-tp-btn wf-tp-play" id="wf-tp-play-btn">${icon}</span>
      <span class="wf-tp-btn">${ICON_NEXT}</span>
      <span class="wf-player-elapsed">${timeLabel}</span>
    </div>
    <div class="wf-eq" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
  `;
}

// Patches just the persistent player bar + any visible track rows in place,
// rather than a full layout() re-render, so playing a track doesn't reset
// scroll position or whatever page you're on.
function syncPlayerState() {
  const footer = document.querySelector('.wf-player');
  if (footer) {
    footer.className = 'wf-player' + (isPlaying ? ' wf-player-playing' : '');
    footer.innerHTML = playerBarHtml();
  }
  document.querySelectorAll('[data-play]').forEach((btn) => {
    const active = nowPlaying && nowPlaying.id === Number(btn.dataset.id);
    btn.closest('.wf-track')?.classList.toggle('wf-track-active', !!active);
    btn.innerHTML = active && isPlaying ? PAUSE_ICON : PLAY_ICON;
  });
}

function trackRowHtml(t, playerArtist, badgeText, removePlaylistId, artistId) {
  const active = nowPlaying && nowPlaying.id === Number(t.id);
  const icon = active && isPlaying ? PAUSE_ICON : PLAY_ICON;
  const removeBtn = removePlaylistId
    ? `<button class="wf-remove-btn" data-remove-track data-playlist-id="${removePlaylistId}" data-track-id="${t.id}" title="Remove from playlist">${ICON_REMOVE}</button>`
    : '';
  const artistIdAttr = artistId ? ` data-artist-id="${artistId}"` : '';
  return `
    <div class="wf-track${active ? ' wf-track-active' : ''}">
      <button class="wf-play-btn" data-play data-id="${t.id}" data-title="${escapeAttr(t.title)}" data-artist="${escapeAttr(playerArtist)}" data-duration="${t.duration_sec || 180}"${artistIdAttr}>${icon}</button>
      <span class="wf-track-title">${escapeHtml(t.title)}</span>
      <span class="wf-badge">${escapeHtml(badgeText)}</span>
      <button class="wf-add-btn" data-open-add-sheet data-track-id="${t.id}" data-track-title="${escapeAttr(t.title)}" title="Add to playlist">${ICON_ADD}</button>
      ${removeBtn}
    </div>`;
}

// Transient toast, independent of whatever page is currently mounted —
// appended straight to <body> and self-removing, so it survives being
// triggered from the persistent player bar as well as from page content.
function showToast(text, isFlag) {
  const id = 'wf-toast-' + Date.now() + Math.random().toString(36).slice(2, 6);
  document.body.insertAdjacentHTML('beforeend', `<div class="wf-toast${isFlag ? ' wf-toast-flag' : ''}" id="${id}">${escapeHtml(text)}</div>`);
  const el = document.getElementById(id);
  requestAnimationFrame(() => el.classList.add('wf-toast-show'));
  setTimeout(() => {
    el.classList.remove('wf-toast-show');
    setTimeout(() => el.remove(), 300);
  }, isFlag ? 6000 : 2600);
}

// "Add to playlist" side sheet — reachable from any track row or the
// now-playing bar. The picker only lists *your own* playlists (from
// /api/playlists/mine), but the add itself goes through the same
// POST /api/playlists/<id>/tracks endpoint used elsewhere, which never
// checks ownership — so the UI looks scoped to "your" playlists while the
// API underneath it happily accepts anyone else's playlist id too.
function addToPlaylistSheetHtml(trackId, trackTitle, playlists) {
  return `
    <div class="wf-sheet-backdrop" id="wf-add-sheet-backdrop">
      <aside class="wf-sheet" id="wf-add-sheet">
        <div class="wf-sheet-head">
          <div>
            <h3>Add to playlist</h3>
            <p class="wf-sheet-track">${escapeHtml(trackTitle)}</p>
          </div>
          <button class="wf-sheet-close" id="wf-sheet-close-btn" title="Close">${ICON_REMOVE}</button>
        </div>
        <div class="wf-sheet-list">
          ${playlists.length ? playlists.map(p => `
            <button class="wf-sheet-item" data-add-target data-playlist-id="${p.id}" data-track-id="${trackId}">
              <span class="wf-sidebar-swatch" style="background:${cardArtBg(p.id)}"></span>
              <span class="wf-sheet-item-text">${escapeHtml(p.title)}</span>
              ${p.is_private ? `<span class="wf-sidebar-lock">${ICON_LOCK}</span>` : ''}
            </button>`).join('')
            : `<p class="wf-sidebar-lib-empty">No playlists yet — create one from your Account page.</p>`}
        </div>
      </aside>
    </div>`;
}

async function openAddToPlaylistSheet(trackId, trackTitle) {
  if (!currentUser) return nav('/account');
  closeAddToPlaylistSheet();
  const playlists = await api('/api/playlists/mine');
  document.body.insertAdjacentHTML('beforeend', addToPlaylistSheetHtml(trackId, trackTitle, Array.isArray(playlists) ? playlists : []));
  requestAnimationFrame(() => document.getElementById('wf-add-sheet')?.classList.add('wf-sheet-open'));
}

function closeAddToPlaylistSheet() {
  const backdrop = document.getElementById('wf-add-sheet-backdrop');
  if (!backdrop) return;
  backdrop.remove();
}

function topbarAccountHtml() {
  if (!currentUser) {
    return `<a href="/account" data-link class="wf-topbar-account" title="Log in">${ICON_PERSON_CIRCLE}</a>`;
  }
  const initial = (currentUser.display_name || currentUser.username || '?').trim().charAt(0).toUpperCase();
  return `
    <a href="/account" data-link class="wf-topbar-account wf-topbar-avatar${isActive('/account') ? ' active' : ''}" title="${escapeAttr(currentUser.display_name)}" style="background:${cardArtBg(currentUser.id)}">
      <span>${initial}</span>
    </a>`;
}

function layout(body) {
  document.body.innerHTML = `
    <div class="wf-shell">
      <aside class="wf-sidebar">
        <a class="wf-brand" href="/" data-link><span class="wf-brand-mark">${ICON_NOTE}</span> Waveform</a>
        <form id="wf-search-form" class="wf-sidebar-search">
          <span class="wf-search-icon">${ICON_SEARCH}</span>
          <input type="text" name="q" placeholder="What do you want to play?">
        </form>
        <nav class="wf-sidenav">
          <a href="/" data-link class="wf-sidenav-item${isActive('/') ? ' active' : ''}">${ICON_HOME}<span>Home</span></a>
          <a href="/playlists" data-link class="wf-sidenav-item${isActive('/playlists') ? ' active' : ''}">${ICON_PLAYLISTS}<span>Playlists</span></a>
          <a href="/artists" data-link class="wf-sidenav-item${isActive('/artists') ? ' active' : ''}">${ICON_ARTISTS}<span>Artists</span></a>
          ${currentUser && currentUser.is_admin ? `<a href="/admin" data-link class="wf-sidenav-item wf-sidenav-admin${isActive('/admin') ? ' active' : ''}">${ICON_ADMIN}<span>Admin</span></a>` : ''}
        </nav>
        <div class="wf-sidebar-lib-slot">${sidebarLibraryHtml()}</div>
        <div class="wf-sidebar-foot">
          <a href="/commonhuman">CommonHuman-Lab</a>
        </div>
      </aside>
      <div class="wf-topbar">${topbarAccountHtml()}</div>
      <main id="wf-main" class="wf-main">${body}</main>
      <footer class="wf-player${isPlaying ? ' wf-player-playing' : ''}">${playerBarHtml()}</footer>
    </div>
  `;
  const form = document.getElementById('wf-search-form');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = new FormData(form).get('q') || '';
    nav('/search?q=' + encodeURIComponent(q));
  });
}

// Registered once at load, not inside layout() — layout() replaces
// document.body's *children* via innerHTML on every navigation, but the
// body element itself persists, so a listener added inside layout() would
// stack a new copy on every single-page-app navigation instead of being
// replaced. Event delegation off this one listener still reaches every
// dynamically-inserted [data-link]/[data-play] element going forward.
document.body.addEventListener('click', (e) => {
  const link = e.target.closest('[data-link]');
  if (link) {
    e.preventDefault();
    nav(link.getAttribute('href'));
    return;
  }
  const playBtn = e.target.closest('[data-play]');
  if (playBtn) {
    const id = Number(playBtn.dataset.id);
    if (nowPlaying && nowPlaying.id === id) togglePlay();
    else playTrack(id, playBtn.dataset.title, playBtn.dataset.artist, Number(playBtn.dataset.duration), playBtn.dataset.artistId);
    return;
  }
  if (e.target.closest('#wf-tp-play-btn')) togglePlay();
  const removeBtn = e.target.closest('[data-remove-track]');
  if (removeBtn) {
    const playlistId = removeBtn.dataset.playlistId;
    const trackId = removeBtn.dataset.trackId;
    api(`/api/playlists/${playlistId}/tracks/${trackId}`, { method: 'DELETE' }).then(async (result) => {
      await renderPlaylist(playlistId);
      if (result.flag) showPlaylistFlag(result.flag);
    });
    return;
  }
  const openAddBtn = e.target.closest('[data-open-add-sheet]');
  if (openAddBtn) {
    openAddToPlaylistSheet(Number(openAddBtn.dataset.trackId), openAddBtn.dataset.trackTitle);
    return;
  }
  const deletePlaylistBtn = e.target.closest('[data-delete-playlist]');
  if (deletePlaylistBtn) {
    const playlistId = deletePlaylistBtn.dataset.playlistId;
    if (!confirm('Delete this playlist? This cannot be undone.')) return;
    api(`/api/playlists/${playlistId}`, { method: 'DELETE' }).then(async () => {
      showToast('Playlist deleted.', false);
      await syncSidebarLibrary();
      if (location.pathname === `/playlist/${playlistId}`) nav('/playlists');
      else if (location.pathname === '/account') renderAccount();
    });
    return;
  }
  if (e.target.closest('#wf-sheet-close-btn') || e.target.id === 'wf-add-sheet-backdrop') {
    closeAddToPlaylistSheet();
    return;
  }
  const addTarget = e.target.closest('[data-add-target]');
  if (addTarget) {
    const playlistId = addTarget.dataset.playlistId;
    const trackId = Number(addTarget.dataset.trackId);
    api(`/api/playlists/${playlistId}/tracks`, {
      method: 'POST',
      body: JSON.stringify({ track_id: trackId }),
    }).then((result) => {
      closeAddToPlaylistSheet();
      showToast(result.flag || 'Added to playlist.', !!result.flag);
    });
  }
});

// The sidebar's quick-create form gets replaced every time syncSidebarLibrary()
// patches the library slot in place, so it's handled via the same top-level
// delegation as clicks rather than a listener re-attached on every re-render.
document.body.addEventListener('submit', (e) => {
  const form = e.target.closest('#wf-sidebar-create-playlist-form');
  if (!form) return;
  e.preventDefault();
  const title = (new FormData(form).get('title') || '').trim();
  if (!title) return;
  api('/api/playlists', { method: 'POST', body: JSON.stringify({ title }) }).then(async () => {
    await syncSidebarLibrary();
  });
});

async function renderHome() {
  const playlists = await api('/api/playlists/featured');
  layout(`
    <h1>Featured playlists</h1>
    <p class="wf-lede">Hand-picked mixes from across Waveform.</p>
    <div class="wf-grid">
      ${playlists.map(p => `
        <a class="wf-card" href="/playlist/${p.id}" data-link>
          <div class="wf-card-art" style="background:${cardArtBg(p.id)}">${ICON_NOTE_LG}</div>
          <h3>${escapeHtml(p.title)}</h3>
          <p>${escapeHtml(p.description)}</p>
        </a>`).join('')}
    </div>
  `);
}

async function renderArtists() {
  const artists = await api('/api/artists');
  layout(`
    <h1>Artists</h1>
    <p class="wf-lede">${artists.length} artists on the platform.</p>
    <div class="wf-grid">
      ${artists.map(a => `
        <a class="wf-card" href="/artist/${a.id}" data-link>
          <div class="wf-card-art" style="background:${cardArtBg(a.id)}">${ICON_NOTE_LG}</div>
          <h3>${escapeHtml(a.name)}</h3>
          <p>${escapeHtml(a.genre)}</p>
        </a>`).join('')}
    </div>
  `);
}

async function renderPlaylists() {
  const playlists = await api('/api/playlists/featured');
  layout(`
    <h1>Playlists</h1>
    <p class="wf-lede">${playlists.length} public playlists from across Waveform.</p>
    <div class="wf-page-filter">
      <span class="wf-search-icon">${ICON_SEARCH}</span>
      <input type="text" id="wf-playlist-filter" placeholder="Filter by title, description, or creator...">
    </div>
    <div class="wf-grid" id="wf-playlist-grid">
      ${playlists.map(p => `
        <a class="wf-card" href="/playlist/${p.id}" data-link data-filter="${escapeAttr((p.title + ' ' + p.description + ' ' + p.owner).toLowerCase())}">
          <div class="wf-card-art" style="background:${cardArtBg(p.id)}">${ICON_NOTE_LG}</div>
          <h3>${escapeHtml(p.title)}</h3>
          <p>${escapeHtml(p.description)}</p>
        </a>`).join('')}
    </div>
    <p class="wf-lede" id="wf-playlist-filter-empty" style="display:none">No playlists match that filter.</p>
  `);
}

async function renderArtist(id) {
  const [data, followData, allArtists] = await Promise.all([
    api(`/api/artists/${id}`),
    api(`/api/artists/${id}/followers/count`),
    api('/api/artists'),
  ]);
  if (data.error) return layout(`<h1>Not found</h1>`);
  const alreadyFollowing = currentUser && sidebarLibrary.following.some(f => f.artist_id === Number(id));
  const listeners = (data.artist.monthly_listeners || 0).toLocaleString();
  const related = Array.isArray(allArtists) ? allArtists.filter(a => a.id !== Number(id)).slice(0, 4) : [];
  layout(`
    <h1>${escapeHtml(data.artist.name)} <span class="wf-badge">${escapeHtml(data.artist.genre)}</span></h1>
    <p class="wf-lede">${listeners} monthly listeners</p>
    <p class="wf-lede">${escapeHtml(data.artist.bio)}</p>
    <div class="wf-inline-form">
      <button class="wf-btn wf-btn-ghost wf-follow-toggle" id="wf-follow-btn">${followBtnHtml(alreadyFollowing)}</button>
      <span id="wf-follow-count">${followData.follower_count} followers</span>
    </div>

    ${data.top_tracks && data.top_tracks.length ? `
      <h2>Popular</h2>
      ${data.top_tracks.map(t => trackRowHtml(t, data.artist.name, t.album_title, null, data.artist.id)).join('')}
    ` : ''}

    <h2>Albums</h2>
    <div class="wf-grid">
      ${data.albums.map(al => `
        <a class="wf-card" href="/album/${al.id}" data-link>
          <div class="wf-card-art" style="background:${cardArtBg(al.id)}">${ICON_NOTE_LG}</div>
          <h3>${escapeHtml(al.title)}</h3>
          <p>${al.year}</p>
        </a>`).join('')}
    </div>

    ${related.length ? `
      <h2>Fans also like</h2>
      <div class="wf-grid">
        ${related.map(a => `
          <a class="wf-card" href="/artist/${a.id}" data-link>
            <div class="wf-card-art" style="background:${cardArtBg(a.id)}">${ICON_NOTE_LG}</div>
            <h3>${escapeHtml(a.name)}</h3>
            <p>${escapeHtml(a.genre)}</p>
          </a>`).join('')}
      </div>
    ` : ''}
  `);
  const followBtn = document.getElementById('wf-follow-btn');
  followBtn.addEventListener('click', async () => {
    if (!currentUser) return nav('/account');
    const result = await api(`/api/artists/${id}/follow`, { method: 'POST' });
    followBtn.innerHTML = followBtnHtml(result.following);
    document.getElementById('wf-follow-count').textContent = `${result.follower_count} followers`;
    await syncSidebarLibrary();
  });
}

async function renderAlbum(id) {
  const data = await api(`/api/albums/${id}`);
  if (data.error) return layout(`<h1>Not found</h1>`);
  layout(`
    <h1>${escapeHtml(data.album.title)}</h1>
    <p class="wf-lede">by <a href="/artist/${data.album.artist_id}" data-link>${escapeHtml(data.album.artist_name)}</a> &middot; ${data.album.year}</p>
    ${data.tracks.map(t => trackRowHtml(t, data.album.artist_name, `${Math.floor(t.duration_sec / 60)}:${String(t.duration_sec % 60).padStart(2, '0')}`, null, data.album.artist_id)).join('')}
  `);
}

async function showPlaylistFlag(flag) {
  const el = document.getElementById('wf-playlist-flash');
  if (el) {
    el.textContent = flag;
    el.style.display = 'block';
  }
}

async function renderPlaylist(id) {
  const data = await api(`/api/playlists/${id}`);
  if (data.error) return layout(`<h1>Not found</h1>`);
  // Stored-XSS sink: owner display name is rendered unescaped.
  layout(`
    <h1>${escapeHtml(data.playlist.title)}</h1>
    <p class="wf-lede">Created by ${data.playlist.owner}</p>
    <p>${escapeHtml(data.playlist.description)}</p>
    ${data.tracks.map(t => trackRowHtml(t, t.artist_name, t.album_title, id, t.artist_id)).join('')}
    <form class="wf-inline-form wf-section" id="wf-add-track-form">
      <input type="number" name="track_id" placeholder="Track ID" required>
      <button type="submit" class="wf-btn wf-btn-ghost wf-btn-sm">${ICON_ADD}<span>Add track</span></button>
    </form>
    <p id="wf-playlist-flash" class="wf-flag-banner" style="display:none"></p>
  `);
  document.getElementById('wf-add-track-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const result = await api(`/api/playlists/${id}/tracks`, {
      method: 'POST',
      body: JSON.stringify({ track_id: Number(fd.get('track_id')) }),
    });
    await renderPlaylist(id);
    if (result.flag) showPlaylistFlag(result.flag);
  });
}

async function renderSearch(q) {
  const results = await api('/api/search?q=' + encodeURIComponent(q));
  // DOM XSS sink: the raw query is interpolated into the results heading
  // without escaping.
  layout(`
    <h1>Results for "${q}"</h1>
    ${Array.isArray(results) ? results.map(r => trackRowHtml(r, r.subtitle, r.subtitle)).join('') : `<p class="wf-error">${escapeHtml(results.error || 'search failed')}</p>`}
  `);
}

async function renderAccount() {
  const me = await api('/api/auth/me');
  if (!me.user) return renderLogin();
  const [recent, following, mine] = await Promise.all([
    api(`/api/users/${me.user.id}/recent`),
    api(`/api/users/${me.user.id}/following`),
    api('/api/playlists/mine'),
  ]);
  layout(`
    <h1>Account</h1>
    <p class="wf-lede">Signed in as <strong>${escapeHtml(me.user.username)}</strong>${me.user.is_admin ? ' <span class="wf-badge">admin</span>' : ''}</p>
    <form class="wf-form" id="wf-account-form">
      <label>Display name<input type="text" name="display_name" value="${escapeAttr(me.user.display_name)}"></label>
      <label>Bio<textarea name="bio">${escapeHtml(me.user.bio || '')}</textarea></label>
      <button type="submit">Save</button>
    </form>
    <p><a href="#" id="wf-logout">Log out</a></p>

    <div class="wf-section">
      <h2>Recently played</h2>
      ${Array.isArray(recent) && recent.length ? recent.map(r => `<div class="wf-track"><span class="wf-track-title">${escapeHtml(r.title)}</span><span class="wf-badge">${escapeHtml(r.note)}</span></div>`).join('') : '<p class="wf-lede">Nothing played yet.</p>'}
    </div>

    <div class="wf-section">
      <h2>Following</h2>
      ${Array.isArray(following) && following.length ? following.map(f => `<div class="wf-track"><a class="wf-track-title" href="/artist/${f.artist_id}" data-link>${escapeHtml(f.artist_name)}</a><span class="wf-badge">${escapeHtml(f.note)}</span></div>`).join('') : '<p class="wf-lede">Not following anyone yet.</p>'}
    </div>

    <div class="wf-section">
      <h2>Your playlists</h2>
      <form class="wf-inline-form" id="wf-create-playlist-form">
        <input type="text" name="title" placeholder="Playlist title" required>
        <input type="text" name="description" placeholder="Description (optional)">
        <label class="wf-checkbox-label"><input type="checkbox" name="is_private"> Private</label>
        <button type="submit" class="wf-btn wf-btn-ghost wf-btn-sm">${ICON_ADD}<span>Create</span></button>
      </form>
      ${Array.isArray(mine) && mine.length ? mine.map(p => `<div class="wf-track"><a class="wf-track-title" href="/playlist/${p.id}" data-link>${escapeHtml(p.title)}</a><span class="wf-badge">${p.is_private ? 'Private' : 'Public'}</span><button class="wf-remove-btn" data-delete-playlist data-playlist-id="${p.id}" title="Delete playlist">${ICON_REMOVE}</button></div>`).join('') : '<p class="wf-lede">No playlists yet.</p>'}
    </div>
  `);
  document.getElementById('wf-account-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api('/api/account', { method: 'POST', body: JSON.stringify({ display_name: fd.get('display_name'), bio: fd.get('bio') }) });
    await refreshSession();
    renderAccount();
  });
  document.getElementById('wf-logout').addEventListener('click', async (e) => {
    e.preventDefault();
    await api('/api/auth/logout', { method: 'POST' });
    await refreshSession();
    nav('/');
  });
  document.getElementById('wf-create-playlist-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api('/api/playlists', {
      method: 'POST',
      body: JSON.stringify({
        title: fd.get('title'),
        description: fd.get('description'),
        is_private: fd.get('is_private') ? 1 : 0,
      }),
    });
    renderAccount();
  });
}

function renderLogin() {
  layout(`
    <h1>Log in</h1>
    <form class="wf-form" id="wf-login-form">
      <input type="text" name="username" placeholder="Username" required>
      <input type="password" name="password" placeholder="Password" required>
      <button type="submit">Log in</button>
    </form>
    <p id="wf-login-error" class="wf-error"></p>
  `);
  document.getElementById('wf-login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const result = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ username: fd.get('username'), password: fd.get('password') }) });
    if (result.ok) { await refreshSession(); nav('/account'); } else { document.getElementById('wf-login-error').textContent = result.error; }
  });
}

async function renderAdmin() {
  const me = await api('/api/auth/me');
  if (!me.user) return renderLogin();
  const stats = await api('/api/admin/stats');
  layout(`
    <h1>Admin dashboard</h1>
    ${stats.error ? `<p class="wf-error">${escapeHtml(stats.error)}</p>` : `
      <p>Users: ${stats.user_count}</p>
      <p>Playlists: ${stats.playlist_count}</p>
      <p style="color:#ff6f59">${escapeHtml(stats.flag)}</p>
    `}

    <div class="wf-section">
      <h2>Import cover art</h2>
      <p class="wf-lede">Fetch cover art from a URL for a given artist id.</p>
      <form class="wf-form" id="wf-import-form">
        <label>Artist ID<input type="number" name="artist_id" value="1"></label>
        <label>Image URL<input type="text" name="url" placeholder="https://..."></label>
        <button type="submit">Import</button>
      </form>
      <pre class="wf-console" id="wf-import-result"></pre>
    </div>
  `);
  const importForm = document.getElementById('wf-import-form');
  importForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(importForm);
    const result = await api('/api/admin/import-cover', {
      method: 'POST',
      body: JSON.stringify({ artist_id: Number(fd.get('artist_id')), url: fd.get('url') }),
    });
    document.getElementById('wf-import-result').textContent = JSON.stringify(result, null, 2);
  });
}

function render404() {
  layout(`<h1>Not found</h1>`);
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function escapeAttr(s) { return escapeHtml(s); }

const routes = [
  [/^\/$/, () => renderHome()],
  [/^\/playlists$/, () => renderPlaylists()],
  [/^\/artists$/, () => renderArtists()],
  [/^\/artist\/(\d+)$/, (m) => renderArtist(m[1])],
  [/^\/album\/(\d+)$/, (m) => renderAlbum(m[1])],
  [/^\/playlist\/(\d+)$/, (m) => renderPlaylist(m[1])],
  [/^\/account$/, () => renderAccount()],
  [/^\/admin$/, () => renderAdmin()],
];

function render() {
  const path = location.pathname;
  if (path === '/search') {
    const q = new URLSearchParams(location.search).get('q') || '';
    return renderSearch(q);
  }
  for (const [pattern, handler] of routes) {
    const m = path.match(pattern);
    if (m) return handler(m);
  }
  render404();
}

window.addEventListener('popstate', render);
refreshSession().then(render);
