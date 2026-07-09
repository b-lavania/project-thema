(function () {
  document.querySelectorAll('.contact-reveal').forEach(function (el) {
    el.addEventListener('click', function () {
      if (this.classList.contains('revealed')) return;
      var decoded = atob(this.dataset.v);
      var link = document.createElement('a');
      link.href = 'mailto:' + decoded;
      link.textContent = decoded;
      link.style.color = 'inherit';
      link.style.fontWeight = '500';
      link.style.textDecoration = 'underline';
      this.classList.add('revealed');
      this.replaceWith(link);
    });
  });
})();
