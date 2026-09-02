/* ==========================================================================
   02805 Social Graphs — group site
   1. SITE: the one place to edit team name, members and repo URL.
   2. Week-state: lights up the spider legs / week grid for the current week.
   Everything degrades gracefully: with JS off the page still shows the
   placeholder text written in the HTML.
   ========================================================================== */

var SITE = {
  // ---- Fill these in and every page updates ------------------------------
  teamName: 'Varmel',
  repoUrl: 'https://github.com/balpaula/02805-Social-graphs-and-interactions',
  repoLabel: 'balpaula/02805-Social-graphs-and-interactions',
  members: [
    // Roles below are a first guess — swap them around as you like.
    { name: 'Alvaro Vega',    role: 'Network analysis', link: '' },
    { name: 'Oier Garcia',    role: 'Visualization',    link: '' },
    { name: 'Paula Balcells', role: 'Writing',          link: '' }
  ],

  // ---- Course calendar ---------------------------------------------------
  // Week 1 = Wednesday 2 September 2026. Weeks 1-8 are the taught weeks,
  // 9-13 the project period.
  courseStart: new Date(2026, 8, 2),
  weekOverride: null                  // set to 1..13 to preview another week
};

(function () {
  'use strict';

  /* ---- 1. Config injection -------------------------------------------- */

  function fillConfig() {
    var i, el, els;

    if (SITE.teamName) {
      els = document.querySelectorAll('[data-site="team-name"]');
      for (i = 0; i < els.length; i++) els[i].textContent = SITE.teamName;
    }

    els = document.querySelectorAll('[data-site="repo-link"]');
    for (i = 0; i < els.length; i++) {
      el = els[i];
      if (SITE.repoUrl) el.setAttribute('href', SITE.repoUrl);
      var label = el.querySelector('[data-site="repo-label"]');
      if (label && SITE.repoLabel) label.textContent = SITE.repoLabel;
    }

    for (i = 0; i < SITE.members.length; i++) {
      var m = SITE.members[i];
      var nameEl = document.querySelector('[data-member="' + (i + 1) + '-name"]');
      var roleEl = document.querySelector('[data-member="' + (i + 1) + '-role"]');
      var linkEl = document.querySelector('[data-member="' + (i + 1) + '-link"]');
      if (nameEl && m.name) nameEl.textContent = m.name;
      if (roleEl && m.role) roleEl.textContent = m.role;
      if (linkEl) {
        if (m.link) {
          linkEl.setAttribute('href', m.link);
          linkEl.textContent = m.link.replace(/^https?:\/\//, '');
        } else {
          linkEl.parentNode.style.display = 'none';
        }
      }
    }
  }

  /* ---- 2. Week state --------------------------------------------------- */

  function legStyle(status) {
    if (status === 'past') {
      return { lineColor: 'var(--text)', lineOpacity: '0.42', lineWidth: '2.4', dash: '0', footFill: 'var(--line-node)', footStroke: 'none', footStrokeWidth: '0', footR: '6', glowOpacity: '0' };
    }
    if (status === 'current') {
      return { lineColor: 'var(--accent)', lineOpacity: '1', lineWidth: '3', dash: '0', footFill: 'var(--accent)', footStroke: 'none', footStrokeWidth: '0', footR: '9', glowOpacity: '0.85' };
    }
    return { lineColor: 'var(--line)', lineOpacity: '0.4', lineWidth: '1.4', dash: '3 5', footFill: 'var(--bg-panel)', footStroke: 'var(--line)', footStrokeWidth: '1.5', footR: '5', glowOpacity: '0' };
  }

  function footerStyle(status) {
    if (status === 'past') return { color: 'var(--text)', opacity: '0.88', tag: 'done', tagColor: 'var(--muted)' };
    if (status === 'current') return { color: 'var(--accent)', opacity: '1', tag: 'live', tagColor: 'var(--accent)' };
    return { color: 'var(--muted)', opacity: '0.62', tag: 'coming', tagColor: 'var(--line)' };
  }

  function computeCurrentWeek() {
    if (SITE.weekOverride !== null && SITE.weekOverride > 0) return Math.min(SITE.weekOverride, 13);
    var diffDays = Math.floor((new Date().getTime() - SITE.courseStart.getTime()) / 86400000);
    var week = diffDays < 0 ? 0 : Math.floor(diffDays / 7) + 1;
    return Math.min(week, 13);
  }

  function setLine(id, s) {
    var el = document.getElementById(id);
    if (!el) return;
    el.setAttribute('stroke', s.lineColor);
    el.setAttribute('stroke-width', s.lineWidth);
    el.setAttribute('stroke-opacity', s.lineOpacity);
    el.setAttribute('stroke-dasharray', s.dash);
  }

  function applyWeekState() {
    var currentWeek = computeCurrentWeek();

    for (var w = 1; w <= 8; w++) {
      var status = w < currentWeek ? 'past' : (w === currentWeek ? 'current' : 'upcoming');
      var leg = legStyle(status);
      setLine('leg' + w + '-line1', leg);
      setLine('leg' + w + '-line2', leg);

      var glow = document.getElementById('leg' + w + '-glow');
      if (glow) glow.setAttribute('opacity', leg.glowOpacity);

      var foot = document.getElementById('leg' + w + '-foot');
      if (foot) {
        foot.setAttribute('r', leg.footR);
        foot.setAttribute('fill', leg.footFill);
        foot.setAttribute('stroke', leg.footStroke);
        foot.setAttribute('stroke-width', leg.footStrokeWidth);
      }

      var fs = footerStyle(status);
      var tagEl = document.getElementById('footer-w' + w + '-tag');
      if (tagEl) {
        tagEl.textContent = fs.tag;
        tagEl.style.borderColor = fs.tagColor;
        tagEl.style.color = fs.tagColor;
      }
      var titleEl = document.getElementById('footer-w' + w + '-title');
      if (titleEl) {
        titleEl.style.color = fs.color;
        titleEl.style.opacity = fs.opacity;
      }
    }

    var projectStatus = currentWeek > 13 ? 'past' : (currentWeek >= 9 ? 'current' : 'upcoming');
    var projectFooter;
    if (projectStatus === 'current') {
      projectFooter = { color: 'var(--accent2)', opacity: '1', tag: 'in progress', tagColor: 'var(--accent2)' };
    } else if (projectStatus === 'past') {
      projectFooter = { color: 'var(--text)', opacity: '0.88', tag: 'done', tagColor: 'var(--muted)' };
    } else {
      projectFooter = { color: 'var(--muted)', opacity: '0.62', tag: 'coming', tagColor: 'var(--line)' };
    }
    var pTag = document.getElementById('project-tag');
    if (pTag) {
      pTag.textContent = projectFooter.tag;
      pTag.style.borderColor = projectFooter.tagColor;
      pTag.style.color = projectFooter.tagColor;
    }
    var pTitle = document.getElementById('project-title');
    if (pTitle) {
      pTitle.style.color = projectFooter.color;
      pTitle.style.opacity = projectFooter.opacity;
    }

    var bodyGlow = document.getElementById('body-glow');
    if (bodyGlow) bodyGlow.setAttribute('opacity', currentWeek > 8 ? '0.85' : '0');
    var bodyFill = document.getElementById('body-fill');
    if (bodyFill) bodyFill.setAttribute('fill', currentWeek >= 1 ? 'var(--text)' : 'var(--line)');

    var labelEl = document.getElementById('week-label');
    if (labelEl) {
      labelEl.textContent = currentWeek <= 0 ? 'Starting soon'
        : (currentWeek <= 8 ? ('Week ' + currentWeek + ' of 8') : 'Project period');
    }

    var caption = document.getElementById('reveal-caption');
    if (caption) caption.style.display = currentWeek >= 8 ? '' : 'none';
  }

  function init() {
    fillConfig();
    applyWeekState();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
