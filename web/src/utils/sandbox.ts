import type { SandboxType, SandboxStatus } from '@/types/sandbox'

const TYPE_TAG_MAP: Record<SandboxType, string> = {
  localdocker: 'primary',
  remotedocker: 'warning',
  localsystem: 'success',
  remotesystem: '',
}

const STATUS_TAG_MAP: Record<SandboxStatus, string> = {
  active: 'success',
  inactive: 'info',
  error: 'danger',
}

export function getTypeTagType(type: SandboxType): string {
  return TYPE_TAG_MAP[type] || 'info'
}

export function getStatusTagType(status: SandboxStatus): string {
  return STATUS_TAG_MAP[status] || 'info'
}
