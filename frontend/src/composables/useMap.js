import { ref } from 'vue'

const AMAP_KEY = 'efb252f9c97e90648513ddff306b5226' // 在此填入高德地图 JS API Key（从 https://lbs.amap.com/ 获取）
const loaded = ref(false)
let loadPromise = null

export function useMap() {
  function loadAMap() {
    if (loaded.value) return Promise.resolve(window.AMap)
    if (loadPromise) return loadPromise

    if (!AMAP_KEY) {
      console.warn('AMap Key 未配置，地址自动完成功能不可用。请在 src/composables/useMap.js 中填入 Key')
      return Promise.resolve(null)
    }

    loadPromise = new Promise((resolve, reject) => {
      if (typeof window.AMap !== 'undefined') {
        loaded.value = true
        resolve(window.AMap)
        return
      }

      const script = document.createElement('script')
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}&plugin=AMap.Autocomplete,AMap.Geocoder`
      script.onload = () => {
        loaded.value = true
        resolve(window.AMap)
      }
      script.onerror = () => {
        loadPromise = null
        reject(new Error('AMap 加载失败'))
      }
      document.head.appendChild(script)
    })

    return loadPromise
  }

  return { loadAMap, amapLoaded: loaded }
}
