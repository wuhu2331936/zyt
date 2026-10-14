<template>
  <div
    class="voice-btn"
    :class="{ recording }"
    @touchstart.prevent="handlePress"
    @touchend.prevent="handleRelease"
    @mousedown.prevent="handlePress"
    @mouseup.prevent="handleRelease"
    @mouseleave="handleRelease"
  >
    <van-icon :name="recording ? 'stop-circle-o' : 'volume-o'" size="36" color="#fff" />
    <p class="hint">{{ recording ? '正在聆听... 松开结束' : '按住 说话' }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { startRecognition, stopRecognition } from '@/utils/audio'

const props = defineProps({
  onResult: { type: Function },
  onError: { type: Function },
})
const recording = ref(false)

function handlePress() {
  if (recording.value) return
  recording.value = true
  startRecognition({
    onResult: (text, isFinal) => {
      if (isFinal) {
        recording.value = false
        props.onResult?.(text)
      }
    },
    onEnd: () => {
      recording.value = false
    },
    onError: (e) => {
      recording.value = false
      props.onError?.(e)
    },
  })
}

function handleRelease() {
  if (recording.value) {
    stopRecognition()
    recording.value = false
  }
}
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
}
.voice-btn.recording {
  transform: scale(1.08);
  background: linear-gradient(135deg, #ee0a24, #c2061a);
  box-shadow: 0 8px 24px rgba(238, 10, 36, 0.4);
}
.hint {
  margin: 6px 0 0;
  font-size: 13px;
}
</style>