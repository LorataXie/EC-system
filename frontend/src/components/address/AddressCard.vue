<template>
  <div class="address-card" :class="{ default: address.is_default }">
    <div class="address-info">
      <div class="address-header">
        <strong>{{ address.recipient_name }}</strong>
        <span>{{ address.phone }}</span>
        <el-tag v-if="address.is_default" type="danger" size="small">默认</el-tag>
      </div>
      <p class="address-text">{{ address.state }} {{ address.city }} {{ address.address_line1 }} {{ address.address_line2 }}</p>
      <p class="postal" v-if="address.postal_code">邮编：{{ address.postal_code }}</p>
    </div>
    <div class="address-actions">
      <el-button text @click="$emit('edit', address)">编辑</el-button>
      <el-button text type="danger" @click="$emit('delete', address.id)">删除</el-button>
      <el-button text v-if="!address.is_default" @click="$emit('set-default', address.id)">设为默认</el-button>
    </div>
  </div>
</template>

<script setup>
defineProps({ address: { type: Object, required: true } })
defineEmits(['edit', 'delete', 'set-default'])
</script>

<style scoped>
.address-card { border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; }
.address-card.default { border-color: #e4393c; }
.address-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.address-text { color: #666; }
.postal { color: #999; font-size: 12px; margin-top: 4px; }
.address-actions { display: flex; flex-direction: column; }
</style>
