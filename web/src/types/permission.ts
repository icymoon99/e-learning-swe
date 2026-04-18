export interface MenuItem {
  id: string
  name: string
  path: string
  icon: string
  order: number
  hidden: boolean
  permission: string
  children?: MenuItem[]
}
