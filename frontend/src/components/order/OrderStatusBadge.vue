<template>
  <el-tag size="small">{{ status }}</el-tag>
</template>

<script setup>
defineProps({ status: { type: String, required: true } })
</script>
