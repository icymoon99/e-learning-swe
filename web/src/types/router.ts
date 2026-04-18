import type { RouteMeta } from 'vue-router'

export interface AppRouteMeta extends RouteMeta {
  title?: string
  icon?: string
  hidden?: boolean
  keepAlive?: boolean
  permission?: string
  activeMenu?: string
  layout?: 'default' | 'blank'
}
