<template>
  <div class="voice-qa">
    <van-nav-bar title="语音用药问答" fixed safe-area-inset-top>
      <template #right>
        <van-icon name="delete-o" size="20" @click="confirmClear" />
      </template>
    </van-nav-bar>

    <div class="chat-area" ref="chatArea">
      <EmptyState v-if="!history.length" text="按住下方按钮开始说话，例如「高血压能吃布洛芬吗」" />

      <div
        v-for="m in history"
        :key="m.id"
        class="msg"
        :class="m.role"
      >
        <div class="bubble">
          {{ m.content }}
          <span v-if="m.role === 'assistant' && m.isDemo" class="demo-flag">
            ⚠️ AI 不可用，这是预置兜底回答
          </span>
        </div>
      </div>

      <div v-if="loading" class="msg assistant">
        <div class="bubble loading">
          <van-loading type="dots" size="20" /> 正在思考...
        </div>
      </div>
    </div>

    <div class="input-area">
      <van-field
        v-model="textInput"
        placeholder="或直接输入问题..."
        :border="false"
        clearable
        @keyup.enter="sendText"
      >
        <template #button>
          <van-button size="small" type="primary" @click="sendText">发送</van-button>
        </template>
      </van-field>
      <VoiceButton
        v-if="asrSupported"
        :on-result="onVoiceResult"
        :on-error="onVoiceError"
      />
      <p v-else class="asr-unsupported">
        当前浏览器不支持语音识别（仅 Chrome / Edge / Safari 可用），请直接在上方输入文字提问
      </p>
      <p class="footer-tip">
        <van-icon name="info-o" />
        当前用药 {{ medicines.length }} 种，回答时会一并考虑
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { showToast, showDialog } from 'vant'
import { useVoiceStore } from '@/stores/voice'
import { useMedicineStore } from '@/stores/medicine'
import { voiceChat, textToSpeech } from '@/api/voice'
import { playAudio, isASRSupported } from '@/utils/audio'
import VoiceButton from '@/components/VoiceButton.vue'
import EmptyState from '@/components/EmptyState.vue'

const voiceStore = useVoiceStore()
const medicineStore = useMedicineStore()
const { history } = storeToRefs(voiceStore)
const { medicines } = storeToRefs(medicineStore)

const textInput = ref('')
const loading = ref(false)
const chatArea = ref(null)
// QQ 浏览器 / 微信内置浏览器不支持 Web Speech API，提前判断避免按钮点了没反应
const asrSupported = ref(isASRSupported())

function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    }
  })
}

async function sendText() {
  const text = textInput.value.trim()
  if (!text) return
  textInput.value = ''
  await ask(text)
}

async function onVoiceResult(text) {
  if (!text) return
  await ask(text)
}

function onVoiceError(e) {
  showToast(e.message || '识别失败')
}

async function ask(question) {
  voiceStore.addMessage({ role: 'user', content: question })
  scrollToBottom()
  loading.value = true

  try {
    const ctx = medicines.value.map((m) => m.name)
    const hist = history.value
      .filter((m) => m.id !== history.value[history.value.length - 1].id) // 排除刚加的
      .map((m) => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
    const res = await voiceChat({ question, medicineContext: ctx, history: hist })

    voiceStore.addMessage({
      role: 'assistant',
      content: res.answer,
      isDemo: res.isDemo,
    })
    scrollToBottom()

    // 自动 TTS 播放
    if (voiceStore.voiceEnabled) {
      try {
        const url = await textToSpeech(res.answer)
        playAudio(url)
      } catch {
        // 静默失败
      }
    }
  } catch (e) {
    voiceStore.addMessage({ role: 'assistant', content: '抱歉，回答失败，请稍后再试。' })
  } finally {
    loading.value = false
  }
}

function confirmClear() {
  showDialog({ title: '清空历史', message: '确定要清空对话吗？', showCancelButton: true })
    .then(() => voiceStore.clearHistory())
    .catch(() => {})
}
</script>

<style scoped>
.voice-qa {
  padding-top: 46px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--zyt-bg);
}
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.msg {
  margin-bottom: 16px;
  display: flex;
}
.msg.user {
  justify-content: flex-end;
}
.msg.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 16px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
.msg.user .bubble {
  background: linear-gradient(135deg, #3b8dff 0%, #2f7ef7 100%);
  color: #fff;
  border-bottom-right-radius: 6px;
  box-shadow: 0 6px 16px rgba(47, 126, 247, 0.22);
}
.msg.assistant .bubble {
  background: #fff;
  color: #1f2733;
  border-bottom-left-radius: 6px;
  box-shadow: 0 6px 18px rgba(31, 45, 61, 0.08);
}
.bubble.loading {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7787;
}
.input-area {
  padding: 12px 12px env(safe-area-inset-bottom);
  background: #fff;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}
.input-area :deep(.van-field) {
  width: 100%;
  background: #f2f6fb;
  border-radius: 22px;
  padding: 4px 12px;
}
.footer-tip {
  margin: 0;
  font-size: 12px;
  color: #999;
  text-align: center;
}
.demo-flag {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #ff976a;
}
.asr-unsupported {
  margin: 4px 0 0;
  font-size: 13px;
  color: #ff976a;
  text-align: center;
  line-height: 1.5;
}
</style>