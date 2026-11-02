/* CertiHire – home page animations. No dependencies. */
(() => {
    'use strict';
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
    const $$ = (s, r = document) => [...r.querySelectorAll(s)];

    /* ---------- 1. Scroll progress bar ---------- */
    const bar = document.createElement('div');
    bar.className = 'scroll-progress';
    document.body.appendChild(bar);
    const onScroll = () => {
        const h = document.documentElement;
        bar.style.transform = `scaleX(${h.scrollTop / ((h.scrollHeight - h.clientHeight) || 1)})`;
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* ---------- 2. Counters (work even with reduced motion) ---------- */
    const countUp = (el) => {
        const m = el.textContent.trim().match(/^([^\d]*)([\d.,]+)(.*)$/);
        if (!m) return;
        const [, pre, num, suf] = m;
        const target = parseFloat(num.replace(/,/g, ''));
        if (isNaN(target)) return;
        const dec = (num.split('.')[1] || '').length;
        if (reduce) return;
        const t0 = performance.now(), dur = 2200;
        const tick = (t) => {
            const p = Math.min((t - t0) / dur, 1);
            const e = 1 - Math.pow(1 - p, 4);              // easeOutQuart
            el.textContent = pre + (target * e).toFixed(dec) + suf;
            if (p < 1) requestAnimationFrame(tick);
        };
        el.textContent = pre + (0).toFixed(dec) + suf;
        requestAnimationFrame(tick);
    };

    if (reduce) {
        $$('.counter-card h2').forEach(countUp);
        return;
    }

    /* ---------- 3. Cursor glow ---------- */
    if (fine) {
        const glow = document.createElement('div');
        glow.className = 'cursor-glow';
        document.body.appendChild(glow);
        let gx = innerWidth / 2, gy = innerHeight / 2, tx = gx, ty = gy;
        addEventListener('mousemove', (e) => { tx = e.clientX; ty = e.clientY; glow.classList.add('on'); });
        document.addEventListener('mouseleave', () => glow.classList.remove('on'));
        (function loop() {
            gx += (tx - gx) * 0.12; gy += (ty - gy) * 0.12;
            glow.style.transform = `translate3d(${gx}px, ${gy}px, 0)`;
            requestAnimationFrame(loop);
        })();
    }

    /* ---------- 4. Hero: orbs, particle network, parallax ---------- */
    const hero = document.querySelector('.hero');
    if (hero) {
        ['o1', 'o2'].forEach(c => {
            const o = document.createElement('div');
            o.className = 'hero-orb ' + c;
            hero.appendChild(o);
        });

        const cv = document.createElement('canvas');
        cv.className = 'hero-canvas';
        hero.appendChild(cv);
        const ctx = cv.getContext('2d');
        let W, H, dpr, pts = [], visible = true;
        const mouse = { x: -9999, y: -9999 };

        const resize = () => {
            dpr = Math.min(devicePixelRatio || 1, 2);
            W = hero.clientWidth; H = hero.clientHeight;
            cv.width = W * dpr; cv.height = H * dpr;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            const n = Math.round(Math.min(90, (W * H) / 14000));
            pts = Array.from({ length: n }, () => ({
                x: Math.random() * W, y: Math.random() * H,
                vx: (Math.random() - .5) * .5, vy: (Math.random() - .5) * .5,
                r: Math.random() * 1.8 + .6
            }));
        };
        resize();
        addEventListener('resize', resize);

        hero.addEventListener('mousemove', (e) => {
            const b = hero.getBoundingClientRect();
            mouse.x = e.clientX - b.left; mouse.y = e.clientY - b.top;
            const nx = (mouse.x / b.width - .5), ny = (mouse.y / b.height - .5);
            hero.style.setProperty('--px', (nx * -28).toFixed(1) + 'px');
            hero.style.setProperty('--py', (ny * -22).toFixed(1) + 'px');
        });
        hero.addEventListener('mouseleave', () => {
            mouse.x = mouse.y = -9999;
            hero.style.setProperty('--px', '0px'); hero.style.setProperty('--py', '0px');
        });
        new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(hero);

        const LINK = 130, PULL = 170;
        (function draw() {
            requestAnimationFrame(draw);
            if (!visible) return;
            ctx.clearRect(0, 0, W, H);
            for (let i = 0; i < pts.length; i++) {
                const p = pts[i];
                const dx = mouse.x - p.x, dy = mouse.y - p.y, d = Math.hypot(dx, dy);
                if (d < PULL) { p.x += dx * .012; p.y += dy * .012; }   // drawn toward cursor
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0 || p.x > W) p.vx *= -1;
                if (p.y < 0 || p.y > H) p.vy *= -1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, 6.283);
                ctx.fillStyle = 'rgba(196,181,253,.9)';
                ctx.fill();
                for (let j = i + 1; j < pts.length; j++) {
                    const q = pts[j], l = Math.hypot(p.x - q.x, p.y - q.y);
                    if (l < LINK) {
                        ctx.strokeStyle = `rgba(139,164,255,${(1 - l / LINK) * .45})`;
                        ctx.lineWidth = .8;
                        ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
                    }
                }
                if (d < PULL) {                                           // cursor links
                    ctx.strokeStyle = `rgba(236,72,153,${(1 - d / PULL) * .6})`;
                    ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
                }
            }
        })();

        // hero text entrance (after the title's own reveal)
        $$('.hero-chip, .hero p, .hero-buttons').forEach((el, i) => {
            el.classList.add('rv', 'in');
            el.style.setProperty('--d', (0.1 + i * 0.35) + 's');
            el.addEventListener('animationend', () => el.classList.remove('rv', 'in'), { once: true });
        });
    }

    /* ---------- 5. Scroll reveal with stagger ---------- */
    const groups = [
        ['.section-header', 'rv-up'],
        ['.gig-card', 'rv-up'],
        ['.category-card', 'rv-flip'],
        ['.feature-card', 'rv-left'],
        ['.freelancer-card', 'rv-up'],
        ['.counter-card', 'rv-zoom'],
        ['.cta-box', 'rv-zoom']
    ];
    const io = new IntersectionObserver((entries) => {
        entries.forEach(en => {
            if (!en.isIntersecting) return;
            const el = en.target;
            el.classList.add('in');
            el.addEventListener('animationend', () => {
                el.classList.remove('rv', 'in', 'rv-up', 'rv-left', 'rv-zoom', 'rv-flip');
                if (el.matches('.section-header')) el.classList.add('in');   // keeps underline drawn
            }, { once: true });
            io.unobserve(el);
            const h2 = el.closest('.counter-card') && el.querySelector('h2');
            if (h2) countUp(h2);
        });
    }, { threshold: .18, rootMargin: '0px 0px -40px 0px' });

    groups.forEach(([sel, cls]) => {
        $$(sel).forEach(el => {
            const sibs = [...el.parentElement.children].filter(c => c.matches(sel));
            const idx = Math.max(sibs.indexOf(el), 0);
            el.classList.add('rv', cls);
            el.style.setProperty('--d', (idx % 4) * 0.13 + 's');
            io.observe(el);
        });
    });

    /* ---------- 6. 3D tilt + glare, magnetic buttons ---------- */
    if (fine) {
        $$('.gig-card, .category-card, .feature-card, .freelancer-card, .counter-card').forEach(card => {
            card.classList.add('tilt');
            card.addEventListener('mousemove', (e) => {
                const b = card.getBoundingClientRect();
                const x = (e.clientX - b.left) / b.width, y = (e.clientY - b.top) / b.height;
                card.classList.add('is-tilting');
                card.style.transform =
                    `perspective(900px) rotateX(${((.5 - y) * 12).toFixed(2)}deg) ` +
                    `rotateY(${((x - .5) * 14).toFixed(2)}deg) translateY(-8px) scale(1.02)`;
                card.style.setProperty('--mx', (x * 100) + '%');
                card.style.setProperty('--my', (y * 100) + '%');
            });
            card.addEventListener('mouseleave', () => {
                card.classList.remove('is-tilting');
                card.style.transform = '';
            });
        });

        $$('.btn-register, .cta-primary, .cta-secondary, .profile-btn').forEach(btn => {
            btn.addEventListener('mousemove', (e) => {
                const b = btn.getBoundingClientRect();
                const x = (e.clientX - (b.left + b.width / 2)) * .28;
                const y = (e.clientY - (b.top + b.height / 2)) * .4;
                btn.style.transform = `translate(${x}px, ${y}px)`;
            });
            btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
        });
    }
})();