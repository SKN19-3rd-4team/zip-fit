<script setup lang="ts">
// Vue Router의 컴포넌트들을 임포트합니다.
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="layout-wrap" id="page-wrap">
    <div class="com-nav-wrap">
      <h1>
        <RouterLink to="/" class="ui-logo">
          <div class="icon">
            <i class="icons-home"></i>
          </div>

          <div class="logo-txt">
            <div>
              <strong class="tit sb">
                집핏<strong class="b txt-green400">'</strong>
              </strong>
            </div>
            <div>
              <small>ZIPFIT</small>
            </div>
          </div>
        </RouterLink>
      </h1>

      <nav class="inner">
        <ul>
          <li>
            <RouterLink to="/" class="ui-btn" active-class="active">
              <span class="has-icon">
                <i class="fa-regular fa-house"></i>
                <span class="txt">홈</span>
              </span>
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/ai" class="ui-btn" active-class="active">
              <span class="has-icon">
                <i class="fa-regular fa-message"></i>
                <span class="txt">
                  <strong class="sb txt-blue600">AI</strong>
                  상담
                </span>
              </span>
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/list" class="ui-btn" active-class="active">
              <span class="has-icon">
                <i class="fa-regular fa-file"></i>
                <span class="txt">공고 목록</span>
              </span>
            </RouterLink>
          </li>
        </ul>
      </nav>
    </div>
    <div class="layout-contents-wrap">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
/* App.vue에는 공통 스타일만 남기고, 나머지 스타일은 전역 스타일이나 각 컴포넌트의 스타일로 분리합니다. */
</style>