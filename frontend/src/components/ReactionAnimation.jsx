import { useEffect, useState, useMemo } from 'react';

/* ─── helpers ─── */
function seededRandom(seed) {
  let s = seed;
  return () => { s = (s * 16807 + 0) % 2147483647; return s / 2147483647; };
}

function hexToRgba(hex, alpha = 1) {
  if (!hex) return null;
  const h = hex.replace('#', '');
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

/* ─── constants ─── */
const BUBBLE_COUNTS = { low: 6, medium: 12, high: 25 };
const PRECIPITATE_COUNTS = { low: 8, medium: 16, high: 28 };
const SMOKE_COUNTS = { low: 3, medium: 6, high: 10 };
const EMBER_COUNT = 8;

/* ─── sub-components ─── */

function Bubbles({ intensity, speed }) {
  const count = BUBBLE_COUNTS[intensity] || 12;
  const rand = useMemo(() => seededRandom(42), []);
  const items = useMemo(() => Array.from({ length: count }, (_, i) => {
    const size = rand() * 10 + 4;
    const left = rand() * 70 + 15;
    const delay = rand() * 3;
    const dur = (rand() * 1.5 + 1.5) * speed;
    const highlight = rand() > 0.5;
    return { size, left, delay, dur, highlight, id: i };
  }), [count, speed, rand]);

  return (
    <>
      {items.map(b => (
        <div key={b.id} className="absolute animate-bubble-rise" style={{
          width: b.size, height: b.size, left: `${b.left}%`, bottom: '4px',
          animationDuration: `${b.dur}s`, animationDelay: `${b.delay}s`,
          borderRadius: '50%',
          background: b.highlight
            ? 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.6), rgba(255,255,255,0.1))'
            : 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.4), rgba(255,255,255,0.05))',
          border: '1px solid rgba(255,255,255,0.3)',
          boxShadow: '0 0 3px rgba(255,255,255,0.15)',
        }} />
      ))}
      {/* surface ripples */}
      {items.filter((_, i) => i % 4 === 0).map(b => (
        <div key={`r-${b.id}`} className="absolute animate-ripple" style={{
          width: 6, height: 6, left: `${b.left}%`, top: '0',
          borderRadius: '50%', border: '1px solid rgba(255,255,255,0.3)',
          animationDelay: `${b.delay + b.dur * 0.9}s`,
        }} />
      ))}
    </>
  );
}

function Precipitate({ intensity, speed, color }) {
  const count = PRECIPITATE_COUNTS[intensity] || 16;
  const rand = useMemo(() => seededRandom(99), []);
  const pColor = color || 'rgba(253,224,71,0.9)';
  const items = useMemo(() => Array.from({ length: count }, (_, i) => {
    const left = rand() * 70 + 15;
    const delay = rand() * 3;
    const dur = (rand() * 2 + 2) * speed;
    const size = rand() * 5 + 3;
    const isRound = rand() > 0.5;
    return { left, delay, dur, size, isRound, id: i };
  }), [count, speed, rand, pColor]);

  return (
    <>
      {items.map(p => (
        <div key={p.id} className="absolute animate-precipitate-sink" style={{
          width: p.size, height: p.size, left: `${p.left}%`, top: '10%',
          animationDuration: `${p.dur}s`, animationDelay: `${p.delay}s`,
          background: pColor,
          borderRadius: p.isRound ? '50%' : '2px',
          boxShadow: `0 0 4px ${pColor}`,
        }} />
      ))}
      {/* sediment layer at bottom */}
      <div style={{
        position: 'absolute', bottom: 0, left: '5%', right: '5%', height: '12%',
        borderRadius: '0 0 1.8rem 1.8rem',
        background: `linear-gradient(to top, ${pColor}, transparent)`,
        opacity: 0.6,
        animation: 'liquidShimmer 4s infinite ease-in-out',
      }} />
    </>
  );
}

function Smoke({ intensity, speed, color }) {
  const count = SMOKE_COUNTS[intensity] || 6;
  const rand = useMemo(() => seededRandom(77), []);
  const smokeColor = color || 'rgba(203,213,225,0.5)';
  const items = useMemo(() => Array.from({ length: count }, (_, i) => {
    const left = rand() * 50 + 25;
    const delay = rand() * 2.5;
    const size = rand() * 25 + 30;
    return { left, delay, size, id: i };
  }), [count, rand]);

  return items.map(s => (
    <div key={s.id} className="absolute animate-smoke-rise" style={{
      width: s.size, height: s.size, left: `${s.left}%`, top: '-15px',
      borderRadius: '50%', background: smokeColor,
      filter: 'blur(8px)',
      animationDuration: `${(3 + s.delay * 0.5) * speed}s`,
      animationDelay: `${s.delay}s`,
    }} />
  ));
}

function Fire({ intensity, colorOverlay }) {
  const isBright = intensity === 'high';
  const w = isBright ? 56 : 44;
  const h = isBright ? 72 : 56;

  const rand = useMemo(() => seededRandom(55), []);
  const embers = useMemo(() => Array.from({ length: EMBER_COUNT }, (_, i) => ({
    left: rand() * 60 + 20,
    delay: rand() * 2,
    dur: rand() * 1.5 + 1,
    id: i,
  })), [rand]);

  const outerColor = colorOverlay || '#f97316';
  const midColor = '#facc15';
  const coreColor = isBright ? '#ffffff' : '#fef08a';

  return (
    <div className="absolute left-1/2 z-20" style={{
      bottom: '55%', width: w, height: h, transform: 'translateX(-50%)',
    }}>
      {/* glow behind flame */}
      <div style={{
        position: 'absolute', inset: '-20px', borderRadius: '50%',
        background: `radial-gradient(circle, ${hexToRgba(outerColor, 0.3) || 'rgba(249,115,22,0.3)'} 0%, transparent 70%)`,
        filter: 'blur(10px)',
      }} />

      {/* outer flame */}
      <div className="animate-fire-flicker" style={{
        position: 'absolute', bottom: 0, left: '50%', width: '100%', height: '100%',
        transform: 'translateX(-50%)',
        background: `linear-gradient(to top, ${outerColor}, ${midColor} 60%, transparent)`,
        borderRadius: '50% 50% 20% 20%', filter: 'blur(2px)',
        animationDuration: '0.25s',
      }} />

      {/* mid flame */}
      <div className="animate-fire-flicker" style={{
        position: 'absolute', bottom: 0, left: '50%', width: '70%', height: '75%',
        transform: 'translateX(-50%)',
        background: `linear-gradient(to top, ${midColor}, ${coreColor} 70%, transparent)`,
        borderRadius: '50% 50% 20% 20%', filter: 'blur(1px)',
        animationDuration: '0.18s',
      }} />

      {/* inner core */}
      {isBright && (
        <div className="animate-fire-flicker" style={{
          position: 'absolute', bottom: 0, left: '50%', width: '40%', height: '50%',
          transform: 'translateX(-50%)',
          background: `linear-gradient(to top, ${coreColor}, transparent)`,
          borderRadius: '50% 50% 20% 20%',
          animationDuration: '0.12s',
        }} />
      )}

      {/* embers */}
      {embers.map(e => (
        <div key={e.id} className="absolute animate-ember-float" style={{
          width: 3, height: 3, borderRadius: '50%',
          background: '#fbbf24', boxShadow: '0 0 4px #f59e0b',
          left: `${e.left}%`, bottom: '40%',
          animationDuration: `${e.dur}s`, animationDelay: `${e.delay}s`,
        }} />
      ))}
    </div>
  );
}

function Dissolve({ speed, colorOverlay }) {
  const rand = useMemo(() => seededRandom(33), []);
  const fragments = useMemo(() => Array.from({ length: 8 }, (_, i) => ({
    dx: (rand() - 0.5) * 40,
    dy: (rand() - 0.5) * 30,
    delay: rand() * 2,
    dur: rand() * 1 + 1,
    id: i,
  })), [rand]);

  return (
    <>
      {/* main solid chunk */}
      <div className="animate-dissolve-shrink" style={{
        position: 'absolute', bottom: '15%', left: '50%',
        width: 28, height: 28,
        background: 'linear-gradient(135deg, #9ca3af, #d1d5db, #6b7280)',
        borderRadius: '4px', boxShadow: 'inset 0 0 8px rgba(0,0,0,0.3)',
        animationDuration: `${4 * speed}s`,
      }} />
      {/* breaking-off particles */}
      {fragments.map(f => (
        <div key={f.id} className="animate-dissolve-break" style={{
          position: 'absolute', bottom: '20%', left: '50%',
          width: 4, height: 4, borderRadius: '1px',
          background: '#9ca3af',
          animationDuration: `${f.dur * speed}s`,
          animationDelay: `${f.delay + 0.5}s`,
          '--dx': `${f.dx}px`, '--dy': `${f.dy}px`,
        }} />
      ))}
    </>
  );
}

function HeatHaze() {
  return (
    <div className="absolute inset-x-0 -top-4 h-8 z-30 animate-heat-haze" style={{
      background: 'linear-gradient(to top, rgba(255,255,255,0.08), transparent)',
      filter: 'blur(3px)',
    }} />
  );
}

function Thermometer({ direction }) {
  const level = direction === 'up' ? '85%' : direction === 'down' ? '10%' : '45%';
  const isHot = direction === 'up';

  return (
    <div className="flex flex-col items-center justify-end h-44 z-10 select-none">
      {/* labels */}
      <span className="text-[9px] font-bold tracking-wider mb-1" style={{
        color: isHot ? '#ef4444' : 'rgba(255,255,255,0.4)',
      }}>HOT</span>

      <div className="relative w-5 h-36 rounded-t-full rounded-b-sm z-10" style={{
        background: 'rgba(255,255,255,0.07)',
        border: '2px solid rgba(255,255,255,0.15)',
      }}>
        {/* graduation marks */}
        {[20, 35, 50, 65, 80].map(pct => (
          <div key={pct} style={{
            position: 'absolute', left: '100%', top: `${100 - pct}%`,
            width: 6, height: 1, marginLeft: 2,
            background: 'rgba(255,255,255,0.25)',
          }} />
        ))}

        {/* mercury */}
        <div style={{
          position: 'absolute', bottom: 2, left: 3, right: 3,
          borderRadius: '999px',
          height: level,
          transition: 'height 2.5s cubic-bezier(0.34,1.56,0.64,1)',
          background: isHot
            ? 'linear-gradient(to top, #dc2626, #ef4444)'
            : 'linear-gradient(to top, #3b82f6, #60a5fa)',
          boxShadow: isHot ? '0 0 8px rgba(239,68,68,0.6)' : 'none',
        }} />
      </div>

      {/* bulb */}
      <div style={{
        width: 24, height: 24, borderRadius: '50%', marginTop: -8,
        background: isHot
          ? 'radial-gradient(circle at 40% 40%, #ef4444, #b91c1c)'
          : 'radial-gradient(circle at 40% 40%, #60a5fa, #2563eb)',
        boxShadow: isHot ? '0 0 12px rgba(239,68,68,0.5)' : '0 0 6px rgba(59,130,246,0.3)',
        animation: isHot ? 'ambientPulse 2s infinite ease-in-out' : 'none',
      }} />

      <span className="text-[9px] font-bold tracking-wider mt-1" style={{
        color: !isHot ? '#60a5fa' : 'rgba(255,255,255,0.4)',
      }}>COLD</span>
    </div>
  );
}

/* ─── main component ─── */
export default function ReactionAnimation({
  asset, colorOverlay, intensity, showThermometer, thermometerDirection, thermodynamics,
}) {
  const [active, setActive] = useState(false);

  /* Determine what to render (must be before hooks that depend on these) */
  const isBubbles = asset?.includes('bubbles');
  const isFire = asset?.includes('fire') || asset?.includes('explosion');
  const isPrecipitate = asset?.includes('precipitate');
  const isSmoke = asset?.includes('smoke');
  const isDissolve = asset?.includes('dissolve');
  const isColorChange = asset?.includes('color_change');
  const isNoReaction = asset?.includes('no_reaction');

  const speed = intensity === 'high' ? 0.6 : intensity === 'low' ? 1.6 : 1;

  /* liquid color logic */
  const isExothermic = thermodynamics?.toLowerCase?.()?.includes?.('exothermic') || isFire;
  const isEndothermic = thermodynamics?.toLowerCase?.()?.includes?.('endothermic');

  let liquidColor;
  if (isColorChange && colorOverlay) {
    liquidColor = hexToRgba(colorOverlay, 0.7);
  } else if (colorOverlay && !isPrecipitate && !isSmoke && !isFire) {
    liquidColor = hexToRgba(colorOverlay, 0.5);
  } else {
    liquidColor = 'rgba(147,197,253,0.45)';
  }

  /* All hooks MUST be called before any conditional return */
  const [liquidBg, setLiquidBg] = useState('rgba(147,197,253,0.35)');

  useEffect(() => {
    setActive(false);
    const t = setTimeout(() => setActive(true), 60);
    return () => clearTimeout(t);
  }, [asset, colorOverlay, intensity, showThermometer, thermometerDirection]);

  useEffect(() => {
    if (isColorChange && colorOverlay) {
      setLiquidBg('rgba(147,197,253,0.35)');
      const t = setTimeout(() => setLiquidBg(hexToRgba(colorOverlay, 0.75)), 300);
      return () => clearTimeout(t);
    } else {
      setLiquidBg(liquidColor);
    }
  }, [isColorChange, colorOverlay, liquidColor]);

  /* ambient glow */
  let ambientGlow;
  if (isFire || isExothermic) {
    ambientGlow = 'radial-gradient(ellipse at 40% 80%, rgba(249,115,22,0.15) 0%, transparent 60%)';
  } else if (isEndothermic) {
    ambientGlow = 'radial-gradient(ellipse at 40% 80%, rgba(59,130,246,0.12) 0%, transparent 60%)';
  } else if (isColorChange && colorOverlay) {
    ambientGlow = `radial-gradient(ellipse at 40% 80%, ${hexToRgba(colorOverlay, 0.1)} 0%, transparent 60%)`;
  } else {
    ambientGlow = 'none';
  }

  /* NOW we can do the early return */
  if (!active) {
    return (
      <div className="h-72 w-full flex justify-center items-center rounded-xl bg-slate-900">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-teal-400 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="relative flex items-end justify-center gap-10 py-6 h-72 rounded-xl overflow-hidden select-none"
      style={{ background: `#0f172a`, boxShadow: 'inset 0 0 40px rgba(0,0,0,0.5)' }}>

      {/* ambient glow layer */}
      <div className="absolute inset-0 animate-ambient-pulse pointer-events-none" style={{ background: ambientGlow }} />

      {/* lab bench surface */}
      <div className="absolute bottom-0 left-0 right-0 h-6" style={{
        background: 'linear-gradient(to top, rgba(30,41,59,1), rgba(30,41,59,0))',
      }} />

      {/* ── Test Tube ── */}
      <div className="relative z-10" style={{ width: 80, height: 200 }}>

        {/* glass tube body */}
        <div style={{
          position: 'absolute', inset: 0, top: 8,
          borderLeft: '3px solid rgba(255,255,255,0.18)',
          borderRight: '3px solid rgba(255,255,255,0.12)',
          borderBottom: '3px solid rgba(255,255,255,0.15)',
          borderTop: 'none',
          borderRadius: '0 0 2.2rem 2.2rem',
          background: 'linear-gradient(105deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 50%, rgba(255,255,255,0.04) 100%)',
          backdropFilter: 'blur(2px)',
          boxShadow: 'inset 0 -12px 24px rgba(255,255,255,0.04), 0 0 20px rgba(0,0,0,0.3)',
        }}>

          {/* liquid container */}
          <div style={{
            position: 'absolute', bottom: 0, left: 0, right: 0,
            height: '65%', borderRadius: '0 0 1.9rem 1.9rem', overflow: 'hidden',
          }}>
            {/* liquid fill */}
            <div className="animate-liquid-shimmer" style={{
              position: 'absolute', inset: 0,
              background: liquidBg,
              transition: 'background 3s ease-in-out',
            }}>
              {/* meniscus / surface tension highlight */}
              <div style={{
                position: 'absolute', top: 0, left: '5%', right: '5%', height: 6,
                background: 'linear-gradient(to bottom, rgba(255,255,255,0.25), transparent)',
                borderRadius: '0 0 50% 50%',
              }} />

              {isBubbles && <Bubbles intensity={intensity} speed={speed} />}
              {isPrecipitate && <Precipitate intensity={intensity} speed={speed} color={colorOverlay ? hexToRgba(colorOverlay, 0.9) : null} />}
              {isDissolve && <Dissolve speed={speed} colorOverlay={colorOverlay} />}
            </div>
          </div>

          {/* heat haze above liquid for hot reactions */}
          {(isExothermic || isFire) && <HeatHaze />}
        </div>

        {/* tube lip / rim */}
        <div style={{
          position: 'absolute', top: 0, left: -6, right: -6, height: 10,
          borderRadius: '50%',
          border: '2.5px solid rgba(255,255,255,0.25)',
          background: 'linear-gradient(to bottom, rgba(255,255,255,0.1), transparent)',
        }} />

        {/* smoke / fumes above tube */}
        {isSmoke && <Smoke intensity={intensity} speed={speed} color={colorOverlay ? hexToRgba(colorOverlay, 0.5) : null} />}

        {/* fire above liquid */}
        {isFire && <Fire intensity={intensity} colorOverlay={colorOverlay} />}

        {/* no reaction idle shimmer */}
        {isNoReaction && (
          <div style={{
            position: 'absolute', bottom: 3, left: 3, right: 3, height: '40%',
            borderRadius: '0 0 1.8rem 1.8rem', overflow: 'hidden',
          }}>
            <div className="animate-liquid-shimmer" style={{
              width: '100%', height: '100%',
              background: 'rgba(147,197,253,0.3)',
            }} />
          </div>
        )}

        {/* heat-only / explosion_safe: simmer effect */}
        {asset?.includes('explosion') && (
          <>
            <Bubbles intensity="low" speed={2} />
            <HeatHaze />
          </>
        )}
      </div>

      {/* ── Thermometer ── */}
      {showThermometer && <Thermometer direction={thermometerDirection} />}
    </div>
  );
}
