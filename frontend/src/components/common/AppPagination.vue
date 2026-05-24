<template>
  <div class="app-pagination" v-if="total > 0">
    <el-pagination
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :page-sizes="[12, 20, 40, 60]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      background
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  total: { type: Number, default: 0 },
  pageSizeProp: { type: Number, default: 20 },
})

const emit = defineEmits(['page-change', 'size-change'])

const currentPage = ref(1)
const pageSize = ref(props.pageSizeProp)

watch(() => props.total, () => {
  currentPage.value = 1
})

function handlePageChange(page) {
  emit('page-change', page)
}

function handleSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  emit('size-change', size)
}
</script>

<style scoped>
.app-pagination { display: flex; justify-content: center; padding: 24px 0; }
</style>
