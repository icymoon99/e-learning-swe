<template>
  <router-view />
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
appStore.init()
</script>
