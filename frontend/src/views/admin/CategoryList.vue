<template>
  <div>
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="handleAdd()">新增分类</el-button>
    </div>
    <el-table :data="categories" row-key="id" v-loading="loading" stripe>
      <el-table-column prop="name" label="分类名称" />
      <el-table-column prop="parent_name" label="父分类" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingCategory?.id ? '编辑分类' : '新增分类'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="form.parent" placeholder="留空则为顶级分类" clearable>
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const categories = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingCategory = ref({})

const form = reactive({
  name: '', parent: null,
})

async function loadCategories() {
  loading.value = true
  try {
    const res = await request.get('/categories?flat=true')
    categories.value = res.data || []
  } catch (e) {
    console.error('Failed to load categories')
  } finally {
    loading.value = false
  }
}

loadCategories()

function handleAdd() {
  editingCategory.value = {}
  Object.assign(form, { name: '', parent: null })
  dialogVisible.value = true
}

function handleEdit(row) {
  editingCategory.value = row
  Object.assign(form, { name: row.name, parent: row.parent })
  dialogVisible.value = true
}

async function handleSave() {
  try {
    if (editingCategory.value?.id) {
      await request.patch(`/admin/categories/${editingCategory.value.id}`, form)
      ElMessage.success('分类已更新')
    } else {
      await request.post('/admin/categories', form)
      ElMessage.success('分类已创建')
    }
    dialogVisible.value = false
    loadCategories()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function handleDelete(id) {
  try {
    await request.delete(`/admin/categories/${id}`)
    ElMessage.success('已删除')
    loadCategories()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; }
</style>
