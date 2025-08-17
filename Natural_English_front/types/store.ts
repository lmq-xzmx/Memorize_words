import type { User, Word, LearningProgress, StudySession, AppState } from './index'

// Vuex State 类型定义
export interface RootState {
  user: UserState
  learning: LearningState
  app: AppState
  words: WordsState
}

export interface UserState {
  isAuthenticated: boolean
  profile: User['profile']
  token: string | null
}

export interface LearningState {
  currentWord: Word | null
  learningProgress: Record<string | number, LearningProgress>
  studySession: StudySession | null
}

export interface WordsState {
  currentWordList: Word[]
  selectedWords: Word[]
  searchResults: Word[]
  favorites: Word[]
}

// Mutations 类型定义
export interface UserMutations {
  SET_USER_AUTHENTICATED: (state: UserState, status: boolean) => void
  SET_USER_PROFILE: (state: UserState, profile: User['profile']) => void
  SET_USER_TOKEN: (state: UserState, token: string | null) => void
  CLEAR_USER_DATA: (state: UserState) => void
}

export interface LearningMutations {
  SET_CURRENT_WORD: (state: LearningState, word: Word | null) => void
  UPDATE_LEARNING_PROGRESS: (state: LearningState, progress: { wordId: string | number, data: LearningProgress }) => void
  SET_STUDY_SESSION: (state: LearningState, session: StudySession | null) => void
  CLEAR_LEARNING_DATA: (state: LearningState) => void
}

export interface AppMutations {
  SET_LOADING: (state: AppState, loading: boolean) => void
  SET_ERROR: (state: AppState, error: string | null) => void
  SET_THEME: (state: AppState, theme: 'light' | 'dark') => void
  SET_LANGUAGE: (state: AppState, language: string) => void
}

export interface WordsMutations {
  SET_CURRENT_WORD_LIST: (state: WordsState, words: Word[]) => void
  SET_SELECTED_WORDS: (state: WordsState, words: Word[]) => void
  SET_SEARCH_RESULTS: (state: WordsState, words: Word[]) => void
  ADD_TO_FAVORITES: (state: WordsState, word: Word) => void
  REMOVE_FROM_FAVORITES: (state: WordsState, wordId: string | number) => void
  CLEAR_WORDS_DATA: (state: WordsState) => void
}

// Actions 类型定义
export interface UserActions {
  login: (context: any, credentials: { username: string, password: string }) => Promise<void>
  logout: (context: any) => Promise<void>
  fetchUserProfile: (context: any) => Promise<void>
  updateProfile: (context: any, profileData: Partial<User['profile']>) => Promise<void>
}

export interface LearningActions {
  startStudySession: (context: any) => Promise<void>
  endStudySession: (context: any) => Promise<void>
  updateWordProgress: (context: any, data: { wordId: string | number, correct: boolean }) => Promise<void>
  fetchLearningProgress: (context: any) => Promise<void>
}

export interface WordsActions {
  fetchWords: (context: any, params?: any) => Promise<void>
  searchWords: (context: any, query: string) => Promise<void>
  addToFavorites: (context: any, word: Word) => Promise<void>
  removeFromFavorites: (context: any, wordId: string | number) => Promise<void>
}

// Getters 类型定义
export interface RootGetters {
  isAuthenticated: (state: RootState) => boolean
  currentUser: (state: RootState) => User['profile']
  currentTheme: (state: RootState) => string
  learningStats: (state: RootState) => {
    totalWords: number
    studiedWords: number
    accuracy: number
  }
  favoriteWords: (state: RootState) => Word[]
}