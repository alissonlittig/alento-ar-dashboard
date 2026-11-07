<script>
  import { Chart, LineController, BarController, LineElement, BarElement, PointElement, CategoryScale, LinearScale, Filler, Legend, Tooltip } from 'chart.js';
  Chart.register(LineController, BarController, LineElement, BarElement, PointElement, CategoryScale, LinearScale, Filler, Legend, Tooltip);
  let { config, label } = $props();
  let canvas, visible = $state(false);
  // Draw only once near the viewport: keeps first load light.
  $effect(() => {
    const io = new IntersectionObserver((e) => e.some((x) => x.isIntersecting) && (visible = true), { rootMargin: '150px' });
    io.observe(canvas);
    return () => io.disconnect();
  });
  $effect(() => {
    if (!visible) return;
    const c = new Chart(canvas, config);
    return () => c.destroy();
  });
</script>

<div class="chart"><canvas bind:this={canvas} role="img" aria-label={label}></canvas></div>

<style>
  .chart { position: relative; height: 100%; width: 100%; }
</style>
