/* ── PAPIK cursor: bolita corporativa · llateja ── */
(function () {

  /* Només en dispositius amb punter fi (ratolí). Tàctil → sortir */
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

  var style = document.createElement('style');
  style.textContent = [
    '*, *::before, *::after { cursor: none !important; }',

    '@keyframes dotPulse {',
    '  0%   { transform: translate(-50%,-50%) scale(1);    box-shadow: 0 0 0 0   rgba(143,181,164,.70); }',
    '  60%  { transform: translate(-50%,-50%) scale(1.08); box-shadow: 0 0 0 9px rgba(143,181,164,.00); }',
    '  100% { transform: translate(-50%,-50%) scale(1);    box-shadow: 0 0 0 0   rgba(143,181,164,.00); }',
    '}',

    '#papik-dot {',
    '  position: fixed;',
    '  width: 13px;',
    '  height: 13px;',
    '  background: #8FB5A4;',
    '  border-radius: 50%;',
    '  pointer-events: none;',
    '  z-index: 2147483647;',
    '  animation: dotPulse 1.6s ease-in-out infinite;',
    '  opacity: 0;',
    '}'
  ].join('\n');
  document.head.appendChild(style);

  var dot = document.createElement('div');
  dot.id = 'papik-dot';
  document.body.appendChild(dot);

  document.addEventListener('mousemove', function (e) {
    dot.style.opacity = '1';
    dot.style.left = e.clientX + 'px';
    dot.style.top  = e.clientY + 'px';
  });

})();
