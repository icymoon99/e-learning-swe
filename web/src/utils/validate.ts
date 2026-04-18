/**
 * 校验用户名
 */
export function validateUsername(username: string): boolean {
  return username.trim().length >= 2
}

/**
 * 校验密码
 */
export function validatePassword(password: string): boolean {
  return password.length >= 6
}
