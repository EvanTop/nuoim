<script setup lang="ts">
import Empty from '@typewords/core/components/Empty.vue'
import ArticleList from '@typewords/core/components/list/ArticleList.vue'
import { useBaseStore } from '@typewords/core/stores/base.ts'
import type { Article, Dict, Statistics } from '@typewords/core/types/types.ts'
import { useRuntimeStore } from '@typewords/core/stores/runtime.ts'
import { BackIcon, BaseButton, BaseIcon, Switch, Toast } from '@typewords/base'
import { useRoute, useRouter } from 'vue-router'
import EditBook from '@typewords/core/components/article/EditBook.vue'
import { computed, onMounted, onUnmounted, watch } from 'vue'
import {
  _dateFormat,
  _getDictDataByUrl,
  _nextTick,
  msToHourMinute,
  resourceWrap,
  total,
  useNav,
} from '@typewords/core/utils'
import { getDefaultArticle, getDefaultDict } from '@typewords/core/types/func.ts'
import ArticleAudio from '@typewords/core/components/article/ArticleAudio.vue'
import { MessageBox } from '@typewords/core/utils/MessageBox.tsx'
import { useSettingStore } from '@typewords/core/stores/setting.ts'
import { useFetch } from '@vueuse/core'
import { DICT_LIST } from '@typewords/core/config/env.ts'
import { useGetDict } from '@typewords/core/hooks/dict.ts'
import { DictType } from '@typewords/core/types/enum.ts'
import { usePracticeWordPersistence } from '@typewords/core/composables/usePracticePersistence.ts'
import { getPracticeArticleCacheLocal } from '@typewords/core/utils/cache.ts'

const { t } = useI18n()

const runtimeStore = useRuntimeStore()
const settingStore = useSettingStore()
const store = useBaseStore()
const router = useRouter()
const route = useRoute()
const { nav } = useNav()

const practice = usePracticeWordPersistence()
// useHead({
//   title: `${runtimeStore.editDict.name ?? ''}`,
// })

let isEdit = $ref(false)
let isAdd = $ref(false)
let studyLoading = $ref(false)
let articleRef = $ref<HTMLDivElement>()

let selectArticle: Article = $ref(getDefaultArticle({ id: -1 }))

function handleCheckedChange(val) {
  selectArticle = val.item
}

async function startPractice() {
  let sbook = runtimeStore.editDict
  if (!sbook.articles.length) {
    return Toast.warning('没有文章可学习！')
  }

  studyLoading = true
  const cache = await getPracticeArticleCacheLocal()
  if (cache) {
    let currentArticle = store.sbook.articles[store.sbook.lastLearnIndex]
    let data: Partial<Statistics> & { title: string; articleId: number } = {
      articleId: Number(currentArticle?.id),
      title: currentArticle?.title,
      spend: cache?.statStoreData?.spend,
      startDate: cache?.statStoreData?.startDate,
      total: cache?.statStoreData?.total,
      wrong: cache?.statStoreData?.wrong,
    }
    store.sbook.statistics.push(data as any)
    await practice.clear()
  }
  await store.changeBook(sbook)
  studyLoading = false

  window.umami?.track('startStudyArticle', {
    name: sbook.name,
    custom: sbook.custom,
    complete: sbook.complete,
    s: `name:${sbook.name},index:${sbook.lastLearnIndex},title:${sbook.articles[sbook.lastLearnIndex].title}`,
  })
  nav('/practice-articles/' + sbook.id)
}

const showBookDetail = computed(() => {
  return !(isAdd || isEdit)
})

const { loading } = useGetDict()

onMounted(() => {
  if (route.query?.isAdd) {
    isAdd = true
    runtimeStore.editDict = getDefaultDict()
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  if (displayMode === 'inline') {
    positionTranslations()
  }
}

function formClose() {
  if (isEdit) isEdit = false
  else router.back()
}

const { data: book_list } = useFetch(resourceWrap(DICT_LIST.ARTICLE.ALL)).json()

function reset() {
  MessageBox.confirm(
    '继续此操作会重置所有文章，并从官方书籍获取最新文章列表，学习记录不会被重置。确认恢复默认吗？',
    '恢复默认',
    async () => {
      let dict = book_list.value.find(v => v.url === runtimeStore.editDict.url) as Dict
      if (dict && dict.id) {
        dict = await _getDictDataByUrl(dict, DictType.article)
        let rIndex = store.article.bookList.findIndex(v => v.id === runtimeStore.editDict.id)
        if (rIndex > -1) {
          let item = store.article.bookList[rIndex]
          item.custom = false
          item.id = dict.id
          item.articles = dict.articles
          if (item.lastLearnIndex >= item.articles.length) {
            item.lastLearnIndex = item.articles.length - 1
          }
          runtimeStore.editDict = item
          Toast.success('恢复成功')
          return
        }
      }
      Toast.error('恢复失败')
    },
    null,
    null,
    { t }
  )
}

const currentPractice = $computed(() => {
  if (runtimeStore.editDict.statistics?.length) {
    return runtimeStore.editDict.statistics.filter(v => v.title === selectArticle.title)
  }
  return []
})

const totalSpend = $computed(() => {
  if (runtimeStore.editDict.statistics?.length) {
    return msToHourMinute(total(runtimeStore.editDict.statistics, 'spend'))
  }
  return 0
})

function next() {
  if (!settingStore.articleAutoPlayNext) return
  startPlay = true
  let index = runtimeStore.editDict.articles.findIndex(v => v.id === selectArticle.id)
  if (index > -1) {
    //如果是最后一个
    if (index === runtimeStore.editDict.articles.length - 1) index = -1
    selectArticle = runtimeStore.editDict.articles[index + 1]
  }
}

const list = $computed(() => {
  return [
    getDefaultArticle({
      title: '介绍',
      id: -1,
    }),
  ].concat(runtimeStore.editDict.articles)
})

let showTranslate = $ref(true)
let startPlay = $ref(false)
let showDisplayMode = $ref(false)
let displayMode = $ref<'card' | 'inline' | 'line'>('inline')
let articleWrapperRef = $ref<HTMLElement>()

const handleVolumeUpdate = (volume: number) => {
  settingStore.articleSoundVolume = volume
}

const handleSpeedUpdate = (speed: number) => {
  settingStore.articleSoundSpeed = speed
}

// 计算段落数量
const paragraphCount = $computed(() => {
  if (!selectArticle.text) return 0
  return selectArticle.text.split('\n\n').filter(p => p.trim()).length
})

// 判断是否应该在段落下显示译文（card 模式且段落数 > 1）
const shouldShowInlineTranslation = $computed(() => {
  return displayMode === 'card' && paragraphCount > 1
})

// 定位翻译到原文下方
function positionTranslations() {
  if (loading.value || selectArticle.id === -1) return
  _nextTick(() => {
    const articleRect = articleWrapperRef.getBoundingClientRect()
    selectArticle.textTranslate.split('\n\n').forEach((paragraph, paraIndex) => {
      paragraph.split('\n').forEach((sentence, sentIndex) => {
        const location = `${paraIndex}-${sentIndex}`
        const sentenceClassName = `.word-${location}-0`
        const sentenceEl = articleWrapperRef?.querySelector(sentenceClassName)
        const translateClassName = `.translate-${location}`
        const translateEl = articleWrapperRef?.querySelector(translateClassName) as HTMLDivElement

        if (sentenceEl && translateEl && sentence) {
          const sentenceRect = sentenceEl.getBoundingClientRect()
          translateEl.style.opacity = '1'
          translateEl.style.top = sentenceRect.top - articleRect.top + 24 + 'px'
          const spaceEl = translateEl.firstElementChild as HTMLElement
          if (spaceEl) {
            spaceEl.style.width = sentenceRect.left - articleRect.left + 'px'
          }
        }
      })
    })
  })
}

// 监听显示模式和文章变化，重新定位翻译
watch([() => displayMode, () => selectArticle.id, () => showTranslate], () => {
  if (displayMode !== 'card') {
    positionTranslations()
  }
})

watch(
  () => selectArticle.id,
  () => {
    _nextTick(() => {
      articleRef?.scrollTo(0, 0)
    })
  }
)
</script>

<template>
  <div class="center h-screen">
    <div
      class="bg-second w-full 3xl:w-7/10 2xl:w-8/10 xl:w-full 2xl:card 2xl:h-[97vh] h-full p-3 box-border overflow-hidden mb-0"
    >
      <div class="flex box-border flex-col h-full" v-if="showBookDetail" v-loading="loading">
        <div class="dict-header flex justify-between items-center relative">
          <div class="flex gap-space">
            <BackIcon class="dict-back z-2" />
            <div class="dict-title text-2xl text-align-center">{{ runtimeStore.editDict.name }}</div>
          </div>
          <div class="dict-actions flex">
            <BaseButton v-if="runtimeStore.editDict.custom && runtimeStore.editDict.url" type="info" @click="reset">
              {{ $t('restore_default') }}
            </BaseButton>
            <BaseButton :loading="studyLoading || loading" type="info" @click="isEdit = true">{{
              $t('edit')
            }}</BaseButton>
            <BaseButton type="info" @click="router.push('/batch-edit-article')">{{
              $t('article_management')
            }}</BaseButton>
            <BaseButton :loading="studyLoading || loading" @click="startPractice">{{ $t('learn') }}</BaseButton>
          </div>
        </div>
        <div class="flex flex-1 overflow-hidden mt-3">
          <div class="3xl:w-80 2xl:w-60 xl:w-55 lg:w-50 overflow-auto">
            <ArticleList
              :show-desc="true"
              v-if="list.length"
              @click="handleCheckedChange"
              :list="list"
              :active-id="selectArticle.id"
            >
            </ArticleList>
            <Empty v-else />
          </div>
          <div class="flex-1 shrink-0 pl-4 flex flex-col overflow-hidden">
            <template v-if="selectArticle.id">
              <template v-if="selectArticle.id === -1">
                <div class="flex gap-4 mt-2">
                  <NuxtImg
                    :src="runtimeStore.editDict?.cover"
                    class="w-30 rounded-md"
                    v-if="runtimeStore.editDict?.cover"
                    alt=""
                  />
                  <div class="text-lg">{{ runtimeStore.editDict.description }}</div>
                </div>
                <div class="text-base mt-10" v-if="totalSpend">{{ $t('total_study_time') }}：{{ totalSpend }}</div>
              </template>
              <template v-else>
                <div ref="articleRef" class="flex-1 overflow-auto pb-30">
                  <div>
                    <div class="flex justify-between items-center relative">
                      <span>
                        <span class="text-3xl">{{ selectArticle.title }}</span>
                        <span class="ml-6 text-2xl" v-if="showTranslate">{{ selectArticle.titleTranslate }}</span>
                      </span>
                      <div class="flex items-center gap-2 mr-4">
                        <BaseIcon :title="$t('toggle_translation')" @click="showTranslate = !showTranslate">
                          <IconPhTranslate v-if="showTranslate" />
                          <IconFluentTranslateOff16Regular v-else />
                        </BaseIcon>
                        <BaseIcon
                          :disabled="!showTranslate"
                          :title="$t('switch_display_mode')"
                          @click="showDisplayMode = !showDisplayMode"
                        >
                          <IconFluentTextAlignLeft16Regular />
                        </BaseIcon>
                      </div>
                    </div>

                    <div class="flex gap-1 mr-4 justify-end" v-if="showDisplayMode">
                      <BaseIcon :title="$t('line_by_line')" @click="displayMode = 'inline'">
                        <IconFluentTextPositionThrough20Regular />
                      </BaseIcon>
                      <BaseIcon :title="$t('single_line')" @click="displayMode = 'line'">
                        <IconFluentTextAlignLeft16Regular />
                      </BaseIcon>
                      <BaseIcon :title="$t('comparison')" @click="displayMode = 'card'">
                        <IconFluentAlignSpaceFitVertical20Regular />
                      </BaseIcon>
                    </div>

                    <div class="mt-2 text-2xl" v-if="selectArticle?.question?.text">
                      <div>Question: {{ selectArticle?.question?.text }}</div>
                      <div
                        class="text-xl color-translate-second"
                        v-if="showTranslate && (displayMode !== 'card' || shouldShowInlineTranslation)"
                      >
                        {{ $t('question') }}: {{ selectArticle?.question?.translate }}
                      </div>
                    </div>
                  </div>

                  <div
                    class="article-content mt-6"
                    :class="[showTranslate && displayMode !== 'card' && 'tall']"
                    ref="articleWrapperRef"
                  >
                    <article>
                      <template v-for="(t, i) in selectArticle.text.split('\n\n')" :key="`para-${i}`">
                        <div class="article-row w-full mb-10">
                          <span
                            :class="displayMode === 'line' && 'block'"
                            v-for="(w, j) in t.split('\n')"
                            :key="`${i}-${j}`"
                          >
                            <span
                              v-for="(s, n) in w.split(' ').filter(Boolean)"
                              :class="`inline-block word-${i}-${j}-${n}`"
                              :key="`${i}-${j}-${n}`"
                              ><span>{{ s }}</span>
                              <span class="space"></span>
                            </span>
                          </span>
                        </div>

                        <!-- 当 card 模式且段落数 > 1 时，在每个段落下显示对应译文 -->
                        <div
                          v-if="shouldShowInlineTranslation && showTranslate && selectArticle.textTranslate"
                          class="trans-row text-xl color-translate-second -mt-7 mb-10"
                        >
                          <div v-if="selectArticle.textTranslate.split('\n\n')[i]">
                            {{ selectArticle.textTranslate.split('\n\n')[i] }}
                          </div>
                        </div>
                      </template>
                      <div class="text-right italic">
                        <div class="text-2xl" v-if="selectArticle?.quote?.text">{{ selectArticle?.quote?.text }}</div>
                        <div
                          class="trans-row text-xl color-translate-second"
                          v-if="
                            selectArticle?.quote?.translate &&
                            showTranslate &&
                            (displayMode !== 'card' || shouldShowInlineTranslation)
                          "
                        >
                          {{ selectArticle?.quote?.translate }}
                        </div>
                      </div>
                    </article>

                    <template v-if="showTranslate && selectArticle.textTranslate">
                      <div class="translate color-translate-second" v-if="displayMode !== 'card'">
                        <div
                          class="break-words w-full section"
                          v-for="(t, i) in selectArticle.textTranslate.split('\n\n')"
                        >
                          <div v-for="(w, j) in t.split('\n')" :class="`row translate-${i}-${j}`" :key="`${i}-${j}`">
                            <span class="space"></span>
                            <span>{{ w }}</span>
                          </div>
                        </div>
                      </div>
                      <template v-else>
                        <!-- 当段落数 <= 1 时，保持原样在文章末尾显示译文 -->
                        <template v-if="!shouldShowInlineTranslation">
                          <div class="line my-10"></div>
                          <div class="text-xl line-height-normal space-y-5">
                            <div class="mt-2" v-if="selectArticle?.question?.translate">
                              问题: {{ selectArticle?.question?.translate }}
                            </div>
                            <div class="trans-row" v-for="t in selectArticle.textTranslate.split('\n\n')">{{ t }}</div>
                            <div class="trans-row text-right italic">{{ selectArticle?.quote?.translate }}</div>
                          </div>
                        </template>
                      </template>
                    </template>
                  </div>
                  <template v-if="currentPractice.length">
                    <div class="line my-10"></div>
                    <div class="font-family text-base pr-2">
                      <div class="text-2xl font-bold">{{ $t('study_record') }}</div>
                      <div class="mt-1 mb-3">
                        {{ $t('total_study_time') }}：{{ msToHourMinute(total(currentPractice, 'spend')) }}
                      </div>
                      <div
                        class="item border border-item border-solid mt-2 p-2 bg-[var(--bg-history)] rounded-md flex justify-between"
                        v-for="i in currentPractice"
                      >
                        <span class="color-gray">{{ _dateFormat(i.startDate) }}</span>
                        <span>{{ msToHourMinute(i.spend) }}</span>
                      </div>
                    </div>
                  </template>
                </div>
                <div
                  v-if="selectArticle.audioSrc || selectArticle.audioFileId"
                  class="border-t-1 border-t-gray-300 border-solid border-0 center gap-2 pt-4"
                >
                  <ArticleAudio
                    :article="selectArticle"
                    @update-speed="handleSpeedUpdate"
                    @update-volume="handleVolumeUpdate"
                    :autoplay="settingStore.articleAutoPlayNext && startPlay"
                    @ended="next"
                  />
                  <div class="flex items-center gap-1">
                    <span>{{ $t('play_next_after_end') }}</span>
                    <Switch v-model="settingStore.articleAutoPlayNext" />
                  </div>
                </div>
              </template>
            </template>
            <Empty v-else />
          </div>
        </div>
      </div>
      <div class="" v-else>
        <div class="dict-header flex justify-between items-center relative">
          <BackIcon class="dict-back z-2" @click="isAdd ? $router.back() : (isEdit = false)" />
          <div class="dict-title absolute text-2xl text-align-center w-full">
            {{ runtimeStore.editDict.id ? $t('edit_book') : $t('create_book') }}
          </div>
        </div>
        <div class="center">
          <EditBook :is-add="isAdd" :is-book="true" @close="formClose" @submit="isEdit = isAdd = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dict-detail-card {
  height: calc(100vh - 3rem);
}

.dict-header {
  gap: 0.5rem;
}

.dict-actions {
  flex-wrap: wrap;
}

// 打字式显示模式样式（复用 TypingArticle 的样式）
$translate-lh: 3.2;
$article-lh: 2.4;

.article-content {
  position: relative;
  font-size: 1.6rem;

  &.tall {
    article {
      line-height: $article-lh;
      color: var(--color-article);
    }
  }

  .article-row {
    word-break: keep-all;
    word-wrap: break-word;
    white-space: pre-wrap;
  }

  .trans-row {
    @apply cn-article-family font-bold;
  }

  article {
    @apply en-article-family;
  }

  .translate {
    @apply absolute top-0 left-0 h-full w-full text-xl pointer-events-none font-bold cn-article-family;
    line-height: $translate-lh;
    letter-spacing: 0.2rem;

    .row {
      @apply absolute left-0 w-full opacity-0 transition-all duration-300;
    }
  }
}

.space {
  @apply inline-block w-2 transition-all duration-300;
}

.sentence-translate-mobile {
  display: none;
  margin-top: 0.4rem;
  font-size: 0.9rem;
  line-height: 1.4;
  color: var(--color-font-3);
  font-family: var(--zh-article-family);
  word-break: break-word;
}

@media (max-width: 768px) {
  .dict-detail-card {
    height: calc(100vh - 2rem);
  }

  .dict-header {
    width: 100%;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 0.75rem;
  }

  .dict-header .dict-back {
    align-self: flex-start;
  }

  .dict-header .dict-title {
    position: static !important;
    width: 100%;
  }

  .dict-header .dict-actions {
    width: 100%;
    justify-content: center;
    gap: 0.75rem;

    .base-button {
      flex: 1 0 45%;
      min-width: 8rem;
    }
  }
}

@media (max-width: 480px) {
  .dict-header .dict-actions {
    flex-direction: column;

    .base-button {
      width: 100%;
      min-width: auto;
    }
  }
}

// 移动端适配 - 打字式显示模式
@media (max-width: 768px) {
  .article-content {
    article {
      .section {
        margin-bottom: 1rem;

        .sentence {
          font-size: 1rem;
          line-height: 1.6;
          word-break: break-word;
          margin-bottom: 0.5rem;
        }
      }
    }

    .translate {
      display: none;
    }
  }

  .sentence-translate-mobile {
    display: block;
  }
}

@media (max-width: 480px) {
  .article-content {
    article {
      .section {
        .sentence {
          font-size: 0.9rem;
          line-height: 1.5;
        }
      }
    }
  }

  .sentence-translate-mobile {
    font-size: 0.85rem;
    line-height: 1.35;
  }
}
</style>
