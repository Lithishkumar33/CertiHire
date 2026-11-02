/* CertiHire dashboard FX. Works on both buyer and seller dashboards.
   No dependencies. Respects prefers-reduced-motion. */
(function () {
    'use strict';

    var doc = document, root = doc.documentElement, t0 = performance.now();
    var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
    var $ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
    var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

    function watch(el, cb, threshold) {
        if (!('IntersectionObserver' in window)) { cb(el); return; }
        var io = new IntersectionObserver(function (es) {
            es.forEach(function (e) {
                if (e.isIntersecting) { io.unobserve(e.target); cb(e.target); }
            });
        }, { threshold: threshold || 0.2 });
        io.observe(el);
    }

    /* ---------- count-up (keeps ₹ and any text around the number) ---------- */
    function countUp(el) {
        var txt = el.textContent, m = txt.match(/[\d,]+(?:\.\d+)?/);
        if (!m || reduce) return;
        var raw = m[0], target = parseFloat(raw.replace(/,/g, ''));
        if (isNaN(target) || target === 0) return;
        var dec = (raw.split('.')[1] || '').length;
        var pre = txt.slice(0, m.index), post = txt.slice(m.index + raw.length);
        var fmt = function (v) {
            return pre + v.toLocaleString('en-IN', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + post;
        };
        var start = null;
        el.textContent = fmt(0);
        (function step(t) {
            if (start === null) start = t;
            var p = clamp((t - start) / 1600, 0, 1);
            el.textContent = fmt(target * (p === 1 ? 1 : 1 - Math.pow(2, -10 * p)));
            if (p < 1) requestAnimationFrame(step);
            else { el.classList.add('fx-done'); }
        })(performance.now());
    }

    /* ---------- confetti burst ---------- */
    var bc, bx, bits = [], braf, colors = ['#6366f1', '#22d3ee', '#f472b6', '#facc15', '#34d399'];
    function sizeBurst() {
        var d = Math.min(devicePixelRatio || 1, 2);
        bc.width = innerWidth * d; bc.height = innerHeight * d;
        bx.setTransform(d, 0, 0, d, 0, 0);
    }
    function burst(x, y) {
        if (reduce) return;
        if (!bc) {
            bc = doc.createElement('canvas'); bc.className = 'fx-burst';
            doc.body.appendChild(bc); bx = bc.getContext('2d');
            sizeBurst(); addEventListener('resize', sizeBurst);
        }
        for (var i = 0; i < 46; i++) {
            var a = Math.random() * Math.PI * 2, s = 2 + Math.random() * 6;
            bits.push({
                x: x, y: y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 3,
                w: 4 + Math.random() * 5, r: Math.random() * 6, vr: (Math.random() - .5) * .4,
                life: 1, c: colors[i % colors.length]
            });
        }
        if (!braf) braf = requestAnimationFrame(tickBurst);
    }
    function tickBurst() {
        bx.clearRect(0, 0, innerWidth, innerHeight);
        bits = bits.filter(function (b) { return b.life > 0; });
        bits.forEach(function (b) {
            b.vy += .16; b.vx *= .985; b.x += b.vx; b.y += b.vy; b.r += b.vr; b.life -= .014;
            bx.save(); bx.globalAlpha = clamp(b.life, 0, 1);
            bx.translate(b.x, b.y); bx.rotate(b.r); bx.fillStyle = b.c;
            bx.fillRect(-b.w / 2, -b.w / 2, b.w, b.w * .6); bx.restore();
        });
        if (bits.length) braf = requestAnimationFrame(tickBurst);
        else { bx.clearRect(0, 0, innerWidth, innerHeight); braf = 0; }
    }

    /* ---------- hero constellation: nodes drift, gather around your cursor ---------- */
    function constellation(hero) {
        var cv = doc.createElement('canvas');
        cv.className = 'fx-hero-canvas';
        hero.insertBefore(cv, hero.firstChild);
        var ctx = cv.getContext('2d'), dpr = Math.min(devicePixelRatio || 1, 2);
        var rgb = getComputedStyle(root).getPropertyValue('--fx-node').trim() || '255,255,255';
        var W = 0, H = 0, pts = [], mouse = { x: -9999, y: -9999 }, raf = 0, visible = true;

        function size() {
            var r = hero.getBoundingClientRect(); W = r.width; H = r.height;
            cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            var n = clamp(Math.round(W * H / 9000), 24, 90); pts = [];
            for (var i = 0; i < n; i++) pts.push({
                x: Math.random() * W, y: Math.random() * H,
                vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35, r: Math.random() * 1.6 + .8
            });
            if (reduce) frame(true);
        }

        function frame(once) {
            ctx.clearRect(0, 0, W, H);
            var LINK = 120, i, j, p, q, dx, dy, d;
            for (i = 0; i < pts.length; i++) {
                p = pts[i];
                if (!once) {
                    p.x += p.vx; p.y += p.vy;
                    if (p.x < 0 || p.x > W) p.vx *= -1;
                    if (p.y < 0 || p.y > H) p.vy *= -1;
                    dx = p.x - mouse.x; dy = p.y - mouse.y; d = Math.sqrt(dx * dx + dy * dy);
                    if (d < 150 && d > 24) { p.x -= dx * .014; p.y -= dy * .014; }
                }
                ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283);
                ctx.fillStyle = 'rgba(' + rgb + ',.8)'; ctx.fill();
                for (j = i + 1; j < pts.length; j++) {
                    q = pts[j]; dx = p.x - q.x; dy = p.y - q.y; d = Math.sqrt(dx * dx + dy * dy);
                    if (d < LINK) {
                        ctx.strokeStyle = 'rgba(' + rgb + ',' + ((1 - d / LINK) * .45).toFixed(3) + ')';
                        ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
                    }
                }
                dx = p.x - mouse.x; dy = p.y - mouse.y; d = Math.sqrt(dx * dx + dy * dy);
                if (d < 170) {
                    ctx.strokeStyle = 'rgba(34,211,238,' + ((1 - d / 170) * .9).toFixed(3) + ')';
                    ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
                }
            }
            if (!once && visible && !doc.hidden) raf = requestAnimationFrame(frame); else raf = 0;
        }
        function run() { if (!raf && !reduce) raf = requestAnimationFrame(frame); }

        size(); addEventListener('resize', size); run();
        doc.addEventListener('visibilitychange', run);
        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (es) { visible = es[0].isIntersecting; run(); }).observe(hero);
        }

        var img = hero.querySelector('.hero-right img');
        hero.addEventListener('pointermove', function (e) {
            var r = hero.getBoundingClientRect();
            mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
            if (img) {
                var nx = mouse.x / r.width - .5, ny = mouse.y / r.height - .5;
                img.style.setProperty('--px', (nx * 22) + 'px');
                img.style.setProperty('--py', (ny * 14) + 'px');
                img.style.setProperty('--pr', (nx * 8) + 'deg');
            }
        });
        hero.addEventListener('pointerleave', function () {
            mouse.x = mouse.y = -9999;
            if (img) { img.style.setProperty('--px', '0px'); img.style.setProperty('--py', '0px'); img.style.setProperty('--pr', '0deg'); }
        });
        if (img) img.addEventListener('click', function (e) { burst(e.clientX, e.clientY); });
    }

    /* ---------- init ---------- */
    function init() {
        root.classList.add('fx-ready');

        // stagger indexes for the load sequence
        $('.hero-left > *').forEach(function (el, i) { el.style.setProperty('--i', i); });
        $('.stat-card').forEach(function (el, i) { el.style.setProperty('--i', i); });

        // hero constellation
        var hero = $('.dashboard-hero')[0];
        if (hero) constellation(hero);

        // count-up numbers
        $('.stat-card h3, .spending-value, .revenue-value').forEach(function (el) {
            var card = el.closest('.stat-card');
            var delay = card && performance.now() - t0 < 2500
                ? (parseInt(card.style.getPropertyValue('--i'), 10) || 0) * 110 + 500 : 0;
            watch(el, function () { setTimeout(function () { countUp(el); }, delay); }, 0.4);
        });

        // scroll reveal + per-card triggers (progress bar, table rows)
        $('.dashboard-card').forEach(function (card) {
            var bar = card.querySelector('.spending-progress-bar');
            var target = bar ? (bar.style.width || '100%') : '';
            if (bar && !reduce) bar.style.width = '0';
            if (card.querySelector('tbody')) {
                $('tbody tr', card).forEach(function (r, i) { r.style.setProperty('--i', i); });
                card.classList.add('fx-rows');
            }
            card.classList.add('fx-reveal');
            watch(card, function () {
                card.classList.add('fx-in', 'fx-rows-in');
                if (bar) requestAnimationFrame(function () { bar.style.width = target; });
            }, 0.15);
        });

        // sticky bits: scroll progress + cursor glow
        var prog = doc.createElement('div'); prog.className = 'fx-progress'; doc.body.appendChild(prog);
        var ticking = false;
        addEventListener('scroll', function () {
            if (ticking) return; ticking = true;
            requestAnimationFrame(function () {
                var max = root.scrollHeight - innerHeight;
                prog.style.transform = 'scaleX(' + (max > 0 ? scrollY / max : 0) + ')';
                ticking = false;
            });
        }, { passive: true });

        if (fine && !reduce) {
            var glow = doc.createElement('div'); glow.className = 'fx-glow'; doc.body.appendChild(glow);
            addEventListener('pointermove', function (e) {
                glow.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0)';
                glow.classList.add('on');
            }, { passive: true });
            doc.addEventListener('mouseleave', function () { glow.classList.remove('on'); });

            // spotlight on every card, tilt on the compact ones
            $('.stat-card, .dashboard-card').forEach(function (el) {
                var tilt = el.matches('.stat-card, .assessment-card, .spending-overview');
                if (tilt) el.classList.add('fx-tilt');
                el.addEventListener('pointermove', function (e) {
                    var r = el.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
                    el.style.setProperty('--mx', x + 'px'); el.style.setProperty('--my', y + 'px');
                    if (tilt) {
                        el.style.setProperty('--ry', ((x / r.width - .5) * 10) + 'deg');
                        el.style.setProperty('--rx', (-(y / r.height - .5) * 10) + 'deg');
                    }
                });
                el.addEventListener('pointerleave', function () {
                    el.style.setProperty('--rx', '0deg'); el.style.setProperty('--ry', '0deg');
                });
            });

            // magnetic hero buttons
            $('.hero-btn-primary, .hero-btn-secondary').forEach(function (b) {
                b.addEventListener('pointermove', function (e) {
                    var r = b.getBoundingClientRect();
                    b.style.setProperty('--tx', ((e.clientX - r.left - r.width / 2) * .25) + 'px');
                    b.style.setProperty('--ty', ((e.clientY - r.top - r.height / 2) * .35) + 'px');
                });
                b.addEventListener('pointerleave', function () {
                    b.style.setProperty('--tx', '0px'); b.style.setProperty('--ty', '0px');
                });
            });
        }

        // click ripple on buttons
        $('.hero-btn-primary, .hero-btn-secondary, .btn').forEach(function (b) {
            b.addEventListener('pointerdown', function (e) {
                if (reduce) return;
                var r = b.getBoundingClientRect(), s = Math.max(r.width, r.height) * 2;
                var d = doc.createElement('span'); d.className = 'fx-ripple';
                d.style.cssText = 'width:' + s + 'px;height:' + s + 'px;left:' + (e.clientX - r.left - s / 2) + 'px;top:' + (e.clientY - r.top - s / 2) + 'px';
                b.appendChild(d); setTimeout(function () { d.remove(); }, 700);
            });
        });

        // stat icons: click for confetti
        $('.stat-icon').forEach(function (ic) {
            ic.addEventListener('click', function () {
                var r = ic.getBoundingClientRect(); burst(r.left + r.width / 2, r.top + r.height / 2);
            });
        });
    }

    if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init); else init();
})();