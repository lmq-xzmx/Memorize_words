import { createStore, Store } from 'vuex'
import type { InjectionKey } from 'vue'
import auth from './modules/auth'
import user from './modules/user'
import dashboard from './modules/dashboard'

export interface RootState {
  version: string
}

const store = createStore<RootState>({
  state: {
    version: '1.0.0'
  },
  modules: {
    auth,
    user,
    dashboard
  }
})

export const key: InjectionKey<Store<RootState>> = Symbol()

export default store