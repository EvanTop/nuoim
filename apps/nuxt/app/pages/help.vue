<script setup lang="ts">
import { BasePage, Collapse } from '@typewords/base'
import { APP_NAME, GITHUB, Origin } from '@typewords/core/config/env.ts'
import ConflictNoticeText from '@typewords/core/components/dialog/ConflictNoticeText.vue'

let title = APP_NAME + ' 常见问题解答'
let route = useRoute()
useSeoMeta({
  title: title,
  description: title,
  ogTitle: title,
  ogDescription: title,
  ogUrl: Origin + route.fullPath,
  twitterTitle: title,
  twitterDescription: title,
})
</script>

<template>
  <BasePage>
    <a href="https://nuo.im" class="home-link" title="首页"><img src="/imgs/logo/logo.png" alt="首页" class="home-icon" /><span>首页</span></a>
    <div class="center">
      <div class="card-white qa w-2/3">
        <div class="font-bold text-2xl mb-6">{{ $t('faq') }}</div>
        <div class="list">
          <Collapse
            q="数据丢失/被清空/不在了"
            :a="[
              'C盘如果被占满了，是无法保存数据的',
              '无痕模式无法保存数据，关闭浏览器之后数据就没了',
              '开户了“自动清除历史记录”选项也无法保存数据，关闭浏览器之后数据就没了',
            ]"
          >
          </Collapse>

          <div class="line"></div>
          <Collapse :q="$t('qa2_a')">
            <ConflictNoticeText type="keyboard" />
          </Collapse>

          <div class="line"></div>

          <Collapse q="按删除键却返回了上一页">
            <ConflictNoticeText type="del" />
          </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa10_a')" :a="[$t('qa10_q1'), $t('qa10_q2')]"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa11_a')" :a="$t('qa11_q')"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa3_a')" :a="[$t('qa3_q1'), $t('qa3_q2'), $t('qa3_q3')]"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa1_a')" :a="[$t('qa1_q1'), $t('qa1_q2')]" />

          <div class="line"></div>

          <Collapse :q="$t('qa4_a')" :a="[$t('qa4_q1'), $t('qa4_q2')]"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa5_a')" :a="[$t('qa5_q1'), $t('qa5_q2'), $t('qa5_q3'), $t('qa5_q4')]"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa6_a')" :a="$t('qa5_q4')"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa7_a')" :a="[$t('qa7_q1'), $t('qa7_q2'), $t('qa7_q3')]"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa8_a')" :a="[$t('qa8_q1'), $t('qa8_q2'), $t('qa8_q3')]"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa9_a')" :a="$t('qa9_q')"> </Collapse>

          <div class="line"></div>

          <Collapse :q="$t('qa12_a')" :a="$t('qa12_q')"> </Collapse>

        </div>
      </div>
    </div>
  </BasePage>
</template>

<style scoped lang="scss">
/* ── Layout ── */
.center {
  min-height: 100vh;
  padding: 5rem 1.5rem 3rem;
  background: var(--color-primary);
}

/* ── FAQ Card ── */
.card-white.qa {
  background: var(--color-card-bg);
  border: 1px solid var(--color-item-border);
  border-radius: 14px;
  padding: 2rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

/* ── Title ── */
.card-white.qa > .font-bold {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--color-main-text);
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-item-border);
}

/* ── Divider ── */
.card-white.qa .line {
  border-bottom: 1px solid var(--color-item-border);
  margin: 0.25rem 0;
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
