/** 
 * Site público - Navegação mobile, animações e interações
 * Adoção de Gatos e Cães
 */
(function () {
  "use strict";

  // ============================================
  // Mobile Navigation Toggle
  // ============================================
  const toggle = document.getElementById("navToggle");
  const nav = document.querySelector(".nav-main");
  
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      
      // Prevent body scroll when menu is open
      document.body.style.overflow = isOpen ? "hidden" : "";
    });

    // Close menu when clicking on a link
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      });
    });

    // Close menu when clicking outside
    document.addEventListener("click", (e) => {
      if (nav.classList.contains("open") && 
          !nav.contains(e.target) && 
          !toggle.contains(e.target)) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      }
    });

    // Close menu on escape key
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && nav.classList.contains("open")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
        toggle.focus();
      }
    });
  }

  // ============================================
  // Intersection Observer for Animations
  // ============================================
  const observerOptions = {
    root: null,
    rootMargin: "0px 0px -50px 0px",
    threshold: 0.1
  };

  const animateOnScroll = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-in");
        animateOnScroll.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Elements to animate
  const animatableElements = document.querySelectorAll(
    ".pet-card, .steps-list li, .info-checklist, .empty-state"
  );

  animatableElements.forEach((el, index) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = `opacity 0.5s ease ${index * 0.05}s, transform 0.5s ease ${index * 0.05}s`;
    animateOnScroll.observe(el);
  });

  // Add animation class styles dynamically
  const style = document.createElement("style");
  style.textContent = `
    .animate-in {
      opacity: 1 !important;
      transform: translateY(0) !important;
    }
  `;
  document.head.appendChild(style);

  // ============================================
  // Smooth Scroll for Anchor Links
  // ============================================
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      if (targetId === "#") return;
      
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const headerHeight = document.querySelector(".site-header")?.offsetHeight || 0;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: "smooth"
        });
      }
    });
  });

  // ============================================
  // Header Scroll Effect
  // ============================================
  const header = document.querySelector(".site-header");
  let lastScroll = 0;

  if (header) {
    window.addEventListener("scroll", () => {
      const currentScroll = window.pageYOffset;
      
      if (currentScroll > 100) {
        header.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.08)";
      } else {
        header.style.boxShadow = "none";
      }
      
      lastScroll = currentScroll;
    }, { passive: true });
  }

  // ============================================
  // Pet Card Image Lazy Loading Enhancement
  // ============================================
  const petImages = document.querySelectorAll(".pet-card-image img");
  
  petImages.forEach((img) => {
    img.addEventListener("load", function() {
      this.style.opacity = "1";
    });
    
    if (img.complete) {
      img.style.opacity = "1";
    } else {
      img.style.opacity = "0";
      img.style.transition = "opacity 0.3s ease";
    }
  });

  // ============================================
  // Filter Chips Keyboard Navigation
  // ============================================
  const filterBars = document.querySelectorAll(".filter-bar");
  
  filterBars.forEach((bar) => {
    const chips = bar.querySelectorAll(".filter-chip");
    
    chips.forEach((chip, index) => {
      chip.addEventListener("keydown", (e) => {
        let nextIndex;
        
        if (e.key === "ArrowRight" || e.key === "ArrowDown") {
          e.preventDefault();
          nextIndex = (index + 1) % chips.length;
          chips[nextIndex].focus();
        } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
          e.preventDefault();
          nextIndex = (index - 1 + chips.length) % chips.length;
          chips[nextIndex].focus();
        }
      });
    });
  });

  // ============================================
  // Touch Device Detection
  // ============================================
  if ("ontouchstart" in window || navigator.maxTouchPoints > 0) {
    document.body.classList.add("touch-device");
  }

  // ============================================
  // Reduced Motion Support
  // ============================================
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  
  if (prefersReducedMotion.matches) {
    document.documentElement.style.setProperty("--transition-fast", "0ms");
    document.documentElement.style.setProperty("--transition-normal", "0ms");
    
    // Remove scroll animations
    animatableElements.forEach((el) => {
      el.style.opacity = "1";
      el.style.transform = "none";
      el.style.transition = "none";
    });
  }

  // ============================================
  // Console Log for Development
  // ============================================
  console.log("🐾 Adoção de Gatos e Cães - Site carregado com sucesso!");
})();
