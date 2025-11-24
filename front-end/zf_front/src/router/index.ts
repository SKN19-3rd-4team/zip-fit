import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  // URL의 히스토리 모드를 설정합니다.
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 1. 홈 (index copy.html 내용)
    {
      path: '/',
      name: 'home',
      component: HomeView // src/views/HomeView.vue 파일을 연결합니다.
    },
    // 2. AI 상담 (ai.html 경로)
    {
      path: '/ai',
      name: 'ai',
      // 동적 임포트를 사용하여 페이지 로딩을 최적화합니다.
      component: () => import('../views/AiView.vue')
    },
    // 3. 공고 목록 (list.html 경로)
    {
      path: '/list',
      name: 'list',
      // 동적 임포트를 사용하여 페이지 로딩을 최적화합니다.
      component: () => import('../views/ListView.vue')
    }
  ]
})

export default router