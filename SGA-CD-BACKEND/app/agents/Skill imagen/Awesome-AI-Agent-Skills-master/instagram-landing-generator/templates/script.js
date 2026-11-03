/* ══════════════════════════════════════
   Instagram Landing Page — Interactivity
   ══════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", () => {

  // ── Animated counters ──
  const counters = document.querySelectorAll(".stat-number[data-count]");
  const animateCounter = (el) => {
    const target = parseInt(el.dataset.count, 10);
    if (isNaN(target) || target === 0) { el.textContent = "0"; return; }
    const duration = 1800;
    const start = performance.now();
    const fmt = (n) => {
      if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
      if (n >= 1e4) return (n / 1e3).toFixed(1) + "K";
      return n.toLocaleString("es");
    };
    const tick = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      el.textContent = fmt(Math.floor(target * ease));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  // ── Intersection Observer for reveals + counters ──
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("visible");
      // Trigger counters inside stats bar
      if (entry.target.classList.contains("stats-bar")) {
        counters.forEach(animateCounter);
      }
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.2 });

  // Observe sections
  document.querySelectorAll(".stats-bar, .gallery-section, .hashtags-section, .cta-section")
    .forEach((el) => {
      el.classList.add("reveal");
      observer.observe(el);
    });

  // ── Lightbox ──
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  const lightboxClose = document.getElementById("lightbox-close");

  document.querySelectorAll(".gallery-item").forEach((item) => {
    item.addEventListener("click", () => {
      const img = item.querySelector("img");
      if (!img) return;
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt;
      lightbox.classList.add("active");
      document.body.style.overflow = "hidden";
    });
  });

  const closeLightbox = () => {
    lightbox.classList.remove("active");
    document.body.style.overflow = "";
  };
  if (lightboxClose) lightboxClose.addEventListener("click", closeLightbox);
  if (lightbox) lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLightbox();
  });

  // ── Copy username ──
  const usernameLabel = document.querySelector(".username-label");
  if (usernameLabel) {
    usernameLabel.addEventListener("click", () => {
      const text = usernameLabel.textContent.trim();
      navigator.clipboard.writeText(text).then(() => {
        showToast("¡Copiado! " + text);
      }).catch(() => {});
    });
  }

  // ── Ripple effect on CTA buttons ──
  document.querySelectorAll(".cta-btn").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      const ripple = document.createElement("span");
      ripple.classList.add("ripple");
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + "px";
      ripple.style.left = (e.clientX - rect.left - size / 2) + "px";
      ripple.style.top = (e.clientY - rect.top - size / 2) + "px";
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 700);
    });
  });

  // ── Toast notification ──
  function showToast(message) {
    let toast = document.querySelector(".copied-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "copied-toast";
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2000);
  }

});
