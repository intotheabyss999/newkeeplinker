document.addEventListener('DOMContentLoaded', function() {
  var navbarToggler = document.querySelector('.navbar-toggler');
  var body = document.body;

  navbarToggler.addEventListener('click', function() {
    body.classList.toggle('menu-open');
  });
});