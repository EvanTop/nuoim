<script setup lang="ts">
import { Switch, Textarea } from '@typewords/base'
import SettingItem from './SettingItem.vue'
import { useSettingStore } from '../../stores/setting.ts'
import { useBaseStore } from '../../stores/base.ts'
import { ShortcutKey } from '../../types'

const settingStore = useSettingStore()
const store = useBaseStore()

const simpleWords = $computed({
  get: () => store.simpleWords.join(','),
  set: v => {
    try {
      store.simpleWords = v.split(',')
    } catch (e) {}
  },
})
</script>

<template>
  <div>
    <SettingItem
      title="输入框模式"
      desc="开启后，练习时将生成一个隐藏的输入框用于接收键盘事件，如果无法输入/输入异常请关闭此项，修改后请刷新页面"
    >
      <Switch v-model="settingStore.useInputMode" />
    </SettingItem>

    <SettingItem :title="$t('ignore_case')" desc="开启后，输入时不区分大小写，如输入“hello”和“Hello”都会被认为是正确的">
      <Switch v-model="settingStore.ignoreCase" />
    </SettingItem>

    <SettingItem
      :title="$t('allow_dictation_tip')"
      :desc="`${$t('allow_dictation_tip_desc')} ${settingStore.shortcutKeyMap[ShortcutKey.ShowWord]}`"
    >
      <Switch v-model="settingStore.allowWordTip" />
    </SettingItem>

    <div class="line"></div>
    <SettingItem :title="$t('simple_word_filter')" :desc="$t('simple_word_filter_desc')">
      <Switch v-model="settingStore.ignoreSimpleWord" />
    </SettingItem>

    <SettingItem :title="$t('simple_word_list')" class="items-start!" v-if="settingStore.ignoreSimpleWord">
      <Textarea
        :placeholder="$t('words_comma_separated')"
        v-model="simpleWords"
        :autosize="{ minRows: 6, maxRows: 10 }"
      />
    </SettingItem>
  </div>
</template>

<style scoped lang="scss"></style>
