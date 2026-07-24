(function () {
  'use strict';

  document.querySelectorAll('.container > section, .container > header').forEach(function (block) {
    if (block.querySelector('.section-jump-top')) return;
    var jump = document.createElement('p');
    jump.className = 'section-jump-top';
    var link = document.createElement('a');
    link.href = '#top';
    link.textContent = 'Jump to top';
    jump.appendChild(link);
    block.appendChild(jump);
  });

  var header = document.querySelector('.site-header');
  if (!header) return;

  var toggle = header.querySelector('.nav-toggle');
  var nav = header.querySelector('.site-nav');
  var isHome = document.body.classList.contains('page-home');

  function closeMenu() {
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
    document.body.classList.remove('nav-open');
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
      nav.classList.toggle('is-open', !open);
      document.body.classList.toggle('nav-open', !open);
    });

    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.matchMedia('(max-width: 768px)').matches) closeMenu();
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
  }

  if (isHome && nav) {
    var sectionLinks = nav.querySelectorAll('a[href^="#"]');
    var sections = [];

    sectionLinks.forEach(function (link) {
      var id = link.getAttribute('href').slice(1);
      var section = document.getElementById(id);
      if (section) sections.push({ id: id, el: section, link: link });
    });

    function setActiveSection() {
      var scrollY = window.scrollY + header.offsetHeight + 48;
      var current = sections[0];

      sections.forEach(function (item) {
        if (item.el.offsetTop <= scrollY) current = item;
      });

      sectionLinks.forEach(function (link) {
        link.removeAttribute('aria-current');
      });

      if (current) current.link.setAttribute('aria-current', 'true');
    }

    window.addEventListener('scroll', setActiveSection, { passive: true });
    setActiveSection();
  }

  var backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', function () {
      backToTop.classList.toggle('is-visible', window.scrollY > 480);
    }, { passive: true });

    backToTop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  var toc = document.querySelector('.page-toc');
  if (toc && isHome) {
    var tocLinks = toc.querySelectorAll('a[href^="#"]');
    var tocTargets = [];

    tocLinks.forEach(function (link) {
      var id = link.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if (target) tocTargets.push({ el: target, link: link });
    });

    function setActiveToc() {
      var scrollY = window.scrollY + header.offsetHeight + 64;
      var current = tocTargets[0];

      tocTargets.forEach(function (item) {
        if (item.el.offsetTop <= scrollY) current = item;
      });

      tocLinks.forEach(function (link) {
        link.classList.remove('is-active');
      });

      if (current) current.link.classList.add('is-active');
    }

    window.addEventListener('scroll', setActiveToc, { passive: true });
    setActiveToc();
  }

  var selectedWork = document.getElementById('selected-work');
  if (selectedWork) {
    var skillFilters = selectedWork.querySelectorAll('.work-skills-filter');
    var skillClear = selectedWork.querySelector('.work-skills-clear');
    var skillTargets = selectedWork.querySelectorAll('.skill-filter-target');
    var activeSkill = null;

    function applySkillFilter(skill) {
      activeSkill = skill || null;

      if (!activeSkill) {
        selectedWork.classList.remove('selected-work--filtering');
        selectedWork.removeAttribute('data-active-skill');
        skillTargets.forEach(function (target) {
          target.classList.remove('skill-dimmed');
        });
        skillFilters.forEach(function (btn) {
          btn.classList.remove('is-active');
        });
        if (skillClear) skillClear.hidden = true;
        return;
      }

      selectedWork.classList.add('selected-work--filtering');
      selectedWork.setAttribute('data-active-skill', activeSkill);
      skillTargets.forEach(function (target) {
        var skills = (target.getAttribute('data-skills') || '').split(/\s+/).filter(Boolean);
        target.classList.toggle('skill-dimmed', skills.indexOf(activeSkill) === -1);
      });
      skillFilters.forEach(function (btn) {
        btn.classList.toggle('is-active', btn.getAttribute('data-skill') === activeSkill);
      });
      if (skillClear) skillClear.hidden = false;
    }

    skillFilters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var skill = btn.getAttribute('data-skill');
        applySkillFilter(skill === activeSkill ? null : skill);
      });
    });

    if (skillClear) {
      skillClear.addEventListener('click', function () {
        applySkillFilter(null);
      });
    }
  }
})();
