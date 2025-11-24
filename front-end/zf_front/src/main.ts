// import './assets/main.css' // 기본 스타일 파일 (프로젝트 설정에 따라 다름)
import './assets/style/style.css' // ✅ 원본 HTML에 있던 메인 스타일시트 추가
import './assets/images/icons/css/all.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router' // ✅ 우리가 설정한 라우터 임포트

const app = createApp(App)

app.use(createPinia()) // Pinia 사용 설정
app.use(router) // ✅ 라우터 사용 설정 (이 줄이 없으면 페이지 이동이 안 됨)

// ✅ Vue 애플리케이션을 public/index.html의 <div id="app"> 요소에 연결
app.mount('#app')