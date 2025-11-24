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
      component: HomeView, // src/views/HomeView.vue 파일을 연결합니다.
      meta: {
        title: '홈 - ZIP FIT' 
      }
    },
    // 2. AI 상담 (ai.html 경로)
    {
      path: '/ai',
      name: 'ai',
      // 동적 임포트를 사용하여 페이지 로딩을 최적화합니다.
      component: () => import('../views/AiView.vue'),
      meta: {
        title: 'AI 상담 - ZIP FIT' 
      }
    },
    // 3. 공고 목록 (list.html 경로)
    {
      path: '/list',
      name: 'list',
      // 동적 임포트를 사용하여 페이지 로딩을 최적화합니다.
      component: () => import('../views/ListView.vue'),
      meta: {
        title: '공고 목록 - ZIP FIT' 
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  // 라우트의 meta 속성에 title이 있는지 확인합니다.
  if (to.meta.title) {
    // meta.title이 있다면, document.title을 해당 값으로 설정합니다.
    document.title = to.meta.title as string;
  } else {
    // 없다면, 기본 타이틀을 설정하거나 아무것도 하지 않습니다.
    document.title = '나의 Vue 앱';
  }
  next();
});

export default router