<template>
  <div class="scan-view">
    <van-nav-bar title="拍照识药" left-arrow @click-left="$router.back()" fixed safe-area-inset-top />

    <div class="content">
      <div class="hero">
        <div class="hero-icon">📸</div>
        <h2>请上传药盒正面照</h2>
        <p>AI 自动识别药品名、规格、用法用量</p>
      </div>

      <div class="upload-zone" @click="pickImage">
        <div class="upload-inner">
          <div class="upload-emoji">🖼️</div>
          <b>点击选择 / 拍摄照片</b>
          <span>支持 JPG、PNG，单张即可</span>
        </div>
      </div>

      <van-uploader
        v-model="fileList"
        :after-read="afterRead"
        :max-count="1"
        accept="image/*"
        :preview-image="false"
        class="uploader"
        ref="uploaderRef"
      >
        <template #default>
          <van-button icon="plus" type="primary" round block size="large">
            选择照片
          </van-button>
        </template>
      </van-uploader>

      <van-cell-group inset class="tips">
        <van-cell title="📌 拍照小贴士" />
        <van-cell title="· 光线充足，正面拍摄" />
        <van-cell title="· 文字清晰可辨" />
        <van-cell title="· 避免反光与遮挡" />
      </van-cell-group>

      <!-- 识别中 loading -->
      <van-loading v-if="loading" type="circular" size="36" vertical>
        AI 正在识别药盒...
      </van-loading>

      <!-- 识别结果 -->
      <div v-if="result" class="result">
        <h3>✅ 识别结果</h3>
        <van-cell-group inset>
          <van-cell title="药品名称" :value="result.medicine.name" />
          <van-cell v-if="result.medicine.spec" title="规格" :value="result.medicine.spec" />
          <van-cell v-if="result.medicine.manufacturer" title="厂家" :value="result.medicine.manufacturer" />
          <van-cell v-if="result.medicine.usage" title="用法用量" :value="result.medicine.usage" />
          <van-cell v-if="result.medicine.indications" title="适应症" :value="result.medicine.indications" />
          <van-cell v-if="result.medicine.contraindications" title="禁忌" :value="result.medicine.contraindications" />
          <van-cell v-if="result.medicine.remarks" title="备注" :value="result.medicine.remarks" />
        </van-cell-group>

        <van-button
          type="success"
          block
          round
          icon="success"
          size="large"
          @click="addToList"
          style="margin-top: 16px;"
        >
          添加到我的用药清单
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showDialog } from 'vant'
import { recognizeMedicine } from '@/api/medicine'
import { useMedicineStore } from '@/stores/medicine'

const router = useRouter()
const medicineStore = useMedicineStore()

const fileList = ref([])
const loading = ref(false)
const result = ref(null)
const uploaderRef = ref(null)

// 点击自定义上传区 -> 触发 Vant Uploader 的隐藏 input
function pickImage() {
  const el = uploaderRef.value?.$el?.querySelector?.('input[type=file]')
  if (el) el.click()
}

async function afterRead(file) {
  // file.file 是浏览器 File 对象
  if (!file?.file) return
  loading.value = true
  result.value = null
  try {
    const res = await recognizeMedicine(file.file)
    if (res.success && res.medicine) {
      result.value = res
      showToast('识别成功')
    } else {
      showDialog({
        title: '识别失败',
        message: res.error || '请上传更清晰的药盒正面照',
        confirmButtonText: '重试',
      })
    }
  } catch (e) {
    // 错误已被 request 拦截器统一提示
  } finally {
    loading.value = false
  }
}

function addToList() {
  const id = medicineStore.addMedicine(result.value.medicine)
  showToast({ type: 'success', message: '已添加', duration: 1000 })
  setTimeout(() => router.push({ path: '/detail', query: { id } }), 800)
}
</script>

<style scoped>
.scan-view {
  padding-top: 46px;
}
.content {
  padding: 16px;
}
.hero {
  text-align: center;
  padding: 8px 0 4px;
}
.hero-icon {
  width: 84px;
  height: 84px;
  margin: 0 auto;
  border-radius: 26px;
  background: linear-gradient(135deg, #3b8dff 0%, #22c1a4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  box-shadow: 0 10px 24px rgba(47, 126, 247, 0.28);
}
.hero h2 {
  margin: 14px 0 6px;
  font-size: 20px;
  font-weight: 700;
  color: #1f2733;
}
.hero p {
  margin: 0;
  color: #6b7787;
  font-size: 15px;
}

/* 自定义虚线上传区 */
.upload-zone {
  margin: 18px 0 12px;
  border: 2px dashed #b9cdf5;
  border-radius: 18px;
  background: linear-gradient(135deg, #f5f9ff 0%, #f1fbf8 100%);
  padding: 26px 16px;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.upload-zone:active {
  transform: scale(0.985);
}
.upload-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.upload-emoji {
  font-size: 34px;
}
.upload-inner b {
  font-size: 17px;
  color: #1f2733;
}
.upload-inner span {
  font-size: 13px;
  color: #97a1b0;
}

/* 隐藏 Vant 原生选择按钮（保留功能，用自定义区触发） */
.uploader {
  height: 0;
  overflow: hidden;
}
.tips {
  margin-top: 8px;
}
.result {
  margin-top: 24px;
}
.result h3 {
  margin: 0 0 12px;
  font-size: 18px;
}
</style>