<script setup lang="ts">
// 홈 뷰에 필요한 상태(data)나 메서드(methods)가 있다면 여기에 정의합니다.
// 현재는 정적 페이지 구성이므로 비워둡니다.

// 버튼 클릭 시 페이지 이동을 위해 Vue Router의 훅을 사용할 수 있습니다.
import { useRouter } from 'vue-router'

const router = useRouter()

// 'AI' 상담 시작하기 버튼 클릭 핸들러
const startAiConsult = () => {
  // /ai 경로로 이동합니다.
  router.push('/ai')
}

// 공고 둘러보기 버튼 클릭 핸들러
const viewNotices = () => {
  // /list 경로로 이동합니다.
  router.push('/list')
}

// 첨부된 HTML 파일에 있던 간단한 JavaScript 함수는 Vue 방식으로 처리하는 것이 좋습니다.
// function toggleClassName(element, event) { ... } 와 같은 함수는 더 이상 필요 없습니다.
</script>

<template>
  <header class="com-header-wrap">
    <div class="ui-breadcrumb">
      <ul class="location">
        <li>
          <strong class="sb">홈</strong>
        </li>
      </ul>
      <div class="info">
        <small>LH · SH · GH 공식 정보 기반</small>
      </div>
    </div>
  </header>
  <main class="layout-contents bgc-pageBg shadow">
    <div class="inner">
      <div>
        <section class="section1">
          <div class="card">
            <div>
              <i class="ui-badge deep">AI 기반 공공주택 정보 플랫폼</i>
            </div>

            <div class="title">
              <span class="txt-gray500">LH, SH, GH</span>의 실제 공고
              문서를 <strong class="txt-blue600">AI</strong>가 분석하여
              정확하고,
              <br />
              <strong class="txt-green500">
                "명확한 답변을 제공합니다!"
              </strong>
            </div>

            <div class="btns">
              <button class="ui-btn fill primary" @click="startAiConsult">
                <strong class="b">'AI'</strong> 상담 시작하기
              </button>
              <button class="ui-btn outlined" @click="viewNotices">
                공고 둘러보기
              </button>
            </div>
          </div>

          <div class="card">
            <div class="icon-has-txt">
              <i class="fa-solid fa-robot txt-violet400"></i>
              <div class="txt">
                <div class="tit">
                  <strong class="txt-blue600">AI</strong> 기반 분석
                </div>
                <div class="desc">실시간 공고 분석</div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="icon-has-txt">
              <i class="fa-solid fa-circle-info txt-blue400"></i>
              <div class="txt">
                <div class="tit">정확한 정보</div>
                <div class="desc">LH · SH · GH 공식문서</div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="icon-has-txt">
              <i class="fa-solid fa-gear txt-orange400"></i>
              <div class="txt">
                <div class="tit">맞춤형 추천</div>
                <div class="desc">개인별 최적화</div>
              </div>
            </div>
          </div>
        </section>

        <section class="section2">
          <div class="card outlined">
            <div class="icon-has-txt">
              <div class="txt">
                <div class="tit">1,999</div>
                <div class="desc">텍스트 정보</div>
              </div>
            </div>
          </div>
          <div class="card outlined">
            <div class="icon-has-txt">
              <div class="txt">
                <div class="tit">1,999</div>
                <div class="desc">텍스트 정보</div>
              </div>
            </div>
          </div>
          <div class="card outlined">
            <div class="icon-has-txt">
              <div class="txt">
                <div class="tit">1,999</div>
                <div class="desc">텍스트 정보</div>
              </div>
            </div>
          </div>
          <div class="card outlined">
            <div class="icon-has-txt">
              <div class="txt">
                <div class="tit">1,999</div>
                <div class="desc">텍스트 정보</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </main>
  </template>

<style scoped>
/* HomeView.vue에만 적용될 스타일이 있다면 여기에 작성합니다. */
/* 현재는 원본 HTML에 연결된 style.css 파일을 전역적으로 사용한다고 가정합니다. */
</style>