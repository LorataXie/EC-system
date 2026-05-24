<template>
  <el-dialog :model-value="visible" :title="props.address?'编辑地址':'新增地址'" @update:model-value="$emit('close')" width="560px" destroy-on-close>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
      <el-form-item label="收货人" prop="recipient_name">
        <el-input v-model="form.recipient_name" placeholder="请输入收货人姓名" />
      </el-form-item>
      <el-form-item label="联系电话" prop="phone">
        <el-input v-model="form.phone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="搜索地址">
        <div class="search-wrapper">
          <el-input v-model="mapSearch" placeholder="输入地址关键词，如：北京邮电、万达..." @input="onSearch" clearable />
          <div v-if="mapTips.length" class="search-dropdown">
            <div v-for="t in mapTips" :key="t.id||t.name" class="search-item" @click="selectTip(t)">
              <div class="tip-name">{{ t.name }}</div>
              <div class="tip-district">{{ t.district }} {{ t.address }}</div>
            </div>
          </div>
        </div>
      </el-form-item>
      <el-form-item label="所在地区" prop="region">
        <el-cascader v-model="form.region" :options="regionData" placeholder="省/市/区" clearable filterable style="width:100%" />
      </el-form-item>
      <el-form-item label="详细地址" prop="address_line1">
        <el-input v-model="form.address_line1" placeholder="街道、门牌号等" />
      </el-form-item>
      <el-form-item label="地址补充">
        <el-input v-model="form.address_line2" placeholder="楼层、房间号等（选填）" />
      </el-form-item>
      <el-form-item label="邮政编码">
        <el-input v-model="form.postal_code" placeholder="邮政编码（选填）" />
      </el-form-item>
      <el-form-item label="设为默认">
        <el-switch v-model="form.is_default" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { regionData } from '@/utils/regions'

const props = defineProps({ visible: Boolean, address: Object })
const emit = defineEmits(['close', 'save'])
const formRef = ref(null)
const mapSearch = ref('')
const mapTips = ref([])
let amapAC = null
let searchTimer = null

const form = reactive({
  recipient_name: '', phone: '',
  region: [], address_line1: '', address_line2: '', postal_code: '', is_default: false,
})

const validateRegion = (_r, _v, cb) => { form.region.length===0 ? cb(new Error('请选择所在地区')) : cb() }
const rules = {
  recipient_name: [{ required: true, message: '请输入收货人' }],
  phone: [{ required: true, message: '请输入联系电话' }, { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }],
  region: [{ validator: validateRegion, trigger: 'change' }],
  address_line1: [{ required: true, message: '请输入详细地址' }],
}

function resetForm() {
  Object.assign(form, { recipient_name:'', phone:'', region:[], address_line1:'', address_line2:'', postal_code:'', is_default:false })
  mapSearch.value = ''; mapTips.value = []
  nextTick(() => formRef.value?.clearValidate())
}

watch(() => props.visible, (val) => {
  if (!val) return
  if (props.address) {
    Object.assign(form, {
      recipient_name: props.address.recipient_name||'', phone: props.address.phone||'',
      region: [props.address.state||'', props.address.city||''].filter(Boolean),
      address_line1: props.address.address_line1||'', address_line2: props.address.address_line2||'',
      postal_code: props.address.postal_code||'', is_default: props.address.is_default||false,
    })
    mapSearch.value = ''; mapTips.value = []
  } else { resetForm() }
  // Ensure AMap is loaded
  ensureAMap()
})

function ensureAMap() {
  if (window.AMap) { initAutocomplete(); return }
  // Already loading?
  if (document.querySelector('script[src*="webapi.amap.com"]')) return
  const script = document.createElement('script')
  script.src = 'https://webapi.amap.com/maps?v=2.0&key=efb252f9c97e90648513ddff306b5226&plugin=AMap.Autocomplete'
  script.onload = () => initAutocomplete()
  document.head.appendChild(script)
}

function initAutocomplete() {
  if (amapAC) return
  window.AMap.plugin('AMap.Autocomplete', () => {
    amapAC = new window.AMap.Autocomplete({ city: '', citylimit: false })
  })
}

function onSearch(val) {
  if (searchTimer) clearTimeout(searchTimer)
  if (!val || val.length < 1) { mapTips.value = []; return }
  searchTimer = setTimeout(() => {
    if (!amapAC) { mapTips.value = []; return }
    amapAC.search(val, (status, result) => {
      if (status === 'complete' && result.tips) {
        mapTips.value = result.tips.filter(t => t.location).slice(0, 8)
      } else { mapTips.value = [] }
    })
  }, 300)
}

function selectTip(tip) {
  const parts = (tip.district||'').split('-')
  form.region = parts.length >= 2 ? [parts[0], parts[1]] : [tip.district].filter(Boolean)
  form.address_line1 = (tip.name||'') + (tip.address||'')
  mapSearch.value = ''; mapTips.value = []
}

function handleSubmit() {
  formRef.value.validate(valid => {
    if (!valid) return
    const [state, city] = form.region
    emit('save', {
      recipient_name: form.recipient_name, phone: form.phone,
      country: '中国', state: state||'', city: city||'',
      address_line1: form.address_line1, address_line2: form.address_line2,
      postal_code: form.postal_code, is_default: form.is_default,
    })
  })
}
</script>

<style scoped>
.search-wrapper { position: relative; }
.search-dropdown { position: absolute; top: 100%; left: 0; right: 0; z-index: 2000; background: #fff; border: 1px solid #e4e7ed; border-radius: 4px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); max-height: 260px; overflow-y: auto; }
.search-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #f5f5f5; }
.search-item:hover { background: #ecf5ff; }
.search-item:last-child { border-bottom: none; }
.tip-name { font-size: 14px; font-weight: 500; color: #333; }
.tip-district { font-size: 12px; color: #999; margin-top: 2px; }
</style>
