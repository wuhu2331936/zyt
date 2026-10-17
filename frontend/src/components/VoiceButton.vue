<template>
  <div
    class="voice-btn"
    :class="{ recording: status === 'recording', busy: status === 'transcribing' }"
    @touchstart.prevent="handlePress"
    @touchend.prevent="handleRelease"
    @touchcancel.prevent="handleRelease"
    @mousedown.prevent="handlePress"
    @mouseup.prevent="handleRelease"
    @mouseleave="handleRelease"
  >
    <van-icon :name="iconName" size="36" color="#fff" />
    <p class="hint">{{ hintText }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import {
  startVoiceInput,
  finishVoiceInput,
  cancelVoiceInput,
  unlockSpeech,
} from '@/utils/audio'

const props = defineProps({
  onResult: { type: Function },
  onError: { type: Function },
})

// idle | recording | transcribing
const status = ref('idle')
let pressed = false
let maxTimer = null

const iconName = computed(() => {
  if (status.value === 'recording') return 'stop-circle-o'
  if (status.value === 'transcribing') return 'clock-o'
  return 'volume-o'
})

const hintText = computed(() => {
  if (status.value === 'recording') return '正在聆听... 松开结束'
  if (status.value === 'transcribing') return '识别中...'
  return '按住 说话'
})

function setStatus(s) {
  status.value = s || 'idle'
}

function handlePress() {
  if (pressed) return
  pressed = true
  // iOS Safari 要求语音播报必须由用户手势解锁，借按下的时机提前解锁，
  // 否则 await 后端返回后再 speak() 会被系统静默丢弃（手机没声音的真凶）
  unlockSpeech()
  startVoiceInput({
    onStatus: setStatus,
    onResult: (text, meta) => {
      props.onResult?.(text, meta)
    },
    onError: (e) => {
      props.onError?.(e)
    },
  })
  // 兜底：老人可能按住不放，最多录 30 秒自动结束。
  // 30 秒 @16kHz 单声道约 480KB，既能说完一整句话，也不会撞上网关的请求体大小限制。
  clearTimeout(maxTimer)
  maxTimer = setTimeout(() => {
    if (pressed) handleRelease()
  }, 30000)
}

async function handleRelease() {
  if (!pressed) return
  pressed = false
  clearTimeout(maxTimer)
  await finishVoiceInput({
    onStatus: setStatus,
    onResult: (text, meta) => props.onResult?.(text, meta),
    onError: (e) => {
      setStatus('idle')
      props.onError?.(e)
    },
  })
}

onBeforeUnmount(() => {
  clearTimeout(maxTimer)
  cancelVoiceInput()
})
</script>

<style scoped>
.voice-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  margin: 0 auto;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa, #0570e0);
  color: #fff;
  user-select: none;
  -webkit-user-select: none;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(25, 137, 250, 0.4);
  transition: transform 0.15s;
  touch-action: none;
  -webkit-touch-callout: none;
}
.voice-btn.recording {
  transform: scale(1.08);
  background: linear-gradient(135deg, #ee0a24, #c2061a);
  box-shadow: 0 8px 24px rgba(238, 10, 36, 0.4);
}
.voice-btn.busy {
  background: linear-gradient(135deg, #ff976a, #f2783b);
  box-shadow: 0 8px 24px rgba(255, 151, 106, 0.4);
}
.hint {
  margin: 6px 0 0;
  font-size: 13px;
}
</style>
