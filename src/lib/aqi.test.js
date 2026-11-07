import { describe, it, expect } from 'vitest';
import { band, mean, windowDelta, summarize } from './aqi.js';

describe('aqi', () => {
  it('maps values to EPA bands at the edges', () => {
    expect(band(0).key).toBe('good');
    expect(band(50).key).toBe('good');
    expect(band(51).key).toBe('moderate');
    expect(band(301).key).toBe('hazardous');
  });
  it('mean of empty is null', () => expect(mean([])).toBeNull());
  it('windowDelta compares last n with the n before', () => {
    const s = [1, 1, 1, 3, 3, 3].map((v) => ({ v }));
    expect(windowDelta(s, 3, (d) => d.v)).toEqual({ value: 3, delta: 2 });
  });
  it('windowDelta has no delta without history', () => {
    expect(windowDelta([{ v: 4 }], 3, (d) => d.v).delta).toBeNull();
  });
  it('summarize totals rain over 30 days', () => {
    const c = { id: 'x', name: 'X', uf: 'XX', air: [{ aqi: 40 }], weather: Array(40).fill({ tmax: 30, tmin: 20, rain: 1 }) };
    const s = summarize(c);
    expect(s.rain30).toBe(30);
    expect(s.aqi).toBe(40);
    expect(s.temp).toBe(25);
  });
});
