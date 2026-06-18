<script setup lang="ts">
import { defineAsyncComponent, nextTick, ref, watch } from 'vue'
import { getDefaultSettingState, useSettingStore } from '@typewords/core/stores/setting'
import { getShortcutKey, useEventListener } from '@typewords/core/hooks/event'
import {
  checkAndUpgradeSaveDict,
  checkAndUpgradeSaveSetting,
  cloneDeep,
  isEmpty,
  loadJsLib,
} from '@typewords/core/utils'
import { BaseButton, BaseInput, Form, FormItem, type FormType, PopConfirm, Toast, UploadButton } from '@typewords/base'
import { getDefaultBaseState, useBaseStore } from '@typewords/core/stores/base'
import {
  APP_NAME,
  APP_VERSION,
  BACKUP_INDEX_KEY,
  DefaultShortcutKeyMap,
  DictId,
  LIB_JS_URL,
  LOCAL_FILE_KEY,
  Old_Host,
  Origin,
} from '@typewords/core/config/env'
import { get, set } from 'idb-keyval'
import { useRuntimeStore } from '@typewords/core/stores/runtime'
import { useExport } from '@typewords/core/hooks/export'
import MigrateDialog from '@typewords/core/components/dialog/MigrateDialog.vue'
import Log from '@typewords/core/components/setting/Log.vue'
import CommonSetting from '@typewords/core/components/setting/CommonSetting.vue'
import FsrsSetting from '@typewords/core/components/setting/FsrsSetting.vue'
import WordSetting from '@typewords/core/components/setting/WordSetting.vue'
import { PRACTICE_ARTICLE_CACHE, PRACTICE_WORD_CACHE } from '@typewords/core/utils/cache'
import { useDataSyncPersistence } from '@typewords/core/composables/useDataSyncPersistence'
import SettingItem from '@typewords/core/components/setting/SettingItem.vue'
import { Supabase } from '@typewords/core/utils/supabase.ts'
import BackupGateDialog from '@typewords/core/components/dialog/BackupGateDialog.vue'
import type { BackupData, Snapshot } from '@typewords/core'
import { BasePage } from '@typewords/base'

import { createClient } from '@supabase/supabase-js'
import { useRoute } from 'vue-router'

const Dialog = defineAsyncComponent(() => import('@typewords/base/Dialog'))

type HistoryBackupIndexItem = {
  hash: string
  key: string
  createdAt: number
}

type HistoryBackupMeta = HistoryBackupIndexItem & {
  previousHash?: string | null
}

let route = useRoute()
let title = APP_NAME + ' 设置'
useSeoMeta({
  title: title,
  description: title,
  ogTitle: title,
  ogDescription: title,
  ogUrl: Origin + route.fullPath,
  twitterTitle: title,
  twitterDescription: title,
})

const tabIndex = $ref(Number(route?.query?.index ?? 0))
const settingStore = useSettingStore()
const runtimeStore = useRuntimeStore()
const store = useBaseStore()
const dataSyncPersistence = useDataSyncPersistence()

const config = useRuntimeConfig()
const gitLastCommitHash = ref(config?.public?.latestCommitHash)

let editShortcutKey = $ref('')

const disabledDefaultKeyboardEvent = $computed(() => {
  return editShortcutKey && tabIndex === 7
})

// 监听编辑快捷键状态变化，自动聚焦输入框
watch(
  () => editShortcutKey,
  newVal => {
    if (newVal) {
      // 使用nextTick确保DOM已更新
      nextTick(() => {
        focusShortcutInput()
      })
    }
  }
)

useEventListener('keydown', (e: KeyboardEvent) => {
  if (!disabledDefaultKeyboardEvent) return

  // 确保阻止浏览器默认行为
  e.preventDefault()
  e.stopPropagation()

  let shortcutKey = getShortcutKey(e)

  // console.log('e', e, e.keyCode, e.ctrlKey, e.altKey, e.shiftKey)
  // console.log('key', shortcutKey)

  // if (shortcutKey[shortcutKey.length-1] === '+') {
  //   settingStore.shortcutKeyMap[editShortcutKey] = DefaultShortcutKeyMap[editShortcutKey]
  //   return ElMessage.warning('设备失败！')
  // }

  if (editShortcutKey) {
    if (shortcutKey === 'Delete') {
      settingStore.shortcutKeyMap[editShortcutKey] = ''
    } else {
      // 忽略单独的修饰键
      if (
        shortcutKey === 'Ctrl+' ||
        shortcutKey === 'Alt+' ||
        shortcutKey === 'Shift+' ||
        e.key === 'Control' ||
        e.key === 'Alt' ||
        e.key === 'Shift'
      ) {
        return
      }

      for (const [k, v] of Object.entries(settingStore.shortcutKeyMap)) {
        if (v === shortcutKey && k !== editShortcutKey) {
          settingStore.shortcutKeyMap[editShortcutKey] = DefaultShortcutKeyMap[editShortcutKey]
          return Toast.warning('快捷键重复！')
        }
      }
      settingStore.shortcutKeyMap[editShortcutKey] = shortcutKey
    }
  }
})

function handleInputBlur() {
  // 输入框失焦时结束编辑状态
  editShortcutKey = ''
}

function focusShortcutInput() {
  // 找到当前正在编辑的快捷键输入框
  const inputElements = document.querySelectorAll('.set-key input')
  if (inputElements && inputElements.length > 0) {
    // 聚焦第一个找到的输入框
    const inputElement = inputElements[0] as HTMLInputElement
    inputElement.focus()
  }
}

// 快捷键中文名称映射
function getShortcutKeyName(key: string): string {
  const shortcutKeyNameMap = {
    ShowWord: '显示单词',
    Next: '下一个',
    Previous: '上一个',
    Ignore: '跳过单词',
    ToggleSimple: '切换已掌握状态',
    ToggleCollect: '切换收藏状态',
    NextChapter: '下一组',
    PreviousChapter: '上一组',
    NextStep: '下一阶段',
    RepeatChapter: '重复本组',
    DictationChapter: '默写本组',
    PlayWordPronunciation: '播放发音',
    ToggleShowTranslate: '切换显示翻译',
    ToggleDictation: '切换默写模式',
    ToggleTheme: '切换主题',
    ToggleConciseMode: '切换底部工具栏和右侧列表',
    ToggleToolbar: '切换底部工具栏',
    TogglePanel: '切换右侧列表',
    RandomWrite: '随机默写',
    KnowWord: '认识单词',
    UnknownWord: '不认识单词',
    MasteredWord: '已掌握单词',
    ChooseA: '选A',
    ChooseB: '选B',
    ChooseC: '选C',
    ChooseD: '选D',
  }

  return shortcutKeyNameMap[key] || key
}

function resetShortcutKeyMap() {
  editShortcutKey = ''
  settingStore.shortcutKeyMap = cloneDeep(DefaultShortcutKeyMap)
  Toast.success('恢复成功')
}

let importLoading = $ref(false)
let configLoading = $ref(false)

const { loading: exportLoading, exportData, getExportedData } = useExport()

async function importJson(str: string) {
  importLoading = true
  let obj: BackupData = {
    version: -1,
    val: {
      setting: {},
      dict: {},
      [PRACTICE_WORD_CACHE.key]: null,
      [PRACTICE_ARTICLE_CACHE.key]: null,
      // @deprecated 大版本5废弃
      [APP_VERSION.key]: null,
    },
  }
  try {
    debugger
    obj = JSON.parse(str)
    let data = obj.val
    data.dict.val = await checkAndUpgradeSaveDict(data.dict)
    data.setting.val = await checkAndUpgradeSaveSetting(data.setting)
    //老版本兼容逻辑
    if (obj.version === 4) {
      if (!isEmpty(data?.[APP_VERSION.key])) {
        data.setting.val.webAppVersion = data?.[APP_VERSION.key]
      }
    }
    //需在调同步方法前面，同步方法可能报错
    let hasRemote = Supabase.check()
    runtimeStore.globalLoading = true
    const pushOk = await dataSyncPersistence.forcePushLocalDataToRemote(data)
    runtimeStore.globalLoading = false
    if (pushOk) {
      Toast.success('导入数据成功，已强制覆盖远程数据')
    } else {
      Toast.success(hasRemote ? '导入数据成功，但推送远程失败' : '导入成功！')
    }
    runtimeStore.isNew = APP_VERSION.version > Number(data.setting?.val?.webAppVersion ?? APP_VERSION.version)
    data.setting.val.load = true
    settingStore.setState(data.setting.val)
    data.dict.val.load = true
    store.setState(data.dict.val)
    showBackupGate = false
  } catch (err) {
    return Toast.error('导入失败！')
  } finally {
    importLoading = false
  }
}

async function importData(e) {
  importLoading = true
  let file = e.target.files[0]
  if (!file) return (importLoading = false)
  if (file.name.endsWith('.json')) {
    let reader = new FileReader()
    reader.onload = function (v) {
      let str: any = v.target.result
      if (str) {
        importJson(str)
      }
    }
    reader.readAsText(file)
  } else if (file.name.endsWith('.zip')) {
    try {
      const JSZip = await loadJsLib('JSZip', LIB_JS_URL.JSZIP)
      const zip = await JSZip.loadAsync(file)

      const dataFile = zip.file('data.json')
      if (!dataFile) {
        return Toast.error('缺少 data.json，导入失败')
      }

      const mp3Folder = zip.folder('mp3')
      if (mp3Folder) {
        const records: { id: string; file: Blob }[] = []
        for (const filename in zip.files) {
          if (filename.startsWith('mp3/') && filename.endsWith('.mp3')) {
            const entry = zip.file(filename)
            if (!entry) continue
            const blob = await entry.async('blob')
            const id = filename.replace(/^mp3\//, '').replace(/\.mp3$/, '')
            records.push({ id, file: blob })
          }
        }
        await set(LOCAL_FILE_KEY, records)
      }

      const str = await dataFile.async('string')
      await importJson(str)
    } catch (e) {
      Toast.error(e?.message || e || '导入失败')
    } finally {
      importLoading = false
    }
  } else {
    Toast.error('不支持的文件类型')
  }
  importLoading = false
}

let isNewHost = $ref(false)
let showTransfer = $ref(false)
let showBackupGate = $ref(false)
let showHistoryDialog = $ref(false)
let pendingNextAction = $ref<'import' | 'supabase_save' | 'restore_history' | 'transfer' | ''>('')
let historyBackups = $ref<HistoryBackupMeta[]>([])
let restoreTarget = $ref<HistoryBackupMeta | null>(null)
let restoreLoading = $ref(false)
let showSbFirstSyncChoiceDialog = $ref(false)
let sbSyncChoiceLoading = $ref(false)

function openGate(type) {
  pendingNextAction = type
  showBackupGate = true
}

async function openHistoryDialog() {
  const raw = (await get(BACKUP_INDEX_KEY)) as HistoryBackupIndexItem[] | undefined
  const index = Array.isArray(raw)
    ? raw.filter(item => item && typeof item.hash === 'string' && typeof item.key === 'string')
    : []
  const items: HistoryBackupMeta[] = []
  for (const item of index) {
    const snapshot = (await get(item.key)) as { meta?: { previousHash?: string | null } } | undefined
    items.push({
      ...item,
      previousHash: snapshot?.meta?.previousHash ?? null,
    })
  }
  historyBackups = items.sort((a, b) => b.createdAt - a.createdAt)
  showHistoryDialog = true
}

function formatHistoryTime(timestamp: number): string {
  return new Date(timestamp).toLocaleString()
}

function openHistoryRestoreGate(item: HistoryBackupMeta) {
  restoreTarget = item
  openGate('restore_history')
}

function openSupabaseSaveGate() {
  sbFormRef?.validate(valid => {
    if (!valid) return
    openGate('supabase_save')
  })
}

async function restoreHistoryData() {
  if (!restoreTarget) return
  if (restoreLoading) return
  restoreLoading = true
  try {
    const { data: val }: Snapshot = await get(restoreTarget.key)
    debugger
    let data: BackupData['val'] = {
      setting: JSON.parse(val.setting),
      dict: JSON.parse(val.dict),
      [PRACTICE_WORD_CACHE.key]: JSON.parse(val[PRACTICE_WORD_CACHE.key]),
      [PRACTICE_ARTICLE_CACHE.key]: JSON.parse(val[PRACTICE_ARTICLE_CACHE.key]),
    }
    data.dict.val = await checkAndUpgradeSaveDict(data.dict)
    data.setting.val = await checkAndUpgradeSaveSetting(data.setting)

    //需在调同步方法前面，同步方法可能报错
    let hasRemote = Supabase.check()
    runtimeStore.globalLoading = true
    const pushOk = await dataSyncPersistence.forcePushLocalDataToRemote(data)
    runtimeStore.globalLoading = false
    if (pushOk) {
      Toast.success('历史数据恢复成功，已强制覆盖远程数据')
    } else {
      Toast.success(hasRemote ? '历史数据已恢复，但推送远程失败' : '恢复成功！')
    }
    runtimeStore.isNew = APP_VERSION.version > Number(data.setting?.val?.webAppVersion ?? APP_VERSION.version)
    data.setting.val.load = true
    settingStore.setState(data.setting.val)
    data.dict.val.load = true
    store.setState(data.dict.val)
    showBackupGate = false
    showHistoryDialog = false
  } catch (error) {
    Toast.error('恢复失败：' + ((error as Error)?.message ?? String(error)))
  } finally {
    restoreLoading = false
  }
}

let tempSbInstance = null

async function onSbFirstSyncChoice(action: 'push_local' | 'pull_remote') {
  if (sbSyncChoiceLoading) return
  sbSyncChoiceLoading = true
  try {
    if (action === 'push_local') {
      let localData = await getExportedData()
      const ok = await dataSyncPersistence.forcePushLocalDataToRemote(localData.val, tempSbInstance)
      if (!ok) throw new Error('本地推送失败')
      Toast.success('已将本地数据推送到远程')
    } else {
      const ok = await dataSyncPersistence.pullAllRemoteToLocal(tempSbInstance)
      if (!ok) throw new Error('拉取远程失败')
      Toast.success('已拉取远程数据到本地')
    }
    Supabase.setStatus('success')
    sbStatus = Supabase.getStatus()
    Supabase.saveConfig(sbForm?.url, sbForm?.key)
    showSbFirstSyncChoiceDialog = false
  } catch (error) {
    const msg = (error as Error)?.message ?? String(error)
    Supabase.setStatus('error', msg)
    sbStatus = Supabase.getStatus()
    Toast.error('同步失败：' + msg)
  } finally {
    sbSyncChoiceLoading = false
  }
}

onMounted(() => {
  isNewHost = window.location.host !== Old_Host
})

function transferOk() {
  setTimeout(() => {
    window.location.href = '/words'
  }, 1500)
}

function clearAllData() {
  let d = getDefaultBaseState()
  d.load = true
  store.setState(d)
  let d1 = getDefaultSettingState()
  d1.load = true
  settingStore.setState(d1)
}

let sbFormRef = $ref<FormType>()
const initialSbConfig = Supabase.getConfig()
let sbForm = $ref({
  url: initialSbConfig?.url ?? '',
  key: initialSbConfig?.key ?? '',
})
let sbStatus = $ref(Supabase.getStatus())
watch(
  () => tabIndex,
  () => {
    if (tabIndex === 5) sbStatus = Supabase.getStatus()
  }
)

let sbFormRules = {
  url: [{ required: true, message: '请输入 Supabase  Url', trigger: 'blur' }],
  key: [{ required: true, message: '请输入  Supabase  Key', trigger: 'blur' }],
}

//能否使用同步数据功能,如果有自定义的文章里面有音频，则不可以
const canSyncToServe = $computed(() => {
  //筛选自定义和收藏
  let bookList = store.article.bookList.filter(v => v.custom || [DictId.articleCollect].includes(v.id))
  let audioFileIdList = []
  bookList.forEach(v => {
    //筛选 audioFileId 字体有值的
    v.articles
      .filter(s => !s.audioSrc && s.audioFileId)
      .forEach(a => {
        //所有 id 存起来，下次直接判断字符串是否相等，因为这个watch会频繁调用
        audioFileIdList.push(a.audioFileId)
      })
  })
  return audioFileIdList.length === 0
})

async function doSaveSbConfig() {
  if (configLoading) return
  showBackupGate = false
  configLoading = true
  tempSbInstance = createClient(sbForm?.url, sbForm?.key)
  try {
    // 检测 typewords_data 表是否存在
    const { data: existingData, error: checkError } = await tempSbInstance.from('typewords_data').select('type')
    if (checkError) {
      Supabase.setStatus('error', checkError?.message ?? '表不存在')
      sbStatus = Supabase.getStatus()
      Toast.error('表不存在')
    } else {
      // 表已存在，检测是否需要插入默认数据
      const rows = (existingData ?? []) as { type: string }[]
      const existingTypes = rows.map(d => d.type)
      const defaultData = [
        { type: 'dict', data: {} },
        { type: 'setting', data: {} },
        { type: 'practice_word', data: {} },
        { type: 'practice_article', data: {} },
      ]
      for (const item of defaultData) {
        if (!existingTypes.includes(item.type)) {
          await (tempSbInstance as any).from('typewords_data').insert(item)
        }
      }
      const { data: hasVersionData, error: versionError } = await (tempSbInstance as any)
        .from('typewords_data')
        .select('type, data_version')
        .in('type', ['dict', 'setting', 'practice_word', 'practice_article'])
        .not('data_version', 'is', null)
      if (versionError) {
        throw new Error(versionError?.message ?? String(versionError))
      }
      const hasRemoteVersionData = Array.isArray(hasVersionData) && hasVersionData.length > 0

      if (hasRemoteVersionData) {
        showSbFirstSyncChoiceDialog = true
      } else {
        Supabase.setStatus('success')
        sbStatus = Supabase.getStatus()
        Toast.success('保存成功')
        Supabase.saveConfig(sbForm?.url, sbForm?.key)
        transferOk()
      }
    }
  } catch (error) {
    const msg = (error as Error)?.message ?? String(error)
    Supabase.setStatus('error', msg)
    sbStatus = Supabase.getStatus()
    Toast.error('出现错误：' + msg)
  } finally {
    configLoading = false
  }
}

function removeSbConfig() {
  sbFormRef?.validate(async valid => {
    if (valid) {
      Supabase.removeConfig()
      sbForm.url = ''
      sbForm.key = ''
      sbStatus = { status: 'idle', statusMessage: undefined }
      Toast.success('清除成功')
      setTimeout(() => {
        location.href = '/words'
      }, 1000)
    }
  })
}

</script>

<template>
  <BasePage>
    <a href="https://nuo.im" class="home-link" title="首页"><img src="/imgs/logo/logo.png" alt="首页" class="home-icon" /><span>首页</span></a>
    <div class="setting text-md card flex flex-col" style="height: calc(100vh - 3rem)">
      <div class="page-title text-align-center">{{ $t('setting') }}</div>
      <div class="flex flex-1 overflow-hidden gap-4">
        <div class="left">
          <div class="tabs">
            <div class="tab" :class="tabIndex === 0 && 'active'" @click="tabIndex = 0">
              <IconFluentSettings20Regular />
              <span>{{ $t('general_settings') }}</span>
            </div>
            <div class="tab" :class="tabIndex === 1 && 'active'" @click="tabIndex = 1">
              <IconFluentBot20Regular />
              <span>{{ $t('fsrs_settings') }}</span>
            </div>
            <div class="tab" :class="tabIndex === 2 && 'active'" @click="tabIndex = 2">
              <IconFluentTextUnderlineDouble20Regular />
              <span>{{ $t('word_settings') }}</span>
            </div>
            <div class="tab" :class="tabIndex === 5 && 'active'" @click="tabIndex = 5">
              <IconFluentDatabasePerson20Regular />
              <span>{{ $t('data_management') }}</span>
            </div>
            <div
              class="tab"
              :class="tabIndex === 6 && 'active'"
              @click="
                () => {
                  tabIndex = 6
                  runtimeStore.isNew = false
                  settingStore.webAppVersion = APP_VERSION.version
                }
              "
            >
              <IconFluentCloudSync20Regular />
              <span>数据同步</span>
              <div class="red-point" v-if="runtimeStore.isError || runtimeStore.isNew"></div>
            </div>
            <div class="tab" :class="tabIndex === 7 && 'active'" @click="tabIndex = 7">
              <IconFluentKeyboardLayoutFloat20Regular />
              <span>{{ $t('shortcut_settings') }}</span>
            </div>
            <div
              class="tab"
              :class="tabIndex === 8 && 'active'"
              @click="
                () => {
                  tabIndex = 8
                  // runtimeStore.isNew = false
                  // settingStore.webAppVersion = APP_VERSION.version
                }
              "
            >
              <IconFluentTextBulletListSquare20Regular />
              <span>{{ $t('update_log') }}</span>
              <!--              <div class="red-point" v-if="runtimeStore.isNew"></div>-->
            </div>
          </div>
        </div>
        <div class="col-line"></div>
        <div class="flex-1 overflow-y-auto overflow-x-hidden pr-4 content">
          <CommonSetting v-if="tabIndex === 0" />
          <FsrsSetting v-if="tabIndex === 1" />
          <WordSetting v-if="tabIndex === 2" />

          <div v-if="tabIndex === 5">
            <!--            导出数据-->
            <SettingItem
              title="导出数据"
              :desc="`${$t('data_saved_locally')}。如果您需要在不同的设备、浏览器上使用 ${APP_NAME}，
              您需要手动进行数据导出和导入`"
            >
              <BaseButton :loading="exportLoading" @click="exportData()">{{ $t('export_data_backup') }}</BaseButton>
            </SettingItem>
            <div class="text-gray text-sm">💾 导出的ZIP文件包含所有学习数据，可在其他设备上导入恢复</div>
            <div class="line my-3"></div>

            <!--            导入数据-->
            <SettingItem title="导入数据">
              <BaseButton @click="openGate('import')" :loading="importLoading">{{
                $t('import_data_restore')
              }}</BaseButton>
            </SettingItem>
            <div>请注意，导入数据将<b class="text-red"> 完全覆盖 </b>当前所有数据，请谨慎操作。</div>

            <!--            新网站同步-->
            <template v-if="isNewHost">
              <div class="line my-3"></div>
              <SettingItem title="迁移 2study.top 网站数据">
                <BaseButton @click="openGate('transfer')">迁移</BaseButton>
              </SettingItem>
              <div>请注意，迁移数据后将<b class="text-red"> 完全覆盖 </b>当前所有数据，请谨慎操作。</div>
            </template>

            <div class="line my-3"></div>
            <SettingItem title="其他"> </SettingItem>
            <div class="flex gap-space">
              <BaseButton @click="openHistoryDialog">历史数据</BaseButton>
              <PopConfirm title="该操作将会清除所有数据，确认继续？" @confirm="clearAllData">
                <BaseButton>清除所有数据</BaseButton>
              </PopConfirm>
            </div>
          </div>

          <div v-if="tabIndex === 6">
            <!--          Supabase 设置  -->
            <SettingItem title="Supabase 配置" desc="网站不会上传您的 url 和 key，只保存在浏览器本地(Local storage)">
              <div v-if="sbStatus.status !== 'idle'" class="mt-2 text-sm">
                <span v-if="sbStatus.status === 'success'" class="text-green"
                  >状态：同步正常运行中，数据已同步到云端</span
                >
                <span v-else-if="sbStatus.status === 'error'" class="text-red">
                  同步状态：失败{{ sbStatus.statusMessage ? `（${sbStatus.statusMessage}）` : '' }}
                </span>
                <span v-else-if="sbStatus.status === 'syncing'">同步状态：同步中…</span>
              </div>
            </SettingItem>

            <div class="mb-6">
              <div>
                Supbase 官网：
                <a href="https://supabase.com/" target="_blank">https://supabase.com/</a>
              </div>
              <div>
                Supbase 使用教程：
                <a href="https://www.kdocs.cn/l/cduLx52XXXgw" target="_blank">https://www.kdocs.cn/l/cduLx52XXXgw</a>
              </div>
              <div>
                Supbase 是一个（免费版 500 MB数据库）在线数据库工具，可以用来保存/同步
                {{ APP_NAME }} 的数据，免费版额度个人已够使用
              </div>
            </div>

            <div class="relative">
              <Form ref="sbFormRef" :rules="sbFormRules" :model="sbForm">
                <FormItem label="Url" prop="url">
                  <BaseInput v-model="sbForm.url" />
                </FormItem>
                <FormItem label="Key" prop="key">
                  <BaseInput v-model="sbForm.key" />
                </FormItem>
              </Form>
              <div class="flex justify-end">
                <BaseButton @click="removeSbConfig" :disabled="!canSyncToServe">删除配置</BaseButton>
                <BaseButton @click="openSupabaseSaveGate" :loading="configLoading" :disabled="!canSyncToServe">{{
                  runtimeStore.isError ? '重试' : '保存配置'
                }}</BaseButton>
              </div>
              <div
                class="absolute top-0 left-0 w-full h-full bg-[var(--color-card-bg)] opacity-80 cursor-not-allowed z-10 center rounded-md"
                v-if="!canSyncToServe"
              >
                <div class="text-red">检测到自定义文章里面有自定义音频，无法使用同步功能</div>
              </div>
            </div>
          </div>

          <div class="body" v-if="tabIndex === 7">
            <div class="row">
              <label class="main-title">{{ $t('function') }}</label>
              <div class="wrapper">{{ $t('shortcut_key') }}</div>
            </div>
            <div class="scroll">
              <div class="row" v-for="item of Object.entries(settingStore.shortcutKeyMap)">
                <label class="item-title">{{ getShortcutKeyName(item[0]) }}</label>
                <div class="wrapper" @click="editShortcutKey = item[0]">
                  <div class="set-key" v-if="editShortcutKey === item[0]">
                    <input
                      ref="shortcutInput"
                      :value="item[1] ? item[1] : $t('no_shortcut_set')"
                      readonly
                      type="text"
                      @blur="handleInputBlur"
                    />
                    <span @click.stop="editShortcutKey = ''"
                      >{{ $t('press_key_to_set') }}，<span class="text-red!">{{
                        $t('click_here_when_done')
                      }}</span></span
                    >
                  </div>
                  <div v-else>
                    <div v-if="item[1]">{{ item[1] }}</div>
                    <span v-else>{{ $t('no_shortcut_set') }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="row">
              <label class="item-title"></label>
              <div class="wrapper">
                <BaseButton @click="resetShortcutKeyMap">{{ $t('restore_default') }}</BaseButton>
              </div>
            </div>
          </div>

          <!--          日志-->
          <Log v-if="tabIndex === 8" />

        </div>
      </div>
    </div>
  </BasePage>

  <BackupGateDialog v-model="showBackupGate">
    <template v-slot="{ disabled }">
      <BaseButton @click="doSaveSbConfig" :disabled="disabled" v-if="pendingNextAction === 'supabase_save'">{{
        runtimeStore.isError ? '重试' : '保存配置'
      }}</BaseButton>
      <BaseButton @click="showTransfer = true" :disabled="disabled" v-else-if="pendingNextAction === 'transfer'"
        >迁移</BaseButton
      >
      <BaseButton
        v-else-if="pendingNextAction === 'restore_history'"
        @click="restoreHistoryData"
        :disabled="disabled"
        :loading="restoreLoading"
      >
        恢复此历史数据
      </BaseButton>

      <UploadButton
        @change="importData"
        :disabled="disabled"
        :loading="importLoading"
        accept="application/json,.zip,application/zip"
        v-else
      >
        {{ $t('import_data_restore') }}
      </UploadButton>
    </template>
  </BackupGateDialog>

  <Dialog v-model="showHistoryDialog" title="历史数据">
    <div class="p-4 w-120 max-h-100 overflow-auto">
      <div v-if="!historyBackups.length" class="color-gray">暂无历史数据</div>
      <div v-else class="flex flex-col gap-3">
        <div>这里是每次 {{ APP_NAME }} 更新后/报错后自动保存的用户数据，如果您的数据被损坏，您可在此尝试恢复</div>
        <div v-for="item in historyBackups" :key="item.key" class="border rounded-md flex justify-between">
          <div>
            <div class="">版本号：{{ item.hash }}</div>
            <div class="color-gray">自动备份时间：{{ formatHistoryTime(item.createdAt) }}</div>
          </div>
          <div class="mt-2">
            <BaseButton @click="openHistoryRestoreGate(item)" :disabled="restoreLoading">恢复此版本</BaseButton>
          </div>
        </div>
      </div>
    </div>
  </Dialog>

  <Dialog v-model="showSbFirstSyncChoiceDialog" title="检测到远程已有数据">
    <div class="p-4 w-120">
      <div class="">检测到远端已存在数据，请选择同步方向：</div>
      <div class="color-gray mt-2">- 本地推送：用当前本地数据覆盖远程</div>
      <div class="color-gray">- 拉取远程：用远程数据覆盖当前本地</div>
      <div class="flex justify-end mt-4">
        <BaseButton :loading="sbSyncChoiceLoading" @click="onSbFirstSyncChoice('push_local')">本地推送</BaseButton>
        <BaseButton :loading="sbSyncChoiceLoading" @click="onSbFirstSyncChoice('pull_remote')">拉取远程</BaseButton>
      </div>
    </div>
  </Dialog>

  <MigrateDialog v-model="showTransfer" @ok="transferOk" />
</template>

<style scoped lang="scss">
/* ── Layout ── */
.setting {
  background: var(--color-primary);
}

/* ── Left sidebar ── */
.setting .left {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-right: 1px solid var(--color-item-border);
  background: var(--color-card-bg);
  min-width: 180px;
  border-radius: 10px 0 0 10px;
}
.setting .left .tabs {
  padding: 0.6rem 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  width: 100%;
}
.setting .left .tabs .tab {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 0.93rem;
  color: var(--color-font-2);
  font-weight: 500;
}
.setting .left .tabs .tab svg {
  font-size: 1.1rem;
  flex-shrink: 0;
  opacity: 0.6;
}
.setting .left .tabs .tab:hover {
  background: var(--color-second);
  color: var(--color-main-text);
}
.setting .left .tabs .tab:hover svg {
  opacity: 1;
}
.setting .left .tabs .tab.active {
  background: var(--color-fifth);
  color: var(--color-select-bg);
  font-weight: 600;
}
.setting .left .tabs .tab.active svg {
  opacity: 1;
  color: var(--color-select-bg);
}

/* ── Right content ── */
.setting .content {
  padding: 0.5rem 1.5rem;
}

/* ── Divider ── */
.col-line {
  border-right: 1px solid var(--color-item-border);
}

.line {
  border-bottom: 1px solid var(--color-item-border);
}

/* ── Title ── */
.page-title {
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--color-main-text);
  padding: 0.25rem 0 0.75rem;
}

/* ── Setting rows ── */
.content .row {
  min-height: 2.8rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-item-border);
}
.content .row:last-child {
  border-bottom: none;
}
.content .row .main-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-main-text);
}
.content .row .item-title {
  font-size: 0.95rem;
  color: var(--color-main-text);
}
.content .row .sub-title {
  font-size: 0.85rem;
  color: var(--color-font-3);
}
.content .row .wrapper span {
  color: var(--color-font-2);
  font-size: 0.9rem;
}
.content .row .set-key input {
  width: 10rem;
  box-sizing: border-box;
  height: 2rem;
  outline: none;
  font-size: 0.95rem;
  border: 1px solid var(--color-input-border);
  border-radius: 6px;
  padding: 0 0.6rem;
  background: var(--color-input-bg);
  color: var(--color-input-color);
  transition: border-color 0.2s ease;
}
.content .row .set-key input:focus {
  border-color: var(--color-select-bg);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
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
