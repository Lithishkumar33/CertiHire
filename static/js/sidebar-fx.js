/* CertiHire sidebar FX: gliding highlight pill, auto active link,
   cursor glow, click ripple, and mobile drawer toggle. No dependencies. */
(function () {
    'use strict';

    function init() {
        var sidebar = document.querySelector('.sidebar');
        var menu = document.querySelector('.sidebar-menu');
        if (!sidebar || !menu) return;

        var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
        var links = Array.prototype.slice.call(menu.querySelectorAll('a'));

        document.documentElement.classList.add('fx-ready');

        // stagger index for the entrance
        Array.prototype.slice.call(menu.children).forEach(function (el, i) {
            el.style.setProperty('--i', i);
        });

        /* active link from the URL (the template hardcodes "active" on Dashboard) */
        var clean = function (p) { return p.replace(/\/+$/, '') || '/'; };
        var here = clean(location.pathname), best = null, bestLen = -1;
        links.forEach(function (a) {
            var p = clean(new URL(a.getAttribute('href'), location.origin).pathname);
            var hit = p === here || (p !== '/' && here.indexOf(p + '/') === 0);
            if (hit && p.length > bestLen) { best = a; bestLen = p.length; }
        });
        if (best) {
            links.forEach(function (a) { a.classList.remove('active'); a.removeAttribute('aria-current'); });
            best.classList.add('active');
        }
        var active = menu.querySelector('a.active');
        if (active) active.setAttribute('aria-current', 'page');

        /* gliding pill */
        var pill = document.createElement('span');
        pill.className = 'fx-pill no-anim';
        menu.insertBefore(pill, menu.firstChild);

        function place(a, isRest) {
            if (!a || a.offsetWidth === 0) return;
            pill.style.width = a.offsetWidth + 'px';
            pill.style.height = a.offsetHeight + 'px';
            pill.style.transform = 'translate(' + a.offsetLeft + 'px,' + a.offsetTop + 'px)';
            pill.style.opacity = 1;
            pill.classList.toggle('rest', !!isRest);
        }
        function rest() {
            if (active) place(active, true); else pill.style.opacity = 0;
        }

        // start at the top, then glide down to the current page after the entrance
        if (links[0]) {
            place(links[0], false);
            pill.style.opacity = 0;
        }
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                pill.classList.remove('no-anim');
                setTimeout(rest, reduce ? 0 : 650);
            });
        });

        links.forEach(function (a) {
            a.addEventListener('pointerenter', function () { place(a, a === active); });
            a.addEventListener('focus', function () { place(a, a === active); });
            a.addEventListener('blur', rest);
            a.addEventListener('pointerdown', function (e) {
                if (reduce) return;
                var r = a.getBoundingClientRect(), s = Math.max(r.width, r.height) * 2;
                var d = document.createElement('span');
                d.className = 'fx-sripple';
                d.style.cssText = 'width:' + s + 'px;height:' + s + 'px;left:' +
                    (e.clientX - r.left - s / 2) + 'px;top:' + (e.clientY - r.top - s / 2) + 'px';
                a.appendChild(d);
                setTimeout(function () { d.remove(); }, 650);
            });
        });
        menu.addEventListener('pointerleave', rest);
        addEventListener('resize', rest);

        /* Mobile Drawer Toggle */
        var toggleBtn = document.getElementById('sidebarToggle');
        var closeBtn = document.getElementById('sidebarClose');
        var backdrop = document.getElementById('sidebarBackdrop');

        function openSidebar() {
            sidebar.classList.add('show');
            if (backdrop) backdrop.classList.add('show');
            document.body.classList.add('sidebar-open');
            // Re-measure pill once sidebar has completed slide-in
            setTimeout(rest, 320);
        }

        function closeSidebar() {
            sidebar.classList.remove('show');
            if (backdrop) backdrop.classList.remove('show');
            document.body.classList.remove('sidebar-open');
        }

        if (toggleBtn) {
            toggleBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (sidebar.classList.contains('show')) {
                    closeSidebar();
                } else {
                    openSidebar();
                }
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                closeSidebar();
            });
        }

        if (backdrop) {
            backdrop.addEventListener('click', function () {
                closeSidebar();
            });
        }

        // Close sidebar on mobile when any link is clicked
        var allSidebarLinks = sidebar.querySelectorAll('a');
        allSidebarLinks.forEach(function (a) {
            a.addEventListener('click', function () {
                if (window.innerWidth <= 992) {
                    closeSidebar();
                }
            });
        });

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sidebar.classList.contains('show')) {
                closeSidebar();
            }
        });

        // Auto close if window is resized above 992px
        window.addEventListener('resize', function () {
            if (window.innerWidth > 992 && sidebar.classList.contains('show')) {
                closeSidebar();
            }
        });

        /* cursor-following glow */
        if (!reduce && matchMedia('(hover: hover)').matches) {
            if (getComputedStyle(sidebar).position === 'static') sidebar.style.position = 'relative';
            var glow = document.createElement('div');
            glow.className = 'fx-side-glow';
            sidebar.insertBefore(glow, sidebar.firstChild);
            sidebar.addEventListener('pointermove', function (e) {
                var r = sidebar.getBoundingClientRect();
                glow.style.setProperty('--sx', (e.clientX - r.left) + 'px');
                glow.style.setProperty('--sy', (e.clientY - r.top) + 'px');
            });
        }
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
