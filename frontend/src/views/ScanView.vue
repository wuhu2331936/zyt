<template>
  <div class="scan-view">
    <van-nav-bar title="拍照识药" left-arrow @click-left="$router.back()" fixed safe-area-inset-top />

    <div class="content">
      <div class="hero">
        <div class="hero-icon">📸</div>
        <h2>请上传药盒正面照</h2>
        <p>AI 自动识别药品名、规格、用法用量</p>
      </div>

      <van-uploader
        v-model="fileList"
        :after-read="afterRead"
        :max-count="1"
        accept="image/*"
        :preview-image="false"
        class="uploader"
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
  padding: 20px 0;
}
.hero-icon {
  font-size: 56px;
}
.hero h2 {
  margin: 12px 0 6px;
  font-size: 20px;
}
.hero p {
  margin: 0;
  color: #666;
}
.uploader {
  margin: 16px 0;
}
.tips {
  margin-top: 16px;
}
.result {
  margin-top: 24px;
}
.result h3 {
  margin: 0 0 12px;
  font-size: 18px;
}
</style>