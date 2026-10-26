/* ===================================================================
   JOBFLOW - ENHANCED JAVASCRIPT
   Features: theme toggle, smooth interactions, AJAX-style updates,
   form validation, and application state tracking.
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize theme from localStorage
  initTheme();

  // Initialize all UI components
  initNavMobile();
  initFilter animations();
  initApplicationTracking();
  initSmoothScroll();
});

/* --- Theme Management --- */

function initTheme() {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const savedTheme = localStorage.getItem('jobflow-theme');
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;

  // Apply saved theme or preferred scheme
  if (savedTheme === 'dark') {
    body.classList.add('dark');
  } else if (savedTheme === 'light' && !prefersDark) {
    body.classList.remove('dark');
  } else {
    // Use system preference
    if (prefersDark) {
      body.classList.add('dark');
    }
  }

  // Update icon
  updateThemeIcon(body.classList.contains('dark'), themeToggle);
}

/* --- Theme Toggle --- */

const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const body = document.body;
    const isDark = body.classList.toggle('dark');
    localStorage.setItem('jobflow-theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark, themeToggle);
  });
}

function updateThemeIcon(isDark, element) {
  element.innerHTML = isDark ? '☀️' : '🌙';
}

/* --- Mobile Navigation --- */

function initNavMobile() {
  const navbar = document.querySelector('.navbar');
  const navLinks = document.querySelector('.nav-links');
  const menuBtn = document.createElement('button');

  if (window.innerWidth <= 768 && navLinks) {
    // Create mobile menu button
    menuBtn.type = 'button';
    menuBtn.className = 'menu-btn';
    menuBtn.innerHTML = '☰';
    menuBtn.style.display = 'none';
    menuBtn.style.fontSize = '1.5rem';
    menuBtn.style.cursor = 'pointer';
    menuBtn.style.color = var(--text-light);

    // Insert before .logo
    const logo = document.querySelector('.logo');
    if (logo.parentNode) {
      logo.parentNode.insertBefore(menuBtn, logo);
    }

    // Toggle mobile menu
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });

    // Close menu on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
      });
    });
  }
}

/* --- Filter/Sort Animations --- */

function initFilterAnimations() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  if (!filterBtns.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active state
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // In a real implementation, this would filter jobs
      // For now, just smooth transition
      const jobCards = document.querySelectorAll('.job-card');
      jobCards.forEach(card => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      });
    });
  });
}

/* --- Application Tracking --- */

function initApplicationTracking() {
  // Track application status changes
  const statusBads = document.querySelectorAll('.status-badge');
  statusBads.forEach(bad => {
    bad.addEventListener('click', () => {
      // In a real app, this would open a status update form
      const card = bad.closest('.application-card');
      if (card) {
        showStatusModal(card);
      }
    });
  });
}

function showStatusModal(card) {
  const currentStatus = card.querySelector('.status').textContent;
  const statuses = ['Applied', 'Preparing', 'Interview', 'Rejected', 'Offer', 'Confirmation Needed'];

  // Simple modal for demo
  const modal = document.createElement('div');
  modal.style.position = 'fixed';
  modal.style.top = '0';
  modal.style.left = '0';
  modal.style.width = '100%';
  modal.style.height = '100%';
  modal.style.background = 'rgba(0,0,0,0.5)';
  modal.style.display = 'flex';
  modal.style.justifyContent = 'center';
  modal.style.alignItems = 'center';
  modal.style.zIndex = '1000';

  modal.innerHTML = `
    <div style="background: white; padding: 2rem; border-radius: 16px; width: 90%; max-width: 400px; box-shadow: 0 20px 40px rgba(0,0,0,0.3);">
      <h3 style="margin-bottom: 1rem; color: var(--text-dark);">Update Application Status</h3>
      <select style="width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-light); margin-bottom: 1rem; font-family: inherit;">
        ${statuses.map(status => `<option value="${status}" ${status === currentStatus ? 'selected' : ''}>${status}</option>`).join('')}
      </select>
      <div style="display: flex; gap: 1rem; justify-content: flex-end;">
        <button class="btn-secondary" style="flex: 1;">Cancel</button>
        <button class="btn-primary" style="flex: 1;">Update</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Remove modal on cancel
  modal.querySelector('.btn-secondary').addEventListener('click', () => {
    modal.remove();
  });

  // Remove modal on update (would normally save)
  modal.querySelector('.btn-primary').addEventListener('click', () => {
    const newStatus = modal.querySelector('select').value;
    card.querySelector('.status').textContent = newStatus;
    modal.remove();
    showStatusToast(newStatus);
  });

  // Close on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  });
}

function showStatusToast(status) {
  const toast = document.createElement('div');
  toast.style.position = 'fixed';
  toast.style.bottom = '2rem';
  toast.style.left = '50%';
  toast.transform = 'translateX(-50%)';
  toast.background = 'var(--card-light)';
  toast.color = 'var(--text-dark)';
  toast.padding = '1rem 1.5rem';
  toast.borderRadius = '12px';
  toast.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
  toast.transition = 'opacity 0.3s ease';
  toast.innerHTML = `Status updated to ${status}`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/* --- Smooth Scroll --- */

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
        });
      }
    });
  });
}

/* --- Reduced Motion Support --- */

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.body.classList.add('reduced-motion');
}

/* --- Focus Visible Styles --- */

document.addEventListener('focusin', (e) => {
  if (e.target.matches('a, button, input, select, textarea')) {
    e.target.classList.add('focus-visible');
  }
}, true);

document.addEventListener('focusout', (e) => {
  if (e.target.matches('a, button, input, select, textarea')) {
    e.target.classList.remove('focus-visible');
  }
}, true);