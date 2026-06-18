<script setup lang="ts">
useSeoMeta({
  title: 'NUO.IM 反馈群',
  description: 'NUO.IM 反馈群',
  ogTitle: 'NUO.IM 反馈群',
  ogDescription: 'NUO.IM 反馈群',
})
</script>

<template>
      <a href="https://nuo.im" class="home-link" title="首页"><img src="/imgs/logo/logo.png" alt="首页" class="home-icon" /><span>首页</span></a>
<div class="center">
    <h1 style="text-align:center;margin-top:40px;">NUO.IM 反馈群</h1>
    <div style="text-align:center;margin-top:20px;">
      <img src="/imgs/feedback-group-qr.png" alt="NUO.IM 反馈群二维码" style="max-width:300px;" />
    </div>
  </div>
</template>

<style scoped lang="scss">
/* ── Layout ── */
.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: var(--color-primary);
}

/* ── Title ── */
.center h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--color-main-text);
  margin: 0 0 1.5rem;
}

/* ── QR card ── */
.center > div:last-child {
  background: var(--color-card-bg);
  border: 1px solid var(--color-item-border);
  border-radius: 14px;
  padding: 2rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.center > div:last-child:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.center img {
  border-radius: 10px;
}

/* ── Home link ── */
.home-link {
  position: fixed;
  top: 12px;
  left: 16px;
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  color: var(--color-font-2);
  font-size: .85rem;
  font-weight: 600;
  opacity: 0.75;
  transition: all 0.2s ease;
  border-radius: 9999px;
  padding: 6px 14px 6px 10px;
  background: var(--color-card-bg);
  backdrop-filter: blur(8px);
  border: 1px solid var(--color-item-border);
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.home-link:hover {
  opacity: 1;
  color: var(--color-main-text);
  border-color: var(--color-fourth);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.home-link .home-icon {
  width: 18px;
  height: 18px;
  border-radius: 4px;
}
</style>
