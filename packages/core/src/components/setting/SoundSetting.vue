<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Option, Select, Slider, Switch, VolumeIcon } from '@typewords/base'
import SettingItem from './SettingItem.vue'
import { useSettingStore } from '../../stores/setting.ts'
import { ENV, SoundFileOptions } from '../../config/env.ts'
import { getBrowserKey, getAudioFileUrl, usePlayAudio, useTTsPlayAudio } from '../../hooks/sound.ts'

const settingStore = useSettingStore()

// ---- TTS 声色 ----
const ttsVoiceList = ref<SpeechSynthesisVoice[]>([])
// 用于在声色列表异步加载完成后强制重建 Select，使 modelValue watch 重新触发回显
const ttsSelectKey = ref(0)

onMounted(() => {
  if (typeof speechSynthesis === 'undefined') return
  const load = () => {
    ttsVoiceList.value = speechSynthesis
      .getVoices()
      .filter(v => v.lang.startsWith('en'))
      .sort((a, b) => (b.localService ? 0 : 1) - (a.localService ? 0 : 1))
    // 声色列表加载完毕后递增 key，强制 Select 重建，从而触发其内部 watch 重新匹配已保存的声色值
    ttsSelectKey.value++
  }
  load()
  speechSynthesis.onvoiceschanged = load
})

const browserKey = getBrowserKey()

const currentTtsVoice = computed({
  get() {
    return settingStore.ttsVoiceMap?.find(v => v.key === browserKey)?.voice ?? ''
  },
  set(voiceName: string) {
    const map = settingStore.ttsVoiceMap ? [...settingStore.ttsVoiceMap] : []
    const idx = map.findIndex(v => v.key === browserKey)
    if (idx >= 0) {
      map[idx] = { key: browserKey, voice: voiceName }
    } else {
      map.push({ key: browserKey, voice: voiceName })
    }
    settingStore.ttsVoiceMap = map
  },
})

let exampleText = 'How are you? I am fine, thank you. And you?'

function previewTtsVoice(voiceName: string) {
  if (typeof speechSynthesis === 'undefined') return
  speechSynthesis.cancel()
  const msg = new SpeechSynthesisUtterance(exampleText)
  msg.lang = 'en-US'
  const voice = ttsVoiceList.value.find(v => v.name === voiceName)
  if (voice) msg.voice = voice
  speechSynthesis.speak(msg)
}
</script>

<template>
  <div>
    <!-- 单词发音 -->
    <SettingItem :mainTitle="$t('word_pronunciation')" />
    <SettingItem :title="$t('pronunciation_accent')" :desc="$t('pronunciation_accent_desc')">
      <Select v-model="settingStore.soundType" :placeholder="$t('please_select')" class="w-50!">
        <Option :label="$t('us_accent')" value="us" />
        <Option :label="$t('uk_accent')" value="uk" />
      </Select>
    </SettingItem>
    <SettingItem :title="$t('word_auto_pronunciation')">
      <Switch v-model="settingStore.wordSound" />
    </SettingItem>
    <SettingItem :title="$t('volume')">
      <Slider v-model="settingStore.wordSoundVolume" showText showValue unit="%" />
    </SettingItem>
    <SettingItem :title="$t('speed')">
      <Slider v-model="settingStore.wordSoundSpeed" :step="0.1" :min="0.5" :max="3" showText showValue />
    </SettingItem>


    <!-- TTS 声色 -->
    <div class="line"></div>
    <SettingItem :mainTitle="$t('tts_voice')" />
    <div>{{ $t('tts_voice_preview_sentence') }}{{ exampleText }}</div>
    <SettingItem
      :title="$t('tts_voice_setting_title')"
      :desc="$t('tts_voice_setting_desc')"
    >
      <Select
        :key="ttsSelectKey"
        v-model="currentTtsVoice"
        :placeholder="ttsVoiceList.length ? $t('tts_select_placeholder') : $t('tts_no_voice_available')"
        class="w-80!"
      >
        <Option v-for="voice in ttsVoiceList" :key="voice.name" :label="voice.name" :value="voice.name">
          <div class="flex justify-between items-center w-full">
            <span class="truncate">{{ voice.name + `（${voice.localService ? $t('tts_local_voice') : $t('tts_network_voice')}）` }}</span>
            <VolumeIcon :time="100" @click="previewTtsVoice(voice.name)" />
          </div>
        </Option>
      </Select>
    </SettingItem>
    <div v-if="!currentTtsVoice" class="text-sm text-orange-500 mt-1 mb-2">
      {{ $t('tts_no_voice_warning') }}
    </div>


    <!-- 文章音效 -->
    <div class="line"></div>
    <SettingItem :mainTitle="$t('article_sound_settings')" />
    <SettingItem :title="$t('auto_play_sentence')">
      <Switch v-model="settingStore.articleSound" />
    </SettingItem>
    <SettingItem :title="$t('play_next_after_end')">
      <Switch v-model="settingStore.articleAutoPlayNext" />
    </SettingItem>
    <SettingItem :title="$t('article_volume')">
      <Slider v-model="settingStore.articleSoundVolume" showText showValue unit="%" />
    </SettingItem>
    <SettingItem :title="$t('article_speed')">
      <Slider v-model="settingStore.articleSoundSpeed" :step="0.1" :min="0.5" :max="3" showText showValue />
    </SettingItem>

    <!-- 按键音效 -->
    <div class="line"></div>
    <SettingItem :mainTitle="$t('keyboard_sound_settings')" />
    <SettingItem :title="$t('keyboard_sound')">
      <Switch v-model="settingStore.keyboardSound" />
    </SettingItem>
    <SettingItem :title="$t('keyboard_sound_effect')">
      <Select v-model="settingStore.keyboardSoundFile" :placeholder="$t('please_select')" class="w-50!">
        <Option v-for="item in SoundFileOptions" :key="item.value" :label="item.label" :value="item.value">
          <div class="flex justify-between items-center w-full">
            <span>{{ item.label }}</span>
            <VolumeIcon :time="100" @click="usePlayAudio(ENV.RESOURCE_URL + getAudioFileUrl(item.value)[0])" />
          </div>
        </Option>
      </Select>
    </SettingItem>
    <SettingItem :title="$t('volume')">
      <Slider v-model="settingStore.keyboardSoundVolume" showText showValue unit="%" />
    </SettingItem>

    <!-- 效果音 -->
    <div class="line"></div>
    <SettingItem :mainTitle="$t('effect_sound_settings')" />
    <SettingItem :title="$t('effect_sound')">
      <Switch v-model="settingStore.effectSound" />
    </SettingItem>
    <SettingItem :title="$t('effect_volume')">
      <Slider v-model="settingStore.effectSoundVolume" showText showValue unit="%" />
    </SettingItem>

  </div>
</template>

<style scoped lang="scss">
.line {
  border-bottom: 1px solid var(--color-line, #c4c3c3);
  margin: 0.8rem 0;
}
</style>
