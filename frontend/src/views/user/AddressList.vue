<template>
  <div class="page">
    <div class="page-header">
      <h2>收货地址</h2>
      <el-button type="primary" @click="openForm()">新增地址</el-button>
    </div>
    <AddressCard
      v-for="addr in addresses"
      :key="addr.id"
      :address="addr"
      @edit="openForm"
      @delete="handleDelete"
      @set-default="handleSetDefault"
    />
    <el-empty v-if="!addresses.length" description="暂无收货地址" />
    <AddressForm
      :visible="formVisible"
      :address="editingAddress"
      @close="formVisible = false"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAddresses, createAddress, updateAddress, deleteAddress, setDefaultAddress } from '@/api/address'
import AddressCard from '@/components/address/AddressCard.vue'
import AddressForm from '@/components/address/AddressForm.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const addresses = ref([])
const formVisible = ref(false)
const editingAddress = ref(null)

onMounted(() => { fetchAddresses() })

async function fetchAddresses() {
  const res = await getAddresses()
  addresses.value = res.data?.results || res.data || []
}

function openForm(addr = null) {
  editingAddress.value = addr ? { ...addr } : null
  formVisible.value = true
}

async function handleSave(data) {
  try {
    if (editingAddress.value) {
      await updateAddress(editingAddress.value.id, data)
      ElMessage.success('地址已更新')
    } else {
      await createAddress(data)
      ElMessage.success('地址已添加')
    }
    formVisible.value = false
    await fetchAddresses()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定要删除这个地址吗？')
  await deleteAddress(id)
  await fetchAddresses()
  ElMessage.success('地址已删除')
}

async function handleSetDefault(id) {
  await setDefaultAddress(id)
  await fetchAddresses()
  ElMessage.success('已设为默认地址')
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>
