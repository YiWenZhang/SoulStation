<script setup lang="ts">
// 清空原有联调测试代码，只保留路由出口所需的基础结构即可
</script>

<template>
  <!-- 核心：添加路由出口，所有路由组件（Login/Register/Home）都会渲染在这里 -->
  <router-view />
</template>

<style scoped>
/* 可保留全局基础样式，也可清空，不影响核心功能 */
</style>
