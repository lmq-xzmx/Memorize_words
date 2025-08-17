// 用户相关类型
export interface User {
  id: string | number
  username: string
  email?: string
  role: string
  isAuthenticated: boolean
  profile: UserProfile | null
  token: string | null
}

export interface UserProfile {
  id: string | number
  username: string
  email: string
  avatar?: string
  nickname?: string
  createdAt: string
  updatedAt: string
}

// 学习相关类型
export interface Word {
  id: string | number
  word: string
  pronunciation?: string
  definition: string
  examples?: string[]
  difficulty?: number
  category?: string
}

export interface LearningProgress {
  wordId: string | number
  progress: number
  lastStudied: string
  correctCount: number
  totalAttempts: number
}

export interface StudySession {
  id: string
  startTime: string
  endTime?: string
  wordsStudied: number
  correctAnswers: number
  totalQuestions: number
}

// 应用状态类型
export interface AppState {
  loading: boolean
  error: string | null
  theme: 'light' | 'dark'
  language: string
}

// 权限相关类型
export type Permission = string
export type Role = 'admin' | 'dean' | 'academic_director' | 'research_leader' | 'teacher' | 'parent' | 'student'

export interface PermissionConfig {
  role: Role
  permissions: Permission[]
}

// 路由相关类型
export interface RoutePermission {
  path: string
  permission: Permission
  requiresAuth: boolean
}

// API相关类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  success: boolean
}

export interface ApiError {
  code: number
  message: string
  details?: any
}

// 通用类型
export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type ID = string | number

// 事件类型
export interface CustomEvent<T = any> {
  type: string
  data: T
  timestamp: number
}

// 配置类型
export interface AppConfig {
  apiBaseUrl: string
  wsBaseUrl: string
  version: string
  environment: 'development' | 'production' | 'test'
}