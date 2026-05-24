<template>
  <div>
    <h2>{{ isEdit ? '编辑商品' : '新增商品' }}</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" class="product-form" v-loading="loading">
      <el-form-item label="商品名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-select v-model="form.category" placeholder="请选择分类">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="售价" prop="price">
        <el-input-number v-model="form.price" :min="0" :precision="2" />
      </el-form-item>
      <el-form-item label="库存" prop="stock">
        <el-input-number v-model="form.stock" :min="0" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item label="商品图片">
        <el-upload
          :auto-upload="false"
          :limit="1"
          :on-change="handleImageChange"
          :on-remove="handleImageRemove"
          accept="image/*"
          list-type="picture"
        >
          <el-button type="primary" plain>选择图片</el-button>
          <template #tip>
            <div class="el-upload-tip">支持 JPG/PNG 格式，建议尺寸 800x800</div>
          </template>
        </el-upload>
        <img v-if="imagePreview" :src="imagePreview" class="image-preview" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = ref(!!route.params.id)
const formRef = ref(null)
const loading = ref(false)
const saving = ref(false)
const categories = ref([])

const imageFile = ref(null)
const imagePreview = ref('')

const form = reactive({
  name: '', category: null, price: 0,
  stock: 0, description: '',
})

const rules = {
  name: [{ required: true, message: '请输入商品名称' }],
  category: [{ required: true, message: '请选择分类' }],
  price: [{ required: true, message: '请输入价格' }],
  stock: [{ required: true, message: '请输入库存' }],
}

async function loadCategories() {
  const res = await request.get('/categories?flat=true')
  categories.value = res.data || []
}

if (isEdit.value) {
  loadCategories()
  loading.value = true
  request.get(`/admin/products/${route.params.id}`).then(res => {
    Object.assign(form, res.data)
    loading.value = false
  })
} else {
  loadCategories()
}

function handleImageChange(file) {
  imageFile.value = file.raw
  imagePreview.value = URL.createObjectURL(file.raw)
}

function handleImageRemove() {
  imageFile.value = null
  imagePreview.value = ''
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const fd = new FormData()
    Object.entries(form).forEach(([k, v]) => { if (v !== null && v !== '') fd.append(k, v) })
    if (imageFile.value) {
      fd.append('image', imageFile.value)
    }
    const config = { headers: { 'Content-Type': 'multipart/form-data' } }
    if (isEdit.value) {
      await request.patch(`/admin/products/${route.params.id}`, fd, config)
      ElMessage.success('商品已更新')
    } else {
      await request.post('/admin/products', fd, config)
      ElMessage.success('商品已创建')
    }
    router.push('/admin/products')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
h2 { margin-bottom: 20px; }
.product-form { max-width: 600px; background: #fff; padding: 24px; border-radius: 8px; }
</style>
