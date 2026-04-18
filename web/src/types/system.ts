export interface Menu {
  id: string
  name: string
  path: string
  icon: string
  order: number
  hidden: boolean
  permission: string
  parent: string | null
  created_at: string
  updated_at: string
}

export interface Group {
  id: string
  name: string
  created_at: string
  updated_at: string
}
