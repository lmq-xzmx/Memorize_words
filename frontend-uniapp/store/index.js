import { createStore } from 'vuex'
import user from './modules/user'
import permission from './modules/permission'
import app from './modules/app'

const store = createStore({
  modules: {
    user,
    permission,
    app
  },
  strict: process.env.NODE_ENV !== 'production'
})

export default store