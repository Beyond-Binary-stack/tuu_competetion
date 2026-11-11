/* Tiny canvas confetti (no library, no sound).
   Confetti.burst()            -> one short burst
   Confetti.start() / .stop()  -> keeps raining until stopped */
(function(){
  const COLORS = ["#14532d", "#1e6b45", "#991b1b", "#f4c430", "#ffffff", "#3b82f6", "#f97316"];
  let canvas, ctx, pieces = [], raining = false, frame = null;

  function setup(){
    if(canvas) return;
    canvas = document.createElement("canvas");
    canvas.style.cssText = "position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:10000";
    document.body.appendChild(canvas);
    ctx = canvas.getContext("2d");
    const resize = () => { canvas.width = innerWidth; canvas.height = innerHeight; };
    resize(); addEventListener("resize", resize);
  }
  function add(n, fromTop){
    for(let i = 0; i < n; i++){
      pieces.push({
        x: fromTop ? Math.random() * canvas.width : canvas.width / 2 + (Math.random() - .5) * 200,
        y: fromTop ? -20 : canvas.height * .6,
        vx: fromTop ? (Math.random() - .5) * 2 : (Math.random() - .5) * 16,
        vy: fromTop ? 2 + Math.random() * 3 : -10 - Math.random() * 10,
        w: 6 + Math.random() * 6, h: 8 + Math.random() * 8,
        r: Math.random() * Math.PI, vr: (Math.random() - .5) * .3,
        c: COLORS[(Math.random() * COLORS.length) | 0],
      });
    }
  }
  function loop(){
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if(raining && pieces.length < 300) add(4, true);
    pieces = pieces.filter(p => p.y < canvas.height + 30);
    for(const p of pieces){
      p.vy += .25; p.vy = Math.min(p.vy, 6); p.vx *= .99;
      p.x += p.vx; p.y += p.vy; p.r += p.vr;
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.r);
      ctx.fillStyle = p.c; ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.cos(p.r * 2));
      ctx.restore();
    }
    frame = (pieces.length || raining) ? requestAnimationFrame(loop) : null;
    if(!frame) ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
  function run(){ if(!frame) frame = requestAnimationFrame(loop); }

  window.Confetti = {
    burst(){ setup(); add(160, false); run(); },
    start(){ setup(); raining = true; run(); },
    stop(){ raining = false; },
  };
})();
