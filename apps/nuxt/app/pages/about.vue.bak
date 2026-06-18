<script setup lang="ts">
import { BasePage } from '@typewords/base'
import About from '@typewords/core/components/About.vue'
import { APP_NAME, Origin } from '@typewords/core/config/env.ts'

let route = useRoute()
const { t } = useI18n()

const title = APP_NAME + ' — ' + t('about_page_title')
useSeoMeta({
  title: title,
  description: t('about_page_desc'),
  ogTitle: title,
  ogDescription: t('about_page_desc'),
  ogUrl: Origin + route.fullPath,
  twitterTitle: title,
  twitterDescription: t('about_page_desc'),
})
</script>

<template>
  <BasePage>
    <div class="center">
      <div class="card-white w-2/3 center-col pb-20">
        <About />
      </div>
    </div>
  </BasePage>
</template>

<style scoped lang="scss"></style>
