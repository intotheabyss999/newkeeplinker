document.addEventListener('DOMContentLoaded', function() {
    const burgerIcon = document.querySelector('.burger-icon');
    const mobileNav = document.querySelector('.mobile-nav');

    burgerIcon.addEventListener('click', function() {
        mobileNav.classList.toggle('active');
        burgerIcon.classList.toggle('active');
    });
});
