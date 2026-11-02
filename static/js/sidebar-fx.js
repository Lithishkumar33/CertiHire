/* CertiHire sidebar FX: gliding highlight pill, auto active link,
   cursor glow, click ripple. No dependencies. */
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
        place(links[0], false); pill.style.opacity = 0;
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