document.addEventListener('DOMContentLoaded', () => {
    // Hero Section Animation on Load
    const heroText = document.querySelector('.hero-content h2');
    const heroParagraph = document.querySelector('.hero-content p');

    window.addEventListener('load', () => {
        heroText.classList.add('slide-in');
        heroParagraph.classList.add('fade-in');
    });

    // Button Hover Effect
    const ctaButton = document.querySelector('.cta-btn');
    ctaButton.addEventListener('mouseenter', () => {
        ctaButton.style.transform = 'scale(1.1)';
    });
    ctaButton.addEventListener('mouseleave', () => {
        ctaButton.style.transform = 'scale(1)';
    });

    // Smooth Scrolling for Internal Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Scroll-based Header Animation
    const header = document.querySelector('header');
    let lastScrollY = window.scrollY;
    window.addEventListener('scroll', () => {
        if (window.scrollY > lastScrollY) {
            header.classList.add('header-hide');
        } else {
            header.classList.remove('header-hide');
        }
        lastScrollY = window.scrollY;
    });

    // Service Section Animation on Scroll
    const serviceBoxes = document.querySelectorAll('.service');
    const serviceObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('slide-up');
            } else {
                entry.target.classList.remove('slide-up');
            }
        });
    }, { threshold: 0.3 });

    serviceBoxes.forEach(service => {
        serviceObserver.observe(service);
    });

    // Search Form Validation with Animation
    const searchForm = document.querySelector('.search-form');
    const searchInputs = searchForm.querySelectorAll('input, select');
    searchForm.addEventListener('submit', (e) => {
        let valid = true;
        searchInputs.forEach(input => {
            if (!input.value) {
                input.classList.add('shake');
                valid = false;
                setTimeout(() => input.classList.remove('shake'), 500);
            }
        });
        if (!valid) {
            e.preventDefault();
        }
    });

    // Reveal Search Form Slowly on Scroll
    const searchSection = document.querySelector('.search-section');
    const revealSearch = () => {
        const sectionTop = searchSection.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;

        if (sectionTop < windowHeight - 100) {
            searchSection.classList.add('reveal');
        } else {
            searchSection.classList.remove('reveal');
        }
    };
    window.addEventListener('scroll', revealSearch);
    revealSearch(); // Run on page load

    // Footer Animation
    const footer = document.querySelector('footer');
    footer.style.opacity = 0;
    window.addEventListener('scroll', () => {
        if (window.scrollY + window.innerHeight >= document.body.scrollHeight) {
            footer.style.transition = 'opacity 0.5s';
            footer.style.opacity = 1;
        }
    });

});
